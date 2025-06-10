"""
Logging Configuration

Python標準のloggingモジュールを使用したロギング設定
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from enum import Enum
import json
from datetime import datetime


class LogLevel(Enum):
    """MCP仕様に準拠したログレベル（RFC 5424準拠）"""
    DEBUG = "debug"
    INFO = "info"
    NOTICE = "notice"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    ALERT = "alert"
    EMERGENCY = "emergency"


# ログレベルのマッピング（MCP → Python logging）
LOG_LEVEL_MAPPING = {
    LogLevel.DEBUG: logging.DEBUG,
    LogLevel.INFO: logging.INFO,
    LogLevel.NOTICE: logging.INFO + 5,  # NOTICEはINFOとWARNINGの間
    LogLevel.WARNING: logging.WARNING,
    LogLevel.ERROR: logging.ERROR,
    LogLevel.CRITICAL: logging.CRITICAL,
    LogLevel.ALERT: logging.CRITICAL + 5,  # ALERTはCRITICALより上
    LogLevel.EMERGENCY: logging.CRITICAL + 10,  # EMERGENCYは最高レベル
}

# 逆マッピング（Python logging → MCP）
PYTHON_TO_MCP_MAPPING = {v: k for k, v in LOG_LEVEL_MAPPING.items()}


class MCPLogFormatter(logging.Formatter):
    """MCP仕様に準拠したログフォーマッター"""
    
    def __init__(self, include_mcp_format: bool = True):
        """
        Args:
            include_mcp_format: MCP形式の情報を含めるかどうか
        """
        self.include_mcp_format = include_mcp_format
        super().__init__()
    
    def format(self, record: logging.LogRecord) -> str:
        """ログレコードをフォーマット"""
        # 基本的なフォーマット
        timestamp = datetime.fromtimestamp(record.created).isoformat()
        
        # MCPレベルの取得
        mcp_level = self._get_mcp_level(record.levelno)
        
        # 基本情報
        base_info = {
            "timestamp": timestamp,
            "level": mcp_level.value if mcp_level else record.levelname.lower(),
            "logger": record.name,
            "message": record.getMessage()
        }
        
        # 追加情報
        if hasattr(record, 'operation'):
            base_info["operation"] = record.operation
        
        if hasattr(record, 'context'):
            base_info["context"] = record.context
        
        if record.exc_info:
            base_info["exception"] = self.formatException(record.exc_info)
        
        if self.include_mcp_format:
            # MCP形式のJSON出力
            return json.dumps(base_info, ensure_ascii=False, separators=(',', ':'))
        else:
            # 人間が読みやすい形式
            msg = f"{timestamp} - {base_info['logger']} - {base_info['level'].upper()} - {base_info['message']}"
            if 'operation' in base_info:
                msg += f" [operation: {base_info['operation']}]"
            if 'exception' in base_info:
                msg += f"\n{base_info['exception']}"
            return msg
    
    def _get_mcp_level(self, python_level: int) -> Optional[LogLevel]:
        """PythonのログレベルをMCPレベルに変換"""
        # 完全一致を探す
        for mcp_level, py_level in LOG_LEVEL_MAPPING.items():
            if py_level == python_level:
                return mcp_level
        
        # 近似値を探す
        if python_level <= logging.DEBUG:
            return LogLevel.DEBUG
        elif python_level <= logging.INFO:
            return LogLevel.INFO
        elif python_level <= logging.WARNING:
            return LogLevel.WARNING
        elif python_level <= logging.ERROR:
            return LogLevel.ERROR
        else:
            return LogLevel.CRITICAL


class MCPLogHandler(logging.Handler):
    """MCP notifications/message を送信するためのログハンドラー"""
    
    def __init__(self, notification_callback=None):
        """
        Args:
            notification_callback: ログメッセージを送信するためのコールバック関数
        """
        super().__init__()
        self.notification_callback = notification_callback
        self.setFormatter(MCPLogFormatter(include_mcp_format=False))
    
    def emit(self, record: logging.LogRecord):
        """ログレコードを処理してMCP通知として送信"""
        if not self.notification_callback:
            return
        
        try:
            # MCPレベルの取得
            mcp_level = self._get_mcp_level(record.levelno)
            
            # MCP通知データの構築
            notification_data = {
                "level": mcp_level.value if mcp_level else "info",
                "logger": record.name,
                "data": {
                    "message": record.getMessage(),
                    "timestamp": datetime.fromtimestamp(record.created).isoformat()
                }
            }
            
            # 追加情報の追加
            if hasattr(record, 'operation'):
                notification_data["data"]["operation"] = record.operation
            
            if hasattr(record, 'context'):
                notification_data["data"]["context"] = record.context
            
            if record.exc_info:
                import traceback
                notification_data["data"]["exception"] = ''.join(traceback.format_exception(*record.exc_info))
            
            # コールバック関数を呼び出し
            self.notification_callback(notification_data)
            
        except Exception:
            # ログハンドラー内でのエラーは無視（無限ループを防ぐ）
            self.handleError(record)
    
    def _get_mcp_level(self, python_level: int) -> LogLevel:
        """PythonのログレベルをMCPレベルに変換"""
        formatter = MCPLogFormatter()
        return formatter._get_mcp_level(python_level) or LogLevel.INFO


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    enable_mcp_handler: bool = False,
    mcp_notification_callback=None,
    enable_console: bool = True,
    log_format: str = "human"
) -> None:
    """
    ロギングシステムを設定
    
    Args:
        level: ログレベル（DEBUG, INFO, WARNING, ERROR, CRITICAL）
        log_file: ログファイルのパス（Noneの場合はファイル出力なし）
        enable_mcp_handler: MCP通知ハンドラーを有効にするかどうか
        mcp_notification_callback: MCP通知を送信するためのコールバック関数
        enable_console: コンソール出力を有効にするかどうか
        log_format: ログフォーマット（"human" または "json"）
    """
    # ルートロガーの設定
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # 既存のハンドラーをクリア
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # フォーマッターの選択
    use_json_format = log_format.lower() == "json"
    formatter = MCPLogFormatter(include_mcp_format=use_json_format)
    
    # コンソールハンドラー
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # ファイルハンドラー
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # ローテーションファイルハンドラー（最大10MB、5ファイルまで保持）
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # MCPハンドラー
    if enable_mcp_handler and mcp_notification_callback:
        mcp_handler = MCPLogHandler(mcp_notification_callback)
        root_logger.addHandler(mcp_handler)
    
    # サードパーティライブラリのログレベルを調整
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    指定された名前のロガーを取得
    
    Args:
        name: ロガー名
        
    Returns:
        logging.Logger: ロガーインスタンス
    """
    return logging.getLogger(name)


def log_with_context(
    logger: logging.Logger,
    level: int,
    message: str,
    operation: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    exc_info: bool = False
) -> None:
    """
    コンテキスト情報付きでログを出力
    
    Args:
        logger: ロガーインスタンス
        level: ログレベル
        message: ログメッセージ
        operation: 実行中の操作名
        context: コンテキスト情報
        exc_info: 例外情報を含めるかどうか
    """
    # LogRecordに追加情報を設定
    extra = {}
    if operation:
        extra['operation'] = operation
    if context:
        extra['context'] = context
    
    logger.log(level, message, exc_info=exc_info, extra=extra)


def log_operation_start(logger: logging.Logger, operation: str, **kwargs) -> None:
    """操作開始のログ"""
    context = {"status": "started", **kwargs}
    log_with_context(logger, logging.INFO, f"Operation started: {operation}", operation, context)


def log_operation_success(logger: logging.Logger, operation: str, **kwargs) -> None:
    """操作成功のログ"""
    context = {"status": "success", **kwargs}
    log_with_context(logger, logging.INFO, f"Operation completed: {operation}", operation, context)


def log_operation_error(logger: logging.Logger, operation: str, error: Exception, **kwargs) -> None:
    """操作エラーのログ"""
    context = {"status": "error", "error_type": type(error).__name__, **kwargs}
    log_with_context(
        logger, 
        logging.ERROR, 
        f"Operation failed: {operation} - {str(error)}", 
        operation, 
        context, 
        exc_info=True
    )


# デフォルトのロガー設定
def configure_default_logging():
    """デフォルトのロギング設定を適用"""
    setup_logging(
        level="INFO",
        enable_console=True,
        log_format="human"
    )


# モジュール読み込み時にデフォルト設定を適用
if not logging.getLogger().handlers:
    configure_default_logging() 