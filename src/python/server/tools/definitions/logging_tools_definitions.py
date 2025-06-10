"""
Logging Tools Definitions

MCPロギング関連ツールの定義
"""

from typing import List, Dict, Any

# ログレベルの定義
LOG_LEVELS = [
    "debug", "info", "notice", "warning", 
    "error", "critical", "alert", "emergency"
]

LOGGING_TOOL_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "name": "logging_set_level",
        "description": "ログレベルを設定します。指定されたレベル以上のログメッセージのみが出力されます。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "level": {
                    "type": "string",
                    "enum": LOG_LEVELS,
                    "description": "設定するログレベル（RFC 5424準拠）"
                }
            },
            "required": ["level"]
        },
        "annotations": {
            "readOnly": False,
            "safe": True,
            "category": "logging",
            "requiresConfirmation": False,
            "longRunning": False,
            "impact": "low"
        }
    },
    {
        "name": "logging_get_level",
        "description": "現在のログレベルを取得します。",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        },
        "annotations": {
            "readOnly": True,
            "safe": True,
            "category": "logging",
            "requiresConfirmation": False,
            "longRunning": False,
            "impact": "low"
        }
    },
    {
        "name": "logging_send_message",
        "description": "指定されたレベルでログメッセージを送信します。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "level": {
                    "type": "string",
                    "enum": LOG_LEVELS,
                    "description": "ログレベル"
                },
                "message": {
                    "type": "string",
                    "description": "ログメッセージ"
                },
                "logger": {
                    "type": "string",
                    "description": "ロガー名（オプション）",
                    "default": "mcp.user"
                },
                "data": {
                    "type": "object",
                    "description": "追加のコンテキストデータ（オプション）",
                    "additionalProperties": True
                }
            },
            "required": ["level", "message"]
        },
        "annotations": {
            "readOnly": False,
            "safe": True,
            "category": "logging",
            "requiresConfirmation": False,
            "longRunning": False,
            "impact": "low"
        }
    }
] 