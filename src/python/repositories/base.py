"""
Base Repository Classes

リポジトリ基底クラスと共通機能の定義
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging

from ..models.kintone_credentials import KintoneCredentials
from .nodejs_kintone_client import NodeJSKintoneClient as KintoneClient, NodeJSKintoneClientFactory
from ..utils.exceptions import (
    KintoneBaseError,
    KintoneAPIError,
    KintoneValidationError
)
from ..utils.error_handler import (
    ErrorHandler,
    handle_kintone_errors,
    validate_required_params
)

logger = logging.getLogger(__name__)


class BaseKintoneRepository(ABC):
    """Kintoneリポジトリの基底クラス"""
    
    def __init__(self, credentials: KintoneCredentials):
        """
        Args:
            credentials: Kintone認証情報
        """
        self.credentials = credentials
        self.client = NodeJSKintoneClientFactory.create_from_credentials(credentials)
    
    async def close(self):
        """リソースのクリーンアップ"""
        await self.client.close()
    
    def handle_kintone_error(self, error: Exception, operation: str, **context) -> None:
        """
        Kintone API エラーの共通ハンドリング
        
        Args:
            error: 発生した例外
            operation: 実行していた操作名
            **context: エラーのコンテキスト情報
            
        Raises:
            KintoneBaseError: kintone関連エラー
        """
        # エラーをログに記録
        ErrorHandler.log_error(error, {"operation": operation, **context})
        
        # カスタム例外の場合はそのまま再発生
        if isinstance(error, KintoneBaseError):
            raise error
        
        # 標準例外をKintoneBaseErrorに変換
        if isinstance(error, ValueError):
            raise KintoneValidationError(
                message=f"{operation}でバリデーションエラーが発生しました: {str(error)}",
                details={"operation": operation, "original_error": str(error), **context}
            )
        else:
            raise KintoneBaseError(
                message=f"{operation}で予期しないエラーが発生しました: {str(error)}",
                error_code="UNEXPECTED_ERROR",
                details={"operation": operation, "original_error": str(error), **context}
            )
    
    def _validate_app_id(self, app_id: Optional[int]) -> None:
        """
        アプリIDのバリデーション
        
        Args:
            app_id: アプリID
            
        Raises:
            KintoneValidationError: アプリIDが無効な場合
        """
        if app_id is None or app_id <= 0:
            raise KintoneValidationError(
                message="有効なアプリIDが必要です",
                field_errors={"app_id": "正の整数である必要があります"},
                validation_type="app_id_validation"
            )
    
    def _validate_record_id(self, record_id: Optional[int]) -> None:
        """
        レコードIDのバリデーション
        
        Args:
            record_id: レコードID
            
        Raises:
            KintoneValidationError: レコードIDが無効な場合
        """
        if record_id is None or record_id <= 0:
            raise KintoneValidationError(
                message="有効なレコードIDが必要です",
                field_errors={"record_id": "正の整数である必要があります"},
                validation_type="record_id_validation"
            ) 