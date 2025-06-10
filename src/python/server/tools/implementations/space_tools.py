"""
Space Tools Implementation

Space関連のツール実装
"""

from typing import Dict, Any, List, Optional
import logging

from .....repositories.space_repository import SpaceRepository

logger = logging.getLogger(__name__)


async def handle_space_tools(name: str, args: Dict[str, Any], repository: SpaceRepository) -> Dict[str, Any]:
    """
    Space関連のツールを処理
    
    Args:
        name: ツール名
        args: ツール引数
        repository: SpaceRepository インスタンス
        
    Returns:
        ツール実行結果
        
    Raises:
        ValueError: 引数が不正な場合
        Exception: API エラーが発生した場合
    """
    
    if name == "get_space":
        # 引数のチェック
        if not args.get("space_id"):
            raise ValueError("space_id は必須パラメータです。")
        
        # デバッグ用のログ出力
        logger.debug(f"Fetching space: {args['space_id']}")
        
        return await repository.get_space(args["space_id"])
    
    elif name == "update_space":
        # 引数のチェック
        if not args.get("space_id"):
            raise ValueError("space_id は必須パラメータです。")
        
        # デバッグ用のログ出力
        logger.debug(f"Updating space: {args['space_id']}")
        logger.debug(f"Settings: name={args.get('name')}, is_private={args.get('is_private')}, "
                    f"fixed_member={args.get('fixed_member')}, use_multi_thread={args.get('use_multi_thread')}")
        
        await repository.update_space(
            space_id=args["space_id"],
            name=args.get("name"),
            is_private=args.get("is_private"),
            fixed_member=args.get("fixed_member"),
            use_multi_thread=args.get("use_multi_thread")
        )
        return {"success": True}
    
    elif name == "update_space_body":
        # 引数のチェック
        if not args.get("space_id"):
            raise ValueError("space_id は必須パラメータです。")
        if not args.get("body"):
            raise ValueError("body は必須パラメータです。")
        
        # デバッグ用のログ出力
        logger.debug(f"Updating space body: {args['space_id']}")
        
        await repository.update_space_body(args["space_id"], args["body"])
        return {"success": True}
    
    elif name == "get_space_members":
        # 引数のチェック
        if not args.get("space_id"):
            raise ValueError("space_id は必須パラメータです。")
        
        # デバッグ用のログ出力
        logger.debug(f"Fetching space members: {args['space_id']}")
        
        return await repository.get_space_members(args["space_id"])
    
    elif name == "update_space_members":
        # 引数のチェック
        if not args.get("space_id"):
            raise ValueError("space_id は必須パラメータです。")
        if not args.get("members"):
            raise ValueError("members は必須パラメータです。")
        if not isinstance(args["members"], list):
            raise ValueError("members は配列形式で指定する必要があります。")
        
        # デバッグ用のログ出力
        logger.debug(f"Updating space members: {args['space_id']}")
        logger.debug(f"Members: {args['members']}")
        
        await repository.update_space_members(args["space_id"], args["members"])
        return {"success": True}
    
    elif name == "add_thread":
        # 引数のチェック
        if not args.get("space_id"):
            raise ValueError("space_id は必須パラメータです。")
        if not args.get("name"):
            raise ValueError("name は必須パラメータです。")
        
        # デバッグ用のログ出力
        logger.debug(f"Adding thread to space: {args['space_id']}")
        logger.debug(f"Thread name: {args['name']}")
        
        response = await repository.add_thread(args["space_id"], args["name"])
        return {"thread_id": response.get("id")}
    
    elif name == "update_thread":
        # 引数のチェック
        if not args.get("thread_id"):
            raise ValueError("thread_id は必須パラメータです。")
        
        # デバッグ用のログ出力
        logger.debug(f"Updating thread: {args['thread_id']}")
        logger.debug(f"Settings: name={args.get('name')}, body={args.get('body', '(content)' if args.get('body') else None)}")
        
        await repository.update_thread(
            thread_id=args["thread_id"],
            name=args.get("name"),
            body=args.get("body")
        )
        return {"success": True}
    
    elif name == "add_thread_comment":
        # 引数のチェック
        if not args.get("space_id"):
            raise ValueError("space_id は必須パラメータです。")
        if not args.get("thread_id"):
            raise ValueError("thread_id は必須パラメータです。")
        if not args.get("text"):
            raise ValueError("text は必須パラメータです。")
        
        # デバッグ用のログ出力
        logger.debug(f"Adding comment to thread: {args['thread_id']} in space: {args['space_id']}")
        logger.debug(f"Text: {args['text']}")
        if args.get("mentions"):
            logger.debug(f"Mentions: {args['mentions']}")
        
        response = await repository.add_thread_comment(
            space_id=args["space_id"],
            thread_id=args["thread_id"],
            text=args["text"],
            mentions=args.get("mentions")
        )
        return {"comment_id": response.get("id")}
    
    elif name == "update_space_guests":
        # 引数のチェック
        if not args.get("space_id"):
            raise ValueError("space_id は必須パラメータです。")
        if not args.get("guests"):
            raise ValueError("guests は必須パラメータです。")
        if not isinstance(args["guests"], list):
            raise ValueError("guests は配列形式で指定する必要があります。")
        
        # デバッグ用のログ出力
        logger.debug(f"Updating space guests: {args['space_id']}")
        logger.debug(f"Guests: {args['guests']}")
        
        await repository.update_space_guests(args["space_id"], args["guests"])
        return {"success": True}
    
    else:
        raise ValueError(f"Unknown space tool: {name}") 