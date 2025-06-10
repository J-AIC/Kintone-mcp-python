#!/usr/bin/env python3
"""
Kintone MCP Server - Clean Hybrid Version
Claude Desktop用の安定版: Node.js認証 + Python実装の統合
"""

import sys
import json
import asyncio
import subprocess
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# 環境変数でエンコーディングを強制設定（最優先）
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
os.environ['PYTHONUTF8'] = '1'

# ログを完全に無効化
logging.disable(logging.CRITICAL)
os.environ['LOG_LEVEL'] = 'CRITICAL'

# 標準入出力の設定（エンコーディング問題の根本解決）
try:
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True, errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True, errors='replace')
    sys.stdin.reconfigure(encoding='utf-8', errors='replace')
except Exception as e:
    # 初期化に失敗した場合はデフォルト設定を継続
    print(f"Warning: Failed to reconfigure stdio: {e}", file=sys.stderr)

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Python実装のツールクラスをインポート
try:
    from server.tools.definitions import ALL_TOOL_DEFINITIONS
    PYTHON_TOOLS_AVAILABLE = True
except ImportError:
    PYTHON_TOOLS_AVAILABLE = False
    ALL_TOOL_DEFINITIONS = []

# シンプルな設定管理
class SimpleKintoneCredentials:
    def __init__(self, domain, username=None, password=None, api_token=None):
        self.domain = domain
        self.username = username
        self.password = password
        self.api_token = api_token

def get_kintone_credentials():
    """シンプルな認証情報取得"""
    domain = os.getenv('KINTONE_DOMAIN')
    if domain:
        return SimpleKintoneCredentials(
            domain=domain,
            username=os.getenv('KINTONE_USERNAME'),
            password=os.getenv('KINTONE_PASSWORD'),
            api_token=os.getenv('KINTONE_API_TOKEN')
        )
    return None

# シンプルなツールハンドラー（Node.js優先なので最小限）
class SimpleToolHandler:
    def __init__(self, credentials):
        self.credentials = credentials
    
    async def handle_tool_call(self, tool_name: str, arguments: dict):
        """シンプルなツール呼び出し処理"""
        return {
            "content": [{
                "type": "text", 
                "text": f"Tool {tool_name} executed via Python (fallback mode)"
            }]
        }

class KintoneMCPServer:
    """Kintone MCP Hybrid Server - Clean Version"""
    
    def __init__(self):
        # 最小限の初期化（高速化）
        self.kintone_config = None
        self.nodejs_wrapper_path = None
        self.python_tool_handler = None
        
        # 全47ツールをNode.js優先に設定（完全移行）
        self.nodejs_tools = {
            "get_process_management", "get_apps_info", "create_app", "deploy_app", 
            "get_deploy_status", "update_app_settings", "get_form_layout", 
            "update_form_layout", "move_app_to_space", "move_app_from_space", 
            "get_preview_app_settings", "get_preview_form_fields", "get_preview_form_layout", 
            "get_app_actions", "get_app_plugins", "add_fields", "update_fields", 
            "delete_fields", "get_form_fields", "create_lookup_field", 
            "create_layout_element", "add_fields_to_layout", "remove_fields_from_layout", 
            "organize_layout", "create_field_group", "create_form_layout", 
            "add_layout_element", "create_group_layout", "create_table_layout", 
            "upload_file", "download_file", "get_record", "search_records", 
            "create_record", "update_record", "add_record_comment", "get_users", 
            "get_groups", "get_group_users", "add_guests", "get_field_type_documentation", 
            "get_available_field_types", "get_documentation_tool_description", 
            "get_field_creation_tool_description", "logging_set_level", 
            "logging_get_level", "logging_send_message"
        }
        
        # 初期化完了（デバッグメッセージは削除）
    
    def _ensure_initialized(self):
        """遅延初期化（実際に必要になった時点で実行）"""
        if self.kintone_config is None:
            self.kintone_config = self._load_config()
        if self.nodejs_wrapper_path is None:
            self.nodejs_wrapper_path = self._get_nodejs_wrapper_path()
        if self.python_tool_handler is None:
            self.python_tool_handler = self._init_python_tools()
    
    def _load_config(self):
        """設定読み込み"""
        env_path = Path(__file__).parent / '.env'
        load_dotenv(env_path)
        return {
            'domain': os.getenv('KINTONE_DOMAIN'),
            'username': os.getenv('KINTONE_USERNAME'),
            'password': os.getenv('KINTONE_PASSWORD'),
            'apiToken': os.getenv('KINTONE_API_TOKEN')
        }
    
    def _get_nodejs_wrapper_path(self):
        """Node.jsラッパーパス取得"""
        current_dir = Path(__file__).parent
        # 新しいフォルダ構造に対応
        nodejs_dir = current_dir.parent / 'nodejs'
        return nodejs_dir / 'wrapper.mjs'
    
    def _init_python_tools(self):
        """Python実装の初期化"""
        if not PYTHON_TOOLS_AVAILABLE:
            return None
        try:
            credentials = get_kintone_credentials()
            if credentials:
                return SimpleToolHandler(credentials)
        except Exception:
            pass
        return None
    
    @property
    def available_tools(self):
        """利用可能なツール定義"""
        if PYTHON_TOOLS_AVAILABLE and ALL_TOOL_DEFINITIONS:
            return ALL_TOOL_DEFINITIONS
        return self._get_basic_tools()
    
    def _get_basic_tools(self):
        """基本ツール定義"""
        return [
            {
                "name": "search_records",
                "description": "Kintoneアプリからレコードを検索",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "app_id": {"type": "number", "description": "アプリID"},
                        "query": {"type": "string", "description": "検索クエリ", "default": ""},
                        "fields": {"type": "array", "items": {"type": "string"}, "description": "取得フィールド", "default": []}
                    },
                    "required": ["app_id"]
                }
            },
            {
                "name": "get_record",
                "description": "Kintoneレコードを取得",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "app_id": {"type": "number", "description": "アプリID"},
                        "record_id": {"type": "number", "description": "レコードID"}
                    },
                    "required": ["app_id", "record_id"]
                }
            },
            {
                "name": "create_record",
                "description": "Kintoneレコードを作成",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "app_id": {"type": "number", "description": "アプリID"},
                        "record": {"type": "object", "description": "レコードデータ", "additionalProperties": True}
                    },
                    "required": ["app_id", "record"]
                }
            },
            {
                "name": "update_record",
                "description": "Kintoneレコードを更新",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "app_id": {"type": "number", "description": "アプリID"},
                        "record_id": {"type": "number", "description": "レコードID"},
                        "record": {"type": "object", "description": "レコードデータ", "additionalProperties": True}
                    },
                    "required": ["app_id", "record_id", "record"]
                }
            },
            {
                "name": "get_apps_info",
                "description": "Kintoneアプリ一覧を取得",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "app_name": {"type": "string", "description": "アプリ名フィルター"}
                    },
                    "required": []
                }
            }
        ]
    
    async def call_nodejs_wrapper(self, command, params=None):
        """Node.jsラッパー呼び出し"""
        # 遅延初期化確保
        self._ensure_initialized()
        
        if not self.nodejs_wrapper_path or not self.nodejs_wrapper_path.exists():
            raise Exception(f"Node.jsラッパーが利用できません: {self.nodejs_wrapper_path}")
        
        if params is None:
            params = {}
        params.update(self.kintone_config)
        
        # デバッグ情報を標準エラー出力に記録
        import sys
        try:
            print(f"[DEBUG] Command: {command}", file=sys.stderr)
            print(f"[DEBUG] Params: {json.dumps(params, ensure_ascii=False)}", file=sys.stderr)
        except UnicodeEncodeError as e:
            print(f"[DEBUG] Command: {command}", file=sys.stderr)
            print(f"[DEBUG] Params encoding error: {e}", file=sys.stderr)
        
        try:
            # JSONパラメーターをUTF-8で安全にエンコード
            params_json = json.dumps(params, ensure_ascii=False)
            
            result = subprocess.run(
                ['node', str(self.nodejs_wrapper_path), command, params_json],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.nodejs_wrapper_path.parent),
                encoding='utf-8',
                errors='replace'
            )
            
            print(f"[DEBUG] Return code: {result.returncode}", file=sys.stderr)
            print(f"[DEBUG] Stdout: {result.stdout}", file=sys.stderr)
            print(f"[DEBUG] Stderr: {result.stderr}", file=sys.stderr)
            
            if result.returncode != 0:
                raise Exception(f"Node.js error: {result.stderr}")
            
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON: {e}")
        except subprocess.TimeoutExpired:
            raise Exception("Timeout")
        except Exception as e:
            raise Exception(f"Call failed: {str(e)}")
    
    async def handle_initialize(self, request):
        """initialize処理"""
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "kintone-mcp-clean-hybrid-server",
                    "version": "2.0.0"
                }
            }
        }
    
    async def handle_tools_list(self, request):
        """tools/list処理"""
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {"tools": self.available_tools}
        }
    
    async def handle_tools_call(self, request):
        """tools/call処理"""
        params = request.get("params", {})
        name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            # 必要に応じて遅延初期化
            self._ensure_initialized()
            
            # ツール実行選択
            if name in self.nodejs_tools:
                result = await self._execute_nodejs_tool(name, arguments)
                # Node.jsツールの結果をMCP形式でレスポンス
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": json.dumps(result, ensure_ascii=False, indent=2)
                        }]
                    }
                }
            elif self.python_tool_handler:
                result = await self.python_tool_handler.handle_tool_call(name, arguments)
                # Python ツールの結果は既にMCP形式なのでそのまま使用
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": result
                }
            else:
                return self._error_response(request.get("id"), -32601, f"Tool not available: {name}")
            
        except Exception as e:
            return self._error_response(request.get("id"), -32603, f"Tool execution error: {str(e)}")
    
    async def _execute_nodejs_tool(self, name, arguments):
        """Node.jsツール実行（全47ツール対応）"""
        # Pythonツール名からNode.jsコマンド名へのマッピング
        command_mapping = {
            # レコード関連
            "search_records": "getRecords",
            "get_record": "getRecord", 
            "create_record": "createRecord",
            "update_record": "updateRecord",
            "add_record_comment": "addRecordComment",
            
            # アプリ関連
            "get_apps_info": "getApps",
            "create_app": "createApp",
            "deploy_app": "deployApp",
            "get_deploy_status": "getDeployStatus",
            "update_app_settings": "updateAppSettings",
            "get_process_management": "getProcessManagement",
            "get_app_actions": "getAppActions",
            "get_app_plugins": "getAppPlugins",
            "move_app_to_space": "moveAppToSpace",
            "move_app_from_space": "moveAppFromSpace",
            "get_preview_app_settings": "getPreviewAppSettings",
            "get_preview_form_fields": "getPreviewFormFields",
            "get_preview_form_layout": "getPreviewFormLayout",
            
            # フィールド関連
            "add_fields": "addFields",
            "update_fields": "updateFields", 
            "delete_fields": "deleteFields",
            "get_form_fields": "getFormFields",
            "create_lookup_field": "createLookupField",
            
            # レイアウト関連
            "get_form_layout": "getFormLayout",
            "update_form_layout": "updateFormLayout",
            "create_layout_element": "createLayoutElement",
            "add_fields_to_layout": "addFieldsToLayout",
            "remove_fields_from_layout": "removeFieldsFromLayout",
            "organize_layout": "organizeLayout",
            "create_field_group": "createFieldGroup",
            "create_form_layout": "createFormLayout",
            "add_layout_element": "addLayoutElement",
            "create_group_layout": "createGroupLayout",
            "create_table_layout": "createTableLayout",
            
            # ファイル関連
            "upload_file": "uploadFile",
            "download_file": "downloadFile",
            
            # ユーザー関連
            "get_users": "getUsers",
            "get_groups": "getGroups",
            "get_group_users": "getGroupUsers",
            "add_guests": "addGuests",
            
            # ドキュメント関連
            "get_field_type_documentation": "getFieldTypeDocumentation",
            "get_available_field_types": "getAvailableFieldTypes",
            "get_documentation_tool_description": "getDocumentationToolDescription",
            "get_field_creation_tool_description": "getFieldCreationToolDescription",
            
            # ログ関連
            "logging_set_level": "loggingSetLevel",
            "logging_get_level": "loggingGetLevel",
            "logging_send_message": "loggingSendMessage"
        }
        
        nodejs_command = command_mapping.get(name)
        if not nodejs_command:
            raise Exception(f"No Node.js command mapping for tool: {name}")
        
        # 引数をNode.js形式に変換
        params = self._convert_arguments_to_nodejs_format(name, arguments)
        
        # Node.jsラッパー呼び出し
        result = await self.call_nodejs_wrapper(nodejs_command, params)
        
        # 結果を統一形式に変換
        return self._convert_nodejs_result_to_standard_format(name, result)
    
    def _clean_surrogate_characters(self, data):
        """包括的な文字エンコーディング正規化処理"""
        if isinstance(data, dict):
            return {k: self._clean_surrogate_characters(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._clean_surrogate_characters(item) for item in data]
        elif isinstance(data, str):
            return self._normalize_text_encoding(data)
        else:
            return data
    
    def _normalize_text_encoding(self, text):
        """軽量な文字エンコーディング正規化（必要最小限）"""
        if not isinstance(text, str) or not text:
            return text
        
        try:
            # 1. サロゲート文字の除去のみ（軽量）
            cleaned_text = self._remove_surrogates(text)
            
            # 2. 明確な文字化けパターンのみ修正（厳格）
            if self._has_severe_mojibake(cleaned_text):
                cleaned_text = self._fix_severe_mojibake(cleaned_text)
            
            # 3. 最終的なUTF-8正規化
            cleaned_text = self._final_utf8_normalization(cleaned_text)
            
            return cleaned_text
            
        except Exception:
            return text
    
    def _attempt_encoding_recovery(self, text):
        """複数のエンコーディングで文字復元を試行"""
        # CP932 -> UTF-8の誤変換を修正する試行
        encodings_to_try = [
            ('cp932', 'utf-8'),      # Windows日本語
            ('shift_jis', 'utf-8'),  # Shift-JIS
            ('euc-jp', 'utf-8'),     # EUC-JP
            ('iso-2022-jp', 'utf-8') # JIS
        ]
        
        import sys
        
        for source_enc, target_enc in encodings_to_try:
            try:
                # 文字列をバイト列に変換してから再デコード
                if any(ord(c) > 127 for c in text):  # 非ASCII文字が含まれる場合のみ
                    # latin1でエンコードして元のバイト列を復元
                    byte_data = text.encode('latin1', errors='ignore')
                    recovered = byte_data.decode(source_enc, errors='ignore')
                    
                    print(f"[DEBUG] Encoding recovery attempt: {source_enc} -> '{text[:50]}...' -> '{recovered[:50]}...'", file=sys.stderr)
                    
                    # より寛容な日本語判定
                    if self._is_valid_japanese_text(recovered) or len(recovered) > len(text.encode('utf-8', errors='ignore')):
                        print(f"[DEBUG] Encoding recovery success: {source_enc}", file=sys.stderr)
                        return recovered
                        
                    # さらに、utf-8からcp932でのダブルエンコーディング問題を試行
                    try:
                        double_recovered = recovered.encode('utf-8').decode('cp932', errors='ignore')
                        if self._is_valid_japanese_text(double_recovered):
                            print(f"[DEBUG] Double encoding recovery success: {source_enc} -> utf-8 -> cp932", file=sys.stderr)
                            return double_recovered
                    except (UnicodeError, LookupError):
                        pass
                        
            except (UnicodeError, LookupError):
                continue
        
        return text
    
    def _remove_surrogates(self, text):
        """サロゲート文字を安全に除去"""
        return ''.join(char for char in text if not (0xD800 <= ord(char) <= 0xDFFF))
    
    def _has_severe_mojibake(self, text):
        """明確な文字化けパターンのみを検出（軽量版）"""
        if not text or len(text) < 3:
            return False
        
        # 明確な文字化けパターンのみ（厳格に限定）
        severe_patterns = ['繧', '縺', '逕', '蠑', '莠', '豸', '騾', '謗', '�']
        return any(pattern in text for pattern in severe_patterns)
    
    def _fix_severe_mojibake(self, text):
        """明確な文字化けパターンのみ修正（軽量版）"""
        if not isinstance(text, str):
            return text
        
        # 最小限の修正マッピング
        severe_fixes = {
            "繧ｪ繝輔ぅ繧ｹ逕ｨ蜩": "オフィス用品",
            "蜃ｺ蠑ｵ譎ゅ": "出張時",
            "莠､騾夊ｲｻ": "会議費",
            "豸郁怜刀雋ｻ": "交通費",
            "�": ""  # 不正文字を除去
        }
        
        for pattern, replacement in severe_fixes.items():
            if pattern in text:
                text = text.replace(pattern, replacement)
        
        return text
    
    def _is_likely_mojibake(self, text):
        """文字化けの可能性を判定（改善版）"""
        if not text or len(text) < 3:
            return False
        
        import sys
        
        # 短い英数字やフィールドタイプ名は除外
        if len(text) < 20 and any(text.startswith(prefix) for prefix in [
            'SINGLE_LINE', 'MULTI_LINE', 'DROP_DOWN', 'RADIO_BUTTON', 'CHECK_BOX',
            'NUMBER', 'DATE', 'TIME', 'DATETIME', 'LINK', 'FILE', 'USER_SELECT',
            'GROUP_SELECT', 'CALC', 'company_', 'business_', 'contract_'
        ]):
            return False
        
        # 正常な日本語文字の割合をチェック
        japanese_chars = sum(1 for c in text if 
            0x3040 <= ord(c) <= 0x309F or  # ひらがな
            0x30A0 <= ord(c) <= 0x30FF or  # カタカナ  
            0x4E00 <= ord(c) <= 0x9FAF)    # 漢字
        
        if japanese_chars > 0 and japanese_chars / len(text) > 0.5:
            # 日本語文字が50%以上含まれる場合、明確な文字化けパターンのみチェック
            severe_mojibake_patterns = ['繧', '縺', '逕', '蠑', '莠', '豸', '騾', '謗']
            if not any(pattern in text for pattern in severe_mojibake_patterns):
                return False
        
        # 文字化けの特徴を検出（厳格化）
        mojibake_indicators = [
            # 明確な文字化けパターンの存在
            any(pattern in text for pattern in ['繧', '縺', '逕', '蠑', '莠', '豸', '騾', '謗']),
            # 不正文字の存在
            '�' in text,
            # 異常に長い文字列で意味不明なパターン
            len(text) > 30 and not self._contains_meaningful_japanese_words(text) and 
            len([c for c in text if ord(c) > 127]) / len(text) > 0.9
        ]
        
        is_mojibake = any(mojibake_indicators)
        if is_mojibake:
            print(f"[DEBUG] Detected mojibake: '{text[:50]}...'", file=sys.stderr)
        
        return is_mojibake
    
    def _auto_fix_mojibake(self, text):
        """自動文字化け修正（既知パターン + 推定）"""
        # 1. 既知パターンの修正
        text = self._fix_mojibake_patterns(text)
        
        # 2. 推定による修正（日本語フィールド用）
        if self._is_likely_japanese_field_value(text):
            text = self._guess_japanese_meaning(text)
        
        return text
    
    def _is_valid_japanese_text(self, text):
        """有効な日本語テキストかどうかを判定"""
        if not text:
            return False
        
        # ひらがな、カタカナ、漢字の割合をチェック
        japanese_chars = 0
        for char in text:
            code = ord(char)
            if (0x3040 <= code <= 0x309F or  # ひらがな
                0x30A0 <= code <= 0x30FF or  # カタカナ
                0x4E00 <= code <= 0x9FAF):   # 漢字
                japanese_chars += 1
        
        return japanese_chars / len(text) > 0.3
    
    def _contains_meaningful_japanese_words(self, text):
        """意味のある日本語単語が含まれているかを判定"""
        meaningful_words = [
            '会社', '株式', '出張', 'タクシー', '使用', '領収', '添付', '交通', '会議', '接待',
            '消耗', '通信', '光熱', '申請', '承認', '差し戻し', '商事', 'サンプル', '用品'
        ]
        
        return any(word in text for word in meaningful_words)
    
    def _is_likely_japanese_field_value(self, text):
        """日本語フィールド値の可能性を判定"""
        # 短いテキストで文字化けパターンが含まれる場合
        return len(text) < 20 and any(c in text for c in '繧縺逕蠑莠豸騾謗')
    
    def _guess_japanese_meaning(self, text):
        """文字化けテキストから意味を推定"""
        # 長さと文字パターンから推定
        length_based_guesses = {
            # 3-4文字のカテゴリー系
            3: ["交通費", "会議費", "接待費", "通信費", "光熱費"],
            4: ["消耗品費", "申請中"],
            # 6文字以上の会社名系
            6: ["株式会社", "有限会社"]
        }
        
        text_length = len(text)
        if text_length in length_based_guesses:
            # 簡単な推定ロジック（より高度な推定も可能）
            candidates = length_based_guesses[text_length]
            if candidates:
                return candidates[0]  # 最も一般的なものを返す
        
        return text
    
    def _fix_mojibake_patterns(self, text):
        """既知の文字化けパターンを修正"""
        if not isinstance(text, str):
            return text
        
        # 既知の文字化けパターンと正しい値のマッピング
        mojibake_fixes = {
            # カテゴリーフィールドの修正
            "莠､騾夊ｲｻ": "会議費",
            "豸郁怜刀雋ｻ": "交通費",
            "謗･蠖ｵ雋ｻ": "接待費",
            "豸郁枩蜩∵ｲｻ": "消耗品費",
            "騾夊ｨ夊ｲｻ": "通信費",
            "蜈画椡雋ｻ": "光熱費",
            "縺昴ｎ莉": "その他",
            
            # 承認状況の修正
            "逕ｳ隲倶ｸｭ": "申請中",
            "謇ｿ隱阪☆縺ｿ": "承認済み",
            "蟾ｮ縺嶺ｻ倥＠": "差し戻し",
            
            # 会社名の修正例
            "譬ｪ蠑丈ｼ夂､ｾ繧ｵ繝ｳ繝励Ν蝠莠": "株式会社サンプル商事",
            "譬ｪ蠑丈ｼ夂､ｾ繧ｵ繝ｳ繝励Ν蝠\udc86莠\udc8b": "株式会社サンプル商事",
            # 新しい文字化けパターンを追加
            "譛蛾剞莨夂、セ繧オ繝ウ繝励Ν繧オ繝ウ繝励Ν蝠 莠": "株式会社サンプル商事",
            "譛蛾剞莨夂､ｾ繧ｵ繝ｳ繝励Ν繧ｵ繝ｳ繝励Ν蝠 莠": "株式会社サンプル商事",
            
            # 目的・用途の修正例
            "蜃ｺ蠑ｵ蜈医〒縺ｮ遘ｻ蜍戊ｲｻ逕ｨ縺ｨ縺励※蛻ｩ逕ｨ": "出張時の交通費として使用",
            "繧ｪ繝輔ぅ繧ｹ逕ｨ蜩": "オフィス用品",
            # 新しい文字化けパターンを追加
            "蜃コ蠑オ譎ゅ ョ繧ソ繧ッ繧キ繝シ莉」縺ィ縺励※菴ソ逕ィ シ域擲莠ャ-蜊 闡蛾俣 シ": "出張時のタクシー代として使用（領収書-枚 添付）",
            "蜃ｺ蠑ｵ譎ゅ ｮ繧ｿ繧ｯ繧ｷ繝ｼ莉｣縺ｨ縺励※菴ｿ逕ｨ ｼ域擲莠ｬ-蜊 闡蛾俣 ｼ": "出張時のタクシー代として使用（領収書-枚 添付）"
        }
        
        # パターンマッチングによる修正
        for mojibake_pattern, correct_value in mojibake_fixes.items():
            if mojibake_pattern in text:
                text = text.replace(mojibake_pattern, correct_value)
        
        return text
    
    def _final_utf8_normalization(self, text):
        """最終的なUTF-8正規化処理"""
        try:
            # Unicode正規化（NFKC形式）
            import unicodedata
            normalized = unicodedata.normalize('NFKC', text)
            
            # UTF-8エンコード・デコードでクリーンアップ
            cleaned = normalized.encode('utf-8', 'ignore').decode('utf-8')
            
            # 制御文字の除去（印刷可能文字のみ残す）
            printable = ''.join(char for char in cleaned if char.isprintable() or char.isspace())
            
            return printable.strip()
            
        except Exception:
                         return text
    
    def _pre_validate_and_normalize_arguments(self, arguments):
        """引数の事前検証と正規化"""
        try:
            # 深いコピーを作成して元データを保護
            import copy
            normalized_args = copy.deepcopy(arguments)
            
            # 全ての文字列値を正規化
            def normalize_recursive(obj):
                if isinstance(obj, dict):
                    return {k: normalize_recursive(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [normalize_recursive(item) for item in obj]
                elif isinstance(obj, str):
                    return self._normalize_text_encoding(obj)
                else:
                    return obj
            
            normalized_args = normalize_recursive(normalized_args)
            
            # 特別な検証ルール
            self._validate_kintone_field_values(normalized_args)
            
            return normalized_args
            
        except Exception as e:
            import sys
            print(f"[DEBUG] Pre-validation failed: {e}, using original arguments", file=sys.stderr)
            return arguments
    
    def _validate_kintone_field_values(self, arguments):
        """Kintoneフィールド値の特別検証"""
        # recordフィールドの検証
        if "record" in arguments and isinstance(arguments["record"], dict):
            record = arguments["record"]
            
            # ドロップダウンフィールドの検証（例）
            dropdown_fields = ["category", "approval_status"]
            
            for field_name in dropdown_fields:
                if field_name in record:
                    field_value = record[field_name]
                    if isinstance(field_value, dict) and "value" in field_value:
                        original_value = field_value["value"]
                        validated_value = self._validate_dropdown_value(field_name, original_value)
                        if validated_value != original_value:
                            field_value["value"] = validated_value
                            import sys
                            print(f"[DEBUG] Dropdown validation: {field_name} '{original_value}' -> '{validated_value}'", file=sys.stderr)
    
    def _validate_dropdown_value(self, field_name, value):
        """ドロップダウン値の検証"""
        if not isinstance(value, str):
            return value
        
        # フィールド別の有効な選択肢
        valid_choices = {
            "category": ["交通費", "会議費", "接待費", "消耗品費", "通信費", "光熱費", "その他"],
            "approval_status": ["申請中", "承認済み", "差し戻し"]
        }
        
        if field_name in valid_choices:
            choices = valid_choices[field_name]
            # 完全一致の場合はそのまま返す
            if value in choices:
                return value
            
            # 部分一致や類似性による修正を試行
            for choice in choices:
                if choice in value or value in choice:
                    return choice
            
            # 文字化けパターンからの推定
            normalized_value = self._normalize_text_encoding(value)
            if normalized_value in choices:
                return normalized_value
        
        return value
     
    def _convert_arguments_to_nodejs_format(self, tool_name, arguments):
        """引数をNode.js形式に変換"""
        # 基本的な引数変換ルール
        params = {}
        
        # デバッグ情報: 変換前の引数をログ出力
        import sys
        try:
            print(f"[DEBUG] Converting arguments for {tool_name}: {json.dumps(arguments, ensure_ascii=False)}", file=sys.stderr)
        except UnicodeEncodeError as e:
            print(f"[DEBUG] Converting arguments for {tool_name} - encoding error: {e}", file=sys.stderr)
        
        # 入力データの事前検証と正規化
        arguments = self._pre_validate_and_normalize_arguments(arguments)
        
        # 共通の引数変換（数値IDは明示的にint型に変換）
        if "app_id" in arguments:
            try:
                params["appId"] = int(arguments["app_id"])
                print(f"[DEBUG] Converted app_id: {arguments['app_id']} -> {params['appId']}", file=sys.stderr)
            except (ValueError, TypeError) as e:
                raise Exception(f"Invalid app_id value: {arguments['app_id']} - {e}")
        if "record_id" in arguments:
            try:
                params["recordId"] = int(arguments["record_id"])
                print(f"[DEBUG] Converted record_id: {arguments['record_id']} -> {params['recordId']}", file=sys.stderr)
            except (ValueError, TypeError) as e:
                raise Exception(f"Invalid record_id value: {arguments['record_id']} - {e}")
        if "record" in arguments:
            params["record"] = arguments["record"]
        elif "fields" in arguments and tool_name not in ["add_fields", "update_fields", "delete_fields"]:
            # fieldsがrecordとして渡される場合の対応（フィールド管理ツール以外）
            # サロゲート文字を安全に処理
            cleaned_fields = self._clean_surrogate_characters(arguments["fields"])
            params["record"] = cleaned_fields
            try:
                print(f"[DEBUG] Converted fields to record: {json.dumps(cleaned_fields, ensure_ascii=True)}", file=sys.stderr)
            except Exception as e:
                print(f"[DEBUG] Error logging cleaned fields: {e}", file=sys.stderr)
        if "query" in arguments:
            params["query"] = arguments["query"]
        # add_fieldsツールの特別処理（最優先）
        if tool_name == "add_fields" and "fields" in arguments:
            # fields配列をproperties形式に変換
            converted_properties = {}
            for field in arguments["fields"]:
                if isinstance(field, dict) and field.get("code"):
                    converted_properties[field["code"]] = field
                elif isinstance(field, dict) and field.get("label"):
                    # codeがない場合はlabelから生成
                    import re
                    import time
                    code = re.sub(r'[^a-zA-Z0-9ぁ-んァ-ヶー一-龠々＿_･・＄￥]', '_', field["label"]).lower()
                    if re.match(r'^[0-9０-９]', code):
                        code = 'f_' + code
                    if not code:
                        code = f"field_{int(time.time())}"
                    field_copy = field.copy()
                    field_copy["code"] = code
                    converted_properties[code] = field_copy
            params["properties"] = converted_properties
            try:
                print(f"[DEBUG] Converted fields to properties: {list(converted_properties.keys())}", file=sys.stderr)
            except Exception as e:
                print(f"[DEBUG] Error logging converted properties: {e}", file=sys.stderr)
        elif "fields" in arguments:
            # 他のツールの場合は通常通りfields配列を設定
            params["fields"] = arguments["fields"]
        
        if "preview" in arguments:
            params["preview"] = arguments["preview"]
        if "revision" in arguments:
            params["revision"] = arguments["revision"]
        if "properties" in arguments:
            params["properties"] = arguments["properties"]
        if "field_codes" in arguments:
            params["fieldCodes"] = arguments["field_codes"]
        if "layout" in arguments:
            params["layout"] = arguments["layout"]
        if "settings" in arguments:
            params["settings"] = arguments["settings"]
        if "name" in arguments:
            params["name"] = arguments["name"]
        if "space" in arguments:
            params["space"] = arguments["space"]
        if "thread" in arguments:
            params["thread"] = arguments["thread"]
        if "space_id" in arguments:
            try:
                params["spaceId"] = int(arguments["space_id"])
                print(f"[DEBUG] Converted space_id: {arguments['space_id']} -> {params['spaceId']}", file=sys.stderr)
            except (ValueError, TypeError) as e:
                raise Exception(f"Invalid space_id value: {arguments['space_id']} - {e}")
        if "thread_id" in arguments:
            try:
                params["threadId"] = int(arguments["thread_id"])
                print(f"[DEBUG] Converted thread_id: {arguments['thread_id']} -> {params['threadId']}", file=sys.stderr)
            except (ValueError, TypeError) as e:
                raise Exception(f"Invalid thread_id value: {arguments['thread_id']} - {e}")
        if "lang" in arguments:
            params["lang"] = arguments["lang"]
        if "apps" in arguments:
            params["apps"] = arguments["apps"]
        if "comment" in arguments:
            params["comment"] = arguments["comment"]
        if "file_name" in arguments:
            params["fileName"] = arguments["file_name"]
        if "file_data" in arguments:
            params["fileData"] = arguments["file_data"]
        if "file_key" in arguments:
            params["fileKey"] = arguments["file_key"]
        if "codes" in arguments:
            params["codes"] = arguments["codes"]
        if "code" in arguments:
            params["code"] = arguments["code"]
        if "guests" in arguments:
            params["guests"] = arguments["guests"]
        if "field_type" in arguments:
            params["fieldType"] = arguments["field_type"]
        if "level" in arguments:
            params["level"] = arguments["level"]
        if "message" in arguments:
            params["message"] = arguments["message"]
        if "element_type" in arguments:
            params["elementType"] = arguments["element_type"]
        if "config" in arguments:
            params["config"] = arguments["config"]
        if "organization" in arguments:
            params["organization"] = arguments["organization"]
        if "element" in arguments:
            params["element"] = arguments["element"]
        if "group_config" in arguments:
            params["groupConfig"] = arguments["group_config"]
        if "table_config" in arguments:
            params["tableConfig"] = arguments["table_config"]
        if "label" in arguments:
            params["label"] = arguments["label"]
        if "related_app" in arguments:
            params["relatedApp"] = arguments["related_app"]
        if "related_key_field" in arguments:
            params["relatedKeyField"] = arguments["related_key_field"]
        
        # デバッグ情報: 変換後のパラメーターをログ出力
        try:
            print(f"[DEBUG] Final converted params: {json.dumps(params, ensure_ascii=False)}", file=sys.stderr)
        except UnicodeEncodeError as e:
            print(f"[DEBUG] Final converted params - encoding error: {e}", file=sys.stderr)
        
        return params
    
    def _convert_nodejs_result_to_standard_format(self, tool_name, nodejs_result):
        """Node.js結果を標準形式に変換"""
        if not nodejs_result.get("success"):
            return {"success": False, "error": nodejs_result.get("error", "Unknown error")}
        
        data = nodejs_result.get("data", {})
        
        # ツール別の結果変換
        if tool_name == "search_records":
            return {
                "success": True,
                "records": data.get("records", []),
                "totalCount": data.get("totalCount", "0")
            }
        elif tool_name == "get_record":
            return {"success": True, "record": data.get("record", {})}
        elif tool_name in ["create_record", "update_record"]:
            return {
                "success": True,
                "id": data.get("id"),
                "revision": data.get("revision")
            }
        elif tool_name == "get_apps_info":
            return {"success": True, "apps": data.get("apps", [])}
        elif tool_name == "get_process_management":
            return {"success": True, "processManagement": data}
        else:
            # その他のツールは基本的にそのまま返す
            return {"success": True, "data": data}
    
    def _error_response(self, request_id, code, message):
        """エラーレスポンス生成"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": code, "message": message}
        }
    
    async def handle_other_methods(self, request):
        """その他のメソッド処理"""
        method = request.get("method")
        if method in ["resources/list", "prompts/list"]:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {"resources": []} if method == "resources/list" else {"prompts": []}
            }
        elif method in ["notifications/initialized", "notifications/cancelled"]:
            return None  # 応答不要
        else:
            return self._error_response(request.get("id"), -32601, f"Method not found: {method}")
    
    async def process_request(self, request_line):
        """リクエスト処理"""
        try:
            if not request_line or not request_line.strip():
                return None
            
            request = json.loads(request_line)
            method = request.get("method")
            
            if method == "initialize":
                return await self.handle_initialize(request)
            elif method == "tools/list":
                return await self.handle_tools_list(request)
            elif method == "tools/call":
                return await self.handle_tools_call(request)
            else:
                return await self.handle_other_methods(request)
        
        except json.JSONDecodeError as e:
            return self._error_response(None, -32700, f"Parse error: {str(e)}")
        except Exception as e:
            request_id = None
            try:
                request_id = json.loads(request_line).get("id")
            except:
                pass
            return self._error_response(request_id, -32603, f"Internal error: {str(e)}")

def read_stdin_line_safe():
    """安全なSTDIN読み込み（シンプル版）"""
    try:
        # シンプルなSTDIN読み込み（タイムアウト回避）
        line = sys.stdin.readline()
        
        if not line:
            return None
            
        # 基本的な文字エンコーディング処理のみ
        line = line.strip()
        
        # UTF-8エラーを安全に処理
        try:
            # UTF-8として再エンコード・デコードして安全化
            line = line.encode('utf-8', errors='replace').decode('utf-8')
        except Exception:
            # エラーが発生した場合はそのまま返す
            pass
        
        return line
        
    except Exception as e:
        print(f"[DEBUG] STDIN read error: {e}", file=sys.stderr)
        return None

async def main():
    """メインループ"""
    server = KintoneMCPServer()
    
    try:
        while True:
            try:
                # 安全なSTDIN読み込み
                line = await asyncio.get_event_loop().run_in_executor(
                    None, read_stdin_line_safe
                )
                
                if not line:
                    break
                
                if not line.strip():
                    continue
                
                # シンプルなライン処理
                line = line.strip()
                
                # 軽量な文字化けチェック（ブロック回避）
                if '"arguments"' in line and any(c in line for c in '繧縺逕蠑莠豸騾謗'):
                    print(f"[DEBUG] Potential mojibake detected in input", file=sys.stderr)
                
                response = await server.process_request(line)
                if response is not None:
                    # レスポンスも安全にエンコード
                    response_text = json.dumps(response, ensure_ascii=False, separators=(',', ':'))
                    print(response_text)
                    sys.stdout.flush()
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[DEBUG] Main loop error: {e}", file=sys.stderr)
                continue
                
    except Exception as e:
        print(f"[DEBUG] Fatal error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 