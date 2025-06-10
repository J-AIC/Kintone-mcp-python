"""
Record Tools Implementation

レコード関連ツールの実装
"""

import logging
from typing import Any, Dict, List, Optional

from .....models.kintone_record import KintoneRecord
from .....repositories.record_repository import KintoneRecordRepository

logger = logging.getLogger(__name__)


async def handle_record_tools(name: str, args: Dict[str, Any], repository: KintoneRecordRepository) -> Any:
    """
    レコード関連ツールを処理
    
    Args:
        name: ツール名
        args: ツールの引数
        repository: レコードリポジトリ
        
    Returns:
        Any: ツールの実行結果
        
    Raises:
        ValueError: 引数が不正な場合
        Exception: ツール実行エラーが発生した場合
    """
    
    if name == "get_record":
        return await _handle_get_record(args, repository)
    elif name == "search_records":
        return await _handle_search_records(args, repository)
    elif name == "create_record":
        return await _handle_create_record(args, repository)
    elif name == "update_record":
        return await _handle_update_record(args, repository)
    elif name == "add_record_comment":
        return await _handle_add_record_comment(args, repository)
    else:
        raise ValueError(f"Unknown record tool: {name}")


async def _handle_get_record(args: Dict[str, Any], repository: KintoneRecordRepository) -> Dict[str, Any]:
    """
    レコード取得ツールの処理
    
    Args:
        args: ツールの引数
        repository: レコードリポジトリ
        
    Returns:
        Dict[str, Any]: レコードのフィールドデータ
        
    Raises:
        ValueError: 必須パラメータが不足している場合
    """
    # 引数のチェック
    if not args.get("app_id"):
        raise ValueError("app_id は必須パラメータです。")
    if not args.get("record_id"):
        raise ValueError("record_id は必須パラメータです。")
    
    # デバッグ用のログ出力
    logger.debug(f"Fetching record: {args['app_id']}/{args['record_id']}")
    
    record = await repository.get_record(args["app_id"], args["record_id"])
    # システムフィールド（$で始まるフィールド）を除外して返す
    filtered_fields = {
        field_code: field_data 
        for field_code, field_data in record.fields.items() 
        if not field_code.startswith("$")
    }
    return filtered_fields


async def _handle_search_records(args: Dict[str, Any], repository: KintoneRecordRepository) -> List[Dict[str, Any]]:
    """
    レコード検索ツールの処理
    
    Args:
        args: ツールの引数
        repository: レコードリポジトリ
        
    Returns:
        List[Dict[str, Any]]: レコードのフィールドデータのリスト
        
    Raises:
        ValueError: 必須パラメータが不足している場合
    """
    # 引数のチェック
    if not args.get("app_id"):
        raise ValueError("app_id は必須パラメータです。")
    
    # デバッグ用のログ出力
    logger.debug(f"Searching records in app: {args['app_id']}")
    logger.debug(f"Query: {args.get('query', '(none)')}")
    logger.debug(f"Fields: {args.get('fields', '(all)')}")
    
    records = await repository.search_records(
        args["app_id"],
        args.get("query"),
        args.get("fields")
    )
    # 各レコードからシステムフィールド（$で始まるフィールド）を除外
    filtered_records = []
    for record in records:
        filtered_fields = {
            field_code: field_data 
            for field_code, field_data in record.fields.items() 
            if not field_code.startswith("$")
        }
        filtered_records.append(filtered_fields)
    return filtered_records


async def _handle_create_record(args: Dict[str, Any], repository: KintoneRecordRepository) -> Dict[str, int]:
    """
    レコード作成ツールの処理
    
    Args:
        args: ツールの引数
        repository: レコードリポジトリ
        
    Returns:
        Dict[str, int]: 作成されたレコードのID
        
    Raises:
        ValueError: 必須パラメータが不足している場合
    """
    # 引数のチェック
    if not args.get("app_id"):
        raise ValueError("app_id は必須パラメータです。")
    if not args.get("fields"):
        raise ValueError("fields は必須パラメータです。")
    
    # デバッグ用のログ出力
    logger.debug(f"Creating record in app: {args['app_id']}")
    logger.debug(f"Fields: {args['fields']}")
    
    # フィールドの検証（JavaScript版と同様の警告）
    if not args["fields"].get("project_manager"):
        logger.warning("Warning: project_manager field is missing")
    
    record_id = await repository.create_record(
        args["app_id"],
        args["fields"]
    )
    return {"record_id": record_id}


async def _handle_update_record(args: Dict[str, Any], repository: KintoneRecordRepository) -> Dict[str, Any]:
    """
    レコード更新ツールの処理
    
    Args:
        args: ツールの引数
        repository: レコードリポジトリ
        
    Returns:
        Dict[str, Any]: 更新結果
        
    Raises:
        ValueError: 必須パラメータが不足している場合
    """
    # 引数のチェック
    if not args.get("app_id"):
        raise ValueError("app_id は必須パラメータです。")
    
    # レコードIDまたはupdateKeyのいずれかが必要
    if not args.get("record_id") and not args.get("updateKey"):
        raise ValueError("record_id または updateKey のいずれかは必須です。")
    
    # record_idとupdateKeyの同時指定はエラー
    if args.get("record_id") and args.get("updateKey"):
        raise ValueError("record_id と updateKey は同時に指定できません。")
    
    if not args.get("fields"):
        raise ValueError("fields は必須パラメータです。")
    
    # updateKeyのバリデーション
    if args.get("updateKey"):
        update_key = args["updateKey"]
        if not update_key.get("field") or not update_key.get("value"):
            raise ValueError("updateKey には field と value が必要です。")
    
    # デバッグ用のログ出力
    if args.get("record_id"):
        logger.debug(f"Updating record by ID: {args['app_id']}/{args['record_id']}")
    else:
        update_key = args["updateKey"]
        logger.debug(f"Updating record by key: {args['app_id']}/{update_key['field']}={update_key['value']}")
    logger.debug(f"Fields: {args['fields']}")
    
    if args.get("record_id"):
        # レコードIDを使用した更新
        response = await repository.update_record(
            args["app_id"],
            args["record_id"],
            args["fields"],
            args.get("revision")
        )
    else:
        # updateKeyを使用した更新
        update_key = args["updateKey"]
        response = await repository.update_record_by_key(
            args["app_id"],
            update_key["field"],
            update_key["value"],
            args["fields"],
            args.get("revision")
        )
    
    return response


async def _handle_add_record_comment(args: Dict[str, Any], repository: KintoneRecordRepository) -> Dict[str, int]:
    """
    レコードコメント追加ツールの処理
    
    Args:
        args: ツールの引数
        repository: レコードリポジトリ
        
    Returns:
        Dict[str, int]: 追加されたコメントのID
        
    Raises:
        ValueError: 必須パラメータが不足している場合
    """
    # 引数のチェック
    if not args.get("app_id"):
        raise ValueError("app_id は必須パラメータです。")
    if not args.get("record_id"):
        raise ValueError("record_id は必須パラメータです。")
    if not args.get("text"):
        raise ValueError("text は必須パラメータです。")
    
    # デバッグ用のログ出力
    logger.debug(f"Adding comment to record: {args['app_id']}/{args['record_id']}")
    logger.debug(f"Text: {args['text']}")
    if args.get("mentions") and len(args["mentions"]) > 0:
        logger.debug(f"Mentions: {args['mentions']}")
    
    comment_id = await repository.add_record_comment(
        args["app_id"],
        args["record_id"],
        args["text"],
        args.get("mentions", [])
    )
    return {"comment_id": comment_id} 