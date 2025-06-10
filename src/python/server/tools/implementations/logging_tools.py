"""
Logging Tools Implementation

MCPロギング関連ツールの実装
"""

import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from .....utils.logging_config import (
    LogLevel, 
    LOG_LEVEL_MAPPING, 
    get_logger,
    log_with_context
)
from .....utils.error_handler import (
    MCPError,
    MCPErrorCode,
    ErrorHandler
)

logger = get_logger(__name__)

# グローバルな通知コールバック関数
_notification_callback: Optional[Callable] = None
_current_log_level: str = "info"


def set_notification_callback(callback: Callable) -> None:
    """
    MCP通知を送信するためのコールバック関数を設定
    
    Args:
        callback: 通知を送信するためのコールバック関数
    """
    global _notification_callback
    _notification_callback = callback


def get_notification_callback() -> Optional[Callable]:
    """現在の通知コールバック関数を取得"""
    return _notification_callback


async def handle_logging_tools(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    ロギング関連のツールを処理する関数
    
    Args:
        name: ツール名
        args: 引数
        
    Returns:
        Dict[str, Any]: ツールの実行結果
        
    Raises:
        MCPError: ツール実行中にエラーが発生した場合
    """
    try:
        if name == "logging_set_level":
            return await _handle_set_log_level(args)
        elif name == "logging_get_level":
            return await _handle_get_log_level(args)
        elif name == "logging_send_message":
            return await _handle_send_log_message(args)
        else:
            raise MCPError(
                MCPErrorCode.METHOD_NOT_FOUND,
                f"Unknown logging tool: {name}",
                {"tool_name": name}
            )
            
    except MCPError:
        raise
    except Exception as error:
        ErrorHandler.log_error(error, {"tool_name": name, "args": args})
        raise MCPError(
            MCPErrorCode.INTERNAL_ERROR,
            f"ロギングツール '{name}' の実行中にエラーが発生しました: {str(error)}",
            {"tool_name": name, "error_type": type(error).__name__}
        )


async def _handle_set_log_level(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    ログレベル設定ツールの実装
    
    Args:
        args: ツール引数
        
    Returns:
        Dict[str, Any]: 実行結果
    """
    global _current_log_level
    
    # 引数の検証
    if "level" not in args:
        raise MCPError(
            MCPErrorCode.INVALID_PARAMS,
            "level パラメータは必須です",
            {"required_params": ["level"]}
        )
    
    level_str = args["level"].lower()
    
    # ログレベルの検証
    try:
        log_level_enum = LogLevel(level_str)
    except ValueError:
        valid_levels = [level.value for level in LogLevel]
        raise MCPError(
            MCPErrorCode.INVALID_PARAMS,
            f"無効なログレベルです: {level_str}",
            {
                "provided_level": level_str,
                "valid_levels": valid_levels
            },
            f"有効なログレベル: {', '.join(valid_levels)}"
        )
    
    # Pythonのログレベルに変換
    python_level = LOG_LEVEL_MAPPING[log_level_enum]
    
    # ルートロガーのレベルを設定
    root_logger = logging.getLogger()
    old_level = root_logger.level
    root_logger.setLevel(python_level)
    
    # 現在のレベルを更新
    old_level_str = _current_log_level
    _current_log_level = level_str
    
    # ログに記録
    logger.info(f"Log level changed from {old_level_str} to {level_str}")
    
    return {
        "success": True,
        "previous_level": old_level_str,
        "new_level": level_str,
        "message": f"ログレベルを {level_str} に設定しました"
    }


async def _handle_get_log_level(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    現在のログレベル取得ツールの実装
    
    Args:
        args: ツール引数（使用しない）
        
    Returns:
        Dict[str, Any]: 実行結果
    """
    global _current_log_level
    
    root_logger = logging.getLogger()
    python_level = root_logger.level
    
    # PythonレベルからMCPレベルを逆算
    mcp_level = None
    for log_level_enum, py_level in LOG_LEVEL_MAPPING.items():
        if py_level == python_level:
            mcp_level = log_level_enum.value
            break
    
    if not mcp_level:
        # 近似値を探す
        if python_level <= logging.DEBUG:
            mcp_level = "debug"
        elif python_level <= logging.INFO:
            mcp_level = "info"
        elif python_level <= logging.WARNING:
            mcp_level = "warning"
        elif python_level <= logging.ERROR:
            mcp_level = "error"
        else:
            mcp_level = "critical"
    
    return {
        "current_level": mcp_level,
        "python_level": python_level,
        "level_name": logging.getLevelName(python_level)
    }


async def _handle_send_log_message(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    ログメッセージ送信ツールの実装
    
    Args:
        args: ツール引数
        
    Returns:
        Dict[str, Any]: 実行結果
    """
    # 必須引数の検証
    if "level" not in args:
        raise MCPError(
            MCPErrorCode.INVALID_PARAMS,
            "level パラメータは必須です",
            {"required_params": ["level"]}
        )
    
    if "message" not in args:
        raise MCPError(
            MCPErrorCode.INVALID_PARAMS,
            "message パラメータは必須です",
            {"required_params": ["message"]}
        )
    
    level_str = args["level"].lower()
    message = args["message"]
    logger_name = args.get("logger", "mcp.user")
    data = args.get("data", {})
    
    # ログレベルの検証
    try:
        log_level_enum = LogLevel(level_str)
    except ValueError:
        valid_levels = [level.value for level in LogLevel]
        raise MCPError(
            MCPErrorCode.INVALID_PARAMS,
            f"無効なログレベルです: {level_str}",
            {
                "provided_level": level_str,
                "valid_levels": valid_levels
            }
        )
    
    # Pythonのログレベルに変換
    python_level = LOG_LEVEL_MAPPING[log_level_enum]
    
    # ロガーを取得
    target_logger = get_logger(logger_name)
    
    # ログメッセージを出力
    log_with_context(
        target_logger,
        python_level,
        message,
        operation="user_log_message",
        context=data
    )
    
    # MCP通知として送信（コールバックが設定されている場合）
    if _notification_callback:
        try:
            notification_data = {
                "level": level_str,
                "logger": logger_name,
                "data": {
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                    **data
                }
            }
            await _notification_callback(notification_data)
        except Exception as e:
            # 通知送信エラーは警告として記録するが、ツール自体は成功とする
            logger.warning(f"Failed to send MCP notification: {e}")
    
    return {
        "success": True,
        "level": level_str,
        "logger": logger_name,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "notification_sent": _notification_callback is not None
    }


async def send_mcp_log_notification(
    level: str,
    logger_name: str,
    message: str,
    data: Optional[Dict[str, Any]] = None
) -> bool:
    """
    MCP notifications/message を送信する関数
    
    Args:
        level: ログレベル
        logger_name: ロガー名
        message: ログメッセージ
        data: 追加データ
        
    Returns:
        bool: 送信成功かどうか
    """
    if not _notification_callback:
        return False
    
    try:
        notification_data = {
            "level": level,
            "logger": logger_name,
            "data": {
                "message": message,
                "timestamp": datetime.now().isoformat(),
                **(data or {})
            }
        }
        await _notification_callback(notification_data)
        return True
    except Exception as e:
        logger.warning(f"Failed to send MCP log notification: {e}")
        return False 