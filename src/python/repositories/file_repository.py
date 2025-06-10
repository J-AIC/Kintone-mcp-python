"""
Kintone File Repository

ファイル関連の操作を担当するリポジトリクラス
"""

import logging
from typing import Dict, Any

from .base import BaseKintoneRepository

logger = logging.getLogger(__name__)


class KintoneFileRepository(BaseKintoneRepository):
    """Kintoneファイル操作リポジトリ"""
    
    async def upload_file(self, file_name: str, file_data: bytes) -> Dict[str, Any]:
        """
        ファイルをアップロード
        
        Args:
            file_name: ファイル名
            file_data: ファイルデータ（バイト形式）
            
        Returns:
            Dict[str, Any]: アップロード結果（fileKeyを含む）
            
        Raises:
            ValueError: 引数が不正な場合
            Exception: API エラーが発生した場合
        """
        # 引数バリデーション（ValueErrorはそのまま再発生）
        if not file_name or not file_name.strip():
            raise ValueError("File name is required")
        
        if not file_data:
            raise ValueError("File data is required")
        
        try:
            logger.debug(f"Uploading file: {file_name}")
            response = await self.client.upload_file(file_name, file_data)
            
            logger.debug(f"File upload response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"upload file {file_name}")
    
    async def download_file(self, file_key: str) -> bytes:
        """
        ファイルをダウンロード
        
        Args:
            file_key: ファイルキー
            
        Returns:
            bytes: ファイルデータ
            
        Raises:
            ValueError: 引数が不正な場合
            Exception: API エラーが発生した場合
        """
        # 引数バリデーション（ValueErrorはそのまま再発生）
        if not file_key or not file_key.strip():
            raise ValueError("File key is required")
        
        try:
            logger.debug(f"Downloading file with key: {file_key}")
            file_data = await self.client.download_file(file_key)
            
            logger.debug(f"Downloaded file size: {len(file_data)} bytes")
            return file_data
            
        except Exception as error:
            self.handle_kintone_error(error, f"download file with key {file_key}")

    async def upload_multiple_files(self, files: list, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        複数ファイルをアップロード
        
        Args:
            files: ファイルリスト [{"fileName": str, "fileData": bytes}, ...]
            options: アップロードオプション
            
        Returns:
            Dict[str, Any]: アップロード結果
            
        Raises:
            ValueError: 引数が不正な場合
            Exception: API エラーが発生した場合
        """
        if not files or not isinstance(files, list):
            raise ValueError("Files list is required")
        
        if not options:
            options = {}
        
        try:
            logger.debug(f"Uploading {len(files)} files")
            response = await self.client.upload_multiple_files(files, options)
            
            logger.debug(f"Multiple file upload response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"upload multiple files")

    async def get_file_info(self, file_key: str) -> Dict[str, Any]:
        """
        ファイル情報を取得
        
        Args:
            file_key: ファイルキー
            
        Returns:
            Dict[str, Any]: ファイル情報
            
        Raises:
            ValueError: 引数が不正な場合
            Exception: API エラーが発生した場合
        """
        if not file_key or not file_key.strip():
            raise ValueError("File key is required")
        
        try:
            logger.debug(f"Getting file info for key: {file_key}")
            file_info = await self.client.get_file_info(file_key)
            
            logger.debug(f"File info response: {file_info}")
            return file_info
            
        except Exception as error:
            self.handle_kintone_error(error, f"get file info for key {file_key}")

    async def delete_file(self, file_key: str) -> Dict[str, Any]:
        """
        ファイルを削除
        
        Args:
            file_key: ファイルキー
            
        Returns:
            Dict[str, Any]: 削除結果
            
        Raises:
            ValueError: 引数が不正な場合
            Exception: API エラーが発生した場合
        """
        if not file_key or not file_key.strip():
            raise ValueError("File key is required")
        
        try:
            logger.debug(f"Deleting file with key: {file_key}")
            response = await self.client.delete_file(file_key)
            
            logger.debug(f"File deletion response: {response}")
            return response
            
        except Exception as error:
            self.handle_kintone_error(error, f"delete file with key {file_key}")

    async def download_file_stream(self, file_key: str, chunk_size: int = 8192):
        """
        ファイルをストリーミングダウンロード
        
        Args:
            file_key: ファイルキー
            chunk_size: チャンクサイズ（バイト）
            
        Yields:
            bytes: ファイルデータのチャンク
            
        Raises:
            ValueError: 引数が不正な場合
            Exception: API エラーが発生した場合
        """
        if not file_key or not file_key.strip():
            raise ValueError("File key is required")
        
        try:
            logger.debug(f"Streaming download for file key: {file_key}")
            async for chunk in self.client.download_file_stream(file_key, chunk_size):
                yield chunk
                
        except Exception as error:
            self.handle_kintone_error(error, f"stream download file with key {file_key}") 