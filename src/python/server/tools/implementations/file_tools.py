"""
File Tools Implementation

ファイル関連のツール実装
"""

import base64
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def handle_file_tools(name: str, args: Dict[str, Any], repository) -> Dict[str, Any]:
    """
    ファイル関連のツールを処理する関数
    
    Args:
        name: ツール名
        args: 引数
        repository: リポジトリオブジェクト
        
    Returns:
        Dict[str, Any]: ツールの実行結果
        
    Raises:
        ValueError: 不正な引数が指定された場合
        Exception: ツール実行中にエラーが発生した場合
    """
    try:
        if name == "upload_file":
            return await _handle_upload_file(args, repository)
        elif name == "download_file":
            return await _handle_download_file(args, repository)
        elif name == "upload_multiple_files":
            return await _handle_upload_multiple_files(args, repository)
        elif name == "get_file_info":
            return await _handle_get_file_info(args, repository)
        elif name == "delete_file":
            return await _handle_delete_file(args, repository)
        elif name == "download_file_stream":
            return await _handle_download_file_stream(args, repository)
        else:
            raise ValueError(f"Unknown file tool: {name}")
            
    except Exception as error:
        logger.error(f"Error in file tool '{name}': {error}")
        raise


async def _handle_upload_file(args: Dict[str, Any], repository) -> Dict[str, Any]:
    """
    ファイルアップロードツールの処理
    
    Args:
        args: ツール引数
        repository: リポジトリオブジェクト
        
    Returns:
        Dict[str, Any]: アップロード結果
    """
    # 引数の検証
    file_name = args.get("file_name")
    file_data = args.get("file_data")
    
    if not file_name:
        raise ValueError("file_name は必須パラメータです。")
    
    if not file_data:
        raise ValueError("file_data は必須パラメータです。")
    
    try:
        # Base64デコード
        file_bytes = base64.b64decode(file_data)
        
        # ファイルアップロード
        upload_response = await repository.file_repository.upload_file(
            file_name, file_bytes
        )
        
        return {
            "file_key": upload_response.get("fileKey"),
            "message": f"ファイル '{file_name}' をアップロードしました。"
        }
        
    except Exception as error:
        logger.error(f"File upload error: {error}")
        raise Exception(f"ファイルのアップロードに失敗しました: {error}")


async def _handle_download_file(args: Dict[str, Any], repository) -> Dict[str, Any]:
    """
    ファイルダウンロードツールの処理
    
    Args:
        args: ツール引数
        repository: リポジトリオブジェクト
        
    Returns:
        Dict[str, Any]: ダウンロード結果
    """
    # 引数の検証
    file_key = args.get("file_key")
    
    if not file_key:
        raise ValueError("file_key は必須パラメータです。")
    
    try:
        # ファイルダウンロード
        file_data = await repository.file_repository.download_file(file_key)
        
        # MCPプロトコルに準拠したレスポンス形式
        return {
            "uri": f"file://{file_key}",
            "mimeType": "application/octet-stream",
            "blob": base64.b64encode(file_data).decode('utf-8'),
            "message": f"ファイル（キー: {file_key}）をダウンロードしました。"
        }
        
    except Exception as error:
        logger.error(f"File download error: {error}")
        raise Exception(f"ファイルのダウンロードに失敗しました: {error}")


async def _handle_upload_multiple_files(args: Dict[str, Any], repository) -> Dict[str, Any]:
    """
    複数ファイルアップロードツールの処理
    
    Args:
        args: ツール引数
        repository: リポジトリオブジェクト
        
    Returns:
        Dict[str, Any]: アップロード結果
    """
    # 引数の検証
    files = args.get("files")
    options = args.get("options", {})
    
    if not files or not isinstance(files, list):
        raise ValueError("files は必須パラメータです（リスト形式）。")
    
    # ファイルデータの準備
    processed_files = []
    for file_info in files:
        if not isinstance(file_info, dict):
            raise ValueError("各ファイルは辞書形式である必要があります。")
        
        file_name = file_info.get("fileName")
        file_data = file_info.get("fileData")
        
        if not file_name:
            raise ValueError("各ファイルにfileNameが必要です。")
        
        if not file_data:
            raise ValueError("各ファイルにfileDataが必要です。")
        
        try:
            # Base64デコード
            file_bytes = base64.b64decode(file_data)
            processed_files.append({
                "fileName": file_name,
                "fileData": file_bytes
            })
        except Exception as e:
            raise ValueError(f"ファイル '{file_name}' のBase64デコードに失敗しました: {e}")
    
    try:
        # 複数ファイルアップロード
        upload_response = await repository.file_repository.upload_multiple_files(
            processed_files, options
        )
        
        return {
            "results": upload_response.get("results", []),
            "errors": upload_response.get("errors", []),
            "total_files": upload_response.get("totalFiles", len(files)),
            "success_count": upload_response.get("successCount", 0),
            "error_count": upload_response.get("errorCount", 0),
            "message": f"{len(files)}個のファイルのアップロードを処理しました。"
        }
        
    except Exception as error:
        logger.error(f"Multiple file upload error: {error}")
        raise Exception(f"複数ファイルのアップロードに失敗しました: {error}")


async def _handle_get_file_info(args: Dict[str, Any], repository) -> Dict[str, Any]:
    """
    ファイル情報取得ツールの処理
    
    Args:
        args: ツール引数
        repository: リポジトリオブジェクト
        
    Returns:
        Dict[str, Any]: ファイル情報
    """
    # 引数の検証
    file_key = args.get("file_key")
    
    if not file_key:
        raise ValueError("file_key は必須パラメータです。")
    
    try:
        # ファイル情報取得
        file_info = await repository.file_repository.get_file_info(file_key)
        
        return {
            "file_key": file_key,
            "exists": file_info.get("exists", False),
            "size": file_info.get("size"),
            "content_type": file_info.get("contentType"),
            "message": f"ファイル（キー: {file_key}）の情報を取得しました。"
        }
        
    except Exception as error:
        logger.error(f"Get file info error: {error}")
        raise Exception(f"ファイル情報の取得に失敗しました: {error}")


async def _handle_delete_file(args: Dict[str, Any], repository) -> Dict[str, Any]:
    """
    ファイル削除ツールの処理
    
    Args:
        args: ツール引数
        repository: リポジトリオブジェクト
        
    Returns:
        Dict[str, Any]: 削除結果
    """
    # 引数の検証
    file_key = args.get("file_key")
    
    if not file_key:
        raise ValueError("file_key は必須パラメータです。")
    
    try:
        # ファイル削除
        delete_response = await repository.file_repository.delete_file(file_key)
        
        return {
            "file_key": file_key,
            "deleted": True,
            "message": f"ファイル（キー: {file_key}）を削除しました。"
        }
        
    except Exception as error:
        logger.error(f"Delete file error: {error}")
        if "直接サポートされていません" in str(error):
            raise Exception("ファイル削除機能は現在のkintone REST APIでは直接サポートされていません。")
        raise Exception(f"ファイルの削除に失敗しました: {error}")


async def _handle_download_file_stream(args: Dict[str, Any], repository) -> Dict[str, Any]:
    """
    ファイルストリーミングダウンロードツールの処理
    
    Args:
        args: ツール引数
        repository: リポジトリオブジェクト
        
    Returns:
        Dict[str, Any]: ダウンロード結果
    """
    # 引数の検証
    file_key = args.get("file_key")
    chunk_size = args.get("chunk_size", 8192)
    
    if not file_key:
        raise ValueError("file_key は必須パラメータです。")
    
    try:
        # ストリーミングダウンロード（実際にはチャンクに分割）
        chunks = []
        total_size = 0
        
        async for chunk in repository.file_repository.download_file_stream(file_key, chunk_size):
            chunks.append(base64.b64encode(chunk).decode('utf-8'))
            total_size += len(chunk)
        
        return {
            "file_key": file_key,
            "chunks": chunks,
            "total_size": total_size,
            "chunk_count": len(chunks),
            "chunk_size": chunk_size,
            "message": f"ファイル（キー: {file_key}）をストリーミングダウンロードしました。"
        }
        
    except Exception as error:
        logger.error(f"Stream download error: {error}")
        raise Exception(f"ファイルのストリーミングダウンロードに失敗しました: {error}") 