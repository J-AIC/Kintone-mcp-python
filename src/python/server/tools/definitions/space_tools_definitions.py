"""
Space Tools Definitions

Space関連のMCPツール定義
"""

from typing import List, Dict, Any

# Space関連のツール定義
SPACE_TOOLS_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "name": "get_space",
        "description": "スペースの一般情報を取得します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "space_id": {
                    "type": "string",
                    "description": "スペースID"
                }
            },
            "required": ["space_id"]
        },
        "annotations": {
            "readOnly": True,
            "safe": True,
            "category": "space",
            "requiresConfirmation": False,
            "longRunning": False,
            "impact": "low"
        }
    },
    {
        "name": "update_space",
        "description": "スペースの設定を更新します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "space_id": {
                    "type": "string",
                    "description": "スペースID"
                },
                "name": {
                    "type": "string",
                    "description": "スペースの新しい名前"
                },
                "is_private": {
                    "type": "boolean",
                    "description": "プライベート設定"
                },
                "fixed_member": {
                    "type": "boolean",
                    "description": "メンバー固定設定"
                },
                "use_multi_thread": {
                    "type": "boolean",
                    "description": "マルチスレッド設定"
                }
            },
            "required": ["space_id"]
        },
        "annotations": {
            "readOnly": False,
            "safe": False,
            "category": "space",
            "requiresConfirmation": True,
            "longRunning": False,
            "impact": "medium"
        }
    },
    {
        "name": "update_space_body",
        "description": "スペースの本文を更新します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "space_id": {
                    "type": "string",
                    "description": "スペースID"
                },
                "body": {
                    "type": "string",
                    "description": "スペースの本文（HTML形式）"
                }
            },
            "required": ["space_id", "body"]
        },
        "annotations": {
            "readOnly": False,
            "safe": True,
            "category": "space",
            "requiresConfirmation": True,
            "longRunning": False,
            "impact": "medium"
        }
    },
    {
        "name": "get_space_members",
        "description": "スペースメンバーのリストを取得します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "space_id": {
                    "type": "string",
                    "description": "スペースID"
                }
            },
            "required": ["space_id"]
        },
        "annotations": {
            "readOnly": True,
            "safe": True,
            "category": "space",
            "requiresConfirmation": False,
            "longRunning": False,
            "impact": "low"
        }
    },
    {
        "name": "update_space_members",
        "description": "スペースメンバーを更新します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "space_id": {
                    "type": "string",
                    "description": "スペースID"
                },
                "members": {
                    "type": "array",
                    "description": "メンバー情報のリスト",
                    "items": {
                        "type": "object",
                        "properties": {
                            "entity": {
                                "type": "object",
                                "properties": {
                                    "type": {
                                        "type": "string",
                                        "enum": ["USER", "GROUP", "ORGANIZATION"]
                                    },
                                    "code": {
                                        "type": "string"
                                    }
                                },
                                "required": ["type", "code"]
                            },
                            "isAdmin": {
                                "type": "boolean"
                            },
                            "includeSubs": {
                                "type": "boolean"
                            }
                        },
                        "required": ["entity"]
                    }
                }
            },
            "required": ["space_id", "members"]
        },
        "annotations": {
            "readOnly": False,
            "safe": False,
            "category": "space",
            "requiresConfirmation": True,
            "longRunning": False,
            "impact": "high"
        }
    },
    {
        "name": "add_thread",
        "description": "スペースにスレッドを追加します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "space_id": {
                    "type": "string",
                    "description": "スペースID"
                },
                "name": {
                    "type": "string",
                    "description": "スレッド名"
                }
            },
            "required": ["space_id", "name"]
        },
        "annotations": {
            "readOnly": False,
            "safe": True,
            "category": "space",
            "requiresConfirmation": False,
            "longRunning": False,
            "impact": "medium"
        }
    },
    {
        "name": "update_thread",
        "description": "スレッドを更新します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "thread_id": {
                    "type": "string",
                    "description": "スレッドID"
                },
                "name": {
                    "type": "string",
                    "description": "スレッドの新しい名前"
                },
                "body": {
                    "type": "string",
                    "description": "スレッドの本文（HTML形式）"
                }
            },
            "required": ["thread_id"]
        },
        "annotations": {
            "readOnly": False,
            "safe": True,
            "category": "space",
            "requiresConfirmation": True,
            "longRunning": False,
            "impact": "medium"
        }
    },
    {
        "name": "add_thread_comment",
        "description": "スレッドにコメントを追加します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "space_id": {
                    "type": "string",
                    "description": "スペースID"
                },
                "thread_id": {
                    "type": "string",
                    "description": "スレッドID"
                },
                "text": {
                    "type": "string",
                    "description": "コメント本文"
                },
                "mentions": {
                    "type": "array",
                    "description": "メンション情報のリスト",
                    "items": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string"
                            },
                            "type": {
                                "type": "string",
                                "enum": ["USER", "GROUP", "ORGANIZATION"]
                            }
                        },
                        "required": ["code", "type"]
                    }
                }
            },
            "required": ["space_id", "thread_id", "text"]
        },
        "annotations": {
            "readOnly": False,
            "safe": True,
            "category": "space",
            "requiresConfirmation": False,
            "longRunning": False,
            "impact": "low"
        }
    },
    {
        "name": "update_space_guests",
        "description": "スペースのゲストメンバーを更新します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "space_id": {
                    "type": "string",
                    "description": "スペースID"
                },
                "guests": {
                    "type": "array",
                    "description": "ゲストユーザーのメールアドレスのリスト",
                    "items": {
                        "type": "string",
                        "description": "ゲストユーザーのメールアドレス"
                    }
                }
            },
            "required": ["space_id", "guests"]
        },
        "annotations": {
            "readOnly": False,
            "safe": False,
            "category": "space",
            "requiresConfirmation": True,
            "longRunning": False,
            "impact": "high"
        }
    }
] 