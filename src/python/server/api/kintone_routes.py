"""
Kintone APIルート

Kintone APIエンドポイントの定義
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from ...core.lifespan import get_kintone_client
from ...core.response_models import KintoneRecordResponse, KintoneAppResponse, APIResponse
from ...core.exceptions import KintoneAPIError
from ...repositories.nodejs_kintone_client import NodeJSKintoneClientFactory
from ...utils.logging_config import get_logger

logger = get_logger(__name__)

# Kintone APIルーター
kintone_router = APIRouter(
    prefix="/kintone",
    tags=["Kintone API"]
)


# Pydanticモデルの定義
class RecordCreateRequest(BaseModel):
    app_id: str
    record: Dict[str, Any]


class RecordUpdateRequest(BaseModel):
    app_id: str
    record_id: str
    record: Dict[str, Any]


class RecordDeleteRequest(BaseModel):
    app_id: str
    record_id: str


class RecordsGetRequest(BaseModel):
    app_id: str
    query: Optional[str] = None
    fields: Optional[List[str]] = None


# 依存性注入用の関数
def get_kintone_client_dependency() -> NodeJSKintoneClientFactory:
    """Kintoneクライアントを取得（依存性注入用）"""
    client = get_kintone_client()
    if not client:
        raise HTTPException(status_code=503, detail="Kintone client not initialized")
    return client


# Kintone API エンドポイント
@kintone_router.post("/records", response_model=KintoneRecordResponse)
async def create_record(
    request: RecordCreateRequest,
    client: NodeJSKintoneClientFactory = Depends(get_kintone_client_dependency)
) -> KintoneRecordResponse:
    """レコードを作成"""
    try:
        result = await client.create_record(request.app_id, request.record)
        return KintoneRecordResponse(
            success=True,
            record_id=result.get("id"),
            revision=result.get("revision")
        )
    except Exception as e:
        logger.error(f"Error creating record: {e}")
        return KintoneRecordResponse(
            success=False,
            error=str(e)
        )


@kintone_router.get("/records/{app_id}", response_model=KintoneRecordResponse)
async def get_records(
    app_id: str,
    query: Optional[str] = None,
    fields: Optional[str] = None,
    client: NodeJSKintoneClientFactory = Depends(get_kintone_client_dependency)
) -> KintoneRecordResponse:
    """レコードを取得"""
    try:
        field_list = fields.split(",") if fields else None
        result = await client.get_records(app_id, query=query, fields=field_list)
        return KintoneRecordResponse(
            success=True,
            records=result.get("records", []),
            total_count=result.get("totalCount", 0)
        )
    except Exception as e:
        logger.error(f"Error getting records: {e}")
        return KintoneRecordResponse(
            success=False,
            error=str(e)
        )


@kintone_router.put("/records/{app_id}/{record_id}", response_model=KintoneRecordResponse)
async def update_record(
    app_id: str,
    record_id: str,
    request: Dict[str, Any],
    client: NodeJSKintoneClientFactory = Depends(get_kintone_client_dependency)
) -> KintoneRecordResponse:
    """レコードを更新"""
    try:
        result = await client.update_record(app_id, record_id, request)
        return KintoneRecordResponse(
            success=True,
            revision=result.get("revision")
        )
    except Exception as e:
        logger.error(f"Error updating record: {e}")
        return KintoneRecordResponse(
            success=False,
            error=str(e)
        )


@kintone_router.delete("/records/{app_id}/{record_id}", response_model=KintoneRecordResponse)
async def delete_record(
    app_id: str,
    record_id: str,
    client: NodeJSKintoneClientFactory = Depends(get_kintone_client_dependency)
) -> KintoneRecordResponse:
    """レコードを削除"""
    try:
        result = await client.delete_record(app_id, record_id)
        return KintoneRecordResponse(
            success=True,
            revision=result.get("revision")
        )
    except Exception as e:
        logger.error(f"Error deleting record: {e}")
        return KintoneRecordResponse(
            success=False,
            error=str(e)
        )


@kintone_router.get("/apps", response_model=KintoneAppResponse)
async def get_apps(
    client: NodeJSKintoneClientFactory = Depends(get_kintone_client_dependency)
) -> KintoneAppResponse:
    """アプリ一覧を取得"""
    try:
        result = await client.get_apps()
        return KintoneAppResponse(
            success=True,
            apps=result.get("apps", [])
        )
    except Exception as e:
        logger.error(f"Error getting apps: {e}")
        return KintoneAppResponse(
            success=False,
            error=str(e)
        )


@kintone_router.get("/app/{app_id}/form", response_model=KintoneAppResponse)
async def get_app_form(
    app_id: str,
    client: NodeJSKintoneClientFactory = Depends(get_kintone_client_dependency)
) -> KintoneAppResponse:
    """アプリのフォーム設定を取得"""
    try:
        result = await client.get_app_form_fields(app_id)
        return KintoneAppResponse(
            success=True,
            properties=result.get("properties", {})
        )
    except Exception as e:
        logger.error(f"Error getting app form: {e}")
        return KintoneAppResponse(
            success=False,
            error=str(e)
        ) 