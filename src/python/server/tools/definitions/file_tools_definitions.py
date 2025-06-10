"""
File Tools Definitions

ファイル関連のツール定義
"""

from typing import Dict, Any, List

# ファイルツールの定義
FILE_TOOLS_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "name": "upload_file",
        "description": "kintoneアプリにファイルをアップロードします",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_name": {
                    "type": "string",
                    "description": "アップロードするファイルの名前"
                },
                "file_data": {
                    "type": "string",
                    "description": "Base64エンコードされたファイルデータ"
                }
            },
            "required": ["file_name", "file_data"]
        },
        "annotations": {
            "readOnly": False,
            "safe": True,
            "category": "file",
            "requiresConfirmation": False,
            "longRunning": True,
            "impact": "medium"
        }
    },
    {
        "name": "download_file",
        "description": "kintoneアプリからファイルをダウンロードします。注意: 現在の実装では1MB以上のファイルは正常にダウンロードできない場合があります。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_key": {
                    "type": "string",
                    "description": "ダウンロードするファイルのキー"
                }
            },
            "required": ["file_key"]
        },
        "annotations": {
            "readOnly": True,
            "safe": True,
            "category": "file",
            "requiresConfirmation": False,
            "longRunning": True,
            "impact": "low"
        }
    }
] 