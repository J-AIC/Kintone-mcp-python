"""
MCP Server Core Implementation

FastAPIベースのMCPサーバーコア機能
"""

import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from ...models.kintone_credentials import KintoneCredentials
from ...repositories import KintoneClient
from ...utils.error_handler import (
    MCPError,
    MCPErrorCode,
    ErrorHandler
)
from ...utils.exceptions import KintoneBaseError

logger = logging.getLogger(__name__)


class MCPServer:
    """
    Model Context Protocol (MCP) サーバーのコアクラス
    
    FastAPIアプリケーションインスタンスを持ち、
    MCPプロトコルのライフサイクル処理を管理する
    """
    
    def __init__(self, credentials: KintoneCredentials):
        """
        Args:
            credentials: Kintone認証情報
        """
        self.credentials = credentials
        self.client = KintoneClient(credentials)
        
        # FastAPIアプリケーションの初期化
        self.app = FastAPI(
            title="Kintone MCP Server",
            description="Model Context Protocol server for Kintone integration",
            version="1.0.0"
        )
        
        # CORSミドルウェアの設定
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # サーバー情報
        self.server_info = {
            "name": "kintone-mcp-server",
            "version": "1.0.0",
            "protocol_version": "2025-03-26"
        }
        
        # ツールのケーパビリティ（初期は空）
        self.capabilities = {
            "tools": {}
        }
        
        # リクエストハンドラーの設定
        self._setup_routes()
        
        # エラーハンドラーの設定
        self._setup_error_handlers()
        
        logger.info("MCP Server initialized")
    
    def _setup_routes(self):
        """FastAPIルートの設定"""
        
        @self.app.get("/health")
        async def health_check():
            """ヘルスチェックエンドポイント"""
            return {"status": "healthy", "server": self.server_info}
        
        @self.app.post("/mcp/initialize")
        async def initialize(request: Dict[str, Any]):
            """
            MCP initialize リクエストハンドラ
            
            Args:
                request: 初期化リクエスト
                
            Returns:
                初期化レスポンス
            """
            return await self._handle_initialize(request)
        
        @self.app.post("/mcp/notifications/initialized")
        async def initialized():
            """
            MCP notifications/initialized ハンドラ（ダミー実装）
            
            Returns:
                成功レスポンス
            """
            logger.info("MCP client initialized notification received")
            return {"status": "acknowledged"}
    
    def _setup_error_handlers(self):
        """FastAPIエラーハンドラーの設定"""
        
        @self.app.exception_handler(MCPError)
        async def mcp_error_handler(request: Request, exc: MCPError):
            """MCPエラーのハンドラー"""
            logger.error(f"MCP Error: {exc.message}")
            
            # MCP仕様に準拠したエラーレスポンスを返す
            return JSONResponse(
                status_code=400,  # MCPエラーは基本的にクライアントエラー
                content=exc.to_dict()
            )
        
        @self.app.exception_handler(KintoneBaseError)
        async def kintone_error_handler(request: Request, exc: KintoneBaseError):
            """Kintoneエラーのハンドラー"""
            ErrorHandler.log_error(exc, {"path": str(request.url)})
            
            # KintoneエラーをMCP形式に変換
            mcp_response = ErrorHandler.to_mcp_error_response(exc)
            return JSONResponse(
                status_code=400,
                content=mcp_response
            )
        
        @self.app.exception_handler(RequestValidationError)
        async def validation_error_handler(request: Request, exc: RequestValidationError):
            """リクエストバリデーションエラーのハンドラー"""
            logger.error(f"Validation Error: {exc}")
            
            # バリデーションエラーをMCPエラーに変換
            mcp_error = MCPError(
                MCPErrorCode.INVALID_PARAMS,
                "リクエストパラメータが無効です",
                {"validation_errors": exc.errors()}
            )
            
            return JSONResponse(
                status_code=400,
                content=mcp_error.to_dict()
            )
        
        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            """HTTPエラーのハンドラー"""
            logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
            
            # HTTPエラーをMCPエラーに変換
            if exc.status_code == 404:
                error_code = MCPErrorCode.METHOD_NOT_FOUND
            elif exc.status_code == 400:
                error_code = MCPErrorCode.INVALID_PARAMS
            elif exc.status_code == 401:
                error_code = MCPErrorCode.INVALID_REQUEST
            else:
                error_code = MCPErrorCode.INTERNAL_ERROR
            
            mcp_error = MCPError(
                error_code,
                f"HTTPエラー: {exc.detail}",
                {"status_code": exc.status_code}
            )
            
            return JSONResponse(
                status_code=exc.status_code,
                content=mcp_error.to_dict()
            )
        
        @self.app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            """一般的な例外のハンドラー"""
            ErrorHandler.log_error(exc, {"path": str(request.url)})
            
            # 一般的なエラーをMCP形式に変換
            mcp_response = ErrorHandler.to_mcp_error_response(exc)
            
            return JSONResponse(
                status_code=500,
                content=mcp_response
            )
    
    async def _handle_initialize(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP initialize リクエストの処理
        
        Args:
            request: 初期化リクエスト
            
        Returns:
            初期化レスポンス
        """
        try:
            # クライアント情報の取得
            client_info = request.get("params", {}).get("clientInfo", {})
            protocol_version = request.get("params", {}).get("protocolVersion")
            
            logger.info(f"MCP initialize request from client: {client_info}")
            logger.info(f"Protocol version: {protocol_version}")
            
            # プロトコルバージョンの検証
            if protocol_version and protocol_version != self.server_info["protocol_version"]:
                logger.warning(f"Protocol version mismatch: client={protocol_version}, server={self.server_info['protocol_version']}")
            
            # 初期化レスポンスの構築
            response = {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "protocolVersion": self.server_info["protocol_version"],
                    "capabilities": self.capabilities,
                    "serverInfo": {
                        "name": self.server_info["name"],
                        "version": self.server_info["version"]
                    }
                }
            }
            
            logger.info("MCP server initialized successfully")
            return response
            
        except Exception as e:
            # 初期化エラーをログに記録
            ErrorHandler.log_error(e, {"operation": "MCP_initialization", "client_info": client_info})
            raise HTTPException(status_code=500, detail=f"MCP初期化エラー: {str(e)}")
    
    async def get_connection_info(self) -> Dict[str, Any]:
        """
        Kintone接続情報を取得
        
        Returns:
            接続情報
        """
        try:
            return {
                "domain": self.credentials.domain,
                "auth_method": "api_token" if self.credentials.is_api_token_auth else "basic_auth",
                "base_url": self.credentials.base_url,
                "status": "connected"
            }
        except Exception as e:
            # 接続情報取得エラーをログに記録し、安全なエラー情報を返す
            ErrorHandler.log_error(e, {"operation": "get_connection_info"})
            return {
                "domain": self.credentials.domain,
                "status": "error",
                "error": str(e)
            }
    
    async def close(self):
        """リソースのクリーンアップ"""
        await self.client.close()
        logger.info("MCP Server closed") 