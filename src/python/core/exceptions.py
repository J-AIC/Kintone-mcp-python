"""
共通例外クラス

アプリケーション全体で使用する例外クラスを定義
"""

from typing import Optional, Dict, Any


class KintoneMCPError(Exception):
    """Kintone MCPサーバーの基底例外クラス"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """例外情報を辞書形式で返す"""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


class AuthenticationError(KintoneMCPError):
    """認証エラー"""
    pass


class AuthorizationError(KintoneMCPError):
    """認可エラー"""
    pass


class ConnectionError(KintoneMCPError):
    """接続エラー"""
    pass


class ConfigurationError(KintoneMCPError):
    """設定エラー"""
    pass


class KintoneAPIError(KintoneMCPError):
    """Kintone API エラー"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict[str, Any]] = None):
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(
            message,
            error_code=f"KINTONE_API_{status_code}" if status_code else "KINTONE_API_ERROR",
            details={"status_code": status_code, "response": response_data}
        )


class MCPProtocolError(KintoneMCPError):
    """MCPプロトコルエラー"""
    pass


class ValidationError(KintoneMCPError):
    """バリデーションエラー"""
    pass


class ServerInitializationError(KintoneMCPError):
    """サーバー初期化エラー"""
    pass 