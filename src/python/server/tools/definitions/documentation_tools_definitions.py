"""
Documentation tools definitions for kintone MCP Server.
"""

from typing import Dict, Any, List

def get_documentation_tools_definitions() -> List[Dict[str, Any]]:
    """
    ドキュメント関連のツール定義を取得する
    
    Returns:
        List[Dict[str, Any]]: ツール定義のリスト
    """
    return [
        {
            "name": "get_field_type_documentation",
            "description": "フィールドタイプに関するドキュメントを取得します",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "field_type": {
                        "type": "string",
                        "description": "ドキュメントを取得するフィールドタイプ"
                    }
                },
                "required": ["field_type"]
            },
            "annotations": {
                "readOnly": True,
                "safe": True,
                "category": "documentation",
                "requiresConfirmation": False,
                "longRunning": False,
                "impact": "low"
            }
        },
        {
            "name": "get_available_field_types",
            "description": "利用可能なフィールドタイプの一覧を取得します",
            "inputSchema": {
                "type": "object",
                "properties": {}
            },
            "annotations": {
                "readOnly": True,
                "safe": True,
                "category": "documentation",
                "requiresConfirmation": False,
                "longRunning": False,
                "impact": "low"
            }
        },
        {
            "name": "get_documentation_tool_description",
            "description": "ドキュメントツールの説明を取得します",
            "inputSchema": {
                "type": "object",
                "properties": {}
            },
            "annotations": {
                "readOnly": True,
                "safe": True,
                "category": "documentation",
                "requiresConfirmation": False,
                "longRunning": False,
                "impact": "low"
            }
        },
        {
            "name": "get_field_creation_tool_description",
            "description": "フィールド作成ツールの説明を取得します",
            "inputSchema": {
                "type": "object",
                "properties": {}
            },
            "annotations": {
                "readOnly": True,
                "safe": True,
                "category": "documentation",
                "requiresConfirmation": False,
                "longRunning": False,
                "impact": "low"
            }
        }
    ] 