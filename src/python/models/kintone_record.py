"""
Kintone Record Model

Kintoneレコードのデータ構造を定義するPydanticモデル
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class KintoneRecord(BaseModel):
    """
    Kintoneレコードモデル
    
    レコードのメタデータとフィールドデータを管理
    """
    
    app_id: int = Field(..., description="アプリID")
    record_id: Optional[int] = Field(None, description="レコードID（新規作成時はNone）")
    fields: Dict[str, Any] = Field(default_factory=dict, description="フィールドデータ")
    revision: Optional[int] = Field(None, description="リビジョン番号")
    
    def get_field_value(self, field_code: str) -> Any:
        """
        フィールドの値を取得
        
        Args:
            field_code: フィールドコード
            
        Returns:
            Any: フィールドの値、存在しない場合はNone
        """
        field_data = self.fields.get(field_code)
        if field_data and isinstance(field_data, dict):
            return field_data.get("value")
        return field_data
    
    def set_field_value(self, field_code: str, value: Any) -> None:
        """
        フィールドの値を設定
        
        Args:
            field_code: フィールドコード
            value: 設定する値
        """
        self.fields[field_code] = {"value": value}
    
    def get_system_field(self, field_name: str) -> Any:
        """
        システムフィールドの値を取得
        
        Args:
            field_name: システムフィールド名（$id, $revision, $creator, $created_time等）
            
        Returns:
            Any: システムフィールドの値
        """
        return self.get_field_value(field_name)
    
    @property
    def created_time(self) -> Optional[str]:
        """作成日時を取得"""
        return self.get_system_field("$created_time")
    
    @property
    def updated_time(self) -> Optional[str]:
        """更新日時を取得"""
        return self.get_system_field("$updated_time")
    
    @property
    def creator(self) -> Optional[Dict[str, Any]]:
        """作成者情報を取得"""
        return self.get_system_field("$creator")
    
    @property
    def modifier(self) -> Optional[Dict[str, Any]]:
        """更新者情報を取得"""
        return self.get_system_field("$modifier")
    
    def to_update_format(self) -> Dict[str, Any]:
        """
        更新用のフォーマットに変換
        
        Returns:
            Dict[str, Any]: 更新用のフィールドデータ
        """
        # システムフィールドを除外して更新用データを作成
        update_fields = {}
        for field_code, field_data in self.fields.items():
            if not field_code.startswith("$"):
                update_fields[field_code] = field_data
        return update_fields
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "app_id": 123,
                    "record_id": 456,
                    "fields": {
                        "title": {"value": "サンプルタイトル"},
                        "description": {"value": "サンプル説明"},
                        "$id": {"value": "456"},
                        "$revision": {"value": "1"}
                    }
                }
            ]
        }
    } 