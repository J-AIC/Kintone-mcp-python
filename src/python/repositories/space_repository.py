"""
Space Repository

Kintone Space API との通信を担当するリポジトリクラス
"""

from typing import Dict, Any, List, Optional
import logging

from .base import BaseKintoneRepository

logger = logging.getLogger(__name__)


class SpaceRepository(BaseKintoneRepository):
    """Kintone Space API リポジトリ"""
    
    async def get_space(self, space_id: str) -> Dict[str, Any]:
        """
        スペースの一般情報を取得
        
        Args:
            space_id: スペースID
            
        Returns:
            スペース情報
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            logger.debug(f"Fetching space: {space_id}")
            
            params = {"id": space_id}
            response = await self.client.get("/k/v1/space.json", params=params)
            
            logger.debug(f"Space response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"get space {space_id}")
    
    async def update_space(
        self, 
        space_id: str, 
        name: Optional[str] = None,
        is_private: Optional[bool] = None,
        fixed_member: Optional[bool] = None,
        use_multi_thread: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        スペースの設定を更新
        
        Args:
            space_id: スペースID
            name: スペースの新しい名前
            is_private: プライベート設定
            fixed_member: メンバー固定設定
            use_multi_thread: マルチスレッド設定
            
        Returns:
            更新結果
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            logger.debug(f"Updating space: {space_id}")
            
            body = {"id": space_id}
            
            if name is not None:
                body["name"] = name
            if is_private is not None:
                body["isPrivate"] = is_private
            if fixed_member is not None:
                body["fixedMember"] = fixed_member
            if use_multi_thread is not None:
                body["useMultiThread"] = use_multi_thread
            
            logger.debug(f"Update space body: {body}")
            response = await self.client.put("/k/v1/space.json", body=body)
            
            logger.debug(f"Update space response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"update space {space_id}")
    
    async def update_space_body(self, space_id: str, body: str) -> Dict[str, Any]:
        """
        スペースの本文を更新
        
        Args:
            space_id: スペースID
            body: スペースの本文（HTML形式）
            
        Returns:
            更新結果
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            logger.debug(f"Updating space body: {space_id}")
            
            request_body = {
                "id": space_id,
                "body": body
            }
            
            response = await self.client.put("/k/v1/space/body.json", body=request_body)
            
            logger.debug(f"Update space body response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"update space body {space_id}")
    
    async def get_space_members(self, space_id: str) -> Dict[str, Any]:
        """
        スペースメンバーのリストを取得
        
        Args:
            space_id: スペースID
            
        Returns:
            スペースメンバー情報
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            logger.debug(f"Fetching space members: {space_id}")
            
            params = {"id": space_id}
            response = await self.client.get("/k/v1/space/members.json", params=params)
            
            logger.debug(f"Space members response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"get space members {space_id}")
    
    async def update_space_members(
        self, 
        space_id: str, 
        members: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        スペースメンバーを更新
        
        Args:
            space_id: スペースID
            members: メンバー情報のリスト
            
        Returns:
            更新結果
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            logger.debug(f"Updating space members: {space_id}")
            logger.debug(f"Members: {members}")
            
            body = {
                "id": space_id,
                "members": members
            }
            
            response = await self.client.put("/k/v1/space/members.json", body=body)
            
            logger.debug(f"Update space members response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"update space members {space_id}")
    
    async def add_thread(self, space_id: str, name: str) -> Dict[str, Any]:
        """
        スペースにスレッドを追加
        
        Args:
            space_id: スペースID
            name: スレッド名
            
        Returns:
            作成されたスレッド情報
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            logger.debug(f"Adding thread to space: {space_id}")
            logger.debug(f"Thread name: {name}")
            
            body = {
                "space": space_id,
                "name": name
            }
            
            response = await self.client.post("/k/v1/space/thread.json", body=body)
            
            logger.debug(f"Add thread response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"add thread to space {space_id}")
    
    async def update_thread(
        self, 
        thread_id: str, 
        name: Optional[str] = None,
        body: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        スレッドを更新
        
        Args:
            thread_id: スレッドID
            name: スレッドの新しい名前
            body: スレッドの本文（HTML形式）
            
        Returns:
            更新結果
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            logger.debug(f"Updating thread: {thread_id}")
            
            request_body = {"id": thread_id}
            
            if name is not None:
                request_body["name"] = name
            if body is not None:
                request_body["body"] = body
            
            logger.debug(f"Update thread body: {request_body}")
            response = await self.client.put("/k/v1/space/thread.json", body=request_body)
            
            logger.debug(f"Update thread response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"update thread {thread_id}")
    
    async def add_thread_comment(
        self, 
        space_id: str, 
        thread_id: str, 
        text: str,
        mentions: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        スレッドにコメントを追加
        
        Args:
            space_id: スペースID
            thread_id: スレッドID
            text: コメント本文
            mentions: メンション情報のリスト
            
        Returns:
            作成されたコメント情報
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            logger.debug(f"Adding comment to thread: {thread_id} in space: {space_id}")
            logger.debug(f"Text: {text}")
            
            comment_data = {
                "text": text,
                "mentions": mentions or []
            }
            
            if mentions:
                logger.debug(f"Mentions: {mentions}")
            
            body = {
                "space": space_id,
                "thread": thread_id,
                "comment": comment_data
            }
            
            response = await self.client.post("/k/v1/space/thread/comment.json", body=body)
            
            logger.debug(f"Add thread comment response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"add comment to thread {thread_id}")
    
    async def update_space_guests(
        self, 
        space_id: str, 
        guests: List[str]
    ) -> Dict[str, Any]:
        """
        スペースのゲストメンバーを更新
        
        Args:
            space_id: スペースID
            guests: ゲストユーザーのメールアドレスのリスト
            
        Returns:
            更新結果
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            logger.debug(f"Updating space guests: {space_id}")
            logger.debug(f"Guests: {guests}")
            
            body = {
                "id": space_id,
                "guests": guests
            }
            
            response = await self.client.put("/k/v1/space/guests.json", body=body)
            
            logger.debug(f"Update space guests response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"update space guests {space_id}")
    
    async def add_guests(self, guests: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        ゲストユーザーを追加
        
        Args:
            guests: ゲスト情報のリスト
            
        Returns:
            追加結果
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            logger.debug(f"Adding guests: {guests}")
            
            body = {"guests": guests}
            
            response = await self.client.post("/k/v1/guests.json", body=body)
            
            logger.debug(f"Add guests response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, "add guests") 