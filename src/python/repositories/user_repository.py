"""
Kintone User Repository

ユーザー関連の操作を担当するリポジトリクラス
"""

import logging
from typing import Optional, Dict, Any, List

from .base import BaseKintoneRepository

logger = logging.getLogger(__name__)


class KintoneUserRepository(BaseKintoneRepository):
    """Kintoneユーザー操作リポジトリ"""
    
    async def add_guests(self, guests: List[str]) -> Dict[str, Any]:
        """
        ゲストユーザーを追加
        
        Args:
            guests: ゲストユーザーのリスト
            
        Returns:
            Dict[str, Any]: 追加結果
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            if not isinstance(guests, list) or not guests:
                raise ValueError("Guests list is required")
            
            logger.debug(f"Adding guests: {guests}")
            
            body = {"guests": guests}
            response = await self.client.post("/k/v1/guests.json", body=body)
            
            logger.debug(f"Add guests response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, "add guests")
    
    async def get_users(self, codes: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        ユーザー情報を取得
        
        Args:
            codes: ユーザーコードのリスト（オプション）
            
        Returns:
            Dict[str, Any]: ユーザー情報
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            logger.debug("Fetching users information")
            
            params = {}
            if codes and isinstance(codes, list) and len(codes) > 0:
                params["codes"] = codes
            
            response = await self.client.get("/k/v1/users.json", params=params)
            
            users = response.get("users", [])
            logger.debug(f"Found {len(users)} users")
            
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, "get users information")
    
    async def get_groups(self, codes: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        グループ情報を取得
        
        Args:
            codes: グループコードのリスト（オプション）
            
        Returns:
            Dict[str, Any]: グループ情報
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            logger.debug("Fetching groups information")
            
            params = {}
            if codes and isinstance(codes, list) and len(codes) > 0:
                params["codes"] = codes
            
            response = await self.client.get("/k/v1/groups.json", params=params)
            
            groups = response.get("groups", [])
            logger.debug(f"Found {len(groups)} groups")
            
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, "get groups information")
    
    async def get_group_users(self, group_code: str) -> Dict[str, Any]:
        """
        グループに所属するユーザー一覧を取得
        
        Args:
            group_code: グループコード
            
        Returns:
            Dict[str, Any]: グループユーザー情報
            
        Raises:
            Exception: API エラーが発生した場合
        """
        try:
            if not group_code or not group_code.strip():
                raise ValueError("Group code is required")
            
            logger.debug(f"Fetching users in group: {group_code}")
            
            params = {"code": group_code}
            response = await self.client.get("/k/v1/group/users.json", params=params)
            
            users = response.get("users", [])
            logger.debug(f"Found {len(users)} users in group {group_code}")
            
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"get users in group {group_code}") 