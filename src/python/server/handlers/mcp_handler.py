"""
MCP Request Handler

JSON-RPCリクエストの処理とディスパッチ
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from fastapi import Request, HTTPException
from jsonrpcserver import method, dispatch, Result, Success, Error, serve
import json
from datetime import datetime

from ....repositories import KintoneClient
from ....repositories.kintone_repository import KintoneRepository
from ...tools.definitions import ALL_TOOL_DEFINITIONS
from ...tools.implementations.system_tools import handle_system_tools
from ...tools.implementations.file_tools import handle_file_tools
from ...tools.implementations.user_tools import handle_user_tools
from ...tools.implementations.documentation_tools import handle_documentation_tools
from ...tools.implementations.logging_tools import handle_logging_tools
from ...tools.implementations.app_tools import handle_app_tools
from ...tools.implementations.record_tools import handle_record_tools
from ...tools.implementations.field_tools import handle_field_tools
from ...tools.implementations.layout_tools import handle_layout_tools
from ....utils.logging_config import setup_logging
from ....utils.error_handler import (
    MCPError,
    MCPErrorCode,
    ErrorHandler
)

logger = logging.getLogger(__name__)


class MCPHandler:
    """
    MCP JSON-RPCリクエストハンドラ
    
    jsonrpcserverを利用してリクエストを処理し、
    適切なツール実装にディスパッチする
    """
    
    def __init__(self, client: KintoneClient):
        """
        Args:
            client: Kintoneクライアント
        """
        self.client = client
        self.repository = KintoneRepository(client.credentials)
        
        # ロギング設定を初期化
        setup_logging()
        
        logger.info("MCP Handler initialized")
    
    def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP initialize メソッドの処理
        
        Args:
            params: リクエストパラメータ
            
        Returns:
            初期化レスポンス
        """
        client_info = params.get("clientInfo", {})
        protocol_version = params.get("protocolVersion", "")
        
        logger.info(f"Initialize request from client: {client_info}")
        logger.info(f"Protocol version: {protocol_version}")
        
        return {
            "protocolVersion": "2025-03-26",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "kintone-mcp-server",
                "version": "1.0.0"
            }
        }
    
    def _handle_tools_list(self) -> Dict[str, Any]:
        """
        tools/list メソッドの処理
        
        Returns:
            ツール一覧
        """
        return {"tools": ALL_TOOL_DEFINITIONS}
    
    async def _handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        tools/call メソッドの処理
        
        Args:
            params: リクエストパラメータ
            
        Returns:
            ツール実行結果
        """
        name = params.get("name")
        arguments = params.get("arguments", {})
        
        logger.info(f"Tool call: {name}")
        if arguments:
            logger.info(f"Arguments: {json.dumps(arguments, ensure_ascii=False)}")
        
        try:
            # ツールのカテゴリに応じて適切なハンドラーに振り分け
            if name in ["get_connection_info"]:
                return await handle_system_tools(name, arguments, self.client)
            elif name in ["upload_file", "download_file"]:
                return await handle_file_tools(name, arguments, self.repository)
            elif name in ["get_users", "get_groups", "get_group_users", "add_guests"]:
                return await handle_user_tools(name, arguments, self.repository.user_repo)
            elif name in ["get_field_type_documentation", "get_available_field_types", "get_documentation_tool_description", "get_field_creation_tool_description"]:
                return await handle_documentation_tools(name, arguments)
            elif name in ["logging/setLevel", "logging/getLevel", "logging/sendMessage"]:
                return await handle_logging_tools(name, arguments)
            elif name in ["get_process_management", "get_apps_info", "create_app", "deploy_app", "get_deploy_status", "update_app_settings", "get_form_layout", "update_form_layout", "move_app_to_space", "move_app_from_space", "get_preview_app_settings", "get_preview_form_fields", "get_preview_form_layout", "get_app_actions", "get_app_plugins"]:
                return await handle_app_tools(name, arguments, self.repository.app_repo)
            elif name in ["get_record", "search_records", "create_record", "update_record", "add_record_comment"]:
                return await handle_record_tools(name, arguments, self.repository.record_repo)
            elif name in ["add_fields", "update_fields", "delete_fields", "get_form_fields", "create_lookup_field", "update_field", "create_choice_field", "create_reference_table_field"]:
                return await handle_field_tools(name, arguments, self.repository.field_repo)
            elif name in ["add_fields_to_layout", "remove_fields_from_layout", "create_field_group"]:
                return await handle_layout_tools(name, arguments, self.repository.layout_repo)
            else:
                # 未知のツールエラー
                raise MCPError(
                    MCPErrorCode.METHOD_NOT_FOUND,
                    f"ツール '{name}' は存在しません",
                    {"tool_name": name, "available_tools": [tool["name"] for tool in ALL_TOOL_DEFINITIONS]}
                )
                
        except MCPError:
            # MCPErrorはそのまま再発生
            raise
        except Exception as e:
            # 予期しないエラーをMCPErrorに変換
            ErrorHandler.log_error(e, {"tool_name": name, "arguments": arguments})
            raise MCPError(
                MCPErrorCode.INTERNAL_ERROR,
                f"ツール '{name}' の実行中にエラーが発生しました: {str(e)}",
                {"tool_name": name, "error_type": type(e).__name__}
            )
    
    
    async def handle_request(self, request_data: str) -> str:
        """
        JSON-RPCリクエストを処理
        
        Args:
            request_data: JSON-RPC リクエスト文字列
            
        Returns:
            JSON-RPC レスポンス文字列
        """
        request_id = None
        
        try:
            logger.debug(f"Handling JSON-RPC request: {request_data}")
            
            # リクエストを解析
            request_json = json.loads(request_data)
            request_id = request_json.get("id")
            method = request_json.get("method")
            params = request_json.get("params", {})
            
            # メソッドに応じて処理を振り分け
            if method == "initialize":
                result = self._handle_initialize(params)
            elif method == "tools/list":
                result = self._handle_tools_list()
            elif method == "tools/call":
                result = await self._handle_tools_call(params)
            else:
                # 未知のメソッド
                return json.dumps({
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601,
                        "message": "Method not found",
                        "data": method
                    },
                    "id": request_id
                }, ensure_ascii=False)
            
            # 成功レスポンスを生成
            response = {
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id
            }
            
            logger.debug(f"JSON-RPC response: {response}")
            return json.dumps(response, ensure_ascii=False)
            
        except MCPError as mcp_error:
            # MCPErrorの場合は適切なレスポンスを生成
            logger.error(f"MCP Error handling JSON-RPC request: {mcp_error.message}")
            error_response = mcp_error.to_dict()
            if request_id is not None:
                error_response["id"] = request_id
            return json.dumps(error_response, ensure_ascii=False)
            
        except Exception as e:
            # 予期しないエラーの場合
            ErrorHandler.log_error(e, {"request_data": request_data[:500]})
            
            # MCP形式のエラーレスポンスを生成
            error_response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": str(e),
                    "data": {
                        "error_type": type(e).__name__,
                        "timestamp": getattr(e, 'timestamp', datetime.now().isoformat())
                    }
                },
                "id": request_id
            }
            
            return json.dumps(error_response, ensure_ascii=False) 