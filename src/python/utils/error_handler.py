"""
Kintone MCP Server - Error Handling Middleware
エラーハンドリングミドルウェア

このモジュールは、MCP仕様準拠のエラーレスポンス生成と
共通エラーハンドリング機能を提供します。
"""

import logging
import traceback
import subprocess
import asyncio
from typing import Dict, Any, Optional, Callable, Union
from functools import wraps
import json
from enum import IntEnum
from datetime import datetime

from .exceptions import (
    KintoneBaseError,
    KintoneAPIError,
    KintoneAuthenticationError,
    KintonePermissionError,
    KintoneValidationError,
    NodeJSWrapperError,
    KintoneNetworkError,
    KintoneConfigurationError,
    parse_nodejs_error_response
)

logger = logging.getLogger(__name__)


class MCPErrorCode(IntEnum):
    """
    MCP標準エラーコード（互換性のため）
    """
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_ERROR_START = -32000
    SERVER_ERROR_END = -32099


class MCPError(Exception):
    """
    MCP仕様準拠のエラークラス（互換性のため）
    新しいコードではKintoneBaseErrorとその派生クラスを使用してください
    """
    
    def __init__(
        self, 
        code: MCPErrorCode, 
        message: str, 
        data: Optional[Dict[str, Any]] = None,
        request_id: Optional[Union[str, int]] = None
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data or {}
        self.request_id = request_id
    
    def to_dict(self) -> Dict[str, Any]:
        """エラー情報を辞書形式で返す"""
        response = {
            "jsonrpc": "2.0",
            "error": {
                "code": int(self.code),
                "message": self.message
            }
        }
        
        if self.data:
            response["error"]["data"] = self.data
        
        if self.request_id is not None:
            response["id"] = self.request_id
        
        return response


class ErrorHandler:
    """
    エラーハンドリングミドルウェアクラス
    """
    
    @staticmethod
    def handle_subprocess_error(
        process_result: subprocess.CompletedProcess,
        command: str,
        timeout_occurred: bool = False
    ) -> KintoneBaseError:
        """
        サブプロセス実行エラーを処理
        
        Args:
            process_result: subprocess.run()の結果
            command: 実行されたコマンド
            timeout_occurred: タイムアウトが発生したかどうか
            
        Returns:
            適切なカスタム例外インスタンス
        """
        if timeout_occurred:
            return NodeJSWrapperError(
                message="Node.jsラッパーの実行がタイムアウトしました",
                command=command,
                timeout=True,
                exit_code=process_result.returncode if process_result else None,
                stderr=process_result.stderr if process_result and process_result.stderr else None
            )
        
        if process_result.returncode != 0:
            # stderr からエラー情報を解析
            stderr_output = process_result.stderr or ""
            stdout_output = process_result.stdout or ""
            
            # Node.jsラッパーからのJSONエラーレスポンスを解析
            try:
                if stdout_output:
                    error_data = json.loads(stdout_output)
                    if not error_data.get("success", True):
                        return parse_nodejs_error_response(stdout_output)
            except json.JSONDecodeError:
                pass
            
            return NodeJSWrapperError(
                message="Node.jsラッパーの実行に失敗しました",
                command=command,
                exit_code=process_result.returncode,
                stderr=stderr_output
            )
        
        return KintoneBaseError(
            message="予期しないサブプロセスエラー",
            error_code="SUBPROCESS_ERROR",
            details={
                "command": command,
                "exit_code": process_result.returncode,
                "stdout": process_result.stdout,
                "stderr": process_result.stderr
            }
        )
    
    @staticmethod
    def handle_json_parse_error(
        json_string: str,
        original_error: Exception
    ) -> NodeJSWrapperError:
        """
        JSON解析エラーを処理
        
        Args:
            json_string: 解析に失敗したJSON文字列
            original_error: 元の例外
            
        Returns:
            NodeJSWrapperError インスタンス
        """
        return NodeJSWrapperError(
            message="Node.jsラッパーからの無効なJSONレスポンス",
            stderr=json_string,
            original_error=original_error
        )
    
    @staticmethod
    def to_mcp_error_response(error: Exception) -> Dict[str, Any]:
        """
        例外をMCP仕様準拠のエラーレスポンスに変換
        
        Args:
            error: 変換する例外
            
        Returns:
            MCP仕様準拠のエラーレスポンス
        """
        if isinstance(error, KintoneBaseError):
            return error.to_mcp_error()
        
        # 標準例外の場合
        error_code = -32603  # Internal error
        message = str(error)
        
        # 特定の例外タイプに基づいてエラーコードを調整
        if isinstance(error, ValueError):
            error_code = -32602  # Invalid params
        elif isinstance(error, FileNotFoundError):
            error_code = -32601  # Method not found
        elif isinstance(error, PermissionError):
            error_code = -32000  # Server error
        elif isinstance(error, TimeoutError):
            error_code = -32000  # Server error
            message = "操作がタイムアウトしました"
        
        return {
            "error": {
                "code": error_code,
                "message": message,
                "data": {
                    "error_type": type(error).__name__,
                    "timestamp": getattr(error, 'timestamp', datetime.now().isoformat())
                }
            }
        }
    
    @staticmethod
    def log_error(error: Exception, context: Optional[Dict[str, Any]] = None):
        """
        エラーをログに記録
        
        Args:
            error: ログに記録する例外
            context: 追加のコンテキスト情報
        """
        context = context or {}
        
        if isinstance(error, KintoneBaseError):
            logger.error(
                f"Kintone Error: {error.error_code} - {error.message}",
                extra={
                    "error_code": error.error_code,
                    "details": error.details,
                    "context": context
                }
            )
        else:
            logger.error(
                f"Unexpected Error: {type(error).__name__} - {str(error)}",
                extra={
                    "error_type": type(error).__name__,
                    "context": context,
                    "traceback": traceback.format_exc()
                }
            )


def handle_kintone_errors(
    log_errors: bool = True,
    return_mcp_format: bool = True
):
    """
    kintoneエラーハンドリングデコレータ
    
    Args:
        log_errors: エラーをログに記録するかどうか
        return_mcp_format: MCP形式でエラーを返すかどうか
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    ErrorHandler.log_error(e, {"function": func.__name__, "args": args, "kwargs": kwargs})
                
                if return_mcp_format:
                    return ErrorHandler.to_mcp_error_response(e)
                else:
                    raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    ErrorHandler.log_error(e, {"function": func.__name__, "args": args, "kwargs": kwargs})
                
                if return_mcp_format:
                    return ErrorHandler.to_mcp_error_response(e)
                else:
                    raise
        
        # 関数が非同期かどうかを判定
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def validate_required_params(required_params: list, params: Dict[str, Any]):
    """
    必須パラメータのバリデーション
    
    Args:
        required_params: 必須パラメータのリスト
        params: 検証するパラメータ辞書
        
    Raises:
        KintoneValidationError: 必須パラメータが不足している場合
    """
    missing_params = []
    
    for param in required_params:
        if param not in params or params[param] is None:
            missing_params.append(param)
    
    if missing_params:
        raise KintoneValidationError(
            message=f"必須パラメータが不足しています: {', '.join(missing_params)}",
            field_errors={param: "必須パラメータです" for param in missing_params},
            validation_type="required_params"
        )


def validate_param_types(param_types: Dict[str, type], params: Dict[str, Any]):
    """
    パラメータの型バリデーション
    
    Args:
        param_types: パラメータ名と期待される型の辞書
        params: 検証するパラメータ辞書
        
    Raises:
        KintoneValidationError: 型が一致しない場合
    """
    type_errors = {}
    
    for param_name, expected_type in param_types.items():
        if param_name in params and params[param_name] is not None:
            if not isinstance(params[param_name], expected_type):
                type_errors[param_name] = f"期待される型: {expected_type.__name__}, 実際の型: {type(params[param_name]).__name__}"
    
    if type_errors:
        raise KintoneValidationError(
            message="パラメータの型が正しくありません",
            field_errors=type_errors,
            validation_type="type_validation"
        )


class MCPErrorResponse:
    """
    MCP仕様準拠のエラーレスポンス生成ユーティリティ
    """
    
    # MCP標準エラーコード
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_ERROR_START = -32000
    SERVER_ERROR_END = -32099
    
    @classmethod
    def create_error_response(
        cls,
        code: int,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        request_id: Optional[Union[str, int]] = None
    ) -> Dict[str, Any]:
        """
        MCP仕様準拠のエラーレスポンスを作成
        
        Args:
            code: エラーコード
            message: エラーメッセージ
            data: 追加のエラーデータ
            request_id: リクエストID
            
        Returns:
            MCP仕様準拠のエラーレスポンス
        """
        response = {
            "jsonrpc": "2.0",
            "error": {
                "code": code,
                "message": message
            }
        }
        
        if data is not None:
            response["error"]["data"] = data
        
        if request_id is not None:
            response["id"] = request_id
        
        return response
    
    @classmethod
    def invalid_params(
        cls,
        message: str = "Invalid params",
        data: Optional[Dict[str, Any]] = None,
        request_id: Optional[Union[str, int]] = None
    ) -> Dict[str, Any]:
        """無効なパラメータエラー"""
        return cls.create_error_response(cls.INVALID_PARAMS, message, data, request_id)
    
    @classmethod
    def method_not_found(
        cls,
        message: str = "Method not found",
        data: Optional[Dict[str, Any]] = None,
        request_id: Optional[Union[str, int]] = None
    ) -> Dict[str, Any]:
        """メソッドが見つからないエラー"""
        return cls.create_error_response(cls.METHOD_NOT_FOUND, message, data, request_id)
    
    @classmethod
    def internal_error(
        cls,
        message: str = "Internal error",
        data: Optional[Dict[str, Any]] = None,
        request_id: Optional[Union[str, int]] = None
    ) -> Dict[str, Any]:
        """内部エラー"""
        return cls.create_error_response(cls.INTERNAL_ERROR, message, data, request_id)
    
    @classmethod
    def server_error(
        cls,
        message: str = "Server error",
        data: Optional[Dict[str, Any]] = None,
        request_id: Optional[Union[str, int]] = None
    ) -> Dict[str, Any]:
        """サーバーエラー"""
        return cls.create_error_response(cls.SERVER_ERROR_START, message, data, request_id) 