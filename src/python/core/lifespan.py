"""
共通ライフサイクル管理

アプリケーションの起動・終了処理を統一管理
"""

import sys
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI

from ..config.settings import get_settings, MCPMode, KintoneClientType
from ..core.exceptions import ConfigurationError, ServerInitializationError
from ..repositories.nodejs_kintone_client import NodeJSKintoneClientFactory
from ..server.mcp_server import MCPServer
from ..server.handlers.mcp_handler import MCPHandler
from ..utils.logging_config import get_logger

logger = get_logger(__name__)

# グローバル変数
_kintone_client: Optional[NodeJSKintoneClientFactory] = None
_mcp_server: Optional[MCPServer] = None
_mcp_handler: Optional[MCPHandler] = None


async def initialize_kintone_client() -> Optional[NodeJSKintoneClientFactory]:
    """Kintoneクライアントを初期化"""
    global _kintone_client
    
    settings = get_settings()
    credentials = settings.get_kintone_credentials()
    
    if not credentials:
        logger.warning("Kintone認証情報が設定されていません")
        return None
    
    try:
        if settings.kintone_client_type == KintoneClientType.NODEJS:
            _kintone_client = NodeJSKintoneClientFactory.create_from_credentials(credentials)
            
            # 接続テスト
            logger.info("Testing Kintone connection with Node.js client...")
            apps = await _kintone_client.get_apps()
            logger.info(f"✅ Kintone connection successful! Found {len(apps)} apps")
            
        else:
            # Python SDKの実装は今後対応
            raise NotImplementedError("Python Kintone client is not implemented yet")
        
        return _kintone_client
        
    except Exception as e:
        logger.error(f"Failed to initialize Kintone client: {e}")
        raise ServerInitializationError(f"Kintoneクライアントの初期化に失敗しました: {e}")


async def initialize_mcp_server() -> tuple[Optional[MCPServer], Optional[MCPHandler]]:
    """MCPサーバーを初期化"""
    global _mcp_server, _mcp_handler
    
    settings = get_settings()
    
    if not settings.is_native_mcp_enabled:
        logger.info("Native MCP server is disabled")
        return None, None
    
    try:
        credentials = settings.get_kintone_credentials()
        if not credentials:
            raise ConfigurationError("Kintone認証情報が設定されていません")
        
        # MCPサーバーの初期化
        _mcp_server = MCPServer(credentials)
        _mcp_handler = MCPHandler(_mcp_server.client)
        
        logger.info(f"MCP Server initialized for domain: {credentials.domain}")
        
        return _mcp_server, _mcp_handler
        
    except Exception as e:
        logger.error(f"Failed to initialize MCP Server: {e}")
        raise ServerInitializationError(f"MCPサーバーの初期化に失敗しました: {e}")


async def cleanup_resources():
    """リソースのクリーンアップ"""
    global _kintone_client, _mcp_server, _mcp_handler
    
    logger.info("Cleaning up resources...")
    
    # MCPサーバーのクリーンアップ
    if _mcp_server:
        try:
            await _mcp_server.close()
        except Exception as e:
            logger.error(f"Error closing MCP server: {e}")
        finally:
            _mcp_server = None
            _mcp_handler = None
    
    # Kintoneクライアントのクリーンアップ
    if _kintone_client:
        # 必要に応じてクリーンアップ処理を追加
        _kintone_client = None
    
    logger.info("Resource cleanup completed")


@asynccontextmanager
async def application_lifespan(app: FastAPI):
    """アプリケーションライフサイクル管理"""
    settings = get_settings()
    
    logger.info("Starting Kintone MCP Server...")
    logger.info(f"MCP Mode: {settings.mcp_mode.value}")
    logger.info(f"Kintone Client Type: {settings.kintone_client_type.value}")
    
    try:
        # Kintoneクライアント初期化
        await initialize_kintone_client()
        
        # MCPサーバー初期化（必要に応じて）
        if settings.is_native_mcp_enabled:
            await initialize_mcp_server()
        
        logger.info("✅ Server initialization completed successfully")
        
        # アプリケーション実行
        yield
        
    except Exception as e:
        logger.error(f"❌ Server initialization failed: {e}")
        raise
    finally:
        # クリーンアップ
        await cleanup_resources()


def get_kintone_client() -> Optional[NodeJSKintoneClientFactory]:
    """初期化済みKintoneクライアントを取得"""
    return _kintone_client


def get_mcp_server() -> Optional[MCPServer]:
    """初期化済みMCPサーバーを取得"""
    return _mcp_server


def get_mcp_handler() -> Optional[MCPHandler]:
    """初期化済みMCPハンドラーを取得"""
    return _mcp_handler 