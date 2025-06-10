"""
User Tools Implementation

ユーザー関連のツール実装
"""

import logging
from typing import Dict, Any, Optional, List

from .....repositories.user_repository import KintoneUserRepository

logger = logging.getLogger(__name__)


async def handle_user_tools(name: str, args: Dict[str, Any], repository: KintoneUserRepository) -> Dict[str, Any]:
    """
    ユーザー関連のツールを処理する関数
    
    Args:
        name: ツール名
        args: ツールの引数
        repository: ユーザーリポジトリ
        
    Returns:
        Dict[str, Any]: ツールの実行結果
        
    Raises:
        ValueError: 不正な引数が指定された場合
        Exception: ツール実行中にエラーが発生した場合
    """
    try:
        if name == "get_users":
            # 引数のチェック
            codes = args.get("codes", [])
            if codes is not None and not isinstance(codes, list):
                raise ValueError("codes must be a list")
            
            # ユーザー情報を取得
            response = await repository.get_users(codes)
            return response
            
        elif name == "get_groups":
            # 引数のチェック
            codes = args.get("codes", [])
            if codes is not None and not isinstance(codes, list):
                raise ValueError("codes must be a list")
            
            # グループ情報を取得
            response = await repository.get_groups(codes)
            return response
            
        elif name == "get_group_users":
            # 引数のチェック
            group_code = args.get("group_code")
            if not group_code:
                raise ValueError("group_code は必須パラメータです。")
            
            # グループに所属するユーザーを取得
            response = await repository.get_group_users(group_code)
            return response
            
        elif name == "add_guests":
            # 引数のチェック
            guests = args.get("guests")
            if not guests:
                raise ValueError("guests は必須パラメータです。")
            if not isinstance(guests, list):
                raise ValueError("guests must be a list")
            
            # ゲストユーザーを追加
            response = await repository.add_guests(guests)
            return response
            
        else:
            raise ValueError(f"Unknown user tool: {name}")
            
    except Exception as error:
        logger.error(f"Error in user tool {name}: {str(error)}")
        raise 