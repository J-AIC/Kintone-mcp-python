"""
Field Tool Definitions

フィールド関連のツール定義
"""

from typing import Dict, Any, List

# フィールド関連のツール定義
FIELD_TOOL_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "name": "add_fields",
        "description": "kintoneアプリにフィールドを追加します。フィールドコードが指定されていない場合は、ラベルから自動生成されます。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_id": {
                    "type": "number",
                    "description": "kintoneアプリのID"
                },
                "fields": {
                    "type": "array",
                    "description": "追加するフィールドの配列",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": [
                                    "SINGLE_LINE_TEXT", "MULTI_LINE_TEXT", "RICH_TEXT",
                                    "NUMBER", "CALC", "RADIO_BUTTON", "DROP_DOWN", 
                                    "MULTI_SELECT", "CHECK_BOX", "DATE", "TIME", 
                                    "DATETIME", "FILE", "LINK", "USER_SELECT", 
                                    "ORGANIZATION_SELECT", "GROUP_SELECT", "REFERENCE_TABLE",
                                    "SUBTABLE"
                                ],
                                "description": "フィールドタイプ"
                            },
                            "code": {
                                "type": "string",
                                "description": "フィールドコード（省略時はラベルから自動生成）"
                            },
                            "label": {
                                "type": "string",
                                "description": "フィールドラベル"
                            },
                            "required": {
                                "type": "boolean",
                                "description": "必須フィールドかどうか"
                            },
                            "noLabel": {
                                "type": "boolean",
                                "description": "ラベルを表示しないかどうか"
                            },
                            "options": {
                                "type": "array",
                                "description": "選択肢フィールドの選択肢配列",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "label": {"type": "string"},
                                        "value": {"type": "string"}
                                    }
                                }
                            },
                            "defaultValue": {
                                "type": ["string", "array"],
                                "description": "初期値"
                            },
                            "maxValue": {
                                "type": "string",
                                "description": "数値フィールドの最大値"
                            },
                            "minValue": {
                                "type": "string",
                                "description": "数値フィールドの最小値"
                            },
                            "maxLength": {
                                "type": "number",
                                "description": "テキストフィールドの最大文字数"
                            },
                            "minLength": {
                                "type": "number",
                                "description": "テキストフィールドの最小文字数"
                            },
                            "unit": {
                                "type": "string",
                                "description": "数値フィールドの単位記号"
                            },
                            "unitPosition": {
                                "type": "string",
                                "enum": ["BEFORE", "AFTER"],
                                "description": "単位記号の位置"
                            },
                            "digit": {
                                "type": "boolean",
                                "description": "桁区切りを表示するかどうか"
                            },
                            "format": {
                                "type": "string",
                                "enum": ["NUMBER", "NUMBER_DIGIT"],
                                "description": "数値の表示形式"
                            },
                            "displayScale": {
                                "type": "string",
                                "description": "小数点以下の表示桁数"
                            },
                            "expression": {
                                "type": "string",
                                "description": "計算フィールドの計算式"
                            },
                            "formula": {
                                "type": "string",
                                "description": "計算フィールドの計算式（expressionに自動変換）"
                            },
                            "protocol": {
                                "type": "string",
                                "enum": ["WEB", "CALL", "MAIL"],
                                "description": "リンクフィールドのプロトコル"
                            },
                            "entities": {
                                "type": "array",
                                "description": "ユーザー選択フィールドの選択可能エンティティ",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {
                                            "type": "string",
                                            "enum": ["USER", "GROUP", "ORGANIZATION"]
                                        },
                                        "code": {"type": "string"}
                                    }
                                }
                            },
                            "referenceTable": {
                                "type": "object",
                                "description": "関連レコード一覧フィールドの設定",
                                "properties": {
                                    "relatedApp": {
                                        "type": "object",
                                        "properties": {
                                            "app": {"type": "string"},
                                            "code": {"type": "string"}
                                        }
                                    },
                                    "condition": {
                                        "type": "object",
                                        "properties": {
                                            "field": {"type": "string"},
                                            "relatedField": {"type": "string"}
                                        }
                                    },
                                    "displayFields": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "filterCond": {"type": "string"},
                                    "sort": {"type": "string"},
                                    "size": {"type": "number"}
                                }
                            },
                            "fields": {
                                "type": "array",
                                "description": "テーブルフィールド内のフィールド定義",
                                "items": {
                                    "type": "object"
                                }
                            },
                            "unique": {
                                "type": "boolean",
                                "description": "値の重複を禁止するかどうか"
                            },
                            "thumbnailSize": {
                                "type": "string",
                                "description": "ファイルフィールドのサムネイルサイズ"
                            }
                        },
                        "required": ["type", "label"]
                    }
                },
                "revision": {
                    "type": "number",
                    "description": "アプリのリビジョン番号（省略時は-1で最新リビジョンを使用）"
                }
            },
            "required": ["app_id", "fields"]
        }
    },
    {
        "name": "update_fields",
        "description": "kintoneアプリの既存フィールドを更新します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_id": {
                    "type": "number",
                    "description": "kintoneアプリのID"
                },
                "fields": {
                    "type": "array",
                    "description": "更新するフィールドの配列",
                    "items": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "更新対象のフィールドコード"
                            },
                            "label": {
                                "type": "string",
                                "description": "フィールドラベル"
                            },
                            "required": {
                                "type": "boolean",
                                "description": "必須フィールドかどうか"
                            },
                            "noLabel": {
                                "type": "boolean",
                                "description": "ラベルを表示しないかどうか"
                            },
                            "options": {
                                "type": "array",
                                "description": "選択肢フィールドの選択肢配列",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "label": {"type": "string"},
                                        "value": {"type": "string"}
                                    }
                                }
                            },
                            "defaultValue": {
                                "type": ["string", "array"],
                                "description": "初期値"
                            },
                            "maxValue": {
                                "type": "string",
                                "description": "数値フィールドの最大値"
                            },
                            "minValue": {
                                "type": "string",
                                "description": "数値フィールドの最小値"
                            },
                            "maxLength": {
                                "type": "number",
                                "description": "テキストフィールドの最大文字数"
                            },
                            "minLength": {
                                "type": "number",
                                "description": "テキストフィールドの最小文字数"
                            },
                            "unit": {
                                "type": "string",
                                "description": "数値フィールドの単位記号"
                            },
                            "unitPosition": {
                                "type": "string",
                                "enum": ["BEFORE", "AFTER"],
                                "description": "単位記号の位置"
                            },
                            "digit": {
                                "type": "boolean",
                                "description": "桁区切りを表示するかどうか"
                            },
                            "format": {
                                "type": "string",
                                "enum": ["NUMBER", "NUMBER_DIGIT"],
                                "description": "数値の表示形式"
                            },
                            "displayScale": {
                                "type": "string",
                                "description": "小数点以下の表示桁数"
                            },
                            "expression": {
                                "type": "string",
                                "description": "計算フィールドの計算式"
                            },
                            "protocol": {
                                "type": "string",
                                "enum": ["WEB", "CALL", "MAIL"],
                                "description": "リンクフィールドのプロトコル"
                            },
                            "entities": {
                                "type": "array",
                                "description": "ユーザー選択フィールドの選択可能エンティティ",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {
                                            "type": "string",
                                            "enum": ["USER", "GROUP", "ORGANIZATION"]
                                        },
                                        "code": {"type": "string"}
                                    }
                                }
                            },
                            "unique": {
                                "type": "boolean",
                                "description": "値の重複を禁止するかどうか"
                            },
                            "thumbnailSize": {
                                "type": "string",
                                "description": "ファイルフィールドのサムネイルサイズ"
                            }
                        },
                        "required": ["code"]
                    }
                },
                "revision": {
                    "type": "number",
                    "description": "アプリのリビジョン番号（省略時は-1で最新リビジョンを使用）"
                }
            },
            "required": ["app_id", "fields"]
        }
    },
    {
        "name": "delete_fields",
        "description": "kintoneアプリからフィールドを削除します",
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
        "name": "get_form_fields",
        "description": "kintoneアプリのフォームフィールド情報を取得します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_id": {
                    "type": "number",
                    "description": "kintoneアプリのID"
                },
                "lang": {
                    "type": "string",
                    "enum": ["ja", "en", "zh"],
                    "description": "言語設定（オプション）"
                }
            },
            "required": ["app_id"]
        }
    },
    {
        "name": "create_lookup_field",
        "description": "ルックアップフィールドの設定オブジェクトを生成します。このツールは設定を生成するだけで、実際にフィールドを追加するには add_fields ツールを使用してください。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "field_type": {
                    "type": "string",
                    "enum": ["SINGLE_LINE_TEXT", "NUMBER", "DATE", "DATETIME", "DROP_DOWN", "RADIO_BUTTON", "CHECK_BOX", "MULTI_SELECT"],
                    "description": "ルックアップフィールドの基本タイプ"
                },
                "code": {
                    "type": "string",
                    "description": "フィールドコード"
                },
                "label": {
                    "type": "string",
                    "description": "フィールドラベル"
                },
                "related_app": {
                    "type": "object",
                    "properties": {
                        "app": {
                            "type": "string",
                            "description": "参照先アプリID"
                        },
                        "code": {
                            "type": "string",
                            "description": "参照先アプリコード"
                        }
                    },
                    "description": "参照先アプリ情報（appまたはcodeのいずれかが必要）"
                },
                "related_key_field": {
                    "type": "string",
                    "description": "参照先アプリのキーフィールドコード"
                },
                "field_mappings": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "field": {
                                "type": "string",
                                "description": "自アプリのフィールドコード"
                            },
                            "relatedField": {
                                "type": "string",
                                "description": "参照先アプリのフィールドコード"
                            }
                        },
                        "required": ["field", "relatedField"]
                    },
                    "description": "フィールドマッピングの配列"
                },
                "lookup_picker_fields": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "ルックアップピッカーに表示するフィールドコードの配列（推奨）"
                },
                "filter_cond": {
                    "type": "string",
                    "description": "絞り込み条件（オプション）"
                },
                "sort": {
                    "type": "object",
                    "properties": {
                        "field": {
                            "type": "string",
                            "description": "ソート対象フィールド"
                        },
                        "order": {
                            "type": "string",
                            "enum": ["asc", "desc"],
                            "description": "ソート順"
                        }
                    },
                    "description": "ソート条件（推奨）"
                },
                "required": {
                    "type": "boolean",
                    "description": "必須フィールドかどうか"
                }
            },
            "required": ["field_type", "code", "label", "related_app", "related_key_field", "field_mappings"]
        }
    }
] 