"""
Node.js @kintone/rest-api-clientを使用するPython用クライアント
"""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List
from pydantic import ValidationError

from ..utils.logging_config import get_logger
from ..utils.exceptions import (
    KintoneError, KintoneValidationError, NodeJSWrapperError, 
    create_error_from_nodejs_response, format_validation_error
)
from ..models.validation_models import (
    GetRecordRequest, GetRecordsRequest, CreateRecordRequest, 
    UpdateRecordRequest, UpdateRecordByKeyRequest, AddRecordCommentRequest,
    CreateAppRequest, DeployAppRequest, GetDeployStatusRequest, GetAppFormFieldsRequest
)

logger = get_logger(__name__)


class NodeJSKintoneClient:
    """Node.js @kintone/rest-api-clientを使用するPythonクライアント"""
    
    def __init__(self, domain: str, username: str = None, password: str = None, api_token: str = None):
        self.domain = domain
        self.username = username
        self.password = password
        self.api_token = api_token
        
        # Node.jsラッパースクリプトのパス
        # 現在のファイルから相対的にプロジェクトルートを計算 (src/python/repositories/nodejs_kintone_client.py から3つ上)
        project_root = Path(__file__).resolve().parents[3] 
        self.wrapper_path = project_root / 'src' / 'nodejs' / 'wrapper.mjs'
        self.js_dir = self.wrapper_path.parent
        
        logger.info(f"NodeJSKintoneClient initialized for domain: {domain}")
    
    def _validate_request(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """リクエストパラメータをバリデーション"""
        
        # パラメータを取らないコマンドはバリデーションをスキップ
        no_param_commands = {'getApps'}
        if command in no_param_commands:
            return params
        
        # バリデーションモデルのマッピング
        validation_models = {
            'getRecord': GetRecordRequest,
            'getRecords': GetRecordsRequest,
            'createRecord': CreateRecordRequest,
            'updateRecord': UpdateRecordRequest,
            'updateRecordByKey': UpdateRecordByKeyRequest,
            'addRecordComment': AddRecordCommentRequest,
            'createApp': CreateAppRequest,
            'deployApp': DeployAppRequest,
            'getDeployStatus': GetDeployStatusRequest,
            'getAppFormFields': GetAppFormFieldsRequest,
        }
        
        model_class = validation_models.get(command)
        if model_class:
            try:
                # 認証情報を含めてバリデーション
                full_params = {
                    'domain': self.domain,
                    'username': self.username,
                    'password': self.password,
                    'apiToken': self.api_token,
                    **params
                }
                validated_request = model_class(**full_params)
                return validated_request.dict(exclude_none=True)
            except ValidationError as e:
                logger.error(f"Validation error for command {command}: {e}")
                raise format_validation_error(e)
        
        # バリデーションモデルが定義されていないコマンドはそのまま通す
        return params

    async def _execute_nodejs_command(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Node.jsコマンドを実行"""
        
        # パラメータバリデーション
        try:
            validated_params = self._validate_request(command, params)
        except KintoneValidationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected validation error: {e}")
            raise KintoneValidationError(f"パラメータバリデーションでエラーが発生しました: {str(e)}")
        
        # 認証情報を追加（バリデーション済みでない場合）
        if 'domain' not in validated_params:
            full_params = {
                'domain': self.domain,
                'username': self.username,
                'password': self.password,
                'apiToken': self.api_token,
                **validated_params
            }
        else:
            full_params = validated_params
        
        try:
            logger.debug(f"Executing Node.js command: {command}")
            logger.debug(
                f"Params: {json.dumps({k: v for k, v in full_params.items() if k not in ['password', 'apiToken']})}"
            )

            proc = await asyncio.create_subprocess_exec(
                'node',
                str(self.wrapper_path),
                command,
                json.dumps(full_params),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.js_dir)
            )

            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)
            except asyncio.TimeoutError:
                logger.error("Node.js command timed out")
                proc.kill()
                await proc.wait()
                raise Exception("Node.js command timed out")

            stdout_text = stdout.decode('utf-8') if stdout else ''
            stderr_text = stderr.decode('utf-8') if stderr else ''

            if proc.returncode != 0:
                logger.error(f"Node.js command failed with return code: {proc.returncode}")
                logger.error(f"STDERR: {stderr_text}")
                raise Exception(f"Node.js command failed: {stderr_text}")

            try:
                response = json.loads(stdout_text)
                if not response.get('success'):
                    logger.error(f"Kintone API error: {response}")
                    # カスタム例外を使用してエラーを処理
                    raise create_error_from_nodejs_response(response)

                return response.get('data')
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Node.js response: {stdout_text}")
                raise NodeJSWrapperError(
                    f"Node.jsレスポンスの解析に失敗しました: {str(e)}",
                    command=command,
                    details={'stdout': stdout_text, 'stderr': stderr_text}
                )

        except (KintoneError, NodeJSWrapperError):
            # カスタム例外はそのまま再発生
            raise
        except asyncio.TimeoutError:
            logger.error("Node.js command timed out")
            raise NodeJSWrapperError(
                "Node.jsコマンドがタイムアウトしました",
                command=command,
                details={'timeout_seconds': 60}
            )
        except Exception as e:
            logger.error(f"Error executing Node.js command: {e}")
            raise NodeJSWrapperError(
                f"Node.jsコマンドの実行中にエラーが発生しました: {str(e)}",
                command=command,
                details={'original_error': str(e)}
            )

    async def close(self) -> None:
        """互換性のためのダミー実装"""
        return None

    async def request(
        self,
        method: str,
        path: str,
        body: Dict[str, Any] | None = None,
        params: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """HTTPリクエストを実行"""

        return await self._execute_nodejs_command(
            "request",
            {
                "method": method,
                "path": path,
                "body": body,
                "params": params,
            },
        )

    async def get(self, path: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """GETリクエスト"""
        return await self.request("GET", path, params=params)

    async def post(self, path: str, body: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """POSTリクエスト"""
        return await self.request("POST", path, body=body)

    async def put(self, path: str, body: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """PUTリクエスト"""
        return await self.request("PUT", path, body=body)

    async def delete(self, path: str, body: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """DELETEリクエスト"""
        return await self.request("DELETE", path, body=body)
    
    async def get_apps(self) -> List[Dict[str, Any]]:
        """アプリ一覧を取得"""
        return await self._execute_nodejs_command('getApps', {})
    
    async def get_record(self, app_id: int, record_id: int) -> Dict[str, Any]:
        """レコードを取得"""
        return await self._execute_nodejs_command('getRecord', {
            'appId': app_id,
            'recordId': record_id
        })
    
    async def get_records(self, app_id: int, query: str = '', fields: List[str] = None) -> Dict[str, Any]:
        """レコード一覧を取得"""
        return await self._execute_nodejs_command('getRecords', {
            'appId': app_id,
            'query': query,
            'fields': fields or []
        })
    
    async def create_record(self, app_id: int, record: Dict[str, Any]) -> Dict[str, Any]:
        """レコードを作成"""
        return await self._execute_nodejs_command('createRecord', {
            'appId': app_id,
            'record': record
        })
    
    async def update_record(self, app_id: int, record_id: int, record: Dict[str, Any]) -> Dict[str, Any]:
        """レコードを更新"""
        return await self._execute_nodejs_command('updateRecord', {
            'appId': app_id,
            'recordId': record_id,
            'record': record
        })

    async def update_record_by_key(
        self,
        app_id: int,
        key_field: str,
        key_value: str,
        record: Dict[str, Any],
        revision: int | None = None,
    ) -> Dict[str, Any]:
        """重複禁止フィールドを使用してレコードを更新"""

        body = {
            "appId": app_id,
            "keyField": key_field,
            "keyValue": key_value,
            "record": record,
            "revision": revision,
        }
        return await self._execute_nodejs_command("updateRecordByKey", body)

    async def add_record_comment(
        self,
        app_id: int,
        record_id: int,
        text: str,
        mentions: List[Dict[str, str]] | None = None,
    ) -> Dict[str, Any]:
        """レコードにコメントを追加"""

        return await self._execute_nodejs_command(
            "addRecordComment",
            {
                "appId": app_id,
                "recordId": record_id,
                "text": text,
                "mentions": mentions or [],
            },
        )

    async def create_app(
        self,
        name: str,
        space: int | None = None,
        thread: int | None = None,
    ) -> Dict[str, Any]:
        """アプリを作成"""

        return await self._execute_nodejs_command(
            "createApp",
            {"name": name, "space": space, "thread": thread},
        )

    async def deploy_app(self, apps: List[int]) -> Dict[str, Any]:
        """アプリをデプロイ"""
        return await self._execute_nodejs_command("deployApp", {"apps": apps})

    async def get_deploy_status(self, apps: List[int]) -> Dict[str, Any]:
        """デプロイ状況を取得"""
        return await self._execute_nodejs_command(
            "getDeployStatus", {"apps": apps}
        )

    async def get_app_form_fields(self, app_id: int) -> Dict[str, Any]:
        """アプリのフィールド情報を取得"""
        return await self._execute_nodejs_command(
            "getAppFormFields",
            {"appId": app_id},
        )

    # プレビュー関連メソッド
    async def get_preview_apps(self) -> Dict[str, Any]:
        """プレビューアプリ一覧を取得（注意：直接的な取得は不可）"""
        return await self._execute_nodejs_command("getPreviewApps", {})

    async def get_preview_form(self, app_id: int, lang: str = None) -> Dict[str, Any]:
        """プレビュー環境のフォーム詳細を取得"""
        params = {"appId": app_id}
        if lang:
            params["lang"] = lang
        return await self._execute_nodejs_command("getPreviewForm", params)

    async def get_preview_process_management(self, app_id: int) -> Dict[str, Any]:
        """プレビュー環境のプロセス管理設定を取得"""
        return await self._execute_nodejs_command(
            "getPreviewProcessManagement", {"appId": app_id}
        )

    async def get_preview_app_customization(self, app_id: int) -> Dict[str, Any]:
        """プレビュー環境のアプリカスタマイズ設定を取得"""
        return await self._execute_nodejs_command(
            "getPreviewAppCustomization", {"appId": app_id}
        )

    async def get_preview_app_views(self, app_id: int, lang: str = None) -> Dict[str, Any]:
        """プレビュー環境のビュー設定を取得"""
        params = {"appId": app_id}
        if lang:
            params["lang"] = lang
        return await self._execute_nodejs_command("getPreviewAppViews", params)

    async def get_preview_app_permissions(self, app_id: int) -> Dict[str, Any]:
        """プレビュー環境のアプリ権限設定を取得"""
        return await self._execute_nodejs_command(
            "getPreviewAppPermissions", {"appId": app_id}
        )


class NodeJSKintoneClientFactory:
    """NodeJSKintoneClientのファクトリークラス"""
    
    @staticmethod
    def create_from_credentials(credentials) -> NodeJSKintoneClient:
        """認証情報からクライアントを作成"""
        
        if credentials.is_api_token_auth:
            return NodeJSKintoneClient(
                domain=credentials.domain,
                api_token=credentials.api_token
            )
        else:
            return NodeJSKintoneClient(
                domain=credentials.domain,
                username=credentials.username,
                password=credentials.password
            )


# 既存のKintoneClientとの互換性を保つためのエイリアス
KintoneClient = NodeJSKintoneClient 
