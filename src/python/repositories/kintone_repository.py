"""
Kintone Repository

各専門リポジトリを統合するファサードクラス
"""

import logging
from typing import Optional, Dict, Any, List

from ..models.kintone_credentials import KintoneCredentials
from .record_repository import KintoneRecordRepository
from .kintone_app_repository import KintoneAppRepository
from .file_repository import KintoneFileRepository
from .space_repository import SpaceRepository
from .user_repository import KintoneUserRepository

logger = logging.getLogger(__name__)


class KintoneRepository:
    """
    Kintone統合リポジトリ
    
    各専門リポジトリを統合し、統一されたインターフェースを提供
    """
    
    def __init__(self, credentials: KintoneCredentials):
        """
        Args:
            credentials: Kintone認証情報
        """
        self.credentials = credentials
        
        # 各専門リポジトリのインスタンスを作成
        self.record_repo = KintoneRecordRepository(credentials)
        self.app_repo = KintoneAppRepository(credentials)
        self.file_repo = KintoneFileRepository(credentials)
        self.space_repo = SpaceRepository(credentials)
        self.user_repo = KintoneUserRepository(credentials)
    
    async def close(self):
        """全リポジトリのリソースをクリーンアップ"""
        await self.record_repo.close()
        await self.app_repo.close()
        await self.file_repo.close()
        await self.space_repo.close()
        await self.user_repo.close()
    
    # レコード関連のメソッド
    async def get_record(self, app_id: int, record_id: int):
        """レコードを取得"""
        return await self.record_repo.get_record(app_id, record_id)
    
    async def search_records(
        self, 
        app_id: int, 
        query: Optional[str] = None, 
        fields: Optional[List[str]] = None
    ):
        """レコードを検索"""
        return await self.record_repo.search_records(app_id, query, fields)
    
    async def create_record(self, app_id: int, fields: Dict[str, Any]) -> int:
        """レコードを作成"""
        return await self.record_repo.create_record(app_id, fields)
    
    async def update_record(
        self, 
        app_id: int, 
        record_id: int, 
        fields: Dict[str, Any],
        revision: Optional[int] = None
    ):
        """レコードを更新"""
        return await self.record_repo.update_record(app_id, record_id, fields, revision)
    
    async def add_record_comment(
        self, 
        app_id: int, 
        record_id: int, 
        text: str,
        mentions: Optional[List[Dict[str, str]]] = None
    ) -> int:
        """レコードにコメントを追加"""
        return await self.record_repo.add_record_comment(app_id, record_id, text, mentions)
    
    # アプリ関連のメソッド
    async def get_apps_info(self, app_name: Optional[str] = None):
        """アプリ一覧を取得"""
        return await self.app_repo.get_apps_info(app_name)
    
    async def create_app(
        self, 
        name: str, 
        space: Optional[int] = None, 
        thread: Optional[int] = None
    ) -> int:
        """アプリを作成"""
        return await self.app_repo.create_app(name, space, thread)
    
    async def deploy_app(self, apps: List[Dict[str, Any]]):
        """アプリをデプロイ"""
        return await self.app_repo.deploy_app(apps)
    
    async def get_deploy_status(self, apps: List[int]):
        """デプロイ状況を取得"""
        return await self.app_repo.get_deploy_status(apps)
    
    async def get_form_fields(self, app_id: int):
        """アプリのフィールド情報を取得"""
        return await self.app_repo.get_form_fields(app_id)
    
    async def get_form_layout(self, app_id: int):
        """アプリのフォームレイアウト情報を取得"""
        return await self.app_repo.get_form_layout(app_id)
    
    async def add_fields(self, app_id: int, properties: Dict[str, Any]):
        """アプリにフィールドを追加"""
        return await self.app_repo.add_fields(app_id, properties)
    
    async def update_form_layout(
        self, 
        app_id: int, 
        layout: List[Dict[str, Any]], 
        revision: Optional[int] = None
    ):
        """フォームレイアウトを更新"""
        return await self.app_repo.update_form_layout(app_id, layout, revision)
    
    # ファイル関連のメソッド
    async def upload_file(self, file_name: str, file_data: bytes):
        """ファイルをアップロード"""
        return await self.file_repo.upload_file(file_name, file_data)
    
    async def download_file(self, file_key: str) -> bytes:
        """ファイルをダウンロード"""
        return await self.file_repo.download_file(file_key)

    async def upload_multiple_files(self, files: list, options: Dict[str, Any] = None):
        """複数ファイルをアップロード"""
        return await self.file_repo.upload_multiple_files(files, options)

    async def get_file_info(self, file_key: str):
        """ファイル情報を取得"""
        return await self.file_repo.get_file_info(file_key)

    async def delete_file(self, file_key: str):
        """ファイルを削除"""
        return await self.file_repo.delete_file(file_key)

    async def download_file_stream(self, file_key: str, chunk_size: int = 8192):
        """ファイルをストリーミングダウンロード"""
        async for chunk in self.file_repo.download_file_stream(file_key, chunk_size):
            yield chunk
    
    # スペース関連のメソッド
    async def get_space(self, space_id: int):
        """スペース情報を取得"""
        return await self.space_repo.get_space(space_id)
    
    async def update_space(self, space_id: int, settings: Dict[str, Any]):
        """スペース設定を更新"""
        return await self.space_repo.update_space(space_id, settings)
    
    async def update_space_body(self, space_id: int, body_content: str):
        """スペースの本文を更新"""
        return await self.space_repo.update_space_body(space_id, body_content)
    
    async def get_space_members(self, space_id: int):
        """スペースメンバー一覧を取得"""
        return await self.space_repo.get_space_members(space_id)
    
    async def update_space_members(self, space_id: int, members: List[Dict[str, Any]]):
        """スペースメンバーを更新"""
        return await self.space_repo.update_space_members(space_id, members)
    
    async def add_thread(self, space_id: int, name: str):
        """スペースにスレッドを追加"""
        return await self.space_repo.add_thread(space_id, name)
    
    async def update_thread(self, thread_id: int, params: Dict[str, Any]):
        """スレッドを更新"""
        return await self.space_repo.update_thread(thread_id, params)
    
    async def add_thread_comment(self, space_id: int, thread_id: int, comment: str):
        """スレッドにコメントを追加"""
        return await self.space_repo.add_thread_comment(space_id, thread_id, comment)
    
    async def update_space_guests(self, space_id: int, guests: List[str]):
        """スペースのゲストユーザーを更新"""
        return await self.space_repo.update_space_guests(space_id, guests)
    
    # ユーザー関連のメソッド
    async def add_guests(self, guests: List[str]):
        """ゲストユーザーを追加"""
        return await self.user_repo.add_guests(guests)
    
    async def get_users(self, codes: Optional[List[str]] = None):
        """ユーザー情報を取得"""
        return await self.user_repo.get_users(codes)
    
    async def get_groups(self, codes: Optional[List[str]] = None):
        """グループ情報を取得"""
        return await self.user_repo.get_groups(codes)
    
    async def get_group_users(self, group_code: str):
        """グループに所属するユーザー一覧を取得"""
        return await self.user_repo.get_group_users(group_code) 