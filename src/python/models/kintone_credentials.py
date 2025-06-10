"""
Kintone認証情報のモデル定義

Kintoneへの接続に必要な認証情報を管理するPydanticモデル
"""

from typing import Optional, Union
from pydantic import BaseModel, Field, field_validator, model_validator
from urllib.parse import urlparse


class KintoneCredentials(BaseModel):
    """
    Kintone認証情報モデル
    
    ユーザー名/パスワード認証またはAPIトークン認証をサポート
    """
    
    domain: str = Field(
        ..., 
        description="Kintoneドメイン（例: your-domain.cybozu.com）",
        min_length=1
    )
    username: Optional[str] = Field(
        None, 
        description="Kintoneユーザー名（ユーザー名/パスワード認証時に必要）"
    )
    password: Optional[str] = Field(
        None, 
        description="Kintoneパスワード（ユーザー名/パスワード認証時に必要）"
    )
    api_token: Optional[str] = Field(
        None, 
        description="KintoneAPIトークン（APIトークン認証時に必要）"
    )
    
    @field_validator('domain')
    @classmethod
    def validate_domain(cls, v: str) -> str:
        """ドメインの形式をバリデーション"""
        if not v:
            raise ValueError("ドメインは必須です")
        
        # プロトコルが含まれている場合は除去
        if v.startswith(('http://', 'https://')):
            parsed = urlparse(v)
            v = parsed.netloc
        
        # 基本的なドメイン形式チェック
        if not v or '.' not in v:
            raise ValueError("有効なドメイン形式で入力してください（例: your-domain.cybozu.com）")
        
        return v.lower()
    
    @model_validator(mode='after')
    def validate_auth_method(self):
        """認証方法のバリデーション"""
        username = self.username
        password = self.password
        api_token = self.api_token
        
        # APIトークン認証の場合
        if api_token:
            if username or password:
                raise ValueError("APIトークン認証時は、ユーザー名とパスワードは不要です")
            return self
        
        # ユーザー名/パスワード認証の場合
        if username and password:
            return self
        
        # どちらの認証方法も不完全な場合
        if username and not password:
            raise ValueError("ユーザー名が指定されている場合、パスワードも必要です")
        if password and not username:
            raise ValueError("パスワードが指定されている場合、ユーザー名も必要です")
        
        # 認証情報が全く提供されていない場合
        raise ValueError("APIトークンまたはユーザー名/パスワードのいずれかが必要です")
    
    @property
    def is_api_token_auth(self) -> bool:
        """APIトークン認証かどうかを判定"""
        return bool(self.api_token)
    
    @property
    def is_basic_auth(self) -> bool:
        """ユーザー名/パスワード認証かどうかを判定"""
        return bool(self.username and self.password)
    
    @property
    def base_url(self) -> str:
        """KintoneのベースURLを取得"""
        return f"https://{self.domain}"
    
    def get_auth_headers(self) -> dict:
        """認証ヘッダーを取得"""
        if self.is_api_token_auth:
            return {
                "X-Cybozu-API-Token": self.api_token
            }
        elif self.is_basic_auth:
            import base64
            credentials = f"{self.username}:{self.password}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            return {
                "Authorization": f"Basic {encoded_credentials}"
            }
        else:
            raise ValueError("有効な認証情報が設定されていません")
    
    model_config = {
        # 例
        "json_schema_extra": {
            "examples": [
                {
                    "domain": "your-domain.cybozu.com",
                    "username": "your-username",
                    "password": "your-password"
                },
                {
                    "domain": "your-domain.cybozu.com",
                    "api_token": "your-api-token"
                }
            ]
        }
    }


class KintoneConnectionInfo(BaseModel):
    """
    Kintone接続情報モデル
    
    接続状態や基本情報を表現
    """
    
    domain: str = Field(..., description="接続先ドメイン")
    auth_method: str = Field(..., description="認証方法（api_token または basic_auth）")
    base_url: str = Field(..., description="ベースURL")
    is_connected: bool = Field(default=False, description="接続状態")
    
    @classmethod
    def from_credentials(cls, credentials: KintoneCredentials, is_connected: bool = False) -> "KintoneConnectionInfo":
        """KintoneCredentialsから接続情報を生成"""
        auth_method = "api_token" if credentials.is_api_token_auth else "basic_auth"
        
        return cls(
            domain=credentials.domain,
            auth_method=auth_method,
            base_url=credentials.base_url,
            is_connected=is_connected
        ) 