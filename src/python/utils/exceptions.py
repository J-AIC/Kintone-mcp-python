"""
Kintone MCP Server - Custom Exception Classes
カスタム例外クラス群の定義

このモジュールは、kintone MCP サーバーで使用される
カスタム例外クラスを定義します。
"""

from typing import Optional, Dict, Any
import json
from datetime import datetime


class KintoneError(Exception):
    """kintone関連エラーの基底クラス"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


# 既存コードとの互換性のためのエイリアス
KintoneBaseError = KintoneError


class KintoneAPIError(KintoneError):
    """kintone API呼び出しエラー"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 kintone_error_code: Optional[str] = None, 
                 http_status: Optional[int] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, details)
        self.kintone_error_code = kintone_error_code
        self.http_status = http_status


class KintoneAuthenticationError(KintoneError):
    """kintone認証エラー"""
    
    def __init__(self, message: str = "kintoneへの認証に失敗しました", 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "KINTONE_AUTHENTICATION_ERROR", details)


class KintonePermissionError(KintoneError):
    """kintone権限エラー"""
    
    def __init__(self, message: str = "この操作を実行する権限がありません", 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "KINTONE_PERMISSION_ERROR", details)


class KintoneValidationError(KintoneError):
    """kintoneパラメータバリデーションエラー"""
    
    def __init__(self, message: str, validation_errors: Optional[list] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "KINTONE_VALIDATION_ERROR", details)
        self.validation_errors = validation_errors or []


class NodeJSWrapperError(KintoneError):
    """Node.jsラッパー実行エラー"""
    
    def __init__(self, message: str, command: Optional[str] = None,
                 exit_code: Optional[int] = None,
                 stderr: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "NODEJS_WRAPPER_ERROR", details)
        self.command = command
        self.exit_code = exit_code
        self.stderr = stderr


class KintoneNetworkError(KintoneError):
    """kintoneネットワークエラー"""
    
    def __init__(self, message: str = "ネットワークエラーが発生しました", 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "KINTONE_NETWORK_ERROR", details)


class KintoneTimeoutError(KintoneError):
    """kintoneタイムアウトエラー"""
    
    def __init__(self, message: str = "リクエストがタイムアウトしました", 
                 timeout_seconds: Optional[int] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "KINTONE_TIMEOUT_ERROR", details)
        self.timeout_seconds = timeout_seconds


class KintoneConfigurationError(KintoneError):
    """kintone設定エラー"""
    
    def __init__(self, message: str, missing_config: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "KINTONE_CONFIGURATION_ERROR", details)
        self.missing_config = missing_config


def create_error_from_nodejs_response(response_data: Dict[str, Any]) -> KintoneError:
    """Node.jsレスポンスからエラーオブジェクトを作成"""
    
    if not response_data.get('success', True):
        error_info = response_data.get('error', {})
        error_code = error_info.get('code', 'UNKNOWN_ERROR')
        message = error_info.get('message', 'Unknown error occurred')
        details = error_info.get('details', {})
        
        # エラーコードに基づいて適切な例外クラスを選択
        if error_code == 'KINTONE_AUTHENTICATION_ERROR':
            return KintoneAuthenticationError(message, details)
        elif error_code == 'KINTONE_PERMISSION_ERROR':
            return KintonePermissionError(message, details)
        elif error_code == 'KINTONE_VALIDATION_ERROR':
            return KintoneValidationError(message, details=details)
        elif error_code == 'KINTONE_NETWORK_ERROR':
            return KintoneNetworkError(message, details)
        elif error_code == 'NODEJS_WRAPPER_ERROR':
            return NodeJSWrapperError(message, details=details)
        elif error_code == 'KINTONE_API_ERROR':
            return KintoneAPIError(
                message, 
                error_code,
                details.get('kintone_error_code'),
                details.get('http_status'),
                details
            )
        else:
            return KintoneError(message, error_code, details)
    
    return KintoneError("Unknown error occurred")


def format_validation_error(validation_error: Exception) -> KintoneValidationError:
    """Pydanticバリデーションエラーをフォーマット"""
    
    from pydantic import ValidationError
    
    if isinstance(validation_error, ValidationError):
        error_messages = []
        for error in validation_error.errors():
            field_path = '.'.join(str(loc) for loc in error['loc'])
            error_messages.append(f"{field_path}: {error['msg']}")
        
        message = f"パラメータバリデーションエラー: {', '.join(error_messages)}"
        return KintoneValidationError(
            message, 
            validation_errors=validation_error.errors(),
            details={'raw_errors': validation_error.errors()}
        )
    else:
        return KintoneValidationError(str(validation_error))


def parse_nodejs_error_response(response: Dict[str, Any]) -> KintoneError:
    """Node.jsからのエラーレスポンスを解析してKintoneErrorを作成"""
    return create_error_from_nodejs_response(response) 