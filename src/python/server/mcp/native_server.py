"""
ネイティブMCP実装

カスタムMCP JSON-RPCプロトコル実装
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

from ...core.lifespan import get_mcp_handler
from ...core.exceptions import MCPProtocolError
from ...core.response_models import APIResponse
from ...utils.logging_config import get_logger

logger = get_logger(__name__)

# ネイティブMCPルーター
native_mcp_router = APIRouter(
    prefix="/mcp",
    tags=["Native MCP"]
)


@native_mcp_router.post("/rpc")
async def handle_native_mcp_request(request: Request):
    """
    ネイティブMCP JSON-RPCリクエストを処理
    
    Args:
        request: FastAPIリクエスト
        
    Returns:
        JSON-RPCレスポンス
    """
    mcp_handler = get_mcp_handler()
    
    if not mcp_handler:
        raise HTTPException(
            status_code=503, 
            detail="Native MCP Handler not initialized"
        )
    
    try:
        # リクエストボディを取得
        request_data = await request.body()
        request_text = request_data.decode('utf-8')
        
        logger.debug(f"Received native MCP request: {request_text}")
        
        # JSON-RPCリクエストを処理
        response_text = await mcp_handler.handle_request(request_text)
        
        logger.debug(f"Native MCP response: {response_text}")
        
        # JSONレスポンスとして返す
        return JSONResponse(
            content=response_text,
            media_type="application/json"
        )
        
    except Exception as e:
        logger.error(f"Error handling native MCP request: {e}")
        error_response = APIResponse.error_response(
            error=f"Native MCP error: {str(e)}",
            error_code="NATIVE_MCP_ERROR"
        )
        raise HTTPException(
            status_code=500, 
            detail=error_response.dict()
        ) 