"""
Configuration Management

環境変数の読み込みと設定管理
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

from .models.kintone_credentials import KintoneCredentials

# .envファイルを明示的に読み込み
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


class Settings(BaseSettings):
    """アプリケーション設定"""
    
    # サーバー設定
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=7000)
    debug: bool = Field(default=False)
    
    # Kintone認証情報
    kintone_domain: Optional[str] = Field(default=None)
    kintone_username: Optional[str] = Field(default=None)
    kintone_password: Optional[str] = Field(default=None)
    kintone_api_token: Optional[str] = Field(default=None)
    
    model_config = SettingsConfigDict(
        env_file=str(env_path) if env_path.exists() else None,
        env_file_encoding="utf-8"
    )
    
    def get_kintone_credentials(self) -> Optional[KintoneCredentials]:
        """
        環境変数からKintone認証情報を取得
        
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