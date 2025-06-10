"""
Kintone App Repository

Kintoneアプリの操作を担当するリポジトリクラス
"""

import logging
from typing import Dict, Any, List, Optional, Union

from ..models.kintone_credentials import KintoneCredentials
from ..models.kintone_app import (
    AppCreationRequest, AppSettings, AppDeployRequest, DeployStatus,
    AppMoveRequest, FormLayout, FieldProperties, AppInfo
)
from ..models.kintone_field import KintoneField, FieldCreationRequest, FieldUpdateRequest, FieldDeleteRequest
from .base import BaseKintoneRepository
from ..utils.exceptions import KintoneAPIError

logger = logging.getLogger(__name__)


class KintoneAppRepository(BaseKintoneRepository):
    """Kintoneアプリ操作リポジトリ"""
    
    def __init__(self, credentials: KintoneCredentials):
        """
        Args:
            credentials: Kintone認証情報
        """
        super().__init__(credentials)
    
    async def get_apps_info(self, app_name: Optional[str] = None) -> Dict[str, Any]:
        """
        アプリ一覧情報を取得
        
        Args:
            app_name: アプリ名（フィルタ用、オプション）
            
        Returns:
            Dict[str, Any]: アプリ一覧情報
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            logger.debug(f"Fetching apps info: {app_name}")
            
            # 全アプリを取得
            response = await self.client.get_apps()
            logger.debug(f"Apps info response: {response}")
            
            # app_nameが指定されている場合はフィルタリング
            if app_name and isinstance(response, list):
                filtered_apps = [
                    app for app in response 
                    if app_name.lower() in app.get('name', '').lower()
                ]
                return {"apps": filtered_apps}
            elif isinstance(response, list):
                return {"apps": response}
            else:
                return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"get apps info {app_name}")
    
    async def get_app_settings(self, app_id: int, lang: Optional[str] = None) -> Dict[str, Any]:
        """
        アプリ設定を取得
        
        Args:
            app_id: アプリID
            lang: 言語設定（オプション）
            
        Returns:
            Dict[str, Any]: アプリ設定
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Fetching app settings for app: {app_id}")
            
            params = {"app": app_id}
            if lang:
                params["lang"] = lang
            
            response = await self.client.get("/k/v1/app/settings.json", params=params)
            logger.debug(f"App settings response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"get app settings for app {app_id}")
    
    async def create_app(
        self, 
        name: str, 
        space: Optional[int] = None, 
        thread: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        新しいアプリを作成
        
        Args:
            name: アプリ名
            space: スペースID（オプション）
            thread: スレッドID（オプション）
            
        Returns:
            Dict[str, Any]: 作成結果
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            logger.debug(f"Creating new app: {name}")
            response = await self.client.create_app(name, space, thread)
            logger.debug(f"App creation response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"create app {name}")
    
    async def deploy_app(self, apps: List[int]) -> Dict[str, Any]:
        """
        アプリをデプロイ
        
        Args:
            apps: デプロイするアプリIDのリスト
            
        Returns:
            Dict[str, Any]: デプロイ結果
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            logger.debug(f"Deploying apps: {apps}")
            # Node.jsクライアントは単純なIDの配列を受け取り、内部で正しい形式に変換する
            response = await self.client.deploy_app(apps)
            logger.debug(f"Deploy response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"deploy apps {', '.join(map(str, apps))}")
    
    async def get_deploy_status(self, apps: List[int]) -> Dict[str, Any]:
        """
        デプロイ状況を取得
        
        Args:
            apps: 確認するアプリIDのリスト
            
        Returns:
            Dict[str, Any]: デプロイ状況
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            logger.debug(f"Checking deploy status for apps: {apps}")
            response = await self.client.get_deploy_status(apps)
            logger.debug(f"Deploy status: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"get deploy status for apps {', '.join(map(str, apps))}")
    
    async def update_app_settings(self, app_id: int, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        アプリ設定を更新
        
        Args:
            app_id: アプリID
            settings: 更新する設定
            
        Returns:
            Dict[str, Any]: 更新結果
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Updating app settings for app {app_id}")
            logger.debug(f"Settings: {settings}")
            
            body = {"app": app_id, **settings}
            response = await self.client.put("/k/v1/preview/app/settings.json", body=body)
            logger.debug(f"Update response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"update app settings for app {app_id}")
    
    async def get_form_layout(self, app_id: int, preview: bool = False) -> Dict[str, Any]:
        """
        アプリのフォームレイアウト情報を取得
        
        Args:
            app_id: アプリID
            preview: プレビュー環境から取得するかどうか
            
        Returns:
            Dict[str, Any]: レイアウト情報
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Fetching form layout for app: {app_id} (preview: {preview})")
            
            if preview:
                path = "/k/v1/preview/app/form/layout.json"
            else:
                path = "/k/v1/app/form/layout.json"
            
            try:
                response = await self.client.get(path, params={"app": app_id})
                logger.debug(f"Form layout response: {response}")
                return response
            except KintoneAPIError as error:
                # 404エラーの場合、プレビュー環境を試す
                if not preview and (error.code == 'GAIA_AP01' or error.status == 404):
                    logger.debug(f"App {app_id} not found in production, trying preview environment...")
                    preview_response = await self.client.get(
                        "/k/v1/preview/app/form/layout.json", 
                        params={"app": app_id}
                    )
                    preview_response["preview"] = True
                    preview_response["message"] = "このレイアウト情報はプレビュー環境から取得されました。アプリをデプロイするには deploy_app ツールを使用してください。"
                    return preview_response
                raise
            
        except Exception as error:
            self.handle_kintone_error(error, f"get form layout for app {app_id}")
    
    async def get_form_fields(self, app_id: int, preview: bool = False, lang: Optional[str] = None) -> Dict[str, Any]:
        """
        アプリのフィールド情報を取得
        
        Args:
            app_id: アプリID
            preview: プレビュー環境から取得するかどうか
            lang: 言語設定（オプション）
            
        Returns:
            Dict[str, Any]: フィールド情報
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Fetching form fields for app: {app_id} (preview: {preview})")
            
            params = {"app": app_id}
            if lang:
                params["lang"] = lang
            
            if preview:
                path = "/k/v1/preview/app/form/fields.json"
            else:
                path = "/k/v1/app/form/fields.json"
            
            try:
                response = await self.client.get(path, params=params)
                logger.debug(f"Form fields response: {response}")
                return response
            except KintoneAPIError as error:
                # 404エラーの場合、プレビュー環境を試す
                if not preview and (error.code == 'GAIA_AP01' or error.status == 404):
                    logger.debug(f"App {app_id} not found in production, trying preview environment...")
                    preview_response = await self.client.get(
                        "/k/v1/preview/app/form/fields.json", 
                        params=params
                    )
                    
                    # ルックアップフィールドの情報をログ出力
                    properties = preview_response.get("properties", {})
                    lookup_fields = [(code, field) for code, field in properties.items() 
                                   if field.get("lookup") is not None]
                    if lookup_fields:
                        logger.debug(f"Found {len(lookup_fields)} lookup fields in preview environment")
                        for code, field in lookup_fields:
                            lookup_info = field.get("lookup", {})
                            logger.debug(f"Lookup field '{code}': type={field.get('type')}, "
                                       f"relatedApp={lookup_info.get('relatedApp', {}).get('app')}, "
                                       f"relatedKeyField={lookup_info.get('relatedKeyField')}")
                    else:
                        logger.debug("No lookup fields found in preview environment")
                    
                    preview_response["preview"] = True
                    preview_response["message"] = "このフィールド情報はプレビュー環境から取得されました。アプリをデプロイするには deploy_app ツールを使用してください。"
                    return preview_response
                raise
            
        except Exception as error:
            self.handle_kintone_error(error, f"get form fields for app {app_id}")
    
    async def get_preview_app_settings(self, app_id: int, lang: Optional[str] = None) -> Dict[str, Any]:
        """
        プレビュー環境のアプリ設定を取得
        
        Args:
            app_id: アプリID
            lang: 言語設定（オプション）
            
        Returns:
            Dict[str, Any]: アプリ設定情報
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Fetching preview app settings for app: {app_id}")
            
            params = {"app": app_id}
            if lang:
                params["lang"] = lang
            
            response = await self.client.get("/k/v1/preview/app/settings.json", params=params)
            logger.debug(f"Preview app settings response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"get preview app settings for app {app_id}")
    
    async def get_preview_apps(self) -> Dict[str, Any]:
        """
        プレビューアプリ一覧を取得（注意：直接的な取得は不可能）
        
        Returns:
            Dict[str, Any]: エラーメッセージと推奨事項
        """
        try:
            logger.debug("Attempting to get preview apps list")
            # NodeJSクライアント経由で実行
            return await self.client.get_preview_apps()
            
        except Exception as error:
            self.handle_kintone_error(error, "get preview apps")
    
    async def get_preview_form(self, app_id: int, lang: Optional[str] = None) -> Dict[str, Any]:
        """
        プレビュー環境のフォーム詳細情報を取得
        
        Args:
            app_id: アプリID
            lang: 言語設定（オプション）
            
        Returns:
            Dict[str, Any]: フォーム詳細情報
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Fetching preview form for app: {app_id}")
            
            # NodeJSクライアント経由で実行
            return await self.client.get_preview_form(app_id, lang)
            
        except Exception as error:
            self.handle_kintone_error(error, f"get preview form for app {app_id}")
    
    async def get_preview_process_management(self, app_id: int) -> Dict[str, Any]:
        """
        プレビュー環境のプロセス管理設定を取得
        
        Args:
            app_id: アプリID
            
        Returns:
            Dict[str, Any]: プロセス管理設定情報
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Fetching preview process management for app: {app_id}")
            
            # NodeJSクライアント経由で実行
            return await self.client.get_preview_process_management(app_id)
            
        except Exception as error:
            self.handle_kintone_error(error, f"get preview process management for app {app_id}")
    
    async def get_preview_app_customization(self, app_id: int) -> Dict[str, Any]:
        """
        プレビュー環境のアプリカスタマイズ設定を取得
        
        Args:
            app_id: アプリID
            
        Returns:
            Dict[str, Any]: カスタマイズ設定情報
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Fetching preview app customization for app: {app_id}")
            
            # NodeJSクライアント経由で実行
            return await self.client.get_preview_app_customization(app_id)
            
        except Exception as error:
            self.handle_kintone_error(error, f"get preview app customization for app {app_id}")
    
    async def get_preview_app_views(self, app_id: int, lang: Optional[str] = None) -> Dict[str, Any]:
        """
        プレビュー環境のビュー設定を取得
        
        Args:
            app_id: アプリID
            lang: 言語設定（オプション）
            
        Returns:
            Dict[str, Any]: ビュー設定情報
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Fetching preview app views for app: {app_id}")
            
            # NodeJSクライアント経由で実行
            return await self.client.get_preview_app_views(app_id, lang)
            
        except Exception as error:
            self.handle_kintone_error(error, f"get preview app views for app {app_id}")
    
    async def get_preview_app_permissions(self, app_id: int) -> Dict[str, Any]:
        """
        プレビュー環境のアプリ権限設定を取得
        
        Args:
            app_id: アプリID
            
        Returns:
            Dict[str, Any]: 権限設定情報
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Fetching preview app permissions for app: {app_id}")
            
            # NodeJSクライアント経由で実行
            return await self.client.get_preview_app_permissions(app_id)
            
        except Exception as error:
            self.handle_kintone_error(error, f"get preview app permissions for app {app_id}")
    
    async def update_form_layout(
        self, 
        app_id: int, 
        layout: List[Dict[str, Any]], 
        revision: int = -1
    ) -> Dict[str, Any]:
        """
        フォームレイアウトを更新
        
        Args:
            app_id: アプリID
            layout: レイアウト配列
            revision: リビジョン番号（省略時は最新）
            
        Returns:
            Dict[str, Any]: 更新結果
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Updating form layout for app {app_id}")
            
            body = {
                "app": app_id,
                "layout": layout,
                "revision": revision
            }
            
            response = await self.client.put("/k/v1/preview/app/form/layout.json", body=body)
            logger.debug(f"Update layout response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"update form layout for app {app_id}")
    
    async def add_form_fields(
        self, 
        app_id: int, 
        properties: Dict[str, Any], 
        revision: int = -1
    ) -> Dict[str, Any]:
        """
        フォームフィールドを追加
        
        Args:
            app_id: アプリID
            properties: フィールドプロパティ
            revision: リビジョン番号（省略時は最新）
            
        Returns:
            Dict[str, Any]: 追加結果
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Adding fields to app {app_id}")
            logger.debug(f"Field properties: {properties}")
            
            body = {
                "app": app_id,
                "properties": properties,
                "revision": revision
            }
            
            response = await self.client.post("/k/v1/preview/app/form/fields.json", body=body)
            logger.debug(f"Add fields response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"add fields to app {app_id}")
    
    async def update_form_fields(
        self, 
        app_id: int, 
        properties: Dict[str, Any], 
        revision: int = -1
    ) -> Dict[str, Any]:
        """
        フォームフィールドを更新
        
        Args:
            app_id: アプリID
            properties: フィールドプロパティ
            revision: リビジョン番号（省略時は最新）
            
        Returns:
            Dict[str, Any]: 更新結果
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Updating fields for app {app_id}")
            
            body = {
                "app": app_id,
                "properties": properties,
                "revision": revision
            }
            
            response = await self.client.put("/k/v1/preview/app/form/fields.json", body=body)
            logger.debug(f"Update fields response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"update fields for app {app_id}")
    
    async def delete_form_fields(
        self, 
        app_id: int, 
        fields: List[str], 
        revision: int = -1
    ) -> Dict[str, Any]:
        """
        フォームフィールドを削除
        
        Args:
            app_id: アプリID
            fields: 削除するフィールドコードの配列
            revision: リビジョン番号（省略時は最新）
            
        Returns:
            Dict[str, Any]: 削除結果
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Deleting fields from app {app_id}: {fields}")
            
            body = {
                "app": app_id,
                "fields": fields,
                "revision": revision
            }
            
            response = await self.client.delete("/k/v1/preview/app/form/fields.json", body=body)
            logger.debug(f"Delete fields response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"delete fields from app {app_id}")
    
    async def move_app_to_space(self, app_id: int, space_id: int) -> Dict[str, Any]:
        """
        アプリを指定したスペースに移動
        
        Args:
            app_id: アプリID
            space_id: スペースID
            
        Returns:
            Dict[str, Any]: 移動結果
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Moving app {app_id} to space {space_id}")
            
            body = {
                "app": app_id,
                "space": space_id
            }
            
            await self.client.put("/k/v1/app/move.json", body=body)
            return {"success": True}
            
        except Exception as error:
            self.handle_kintone_error(error, f"move app {app_id} to space {space_id}")
    
    async def move_app_from_space(self, app_id: int) -> Dict[str, Any]:
        """
        アプリをスペースに所属させないようにする
        
        Args:
            app_id: アプリID
            
        Returns:
            Dict[str, Any]: 移動結果
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Moving app {app_id} from space")
            
            body = {
                "app": app_id,
                "space": None
            }
            
            await self.client.put("/k/v1/app/move.json", body=body)
            return {"success": True}
            
        except KintoneAPIError as error:
            # kintoneシステム設定による制限の場合の特別なエラーハンドリング
            if error.code == 'CB_NO01' or (
                error.message and 'スペースに所属しないアプリの作成を許可' in error.message
            ):
                raise Exception(
                    f"アプリ {app_id} をスペースに所属させないようにすることができませんでした。\n\n"
                    "【考えられる原因】\n"
                    "kintoneシステム管理の「利用する機能の選択」で「スペースに所属しないアプリの作成を許可する」が無効になっている可能性があります。\n\n"
                    "【対応方法】\n"
                    "1. kintone管理者に「スペースに所属しないアプリの作成を許可する」設定を有効にするよう依頼してください。\n"
                    "2. または、アプリを別のスペースに移動する方法を検討してください。"
                )
            self.handle_kintone_error(error, f"move app {app_id} from space")
        except Exception as error:
            self.handle_kintone_error(error, f"move app {app_id} from space")
    
    async def get_app_actions(self, app_id: int, lang: Optional[str] = None) -> Dict[str, Any]:
        """
        アプリのアクション設定を取得
        
        Args:
            app_id: アプリID
            lang: 言語設定（オプション）
            
        Returns:
            Dict[str, Any]: アクション設定情報
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Fetching app actions for app: {app_id}")
            
            params = {"app": app_id}
            if lang:
                params["lang"] = lang
            
            response = await self.client.get("/k/v1/app/actions.json", params=params)
            logger.debug(f"App actions response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"get app actions for app {app_id}")
    
    async def get_app_plugins(self, app_id: int) -> Dict[str, Any]:
        """
        アプリに追加されているプラグインの一覧を取得
        
        Args:
            app_id: アプリID
            
        Returns:
            Dict[str, Any]: プラグイン情報
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Fetching plugins for app: {app_id}")
            
            response = await self.client.get("/k/v1/app/plugins.json", params={"app": app_id})
            logger.debug(f"Plugins response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"get app plugins for app {app_id}")
    
    async def get_process_management(self, app_id: int, preview: bool = False) -> Dict[str, Any]:
        """
        アプリのプロセス管理設定を取得
        
        Args:
            app_id: アプリID
            preview: プレビュー環境から取得するかどうか
            
        Returns:
            Dict[str, Any]: プロセス管理設定情報
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Fetching process management for app: {app_id} (preview: {preview})")
            
            if preview:
                path = "/k/v1/preview/app/status.json"
            else:
                path = "/k/v1/app/status.json"
            
            response = await self.client.get(path, params={"app": app_id})
            logger.debug(f"Process management response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"get process management for app {app_id}")

    # アプリ設定の詳細操作メソッド
    async def get_app_settings_detailed(self, app_id: int, lang: Optional[str] = None) -> Dict[str, Any]:
        """
        アプリ設定の詳細情報を取得
        
        Args:
            app_id: アプリID
            lang: 言語設定（オプション）
            
        Returns:
            Dict[str, Any]: アプリ設定詳細
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Fetching detailed app settings for app: {app_id}")
            
            params = {"appId": app_id}
            if lang:
                params["lang"] = lang
            
            response = await self.client.execute_nodejs_command("getAppSettings", params)
            logger.debug(f"Detailed app settings response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"get detailed app settings for app {app_id}")

    async def update_app_settings_detailed(
        self, 
        app_id: int, 
        settings: Dict[str, Any], 
        revision: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        アプリ設定の詳細更新
        
        Args:
            app_id: アプリID
            settings: 更新する設定
            revision: リビジョン番号（オプション）
            
        Returns:
            Dict[str, Any]: 更新結果
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Updating detailed app settings for app {app_id}")
            logger.debug(f"Settings: {settings}")
            
            params = {
                "appId": app_id,
                "settings": settings
            }
            if revision is not None:
                params["revision"] = revision
            
            response = await self.client.execute_nodejs_command("updateAppSettings", params)
            logger.debug(f"Update detailed settings response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"update detailed app settings for app {app_id}")

    # アクセス権限管理メソッド
    async def get_app_acl(self, app_id: int) -> Dict[str, Any]:
        """
        アプリのアクセス権限を取得
        
        Args:
            app_id: アプリID
            
        Returns:
            Dict[str, Any]: アクセス権限設定
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Fetching app ACL for app: {app_id}")
            
            params = {"appId": app_id}
            response = await self.client.execute_nodejs_command("getAppAcl", params)
            logger.debug(f"App ACL response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"get app ACL for app {app_id}")

    async def update_app_acl(
        self, 
        app_id: int, 
        rights: List[Dict[str, Any]], 
        revision: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        アプリのアクセス権限を更新
        
        Args:
            app_id: アプリID
            rights: 権限設定のリスト
            revision: リビジョン番号（オプション）
            
        Returns:
            Dict[str, Any]: 更新結果
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Updating app ACL for app {app_id}")
            logger.debug(f"Rights: {rights}")
            
            params = {
                "appId": app_id,
                "rights": rights
            }
            if revision is not None:
                params["revision"] = revision
            
            response = await self.client.execute_nodejs_command("updateAppAcl", params)
            logger.debug(f"Update app ACL response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"update app ACL for app {app_id}")

    async def get_record_acl(self, app_id: int) -> Dict[str, Any]:
        """
        レコードのアクセス権限を取得
        
        Args:
            app_id: アプリID
            
        Returns:
            Dict[str, Any]: レコードアクセス権限設定
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Fetching record ACL for app: {app_id}")
            
            params = {"appId": app_id}
            response = await self.client.execute_nodejs_command("getRecordAcl", params)
            logger.debug(f"Record ACL response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"get record ACL for app {app_id}")

    async def update_record_acl(
        self, 
        app_id: int, 
        rights: List[Dict[str, Any]], 
        revision: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        レコードのアクセス権限を更新
        
        Args:
            app_id: アプリID
            rights: 権限設定のリスト
            revision: リビジョン番号（オプション）
            
        Returns:
            Dict[str, Any]: 更新結果
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Updating record ACL for app {app_id}")
            logger.debug(f"Rights: {rights}")
            
            params = {
                "appId": app_id,
                "rights": rights
            }
            if revision is not None:
                params["revision"] = revision
            
            response = await self.client.execute_nodejs_command("updateRecordAcl", params)
            logger.debug(f"Update record ACL response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"update record ACL for app {app_id}")

    async def get_field_acl(self, app_id: int) -> Dict[str, Any]:
        """
        フィールドのアクセス権限を取得
        
        Args:
            app_id: アプリID
            
        Returns:
            Dict[str, Any]: フィールドアクセス権限設定
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Fetching field ACL for app: {app_id}")
            
            params = {"appId": app_id}
            response = await self.client.execute_nodejs_command("getFieldAcl", params)
            logger.debug(f"Field ACL response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"get field ACL for app {app_id}")

    async def update_field_acl(
        self, 
        app_id: int, 
        rights: List[Dict[str, Any]], 
        revision: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        フィールドのアクセス権限を更新
        
        Args:
            app_id: アプリID
            rights: 権限設定のリスト
            revision: リビジョン番号（オプション）
            
        Returns:
            Dict[str, Any]: 更新結果
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Updating field ACL for app {app_id}")
            logger.debug(f"Rights: {rights}")
            
            params = {
                "appId": app_id,
                "rights": rights
            }
            if revision is not None:
                params["revision"] = revision
            
            response = await self.client.execute_nodejs_command("updateFieldAcl", params)
            logger.debug(f"Update field ACL response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"update field ACL for app {app_id}")

    # フィールド設定の高度な操作メソッド
    async def add_form_fields_advanced(
        self, 
        app_id: int, 
        properties: Dict[str, Any], 
        revision: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        フォームフィールドの高度な追加
        
        Args:
            app_id: アプリID
            properties: フィールドプロパティ
            revision: リビジョン番号（オプション）
            
        Returns:
            Dict[str, Any]: 追加結果
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Adding advanced form fields for app {app_id}")
            logger.debug(f"Properties: {properties}")
            
            params = {
                "appId": app_id,
                "properties": properties
            }
            if revision is not None:
                params["revision"] = revision
            
            response = await self.client.execute_nodejs_command("addFormFields", params)
            logger.debug(f"Add form fields response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"add advanced form fields for app {app_id}")

    async def update_form_fields_advanced(
        self, 
        app_id: int, 
        properties: Dict[str, Any], 
        revision: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        フォームフィールドの高度な更新
        
        Args:
            app_id: アプリID
            properties: フィールドプロパティ
            revision: リビジョン番号（オプション）
            
        Returns:
            Dict[str, Any]: 更新結果
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Updating advanced form fields for app {app_id}")
            logger.debug(f"Properties: {properties}")
            
            params = {
                "appId": app_id,
                "properties": properties
            }
            if revision is not None:
                params["revision"] = revision
            
            response = await self.client.execute_nodejs_command("updateFormFields", params)
            logger.debug(f"Update form fields response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"update advanced form fields for app {app_id}")

    async def delete_form_fields_advanced(
        self, 
        app_id: int, 
        fields: List[str], 
        revision: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        フォームフィールドの高度な削除
        
        Args:
            app_id: アプリID
            fields: 削除するフィールドコードのリスト
            revision: リビジョン番号（オプション）
            
        Returns:
            Dict[str, Any]: 削除結果
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Deleting advanced form fields for app {app_id}")
            logger.debug(f"Fields: {fields}")
            
            params = {
                "appId": app_id,
                "fields": fields
            }
            if revision is not None:
                params["revision"] = revision
            
            response = await self.client.execute_nodejs_command("deleteFormFields", params)
            logger.debug(f"Delete form fields response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"delete advanced form fields for app {app_id}")

    async def get_form_layout_advanced(self, app_id: int) -> Dict[str, Any]:
        """
        フォームレイアウトの高度な取得
        
        Args:
            app_id: アプリID
            
        Returns:
            Dict[str, Any]: フォームレイアウト
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Fetching advanced form layout for app: {app_id}")
            
            params = {"appId": app_id}
            response = await self.client.execute_nodejs_command("getFormLayout", params)
            logger.debug(f"Form layout response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"get advanced form layout for app {app_id}")

    async def update_form_layout_advanced(
        self, 
        app_id: int, 
        layout: List[Dict[str, Any]], 
        revision: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        フォームレイアウトの高度な更新
        
        Args:
            app_id: アプリID
            layout: レイアウト設定
            revision: リビジョン番号（オプション）
            
        Returns:
            Dict[str, Any]: 更新結果
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Updating advanced form layout for app {app_id}")
            logger.debug(f"Layout: {layout}")
            
            params = {
                "appId": app_id,
                "layout": layout
            }
            if revision is not None:
                params["revision"] = revision
            
            response = await self.client.execute_nodejs_command("updateFormLayout", params)
            logger.debug(f"Update form layout response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"update advanced form layout for app {app_id}")

    # プロセス管理機能の拡張
    async def get_process_management_advanced(self, app_id: int, lang: Optional[str] = None) -> Dict[str, Any]:
        """
        プロセス管理設定の高度な取得
        
        Args:
            app_id: アプリID
            lang: 言語設定（オプション）
            
        Returns:
            Dict[str, Any]: プロセス管理設定
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Fetching advanced process management for app: {app_id}")
            
            params = {"appId": app_id}
            if lang:
                params["lang"] = lang
            
            response = await self.client.execute_nodejs_command("getProcessManagement", params)
            logger.debug(f"Process management response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"get advanced process management for app {app_id}")

    async def update_process_management_advanced(
        self, 
        app_id: int, 
        states: List[Dict[str, Any]], 
        actions: List[Dict[str, Any]], 
        revision: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        プロセス管理設定の高度な更新
        
        Args:
            app_id: アプリID
            states: ステータス設定
            actions: アクション設定
            revision: リビジョン番号（オプション）
            
        Returns:
            Dict[str, Any]: 更新結果
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Updating advanced process management for app {app_id}")
            logger.debug(f"States: {states}")
            logger.debug(f"Actions: {actions}")
            
            params = {
                "appId": app_id,
                "states": states,
                "actions": actions
            }
            if revision is not None:
                params["revision"] = revision
            
            response = await self.client.execute_nodejs_command("updateProcessManagement", params)
            logger.debug(f"Update process management response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"update advanced process management for app {app_id}")

    async def get_app_actions_advanced(self, app_id: int, lang: Optional[str] = None) -> Dict[str, Any]:
        """
        アプリアクションの高度な取得
        
        Args:
            app_id: アプリID
            lang: 言語設定（オプション）
            
        Returns:
            Dict[str, Any]: アプリアクション設定
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Fetching advanced app actions for app: {app_id}")
            
            params = {"appId": app_id}
            if lang:
                params["lang"] = lang
            
            response = await self.client.execute_nodejs_command("getAppActions", params)
            logger.debug(f"App actions response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"get advanced app actions for app {app_id}")

    async def update_app_actions_advanced(
        self, 
        app_id: int, 
        actions: List[Dict[str, Any]], 
        revision: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        アプリアクションの高度な更新
        
        Args:
            app_id: アプリID
            actions: アクション設定
            revision: リビジョン番号（オプション）
            
        Returns:
            Dict[str, Any]: 更新結果
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Updating advanced app actions for app {app_id}")
            logger.debug(f"Actions: {actions}")
            
            params = {
                "appId": app_id,
                "actions": actions
            }
            if revision is not None:
                params["revision"] = revision
            
            response = await self.client.execute_nodejs_command("updateAppActions", params)
            logger.debug(f"Update app actions response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"update advanced app actions for app {app_id}")

    # アプリ情報の詳細取得
    async def get_app_detailed(self, app_id: int) -> Dict[str, Any]:
        """
        アプリの詳細情報を取得
        
        Args:
            app_id: アプリID
            
        Returns:
            Dict[str, Any]: アプリ詳細情報
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            logger.debug(f"Fetching detailed app info for app: {app_id}")
            
            params = {"appId": app_id}
            response = await self.client.execute_nodejs_command("getApp", params)
            logger.debug(f"Detailed app info response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"get detailed app info for app {app_id}")

    async def get_apps_with_details(
        self, 
        ids: Optional[List[int]] = None,
        codes: Optional[List[str]] = None,
        name: Optional[str] = None,
        space_ids: Optional[List[int]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        アプリ一覧の詳細情報を取得
        
        Args:
            ids: アプリIDのリスト（オプション）
            codes: アプリコードのリスト（オプション）
            name: アプリ名（部分一致、オプション）
            space_ids: スペースIDのリスト（オプション）
            limit: 取得件数制限
            offset: 取得開始位置
            
        Returns:
            Dict[str, Any]: アプリ一覧詳細情報
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            logger.debug(f"Fetching apps with details")
            
            params = {
                "limit": limit,
                "offset": offset
            }
            if ids:
                params["ids"] = ids
            if codes:
                params["codes"] = codes
            if name:
                params["name"] = name
            if space_ids:
                params["spaceIds"] = space_ids
            
            response = await self.client.execute_nodejs_command("getAppsWithDetails", params)
            logger.debug(f"Apps with details response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"get apps with details") 