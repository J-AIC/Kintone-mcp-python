"""
System Tools Definitions

システム関連ツールの定義
"""

from typing import List, Dict, Any


def get_system_tools_definitions() -> List[Dict[str, Any]]:
    """
    システム関連ツールの定義を取得
    
    Returns:
        ツール定義のリスト
    """
    return [
        {
            "name": "get_connection_info",
            "description": "Kintone接続情報を取得します。ドメイン、認証方法、接続状態などの基本情報を返します。",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            },
            "annotations": {
                "readOnly": True,
                "safe": True,
                "category": "system",
                "requiresConfirmation": False,
                "longRunning": False,
                "impact": "low"
            }
        }
    ] 