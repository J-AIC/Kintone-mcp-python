"""
System Tools Implementation

システム関連ツールの実装
"""

import logging
from typing import Dict, Any

from .....repositories import KintoneClient
from .....utils.error_handler import (
    MCPError,
    MCPErrorCode,
    ErrorHandler
)

logger = logging.getLogger(__name__)


async def handle_get_connection_info(client: KintoneClient) -> Dict[str, Any]:
    """
    get_connection_info ツールの実装
    
    Kintone接続情報を取得して返す
    
    Args:
        client: Kintoneクライアント
        
    Returns:
        接続情報
    """
    try:
        credentials = client.credentials
        
        connection_info = {
            "domain": credentials.domain,
            "auth_method": "api_token" if credentials.is_api_token_auth else "basic_auth",
            "base_url": credentials.base_url,
            "status": "connected",
            "server_info": {
                "name": "kintone-mcp-server",
                "version": "1.0.0",
                "protocol_version": "2025-03-26"
            }
        }
        
        logger.info(f"Connection info retrieved successfully for domain: {credentials.domain}")
        return connection_info
        
    except Exception as e:
        # エラーをログに記録
        ErrorHandler.log_error(e, {"operation": "get_connection_info"})
        
        # エラーが発生した場合でも基本情報は返す（機密情報は除去）
        fallback_info = {
            "domain": getattr(credentials, 'domain', 'unknown') if hasattr(client, 'credentials') else 'unknown',
            "status": "error",
            "error": str(e),
            "server_info": {
                "name": "kintone-mcp-server",
                "version": "1.0.0",
                "protocol_version": "2025-03-26"
            }
        }
        
        return fallback_info


async def handle_get_kintone_domain(client: KintoneClient) -> Dict[str, Any]:
    """
    get_kintone_domain ツールの実装
    
    Kintoneドメインを取得して返す
    
    Args:
        client: Kintoneクライアント
        
    Returns:
        ドメイン情報
    """
    try:
        credentials = client.credentials
        
        domain_info = {
            "domain": credentials.domain,
            "base_url": credentials.base_url,
            "status": "connected"
        }
        
        logger.info(f"Domain info retrieved: {credentials.domain}")
        return domain_info
        
    except Exception as e:
        ErrorHandler.log_error(e, {"operation": "get_kintone_domain"})
        raise MCPError(
            MCPErrorCode.INTERNAL_ERROR,
            f"ドメイン情報の取得中にエラーが発生しました: {str(e)}",
            {"error_type": type(e).__name__}
        )


async def handle_get_kintone_username(client: KintoneClient) -> Dict[str, Any]:
    """
    get_kintone_username ツールの実装
    
    Kintoneユーザー名を取得して返す
    
    Args:
        client: Kintoneクライアント
        
    Returns:
        ユーザー情報
    """
    try:
        credentials = client.credentials
        
        user_info = {
            "username": credentials.username,
            "auth_method": "api_token" if credentials.is_api_token_auth else "basic_auth",
            "status": "connected"
        }
        
        logger.info(f"Username info retrieved: {credentials.username}")
        return user_info
        
    except Exception as e:
        ErrorHandler.log_error(e, {"operation": "get_kintone_username"})
        raise MCPError(
            MCPErrorCode.INTERNAL_ERROR,
            f"ユーザー情報の取得中にエラーが発生しました: {str(e)}",
            {"error_type": type(e).__name__}
        )


async def handle_system_tools(tool_name: str, arguments: Dict[str, Any], client: KintoneClient) -> Dict[str, Any]:
    """
    システム関連ツールのディスパッチャ
    
    Args:
        tool_name: ツール名
        arguments: ツール引数
        client: Kintoneクライアント
        
    Returns:
        ツール実行結果
        
    Raises:
        ValueError: 未知のツール名の場合
    """
    logger.info(f"Executing system tool: {tool_name}")
    
    try:
        if tool_name == "get_connection_info":
            return await handle_get_connection_info(client)
        elif tool_name == "get_kintone_domain":
            return await handle_get_kintone_domain(client)
        elif tool_name == "get_kintone_username":
            return await handle_get_kintone_username(client)
        else:
            # 未知のツールエラー
            raise MCPError(
                MCPErrorCode.METHOD_NOT_FOUND,
                f"システムツール '{tool_name}' は存在しません",
                {"tool_name": tool_name, "category": "system"}
            )
    except MCPError:
        # MCPErrorはそのまま再発生
        raise
    except Exception as e:
        # 予期しないエラーをMCPErrorに変換
        ErrorHandler.log_error(e, {"tool_name": tool_name, "arguments": arguments})
        raise MCPError(
            MCPErrorCode.INTERNAL_ERROR,
            f"システムツール '{tool_name}' の実行中にエラーが発生しました: {str(e)}",
            {"tool_name": tool_name, "error_type": type(e).__name__}
        ) 