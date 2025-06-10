"""
FastAPI-MCP実装

FastAPI-MCPライブラリを使用したMCP実装
"""

from typing import Optional
from fastapi import FastAPI

from ...config.settings import get_settings
from ...utils.logging_config import get_logger

logger = get_logger(__name__)

# FastAPI-MCPインスタンス
_fastapi_mcp: Optional[object] = None


def setup_fastapi_mcp(app: FastAPI) -> bool:
    """
    FastAPI-MCPセットアップ
    
    Args:
        app: FastAPIアプリケーション
        
    Returns:
        bool: セットアップ成功フラグ
    """
    global _fastapi_mcp
    
    settings = get_settings()
    
    if not settings.is_fastapi_mcp_enabled:
        logger.info("FastAPI-MCP is disabled")
        return False
    
    try:
        # FastAPI-MCPライブラリをインポート
        from fastapi_mcp import FastApiMCP
        
        # FastAPI-MCPインスタンスを作成
        _fastapi_mcp = FastApiMCP(app)
        
        # MCPサーバーをマウント（SSE transport）
        _fastapi_mcp.mount(
            mount_path=settings.mcp_fastapi_path,
            transport="sse"
        )
        
        logger.info(f"✅ FastAPI-MCP mounted at {settings.mcp_fastapi_path}")
        return True
        
    except ImportError as e:
        logger.error(f"FastAPI-MCP library not found: {e}")
        logger.info("Please install fastapi-mcp: pip install fastapi-mcp")
        return False
    except Exception as e:
        logger.error(f"Failed to setup FastAPI-MCP: {e}")
        return False


def get_fastapi_mcp():
    """FastAPI-MCPインスタンスを取得"""
    return _fastapi_mcp 