"""
統合設定管理

アプリケーション全体の設定を統一管理
"""

import os
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Optional, Literal

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

from ..models.kintone_credentials import KintoneCredentials

# .envファイルを明示的に読み込み
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


class MCPMode(str, Enum):
    """MCPサーバーモード"""
    NATIVE = "native"           # カスタムMCP実装
    FASTAPI_MCP = "fastapi-mcp" # FastAPI-MCP実装
    BOTH = "both"               # 両方同時実行


class KintoneClientType(str, Enum):
    """Kintoneクライアントタイプ"""
    NODEJS = "nodejs"           # Node.js @kintone/rest-api-client
    PYTHON = "python"           # Python kintone SDK


class Settings(BaseSettings):
    """アプリケーション統合設定"""
    
    # サーバー設定
    server_host: str = Field(default="127.0.0.1", description="サーバーホスト")
    server_port: int = Field(default=7000, description="サーバーポート")
    debug: bool = Field(default=False, description="デバッグモード")
    
    # MCP設定
    mcp_mode: MCPMode = Field(default=MCPMode.NATIVE, description="MCPサーバーモード")
    mcp_native_path: str = Field(default="/mcp/rpc", description="ネイティブMCPエンドポイント")
    mcp_fastapi_path: str = Field(default="/mcp", description="FastAPI-MCPマウントパス")
    
    # Kintone設定
    kintone_domain: Optional[str] = Field(default=None, description="Kintoneドメイン")
    kintone_username: Optional[str] = Field(default=None, description="Kintoneユーザー名")
    kintone_password: Optional[str] = Field(default=None, description="Kintoneパスワード")
    kintone_api_token: Optional[str] = Field(default=None, description="Kintone APIトークン")
    kintone_client_type: KintoneClientType = Field(
        default=KintoneClientType.NODEJS, 
        description="Kintoneクライアントタイプ"
    )
    
    # ログ設定
    log_level: str = Field(default="INFO", description="ログレベル")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="ログフォーマット"
    )
    
    model_config = SettingsConfigDict(
        env_file=str(env_path) if env_path.exists() else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @validator('mcp_mode', pre=True)
    def validate_mcp_mode(cls, v):
        """MCPモードの検証"""
        if isinstance(v, str):
            try:
                return MCPMode(v.lower())
            except ValueError:
                raise ValueError(f"Invalid MCP mode: {v}. Must be one of: {[mode.value for mode in MCPMode]}")
        return v
    
    @validator('kintone_client_type', pre=True)
    def validate_kintone_client_type(cls, v):
        """Kintoneクライアントタイプの検証"""
        if isinstance(v, str):
            try:
                return KintoneClientType(v.lower())
            except ValueError:
                raise ValueError(f"Invalid client type: {v}. Must be one of: {[ct.value for ct in KintoneClientType]}")
        return v
    
    def get_kintone_credentials(self) -> Optional[KintoneCredentials]:
        """
        Kintone認証情報を取得
        
        Returns:
            KintoneCredentials: 認証情報オブジェクト、設定されていない場合はNone
            
        Raises:
            ValueError: 認証情報の形式が不正な場合
        """
        if not self.kintone_domain:
            return None
        
        try:
            return KintoneCredentials(
                domain=self.kintone_domain,
                username=self.kintone_username,
                password=self.kintone_password,
                api_token=self.kintone_api_token
            )
        except Exception as e:
            raise ValueError(f"Kintone認証情報の設定が不正です: {e}")
    
    @property
    def has_kintone_config(self) -> bool:
        """Kintone設定が存在するかチェック"""
        return bool(self.kintone_domain)
    
    @property
    def is_native_mcp_enabled(self) -> bool:
        """ネイティブMCPが有効か"""
        return self.mcp_mode in [MCPMode.NATIVE, MCPMode.BOTH]
    
    @property
    def is_fastapi_mcp_enabled(self) -> bool:
        """FastAPI-MCPが有効か"""
        return self.mcp_mode in [MCPMode.FASTAPI_MCP, MCPMode.BOTH]
    
    def get_server_url(self) -> str:
        """サーバーURLを取得"""
        return f"http://{self.server_host}:{self.server_port}"


@lru_cache()
def get_settings() -> Settings:
    """設定のシングルトンインスタンスを取得"""
    return Settings()


def get_kintone_credentials() -> Optional[KintoneCredentials]:
    """
    Kintone認証情報を取得するヘルパー関数
    
    Returns:
        KintoneCredentials: 認証情報オブジェクト、設定されていない場合はNone
    """
    settings = get_settings()
    return settings.get_kintone_credentials() 