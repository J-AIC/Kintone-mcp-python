"""
Record Tools Schemas

レコード関連ツールのPydantic入力スキーマ
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field


class GetRecordRequest(BaseModel):
    """get_recordツールのリクエストスキーマ"""
    app_id: int = Field(..., description="kintoneアプリのID")
    record_id: int = Field(..., description="レコードID")


class SearchRecordsRequest(BaseModel):
    """search_recordsツールのリクエストスキーマ"""
    app_id: int = Field(..., description="kintoneアプリのID")
    query: Optional[str] = Field(None, description="検索クエリ")
    fields: Optional[List[str]] = Field(None, description="取得するフィールド名の配列")


class CreateRecordRequest(BaseModel):
    """create_recordツールのリクエストスキーマ"""
    app_id: int = Field(..., description="kintoneアプリのID")
    fields: Dict[str, Any] = Field(..., description="レコードのフィールド値（各フィールドは { \"value\": ... } の形式で指定）")


class UpdateKey(BaseModel):
    """レコード更新時のキー指定"""
    field: str = Field(..., description="重複禁止に設定されたフィールドコード")
    value: str = Field(..., description="フィールドの値")


class UpdateRecordRequest(BaseModel):
    """update_recordツールのリクエストスキーマ"""
    app_id: int = Field(..., description="kintoneアプリのID")
    record_id: Optional[int] = Field(None, description="レコードID（updateKeyを使用する場合は不要）")
    updateKey: Optional[UpdateKey] = Field(None, description="重複禁止フィールドを使用してレコードを特定（record_idを使用する場合は不要）")
    fields: Dict[str, Any] = Field(..., description="更新するフィールド値（各フィールドは { \"value\": ... } の形式で指定）")

    def model_post_init(self, __context: Any) -> None:
        """バリデーション後の処理"""
        if not self.record_id and not self.updateKey:
            raise ValueError("record_id または updateKey のいずれかは必須です")


class MentionInfo(BaseModel):
    """メンション情報"""
    code: str = Field(..., description="メンション対象のユーザー、グループ、組織のコード")
    type: str = Field(..., description="メンション対象の種類", pattern="^(USER|GROUP|ORGANIZATION)$")


class AddRecordCommentRequest(BaseModel):
    """add_record_commentツールのリクエストスキーマ"""
    app_id: int = Field(..., description="kintoneアプリのID")
    record_id: int = Field(..., description="レコードID")
    text: str = Field(..., description="コメント本文")
    mentions: Optional[List[MentionInfo]] = Field(None, description="メンション情報の配列")


# ツール名とスキーマクラスのマッピング
RECORD_TOOL_SCHEMAS = {
    "get_record": GetRecordRequest,
    "search_records": SearchRecordsRequest,
    "create_record": CreateRecordRequest,
    "update_record": UpdateRecordRequest,
    "add_record_comment": AddRecordCommentRequest,
} 