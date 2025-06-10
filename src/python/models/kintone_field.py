"""
Kintoneフィールド関連のモデル定義

Kintoneの各種フィールドタイプとその設定を管理するPydanticモデル
"""

from typing import Optional, Union, List, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum


class FieldType(str, Enum):
    """フィールドタイプ"""
    # テキスト系
    SINGLE_LINE_TEXT = "SINGLE_LINE_TEXT"
    MULTI_LINE_TEXT = "MULTI_LINE_TEXT"
    RICH_TEXT = "RICH_TEXT"
    
    # 数値系
    NUMBER = "NUMBER"
    CALC = "CALC"
    
    # 選択系
    RADIO_BUTTON = "RADIO_BUTTON"
    DROP_DOWN = "DROP_DOWN"
    MULTI_SELECT = "MULTI_SELECT"
    CHECK_BOX = "CHECK_BOX"
    
    # 日時系
    DATE = "DATE"
    TIME = "TIME"
    DATETIME = "DATETIME"
    
    # ファイル・リンク系
    FILE = "FILE"
    LINK = "LINK"
    
    # ユーザー・組織系
    USER_SELECT = "USER_SELECT"
    ORGANIZATION_SELECT = "ORGANIZATION_SELECT"
    GROUP_SELECT = "GROUP_SELECT"
    
    # 関連レコード系
    REFERENCE_TABLE = "REFERENCE_TABLE"
    
    # テーブル
    SUBTABLE = "SUBTABLE"
    
    # システムフィールド
    RECORD_NUMBER = "RECORD_NUMBER"
    CREATOR = "CREATOR"
    CREATED_TIME = "CREATED_TIME"
    MODIFIER = "MODIFIER"
    UPDATED_TIME = "UPDATED_TIME"
    STATUS = "STATUS"
    STATUS_ASSIGNEE = "STATUS_ASSIGNEE"
    CATEGORY = "CATEGORY"
    
    # レイアウト要素
    LABEL = "LABEL"
    SPACER = "SPACER"
    HR = "HR"


class NumberFormat(str, Enum):
    """数値フィールドの表示形式"""
    NUMBER = "NUMBER"
    NUMBER_DIGIT = "NUMBER_DIGIT"


class UnitPosition(str, Enum):
    """単位記号の位置"""
    BEFORE = "BEFORE"
    AFTER = "AFTER"


class LinkProtocol(str, Enum):
    """リンクフィールドのプロトコル"""
    WEB = "WEB"
    CALL = "CALL"
    MAIL = "MAIL"


class UserSelectionType(str, Enum):
    """ユーザー選択フィールドの選択タイプ"""
    USER = "USER"
    GROUP = "GROUP"
    ORGANIZATION = "ORGANIZATION"


class DateDefaultValue(str, Enum):
    """日付フィールドの初期値"""
    TODAY = "TODAY"
    NONE = "NONE"


class TimeDefaultValue(str, Enum):
    """時刻フィールドの初期値"""
    NOW = "NOW"
    NONE = "NONE"


class ChoiceOption(BaseModel):
    """選択肢オプション"""
    label: str = Field(..., description="選択肢のラベル")
    value: str = Field(..., description="選択肢の値")


class NumberFieldConfig(BaseModel):
    """数値フィールドの設定"""
    min_value: Optional[str] = Field(None, alias="minValue", description="最小値")
    max_value: Optional[str] = Field(None, alias="maxValue", description="最大値")
    default_value: Optional[str] = Field(None, alias="defaultValue", description="初期値")
    unit: Optional[str] = Field(None, description="単位記号")
    unit_position: Optional[UnitPosition] = Field(None, alias="unitPosition", description="単位記号の位置")
    digit: Optional[bool] = Field(None, description="桁区切りを表示するか")
    format: Optional[NumberFormat] = Field(None, description="表示形式")
    display_scale: Optional[str] = Field(None, alias="displayScale", description="小数点以下の表示桁数")
    
    @field_validator('min_value', 'max_value', 'default_value')
    @classmethod
    def validate_numeric_string(cls, v: Optional[str]) -> Optional[str]:
        """数値文字列のバリデーション"""
        if v is not None:
            try:
                float(v)
            except ValueError:
                raise ValueError("数値として有効な文字列を指定してください")
        return v


class TextFieldConfig(BaseModel):
    """テキストフィールドの設定"""
    default_value: Optional[str] = Field(None, alias="defaultValue", description="初期値")
    max_length: Optional[int] = Field(None, alias="maxLength", description="最大文字数")
    min_length: Optional[int] = Field(None, alias="minLength", description="最小文字数")
    
    @field_validator('max_length', 'min_length')
    @classmethod
    def validate_length(cls, v: Optional[int]) -> Optional[int]:
        """文字数のバリデーション"""
        if v is not None and v < 0:
            raise ValueError("文字数は0以上で指定してください")
        return v


class ChoiceFieldConfig(BaseModel):
    """選択肢フィールドの設定"""
    options: List[ChoiceOption] = Field(..., description="選択肢の配列")
    default_value: Optional[Union[str, List[str]]] = Field(None, alias="defaultValue", description="初期値")
    
    @field_validator('options')
    @classmethod
    def validate_options(cls, v: List[ChoiceOption]) -> List[ChoiceOption]:
        """選択肢のバリデーション"""
        if not v:
            raise ValueError("選択肢を少なくとも1つ指定してください")
        
        # 重複チェック
        values = [option.value for option in v]
        if len(values) != len(set(values)):
            raise ValueError("選択肢の値に重複があります")
        
        return v


class DateFieldConfig(BaseModel):
    """日付フィールドの設定"""
    default_value: Optional[DateDefaultValue] = Field(None, alias="defaultValue", description="初期値")
    default_now_value: Optional[str] = Field(None, alias="defaultNowValue", description="具体的な初期値")
    unique: Optional[bool] = Field(None, description="値の重複を禁止するか")


class TimeFieldConfig(BaseModel):
    """時刻フィールドの設定"""
    default_value: Optional[TimeDefaultValue] = Field(None, alias="defaultValue", description="初期値")
    default_now_value: Optional[str] = Field(None, alias="defaultNowValue", description="具体的な初期値")


class DateTimeFieldConfig(BaseModel):
    """日時フィールドの設定"""
    default_value: Optional[str] = Field(None, alias="defaultValue", description="初期値")
    default_now_value: Optional[str] = Field(None, alias="defaultNowValue", description="具体的な初期値")
    unique: Optional[bool] = Field(None, description="値の重複を禁止するか")


class FileFieldConfig(BaseModel):
    """ファイルフィールドの設定"""
    thumbnail_size: Optional[str] = Field(None, alias="thumbnailSize", description="サムネイルサイズ")


class LinkFieldConfig(BaseModel):
    """リンクフィールドの設定"""
    default_value: Optional[str] = Field(None, alias="defaultValue", description="初期値")
    protocol: Optional[LinkProtocol] = Field(None, description="プロトコル")
    max_length: Optional[int] = Field(None, alias="maxLength", description="最大文字数")
    min_length: Optional[int] = Field(None, alias="minLength", description="最小文字数")


class UserSelectFieldConfig(BaseModel):
    """ユーザー選択フィールドの設定"""
    entities: List[Dict[str, Any]] = Field(..., description="選択可能なユーザー・グループ・組織の配列")
    default_value: Optional[List[Dict[str, Any]]] = Field(None, alias="defaultValue", description="初期値")


class CalcFieldConfig(BaseModel):
    """計算フィールドの設定"""
    expression: str = Field(..., description="計算式")
    digit: Optional[bool] = Field(None, description="桁区切りを表示するか")
    unit: Optional[str] = Field(None, description="単位記号")
    unit_position: Optional[UnitPosition] = Field(None, alias="unitPosition", description="単位記号の位置")
    format: Optional[NumberFormat] = Field(None, description="表示形式")
    display_scale: Optional[str] = Field(None, alias="displayScale", description="小数点以下の表示桁数")
    
    @field_validator('expression')
    @classmethod
    def validate_expression(cls, v: str) -> str:
        """計算式のバリデーション"""
        if not v:
            raise ValueError("計算式は必須です")
        return v


class LookupRelatedApp(BaseModel):
    """ルックアップの参照先アプリ情報"""
    app: Optional[str] = Field(None, description="参照先アプリID")
    code: Optional[str] = Field(None, description="参照先アプリコード")
    
    @model_validator(mode='after')
    def validate_app_reference(self):
        """アプリ参照のバリデーション"""
        if not self.app and not self.code:
            raise ValueError("参照先アプリのIDまたはコードが必要です")
        return self


class LookupFieldMapping(BaseModel):
    """ルックアップのフィールドマッピング"""
    field: str = Field(..., description="自アプリのフィールドコード")
    related_field: str = Field(..., alias="relatedField", description="参照先アプリのフィールドコード")


class LookupSort(BaseModel):
    """ルックアップのソート設定"""
    field: str = Field(..., description="ソート対象フィールド")
    order: Literal["asc", "desc"] = Field(..., description="ソート順")


class LookupConfig(BaseModel):
    """ルックアップフィールドの設定"""
    related_app: LookupRelatedApp = Field(..., alias="relatedApp", description="参照先アプリ")
    related_key_field: str = Field(..., alias="relatedKeyField", description="参照先アプリのキーフィールド")
    field_mappings: List[LookupFieldMapping] = Field(..., alias="fieldMappings", description="フィールドマッピング")
    lookup_picker_fields: Optional[List[str]] = Field(None, alias="lookupPickerFields", description="ルックアップピッカーに表示するフィールド")
    filter_cond: Optional[str] = Field(None, alias="filterCond", description="絞り込み条件")
    sort: Optional[LookupSort] = Field(None, description="ソート条件")
    
    @field_validator('field_mappings')
    @classmethod
    def validate_field_mappings(cls, v: List[LookupFieldMapping]) -> List[LookupFieldMapping]:
        """フィールドマッピングのバリデーション"""
        if not v:
            raise ValueError("フィールドマッピングを少なくとも1つ指定してください")
        return v


class ReferenceTableConfig(BaseModel):
    """関連レコード一覧フィールドの設定"""
    related_app: LookupRelatedApp = Field(..., alias="relatedApp", description="参照先アプリ")
    condition_field: str = Field(..., alias="conditionField", description="自アプリの条件フィールド")
    related_condition_field: str = Field(..., alias="relatedConditionField", description="参照先アプリの条件フィールド")
    display_fields: List[str] = Field(..., alias="displayFields", description="表示するフィールドの配列")
    filter_cond: Optional[str] = Field(None, alias="filterCond", description="絞り込み条件")
    sort: Optional[str] = Field(None, description="ソート条件")
    size: Optional[int] = Field(None, description="一度に表示する最大レコード数")
    
    @field_validator('display_fields')
    @classmethod
    def validate_display_fields(cls, v: List[str]) -> List[str]:
        """表示フィールドのバリデーション"""
        if not v:
            raise ValueError("表示フィールドを少なくとも1つ指定してください")
        return v
    
    @field_validator('size')
    @classmethod
    def validate_size(cls, v: Optional[int]) -> Optional[int]:
        """サイズのバリデーション"""
        if v is not None:
            allowed_sizes = [1, 3, 5, 10, 20, 30, 40, 50]
            if v not in allowed_sizes:
                raise ValueError(f"サイズは {allowed_sizes} のいずれかを指定してください")
        return v


class SubtableField(BaseModel):
    """テーブル内のフィールド定義"""
    type: FieldType = Field(..., description="フィールドタイプ")
    code: str = Field(..., description="フィールドコード")
    label: str = Field(..., description="フィールドラベル")
    no_label: Optional[bool] = Field(None, alias="noLabel", description="ラベルを表示しない")
    required: Optional[bool] = Field(None, description="必須フィールド")
    
    # 各フィールドタイプ固有の設定
    number_config: Optional[NumberFieldConfig] = Field(None, alias="numberConfig", description="数値フィールド設定")
    text_config: Optional[TextFieldConfig] = Field(None, alias="textConfig", description="テキストフィールド設定")
    choice_config: Optional[ChoiceFieldConfig] = Field(None, alias="choiceConfig", description="選択肢フィールド設定")
    date_config: Optional[DateFieldConfig] = Field(None, alias="dateConfig", description="日付フィールド設定")
    time_config: Optional[TimeFieldConfig] = Field(None, alias="timeConfig", description="時刻フィールド設定")
    datetime_config: Optional[DateTimeFieldConfig] = Field(None, alias="datetimeConfig", description="日時フィールド設定")
    file_config: Optional[FileFieldConfig] = Field(None, alias="fileConfig", description="ファイルフィールド設定")
    link_config: Optional[LinkFieldConfig] = Field(None, alias="linkConfig", description="リンクフィールド設定")
    user_select_config: Optional[UserSelectFieldConfig] = Field(None, alias="userSelectConfig", description="ユーザー選択フィールド設定")
    calc_config: Optional[CalcFieldConfig] = Field(None, alias="calcConfig", description="計算フィールド設定")


class SubtableConfig(BaseModel):
    """テーブルフィールドの設定"""
    fields: List[SubtableField] = Field(..., description="テーブル内のフィールド定義")
    
    @field_validator('fields')
    @classmethod
    def validate_fields(cls, v: List[SubtableField]) -> List[SubtableField]:
        """テーブル内フィールドのバリデーション"""
        if not v:
            raise ValueError("テーブル内にフィールドを少なくとも1つ定義してください")
        
        # フィールドコードの重複チェック
        codes = [field.code for field in v]
        if len(codes) != len(set(codes)):
            raise ValueError("テーブル内のフィールドコードに重複があります")
        
        return v


class KintoneField(BaseModel):
    """Kintoneフィールドの統合モデル"""
    type: FieldType = Field(..., description="フィールドタイプ")
    code: str = Field(..., description="フィールドコード")
    label: str = Field(..., description="フィールドラベル")
    no_label: Optional[bool] = Field(None, alias="noLabel", description="ラベルを表示しない")
    required: Optional[bool] = Field(None, description="必須フィールド")
    
    # 各フィールドタイプ固有の設定
    number_config: Optional[NumberFieldConfig] = Field(None, alias="numberConfig", description="数値フィールド設定")
    text_config: Optional[TextFieldConfig] = Field(None, alias="textConfig", description="テキストフィールド設定")
    choice_config: Optional[ChoiceFieldConfig] = Field(None, alias="choiceConfig", description="選択肢フィールド設定")
    date_config: Optional[DateFieldConfig] = Field(None, alias="dateConfig", description="日付フィールド設定")
    time_config: Optional[TimeFieldConfig] = Field(None, alias="timeConfig", description="時刻フィールド設定")
    datetime_config: Optional[DateTimeFieldConfig] = Field(None, alias="datetimeConfig", description="日時フィールド設定")
    file_config: Optional[FileFieldConfig] = Field(None, alias="fileConfig", description="ファイルフィールド設定")
    link_config: Optional[LinkFieldConfig] = Field(None, alias="linkConfig", description="リンクフィールド設定")
    user_select_config: Optional[UserSelectFieldConfig] = Field(None, alias="userSelectConfig", description="ユーザー選択フィールド設定")
    calc_config: Optional[CalcFieldConfig] = Field(None, alias="calcConfig", description="計算フィールド設定")
    lookup_config: Optional[LookupConfig] = Field(None, alias="lookupConfig", description="ルックアップフィールド設定")
    reference_table_config: Optional[ReferenceTableConfig] = Field(None, alias="referenceTableConfig", description="関連レコード一覧フィールド設定")
    subtable_config: Optional[SubtableConfig] = Field(None, alias="subtableConfig", description="テーブルフィールド設定")
    
    @field_validator('code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        """フィールドコードのバリデーション"""
        if not v:
            raise ValueError("フィールドコードは必須です")
        # 基本的な文字チェック（英数字とアンダースコア）
        import re
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', v):
            raise ValueError("フィールドコードは英字で始まり、英数字とアンダースコアのみ使用可能です")
        return v
    
    @field_validator('label')
    @classmethod
    def validate_label(cls, v: str) -> str:
        """フィールドラベルのバリデーション"""
        if not v:
            raise ValueError("フィールドラベルは必須です")
        return v
    
    @property
    def is_lookup_field(self) -> bool:
        """ルックアップフィールドかどうかを判定"""
        return self.lookup_config is not None
    
    @property
    def is_system_field(self) -> bool:
        """システムフィールドかどうかを判定"""
        system_field_types = {
            FieldType.RECORD_NUMBER,
            FieldType.CREATOR,
            FieldType.CREATED_TIME,
            FieldType.MODIFIER,
            FieldType.UPDATED_TIME,
            FieldType.STATUS,
            FieldType.STATUS_ASSIGNEE,
            FieldType.CATEGORY
        }
        return self.type in system_field_types
    
    @property
    def is_layout_element(self) -> bool:
        """レイアウト要素かどうかを判定"""
        layout_element_types = {
            FieldType.LABEL,
            FieldType.SPACER,
            FieldType.HR
        }
        return self.type in layout_element_types


class FieldCreationRequest(BaseModel):
    """フィールド作成リクエスト"""
    app_id: int = Field(..., alias="appId", description="アプリID")
    properties: Dict[str, KintoneField] = Field(..., description="フィールドプロパティの辞書")
    
    @field_validator('properties')
    @classmethod
    def validate_properties(cls, v: Dict[str, KintoneField]) -> Dict[str, KintoneField]:
        """フィールドプロパティのバリデーション"""
        if not v:
            raise ValueError("フィールドプロパティを少なくとも1つ指定してください")
        
        # フィールドコードとキーの一致チェック
        for key, field in v.items():
            if key != field.code:
                raise ValueError(f"キー '{key}' とフィールドコード '{field.code}' が一致しません")
        
        return v


class FieldUpdateRequest(BaseModel):
    """フィールド更新リクエスト"""
    app_id: int = Field(..., alias="appId", description="アプリID")
    properties: Dict[str, KintoneField] = Field(..., description="更新するフィールドプロパティの辞書")
    revision: Optional[int] = Field(None, description="リビジョン番号")


class FieldDeleteRequest(BaseModel):
    """フィールド削除リクエスト"""
    app_id: int = Field(..., alias="appId", description="アプリID")
    fields: List[str] = Field(..., description="削除するフィールドコードの配列")
    revision: Optional[int] = Field(None, description="リビジョン番号")
    
    @field_validator('fields')
    @classmethod
    def validate_fields(cls, v: List[str]) -> List[str]:
        """削除フィールドのバリデーション"""
        if not v:
            raise ValueError("削除するフィールドを少なくとも1つ指定してください")
        if len(v) != len(set(v)):
            raise ValueError("重複するフィールドコードが含まれています")
        return v 