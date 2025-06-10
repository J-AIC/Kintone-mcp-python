"""
統一レスポンスモデル

アプリケーション全体で使用するレスポンス形式を定義
"""

from datetime import datetime
from typing import Any, Optional, Dict, List, Union
from pydantic import BaseModel, Field


class APIResponse(BaseModel):
    """標準APIレスポンス"""
    success: bool = Field(description="処理成功フラグ")
    data: Optional[Any] = Field(default=None, description="レスポンスデータ")
    error: Optional[str] = Field(default=None, description="エラーメッセージ")
    error_code: Optional[str] = Field(default=None, description="エラーコード")
    timestamp: datetime = Field(default_factory=datetime.now, description="処理時刻")
    
    @classmethod
    def success_response(cls, data: Any = None) -> "APIResponse":
        """成功レスポンスを作成"""
        return cls(success=True, data=data)
    
    @classmethod
    def error_response(cls, error: str, error_code: Optional[str] = None, data: Any = None) -> "APIResponse":
        """エラーレスポンスを作成"""
        return cls(success=False, error=error, error_code=error_code, data=data)


class HealthCheckResponse(BaseModel):
    """ヘルスチェックレスポンス"""
    status: str = Field(description="サーバーステータス")
    service: str = Field(description="サービス名")
    version: str = Field(description="バージョン")
    server_info: Optional[Dict[str, Any]] = Field(default=None, description="サーバー情報")
    connection_info: Optional[Dict[str, Any]] = Field(default=None, description="接続情報")


class KintoneRecordResponse(BaseModel):
    """Kintoneレコードレスポンス"""
    success: bool
    record_id: Optional[str] = None
    revision: Optional[str] = None
    records: Optional[List[Dict[str, Any]]] = None
    total_count: Optional[int] = None
    error: Optional[str] = None


class KintoneAppResponse(BaseModel):
    """Kintoneアプリレスポンス"""
    success: bool
    apps: Optional[List[Dict[str, Any]]] = None
    properties: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class MCPToolResponse(BaseModel):
    """MCPツールレスポンス"""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    tool_name: Optional[str] = None
    execution_time: Optional[float] = None 