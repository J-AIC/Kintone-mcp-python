"""
Node.js Wrapper Integration Interface

Node.jsラッパーとPydanticモデル間の変換を行う統合インターフェース
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic
from pydantic import BaseModel
import json
import asyncio
import subprocess
from pathlib import Path

from ..utils.logging_config import get_logger
from ..models.kintone_credentials import KintoneCredentials
from ..utils.exceptions import (
    KintoneBaseError,
    NodeJSWrapperError,
    parse_nodejs_error_response
)
from ..utils.error_handler import ErrorHandler, handle_kintone_errors

logger = get_logger(__name__)

T = TypeVar('T', bound=BaseModel)


class NodeJSWrapperInterface(ABC):
    """Node.jsラッパーを呼び出す共通インターフェース"""
    
    def __init__(self, credentials: KintoneCredentials):
        self.credentials = credentials
        # 現在のファイルから相対的にプロジェクトルートを計算 (src/python/repositories/nodejs_wrapper_interface.py から3つ上)
        project_root = Path(__file__).resolve().parents[3]
        self.wrapper_path = project_root / 'src' / 'nodejs' / 'wrapper.mjs'
        self.js_dir = self.wrapper_path.parent
        
    @handle_kintone_errors(log_errors=True, return_mcp_format=False)
    async def call_nodejs_wrapper(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Node.jsラッパーを呼び出す共通メソッド
        
        Args:
            command: 実行するコマンド
            params: パラメータ
            
        Returns:
            Dict[str, Any]: レスポンスデータ
            
        Raises:
            KintoneBaseError: kintone関連エラー
            NodeJSWrapperError: Node.jsラッパー実行エラー
        """
        # 認証情報を追加
        full_params = {
            'domain': self.credentials.domain,
            'username': self.credentials.username,
            'password': self.credentials.password,
            'apiToken': self.credentials.api_token,
            **params
        }
        
        logger.debug(f"Executing Node.js command: {command}")
        logger.debug(
            f"Params: {json.dumps({k: v for k, v in full_params.items() if k not in ['password', 'apiToken']})}"
        )

        proc = None
        timeout_occurred = False
        
        try:
            proc = await asyncio.create_subprocess_exec(
                'node',
                str(self.wrapper_path),
                command,
                json.dumps(full_params),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.js_dir)
            )

            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)
            except asyncio.TimeoutError:
                timeout_occurred = True
                logger.error("Node.js command timed out")
                proc.kill()
                await proc.wait()
                
                # タイムアウトエラーを作成
                raise NodeJSWrapperError(
                    message="Node.jsラッパーの実行がタイムアウトしました",
                    command=command,
                    timeout=True,
                    exit_code=proc.returncode if proc else None
                )

            stdout_text = stdout.decode('utf-8') if stdout else ''
            stderr_text = stderr.decode('utf-8') if stderr else ''

            # プロセス結果を作成
            process_result = subprocess.CompletedProcess(
                args=['node', str(self.wrapper_path), command],
                returncode=proc.returncode,
                stdout=stdout_text,
                stderr=stderr_text
            )

            # エラーハンドリング
            if proc.returncode != 0:
                error = ErrorHandler.handle_subprocess_error(
                    process_result, command, timeout_occurred
                )
                raise error

            # JSONレスポンスの解析
            try:
                response = json.loads(stdout_text)
                
                # Node.jsラッパーからのエラーレスポンスをチェック
                if not response.get('success', True):
                    error = parse_nodejs_error_response(stdout_text)
                    raise error

                return response.get('data')
                
            except json.JSONDecodeError as e:
                error = ErrorHandler.handle_json_parse_error(stdout_text, e)
                raise error

        except KintoneBaseError:
            # カスタム例外はそのまま再発生
            raise
        except Exception as e:
            # その他の例外をNodeJSWrapperErrorに変換
            if not isinstance(e, KintoneBaseError):
                raise NodeJSWrapperError(
                    message=f"Node.jsラッパーの実行中に予期しないエラーが発生しました: {str(e)}",
                    command=command,
                    details={"original_error": str(e)}
                )
    
    @abstractmethod
    def parse_response(self, response: Dict[str, Any], model_class: type[T]) -> T:
        """
        レスポンスをPydanticモデルに変換
        
        Args:
            response: APIレスポンス
            model_class: 変換先のPydanticモデルクラス
            
        Returns:
            T: Pydanticモデルインスタンス
        """
        pass
    
    @abstractmethod
    def parse_response_list(self, response: Dict[str, Any], model_class: type[T]) -> List[T]:
        """
        レスポンスリストをPydanticモデルリストに変換
        
        Args:
            response: APIレスポンス
            model_class: 変換先のPydanticモデルクラス
            
        Returns:
            List[T]: Pydanticモデルインスタンスのリスト
        """
        pass


class KintoneDataConverter:
    """Kintone APIレスポンスとPydanticモデル間の変換ユーティリティ"""
    
    @staticmethod
    def convert_kintone_record(json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        kintone APIレスポンスをKintoneRecordモデル用に変換
        
        Args:
            json_data: kintone APIレスポンス
            
        Returns:
            Dict[str, Any]: KintoneRecordモデル用データ
        """
        if 'record' in json_data:
            # 単一レコードの場合
            record_data = json_data['record']
            return {
                'record_id': int(record_data.get('$id', {}).get('value', 0)),
                'revision': int(record_data.get('$revision', {}).get('value', 0)),
                'fields': KintoneDataConverter._convert_fields(record_data)
            }
        elif 'records' in json_data:
            # 複数レコードの場合（最初のレコードを返す）
            if json_data['records']:
                return KintoneDataConverter.convert_kintone_record({'record': json_data['records'][0]})
        
        return {}
    
    @staticmethod
    def convert_kintone_records(json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        kintone APIレスポンスをKintoneRecordモデルリスト用に変換
        
        Args:
            json_data: kintone APIレスポンス
            
        Returns:
            List[Dict[str, Any]]: KintoneRecordモデル用データのリスト
        """
        if 'records' in json_data:
            return [
                KintoneDataConverter.convert_kintone_record({'record': record})
                for record in json_data['records']
            ]
        return []
    
    @staticmethod
    def convert_app_info(json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        アプリ情報をAppInfoモデル用に変換
        
        Args:
            json_data: kintone APIレスポンス
            
        Returns:
            Dict[str, Any]: AppInfoモデル用データ
        """
        return {
            'app_id': int(json_data.get('appId', 0)),
            'code': json_data.get('code', ''),
            'name': json_data.get('name', ''),
            'description': json_data.get('description', ''),
            'space_id': json_data.get('spaceId'),
            'thread_id': json_data.get('threadId'),
            'created_at': json_data.get('createdAt'),
            'creator': json_data.get('creator', {}),
            'modified_at': json_data.get('modifiedAt'),
            'modifier': json_data.get('modifier', {})
        }
    
    @staticmethod
    def convert_app_list(json_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        アプリリストをAppInfoモデルリスト用に変換
        
        Args:
            json_data: kintone APIレスポンス
            
        Returns:
            List[Dict[str, Any]]: AppInfoモデル用データのリスト
        """
        return [
            KintoneDataConverter.convert_app_info(app_data)
            for app_data in json_data
        ]
    
    @staticmethod
    def _convert_fields(record_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        レコードフィールドを変換
        
        Args:
            record_data: レコードデータ
            
        Returns:
            Dict[str, Any]: 変換されたフィールドデータ
        """
        fields = {}
        for field_code, field_data in record_data.items():
            if not field_code.startswith('$'):  # システムフィールドを除外
                fields[field_code] = field_data.get('value')
        return fields


class RepositoryIntegrationMixin(NodeJSWrapperInterface):
    """リポジトリ統合用のミックスインクラス"""
    
    def parse_response(self, response: Dict[str, Any], model_class: type[T]) -> T:
        """
        レスポンスをPydanticモデルに変換
        
        Args:
            response: APIレスポンス
            model_class: 変換先のPydanticモデルクラス
            
        Returns:
            T: Pydanticモデルインスタンス
        """
        # モデルクラス名に基づいて適切な変換メソッドを選択
        model_name = model_class.__name__
        
        if 'Record' in model_name:
            converted_data = KintoneDataConverter.convert_kintone_record(response)
        elif 'App' in model_name:
            converted_data = KintoneDataConverter.convert_app_info(response)
        else:
            # デフォルトはそのまま使用
            converted_data = response
        
        return model_class(**converted_data)
    
    def parse_response_list(self, response: Dict[str, Any], model_class: type[T]) -> List[T]:
        """
        レスポンスリストをPydanticモデルリストに変換
        
        Args:
            response: APIレスポンス
            model_class: 変換先のPydanticモデルクラス
            
        Returns:
            List[T]: Pydanticモデルインスタンスのリスト
        """
        # モデルクラス名に基づいて適切な変換メソッドを選択
        model_name = model_class.__name__
        
        if 'Record' in model_name:
            converted_data_list = KintoneDataConverter.convert_kintone_records(response)
        elif 'App' in model_name:
            # レスポンスが直接リストの場合
            if isinstance(response, list):
                converted_data_list = KintoneDataConverter.convert_app_list(response)
            else:
                converted_data_list = []
        else:
            # デフォルトはそのまま使用
            if isinstance(response, list):
                converted_data_list = response
            else:
                converted_data_list = []
        
        return [model_class(**data) for data in converted_data_list] 