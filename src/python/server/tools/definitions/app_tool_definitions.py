"""
App Tool Definitions

アプリ関連のツール定義
"""

from typing import Dict, Any, List

# アプリ関連のツール定義
APP_TOOL_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "name": "get_process_management",
        "description": "kintoneアプリのプロセス管理設定を取得します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_id": {
                    "type": "number",
                    "description": "kintoneアプリのID"
                },
                "preview": {
                    "type": "boolean",
                    "description": "プレビュー環境の設定を取得する場合はtrue（省略時はfalse）"
                }
            },
            "required": ["app_id"]
        }
    },
    {
        "name": "get_apps_info",
        "description": "検索キーワードを指定して該当する複数のkintoneアプリの情報を取得します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_name": {
                    "type": "string",
                    "description": "アプリ名またはその一部（省略時は全アプリを取得）"
                }
            },
            "required": []
        }
    },
    {
        "name": "create_app",
        "description": "新しいkintoneアプリを作成します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "アプリの名前"
                },
                "space": {
                    "type": "number",
                    "description": "スペースID（オプション）"
                },
                "thread": {
                    "type": "number",
                    "description": "スレッドID（オプション）"
                }
            },
            "required": ["name"]
        }
    },
    {
        "name": "deploy_app",
        "description": "kintoneアプリの設定をデプロイします",
        "inputSchema": {
            "type": "object",
            "properties": {
                "apps": {
                    "type": "array",
                    "items": {
                        "type": "number"
                    },
                    "description": "デプロイ対象のアプリID配列"
                }
            },
            "required": ["apps"]
        }
    },
    {
        "name": "get_deploy_status",
        "description": "kintoneアプリのデプロイ状態を確認します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "apps": {
                    "type": "array",
                    "items": {
                        "type": "number"
                    },
                    "description": "確認対象のアプリID配列"
                }
            },
            "required": ["apps"]
        }
    },
    {
        "name": "update_app_settings",
        "description": "kintoneアプリの一般設定を変更します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_id": {
                    "type": "number",
                    "description": "アプリID"
                },
                "name": {
                    "type": "string",
                    "description": "アプリの名前（1文字以上64文字以内）"
                },
                "description": {
                    "type": "string",
                    "description": "アプリの説明（10,000文字以内、HTMLタグ使用可）"
                },
                "icon": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": ["PRESET", "FILE"],
                            "description": "アイコンの種類"
                        },
                        "key": {
                            "type": "string",
                            "description": "PRESTETアイコンの識別子"
                        },
                        "file": {
                            "type": "object",
                            "properties": {
                                "fileKey": {
                                    "type": "string",
                                    "description": "アップロード済みファイルのキー"
                                }
                            }
                        }
                    }
                },
                "theme": {
                    "type": "string",
                    "enum": ["WHITE", "RED", "GREEN", "BLUE", "YELLOW", "BLACK"],
                    "description": "デザインテーマ"
                },
                "titleField": {
                    "type": "object",
                    "properties": {
                        "selectionMode": {
                            "type": "string",
                            "enum": ["AUTO", "MANUAL"],
                            "description": "タイトルフィールドの選択方法"
                        },
                        "code": {
                            "type": "string",
                            "description": "MANUALモード時のフィールドコード"
                        }
                    }
                },
                "enableThumbnails": {
                    "type": "boolean",
                    "description": "サムネイル表示の有効化"
                },
                "enableBulkDeletion": {
                    "type": "boolean",
                    "description": "レコード一括削除の有効化"
                },
                "enableComments": {
                    "type": "boolean",
                    "description": "コメント機能の有効化"
                },
                "enableDuplicateRecord": {
                    "type": "boolean",
                    "description": "レコード再利用機能の有効化"
                },
                "enableInlineRecordEditing": {
                    "type": "boolean",
                    "description": "インライン編集の有効化"
                },
                "numberPrecision": {
                    "type": "object",
                    "properties": {
                        "digits": {
                            "type": "string",
                            "description": "全体の桁数（1-30）"
                        },
                        "decimalPlaces": {
                            "type": "string",
                            "description": "小数部の桁数（0-10）"
                        },
                        "roundingMode": {
                            "type": "string",
                            "enum": ["HALF_EVEN", "UP", "DOWN"],
                            "description": "数値の丸めかた"
                        }
                    }
                },
                "firstMonthOfFiscalYear": {
                    "type": "string",
                    "description": "第一四半期の開始月（1-12）"
                }
            },
            "required": ["app_id"]
        }
    },
    {
        "name": "move_app_to_space",
        "description": "kintoneアプリを指定したスペースに移動します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_id": {
                    "type": "number",
                    "description": "kintoneアプリのID"
                },
                "space_id": {
                    "type": "number",
                    "description": "移動先のスペースID"
                }
            },
            "required": ["app_id", "space_id"]
        }
    },
    {
        "name": "move_app_from_space",
        "description": "kintoneアプリをスペースに所属させないようにします。注意: kintoneシステム管理の「利用する機能の選択」で「スペースに所属しないアプリの作成を許可する」が有効になっている必要があります。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_id": {
                    "type": "number",
                    "description": "kintoneアプリのID"
                }
            },
            "required": ["app_id"]
        }
    },
    {
        "name": "get_preview_app_settings",
        "description": "プレビュー環境のkintoneアプリ設定を取得します",
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
        "name": "get_preview_form_fields",
        "description": "プレビュー環境のkintoneアプリのフォームフィールド情報を取得します",
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
        "name": "get_preview_form_layout",
        "description": "プレビュー環境のkintoneアプリのフォームレイアウト情報を取得します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_id": {
                    "type": "number",
                    "description": "kintoneアプリのID"
                }
            },
            "required": ["app_id"]
        }
    },
    {
        "name": "get_preview_apps",
        "description": "プレビュー状態のアプリに関する情報を取得します（注意：直接的な一覧取得は不可能）",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_preview_form",
        "description": "プレビュー環境のkintoneアプリのフォーム詳細情報（フィールド設定含む）を取得します",
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
        "name": "get_preview_process_management",
        "description": "プレビュー環境のkintoneアプリのプロセス管理設定を取得します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_id": {
                    "type": "number",
                    "description": "kintoneアプリのID"
                }
            },
            "required": ["app_id"]
        }
    },
    {
        "name": "get_preview_app_customization",
        "description": "プレビュー環境のkintoneアプリのカスタマイズ設定を取得します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_id": {
                    "type": "number",
                    "description": "kintoneアプリのID"
                }
            },
            "required": ["app_id"]
        }
    },
    {
        "name": "get_preview_app_views",
        "description": "プレビュー環境のkintoneアプリのビュー設定を取得します",
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
        "name": "get_preview_app_permissions",
        "description": "プレビュー環境のkintoneアプリの権限設定を取得します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_id": {
                    "type": "number",
                    "description": "kintoneアプリのID"
                }
            },
            "required": ["app_id"]
        }
    },
    {
        "name": "get_app_actions",
        "description": "kintoneアプリのアクション設定を取得します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_id": {
                    "type": "number",
                    "description": "kintoneアプリのID"
                },
                "lang": {
                    "type": "string",
                    "enum": ["ja", "en", "zh", "user", "default"],
                    "description": "取得する名称の言語（オプション）"
                }
            },
            "required": ["app_id"]
        }
    },
    {
        "name": "get_app_plugins",
        "description": "kintoneアプリに追加されているプラグインの一覧を取得します",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_id": {
                    "type": "number",
                    "description": "kintoneアプリのID"
                }
            },
            "required": ["app_id"]
        }
    }
] 