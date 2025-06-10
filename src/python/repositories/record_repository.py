"""
Kintone Record Repository

レコード関連の操作を担当するリポジトリクラス
"""

import logging
from typing import Optional, Dict, Any, List

from .base import BaseKintoneRepository
from ..models.kintone_record import KintoneRecord

logger = logging.getLogger(__name__)


class KintoneRecordRepository(BaseKintoneRepository):
    """Kintoneレコード操作リポジトリ"""
    
    async def get_record(self, app_id: int, record_id: int) -> KintoneRecord:
        """
        レコードを取得
        
        Args:
            app_id: アプリID
            record_id: レコードID
            
        Returns:
            KintoneRecord: レコードオブジェクト
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            self._validate_record_id(record_id)
            
            logger.debug(f"Fetching record: {app_id}/{record_id}")
            response = await self.client.get_record(app_id, record_id)
            
            logger.debug(f"Record response: {response}")
            return KintoneRecord(
                app_id=app_id,
                record_id=record_id,
                fields=response.get("record", {})
            )
            
        except Exception as error:
            self.handle_kintone_error(error, f"get record {app_id}/{record_id}")
    
    async def search_records(
        self, 
        app_id: int, 
        query: Optional[str] = None, 
        fields: Optional[List[str]] = None
    ) -> List[KintoneRecord]:
        """
        レコードを検索
        
        Args:
            app_id: アプリID
            query: 検索クエリ
            fields: 取得するフィールドのリスト
            
        Returns:
            List[KintoneRecord]: レコードのリスト
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            
            logger.debug(f"Searching records in app: {app_id}")
            logger.debug(f"Query: {query}")
            logger.debug(f"Fields: {fields}")
            
            response = await self.client.get_records(
                app_id=app_id,
                query=query,
                fields=fields,
                total_count=True
            )
            
            records = response.get("records", [])
            logger.debug(f"Found {len(records)} records")
            
            return [
                KintoneRecord(
                    app_id=app_id,
                    record_id=int(record.get("$id", {}).get("value", 0)),
                    fields=record
                )
                for record in records
            ]
            
        except Exception as error:
            self.handle_kintone_error(error, f"search records in app {app_id}")
    
    async def create_record(self, app_id: int, fields: Dict[str, Any]) -> int:
        """
        レコードを作成
        
        Args:
            app_id: アプリID
            fields: レコードのフィールドデータ
            
        Returns:
            int: 作成されたレコードのID
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            
            logger.debug(f"Creating record in app: {app_id}")
            logger.debug(f"Fields: {fields}")
            
            response = await self.client.create_record(app_id, fields)
            
            record_id = int(response.get("id", 0))
            logger.debug(f"Created record with ID: {record_id}")
            
            return record_id
            
        except Exception as error:
            self.handle_kintone_error(error, f"create record in app {app_id}")
    
    async def update_record(
        self, 
        app_id: int, 
        record_id: int, 
        fields: Dict[str, Any],
        revision: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        レコードを更新
        
        Args:
            app_id: アプリID
            record_id: レコードID
            fields: 更新するフィールドデータ
            revision: リビジョン番号
            
        Returns:
            Dict[str, Any]: 更新結果
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            self._validate_record_id(record_id)
            
            logger.debug(f"Updating record: {app_id}/{record_id}")
            logger.debug(f"Fields: {fields}")
            logger.debug(f"Revision: {revision}")
            
            response = await self.client.update_record(
                app_id=app_id,
                record_id=record_id,
                record=fields,
                revision=revision
            )
            
            logger.debug(f"Update response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"update record {app_id}/{record_id}")
    
    async def update_record_by_key(
        self, 
        app_id: int, 
        key_field: str, 
        key_value: str, 
        fields: Dict[str, Any],
        revision: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        重複禁止フィールドを使用してレコードを更新
        
        Args:
            app_id: アプリID
            key_field: 重複禁止に設定されたフィールドコード
            key_value: フィールドの値
            fields: 更新するフィールドデータ
            revision: リビジョン番号
            
        Returns:
            Dict[str, Any]: 更新結果
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            
            if not key_field or not key_field.strip():
                raise ValueError("Key field is required")
            if not key_value or not key_value.strip():
                raise ValueError("Key value is required")
            
            logger.debug(f"Updating record by key: {app_id}/{key_field}={key_value}")
            logger.debug(f"Fields: {fields}")
            logger.debug(f"Revision: {revision}")
            
            response = await self.client.update_record_by_key(
                app_id=app_id,
                key_field=key_field,
                key_value=key_value,
                record=fields,
                revision=revision
            )
            
            logger.debug(f"Update by key response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"update record by key {app_id}/{key_field}={key_value}")

    async def add_record_comment(
        self, 
        app_id: int, 
        record_id: int, 
        text: str,
        mentions: Optional[List[Dict[str, str]]] = None
    ) -> int:
        """
        レコードにコメントを追加
        
        Args:
            app_id: アプリID
            record_id: レコードID
            text: コメントテキスト
            mentions: メンション情報のリスト
            
        Returns:
            int: 追加されたコメントのID
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            self._validate_app_id(app_id)
            self._validate_record_id(record_id)
            
            if not text or not text.strip():
                raise ValueError("Comment text is required")
            
            logger.debug(f"Adding comment to record: {app_id}/{record_id}")
            logger.debug(f"Text: {text}")
            logger.debug(f"Mentions: {mentions}")
            
            response = await self.client.add_record_comment(
                app_id=app_id,
                record_id=record_id,
                text=text,
                mentions=mentions or []
            )
            
            comment_id = int(response.get("id", 0))
            logger.debug(f"Added comment with ID: {comment_id}")
            
            return comment_id
            
        except Exception as error:
            self.handle_kintone_error(error, f"add comment to record {app_id}/{record_id}") 