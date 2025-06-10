"""
Layout Tool Definitions

レイアウト関連のツール定義
JavaScript版のLayoutToolDefinitions.jsに相当する定義
"""

from typing import Dict, Any, List

# レイアウト関連のツール定義
LAYOUT_TOOL_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "name": "get_form_layout",
        "description": "kintoneアプリのフォームレイアウト情報を取得します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_id": {
                    "type": "number",
                    "description": "kintoneアプリのID"
                },
                "preview": {
                    "type": "boolean",
                    "description": "プレビュー環境のレイアウトを取得する場合はtrue（省略時はfalse）"
                }
            },
            "required": ["app_id"]
        }
    },
    {
        "name": "update_form_layout",
        "description": "kintoneアプリのフォームレイアウトを更新します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_id": {
                    "type": "number",
                    "description": "kintoneアプリのID"
                },
                "layout": {
                    "type": "array",
                    "description": "レイアウト要素の配列",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["ROW", "SUBTABLE", "GROUP", "LABEL", "SPACER", "HR", "REFERENCE_TABLE"],
                                "description": "レイアウト要素のタイプ"
                            },
                            "code": {
                                "type": "string",
                                "description": "フィールドコード（ROWタイプ以外で必要）"
                            },
                            "fields": {
                                "type": "array",
                                "description": "ROWタイプの場合のフィールド配列",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {
                                            "type": "string",
                                            "enum": ["FIELD", "SPACER"],
                                            "description": "要素タイプ"
                                        },
                                        "code": {
                                            "type": "string",
                                            "description": "フィールドコード（FIELDタイプの場合）"
                                        },
                                        "size": {
                                            "type": "object",
                                            "properties": {
                                                "width": {"type": "string"},
                                                "height": {"type": "string"},
                                                "innerHeight": {"type": "string"}
                                            },
                                            "description": "フィールドサイズ"
                                        },
                                        "elementId": {
                                            "type": "string",
                                            "description": "スペーサーのID（SPACERタイプの場合）"
                                        }
                                    }
                                }
                            },
                            "layout": {
                                "type": "array",
                                "description": "GROUPタイプの場合の内部レイアウト",
                                "items": {
                                    "type": "object"
                                }
                            },
                            "label": {
                                "type": "string",
                                "description": "ラベル（LABEL、GROUPタイプの場合）"
                            },
                            "elementId": {
                                "type": "string",
                                "description": "要素ID（SPACER、HRタイプの場合）"
                            }
                        },
                        "required": ["type"]
                    }
                },
                "revision": {
                    "type": "number",
                    "description": "アプリのリビジョン番号（省略時は-1で最新リビジョンを使用）"
                }
            },
            "required": ["app_id", "layout"]
        }
    },
    {
        "name": "create_layout_element",
        "description": "レイアウト要素を生成します。このツールは要素を生成するだけで、実際にレイアウトを更新するには update_form_layout ツールを使用してください。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "element_type": {
                    "type": "string",
                    "enum": ["ROW", "SUBTABLE", "GROUP", "LABEL", "SPACER", "HR", "REFERENCE_TABLE"],
                    "description": "レイアウト要素のタイプ"
                },
                "config": {
                    "type": "object",
                    "description": "要素の設定",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "フィールドコード（SUBTABLE、GROUP、REFERENCE_TABLEタイプの場合）"
                        },
                        "label": {
                            "type": "string",
                            "description": "ラベル（LABEL、GROUPタイプの場合）"
                        },
                        "fields": {
                            "type": "array",
                            "description": "ROWタイプの場合のフィールド配列",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "code": {
                                        "type": "string",
                                        "description": "フィールドコード"
                                    },
                                    "width": {
                                        "type": "string",
                                        "description": "フィールド幅（例: '200px', '50%'）"
                                    },
                                    "height": {
                                        "type": "string",
                                        "description": "フィールド高さ（例: '100px'）"
                                    }
                                }
                            }
                        },
                        "layout": {
                            "type": "array",
                            "description": "GROUPタイプの場合の内部レイアウト",
                            "items": {
                                "type": "object"
                            }
                        },
                        "spacer_width": {
                            "type": "string",
                            "description": "スペーサーの幅（SPACERタイプの場合）"
                        }
                    }
                }
            },
            "required": ["element_type"]
        }
    },
    {
        "name": "add_fields_to_layout",
        "description": "既存のレイアウトに新しいフィールドを追加します。フィールドは最後の行に追加されます。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_id": {
                    "type": "number",
                    "description": "kintoneアプリのID"
                },
                "field_codes": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "追加するフィールドコードの配列"
                },
                "group_fields": {
                    "type": "boolean",
                    "description": "フィールドを1つの行にまとめるかどうか（省略時はfalse）"
                },
                "revision": {
                    "type": "number",
                    "description": "アプリのリビジョン番号（省略時は-1で最新リビジョンを使用）"
                }
            },
            "required": ["app_id", "field_codes"]
        }
    },
    {
        "name": "remove_fields_from_layout",
        "description": "レイアウトから指定されたフィールドを削除します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_id": {
                    "type": "number",
                    "description": "kintoneアプリのID"
                },
                "field_codes": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "削除するフィールドコードの配列"
                },
                "revision": {
                    "type": "number",
                    "description": "アプリのリビジョン番号（省略時は-1で最新リビジョンを使用）"
                }
            },
            "required": ["app_id", "field_codes"]
        }
    },
    {
        "name": "organize_layout",
        "description": "レイアウトを自動整理します。未配置のフィールドを追加し、削除されたフィールドを除去します。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_id": {
                    "type": "number",
                    "description": "kintoneアプリのID"
                },
                "fields_per_row": {
                    "type": "number",
                    "description": "1行あたりのフィールド数（省略時は2）"
                },
                "revision": {
                    "type": "number",
                    "description": "アプリのリビジョン番号（省略時は-1で最新リビジョンを使用）"
                }
            },
            "required": ["app_id"]
        }
    },
    {
        "name": "create_field_group",
        "description": "指定されたフィールドをグループ化します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_id": {
                    "type": "number",
                    "description": "kintoneアプリのID"
                },
                "group_label": {
                    "type": "string",
                    "description": "グループのラベル"
                },
                "field_codes": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "グループ化するフィールドコードの配列"
                },
                "fields_per_row": {
                    "type": "number",
                    "description": "グループ内の1行あたりのフィールド数（省略時は2）"
                },
                "revision": {
                    "type": "number",
                    "description": "アプリのリビジョン番号（省略時は-1で最新リビジョンを使用）"
                }
            },
            "required": ["app_id", "group_label", "field_codes"]
        }
    },
    {
        "name": "create_form_layout",
        "description": "フィールド情報からフォームレイアウトを自動生成します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_id": {
                    "type": "number",
                    "description": "kintoneアプリのID"
                },
                "fields": {
                    "type": "array",
                    "items": {
                        "type": "object"
                    },
                    "description": "レイアウトに配置するフィールド情報の配列"
                },
                "options": {
                    "type": "object",
                    "properties": {
                        "groupBySection": {
                            "type": "boolean",
                            "description": "セクションごとにグループ化するかどうか"
                        },
                        "fieldsPerRow": {
                            "type": "number",
                            "description": "1行あたりのフィールド数"
                        }
                    },
                    "description": "レイアウト生成オプション"
                }
            },
            "required": ["app_id", "fields"]
        }
    },
    {
        "name": "add_layout_element",
        "description": "既存のフォームレイアウトに要素を追加します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_id": {
                    "type": "number",
                    "description": "kintoneアプリのID"
                },
                "element": {
                    "type": "object",
                    "description": "追加する要素"
                },
                "position": {
                    "type": "object",
                    "properties": {
                        "index": {
                            "type": "number",
                            "description": "挿入位置のインデックス"
                        },
                        "type": {
                            "type": "string",
                            "enum": ["GROUP"],
                            "description": "挿入先の要素タイプ"
                        },
                        "groupCode": {
                            "type": "string",
                            "description": "挿入先のグループコード"
                        },
                        "after": {
                            "type": "string",
                            "description": "この要素の後に挿入するフィールドコード"
                        },
                        "before": {
                            "type": "string",
                            "description": "この要素の前に挿入するフィールドコード"
                        }
                    },
                    "description": "要素の挿入位置"
                }
            },
            "required": ["app_id", "element"]
        }
    },
    {
        "name": "create_group_layout",
        "description": "グループ要素を作成します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "グループコード"
                },
                "label": {
                    "type": "string",
                    "description": "グループラベル"
                },
                "fields": {
                    "type": "array",
                    "items": {
                        "type": "object"
                    },
                    "description": "グループ内に配置するフィールド情報の配列"
                },
                "openGroup": {
                    "type": "boolean",
                    "description": "グループを開いた状態で表示するかどうか"
                },
                "options": {
                    "type": "object",
                    "properties": {
                        "fieldsPerRow": {
                            "type": "number",
                            "description": "1行あたりのフィールド数"
                        }
                    },
                    "description": "グループレイアウト生成オプション"
                }
            },
            "required": ["code", "label", "fields"]
        }
    },
    {
        "name": "create_table_layout",
        "description": "テーブルレイアウトを作成します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "rows": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object"
                        }
                    },
                    "description": "テーブルの各行に配置するフィールド情報の二次元配列"
                },
                "options": {
                    "type": "object",
                    "description": "テーブルレイアウト生成オプション"
                }
            },
            "required": ["rows"]
        }
    }
] 