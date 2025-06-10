"""
Kintoneアプリ関連のモデル定義

Kintoneアプリの設定、フィールド、レイアウトなどを管理するPydanticモデル
"""

from typing import Optional, Union, List, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum


class AppTheme(str, Enum):
    """アプリのデザインテーマ"""
    WHITE = "WHITE"
    RED = "RED"
    GREEN = "GREEN"
    BLUE = "BLUE"
    YELLOW = "YELLOW"
    BLACK = "BLACK"


class IconType(str, Enum):
    """アイコンの種類"""
    PRESET = "PRESET"
    FILE = "FILE"


class TitleFieldSelectionMode(str, Enum):
    """タイトルフィールドの選択方法"""
    AUTO = "AUTO"
    MANUAL = "MANUAL"


class RoundingMode(str, Enum):
    """数値の丸めかた"""
    HALF_EVEN = "HALF_EVEN"
    UP = "UP"
    DOWN = "DOWN"


class LayoutElementType(str, Enum):
    """レイアウト要素のタイプ"""
    ROW = "ROW"
    SUBTABLE = "SUBTABLE"
    GROUP = "GROUP"
    LABEL = "LABEL"
    SPACER = "SPACER"
    HR = "HR"
    REFERENCE_TABLE = "REFERENCE_TABLE"


class AppIconFile(BaseModel):
    """アプリアイコンのファイル情報"""
    file_key: str = Field(..., alias="fileKey", description="アップロード済みファイルのキー")


class AppIcon(BaseModel):
    """アプリアイコン設定"""
    type: IconType = Field(..., description="アイコンの種類")
    key: Optional[str] = Field(None, description="PRESTETアイコンの識別子")
    file: Optional[AppIconFile] = Field(None, description="ファイルアイコンの情報")
    
    @model_validator(mode='after')
    def validate_icon_settings(self):
        """アイコン設定のバリデーション"""
        if self.type == IconType.PRESET and not self.key:
            raise ValueError("PRESTETアイコンの場合、keyが必要です")
        if self.type == IconType.FILE and not self.file:
            raise ValueError("FILEアイコンの場合、fileが必要です")
        return self


class TitleField(BaseModel):
    """タイトルフィールド設定"""
    selection_mode: TitleFieldSelectionMode = Field(..., alias="selectionMode", description="タイトルフィールドの選択方法")
    code: Optional[str] = Field(None, description="MANUALモード時のフィールドコード")
    
    @model_validator(mode='after')
    def validate_title_field(self):
        """タイトルフィールド設定のバリデーション"""
        if self.selection_mode == TitleFieldSelectionMode.MANUAL and not self.code:
            raise ValueError("MANUALモード時はフィールドコードが必要です")
        return self


class NumberPrecision(BaseModel):
    """数値精度設定"""
    digits: str = Field(..., description="全体の桁数（1-30）")
    decimal_places: str = Field(..., alias="decimalPlaces", description="小数部の桁数（0-10）")
    rounding_mode: RoundingMode = Field(..., alias="roundingMode", description="数値の丸めかた")
    
    @field_validator('digits')
    @classmethod
    def validate_digits(cls, v: str) -> str:
        """全体桁数のバリデーション"""
        try:
            digits = int(v)
            if not (1 <= digits <= 30):
                raise ValueError("全体の桁数は1-30の範囲で指定してください")
        except ValueError:
            raise ValueError("全体の桁数は数値で指定してください")
        return v
    
    @field_validator('decimal_places')
    @classmethod
    def validate_decimal_places(cls, v: str) -> str:
        """小数部桁数のバリデーション"""
        try:
            decimal_places = int(v)
            if not (0 <= decimal_places <= 10):
                raise ValueError("小数部の桁数は0-10の範囲で指定してください")
        except ValueError:
            raise ValueError("小数部の桁数は数値で指定してください")
        return v


class FieldSize(BaseModel):
    """フィールドのサイズ設定"""
    width: Optional[str] = Field(None, description="幅（数値のみ指定可能、例：100）")
    height: Optional[str] = Field(None, description="高さ（数値のみ指定可能、例：200）")
    inner_height: Optional[str] = Field(None, alias="innerHeight", description="内部高さ（数値のみ指定可能、例：200）")
    
    @field_validator('width', 'height', 'inner_height')
    @classmethod
    def validate_size_value(cls, v: Optional[str]) -> Optional[str]:
        """サイズ値のバリデーション"""
        if v is not None:
            try:
                size_value = int(v)
                if size_value < 0:
                    raise ValueError("サイズは0以上の数値で指定してください")
            except ValueError:
                raise ValueError("サイズは数値のみで指定してください（単位は不要）")
        return v


class LayoutField(BaseModel):
    """レイアウト内のフィールド要素"""
    type: Optional[str] = Field(None, description="フィールド要素のタイプ")
    code: Optional[str] = Field(None, description="フィールドコード")
    size: Optional[FieldSize] = Field(None, description="フィールドのサイズ")
    element_id: Optional[str] = Field(None, alias="elementId", description="要素のID")
    value: Optional[str] = Field(None, description="LABELタイプの場合のラベルテキスト")


class LayoutElement(BaseModel):
    """レイアウト要素"""
    type: LayoutElementType = Field(..., description="レイアウト要素のタイプ")
    fields: Optional[List[LayoutField]] = Field(None, description="ROWタイプの場合のフィールド配列")
    code: Optional[str] = Field(None, description="フィールドコード（SUBTABLEやGROUPの場合）")
    layout: Optional[List["LayoutElement"]] = Field(None, description="GROUPタイプの場合の内部レイアウト")
    label: Optional[str] = Field(None, description="GROUPタイプの場合のラベル")
    open_group: Optional[bool] = Field(None, alias="openGroup", description="グループを開いた状態で表示するか")
    
    @model_validator(mode='after')
    def validate_layout_element(self):
        """レイアウト要素のバリデーション"""
        if self.type == LayoutElementType.ROW and not self.fields:
            raise ValueError("ROWタイプの場合、fieldsが必要です")
        if self.type == LayoutElementType.GROUP and not self.code:
            raise ValueError("GROUPタイプの場合、codeが必要です")
        if self.type == LayoutElementType.SUBTABLE and not self.code:
            raise ValueError("SUBTABLEタイプの場合、codeが必要です")
        return self


# 前方参照の解決
LayoutElement.model_rebuild()


class FormLayout(BaseModel):
    """フォームレイアウト"""
    layout: List[LayoutElement] = Field(..., description="レイアウト要素の配列")
    revision: Optional[int] = Field(None, description="リビジョン番号")


class AppSettings(BaseModel):
    """Kintoneアプリの設定"""
    app_id: int = Field(..., alias="appId", description="アプリID")
    name: Optional[str] = Field(None, description="アプリの名前（1文字以上64文字以内）")
    description: Optional[str] = Field(None, description="アプリの説明（10,000文字以内、HTMLタグ使用可）")
    icon: Optional[AppIcon] = Field(None, description="アプリアイコン設定")
    theme: Optional[AppTheme] = Field(None, description="デザインテーマ")
    title_field: Optional[TitleField] = Field(None, alias="titleField", description="タイトルフィールド設定")
    enable_thumbnails: Optional[bool] = Field(None, alias="enableThumbnails", description="サムネイル表示の有効化")
    enable_bulk_deletion: Optional[bool] = Field(None, alias="enableBulkDeletion", description="レコード一括削除の有効化")
    enable_comments: Optional[bool] = Field(None, alias="enableComments", description="コメント機能の有効化")
    enable_duplicate_record: Optional[bool] = Field(None, alias="enableDuplicateRecord", description="レコード再利用機能の有効化")
    enable_inline_record_editing: Optional[bool] = Field(None, alias="enableInlineRecordEditing", description="インライン編集の有効化")
    number_precision: Optional[NumberPrecision] = Field(None, alias="numberPrecision", description="数値精度設定")
    first_month_of_fiscal_year: Optional[str] = Field(None, alias="firstMonthOfFiscalYear", description="第一四半期の開始月（1-12）")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """アプリ名のバリデーション"""
        if v is not None and (len(v) < 1 or len(v) > 64):
            raise ValueError("アプリ名は1文字以上64文字以内で指定してください")
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """アプリ説明のバリデーション"""
        if v is not None and len(v) > 10000:
            raise ValueError("アプリの説明は10,000文字以内で指定してください")
        return v
    
    @field_validator('first_month_of_fiscal_year')
    @classmethod
    def validate_fiscal_year_month(cls, v: Optional[str]) -> Optional[str]:
        """会計年度開始月のバリデーション"""
        if v is not None:
            try:
                month = int(v)
                if not (1 <= month <= 12):
                    raise ValueError("第一四半期の開始月は1-12の範囲で指定してください")
            except ValueError:
                raise ValueError("第一四半期の開始月は数値で指定してください")
        return v


class AppInfo(BaseModel):
    """アプリ情報"""
    app_id: str = Field(..., alias="appId", description="アプリID")
    code: str = Field(..., description="アプリコード")
    name: str = Field(..., description="アプリ名")
    description: str = Field(..., description="アプリの説明")
    space_id: Optional[str] = Field(None, alias="spaceId", description="スペースID")
    thread_id: Optional[str] = Field(None, alias="threadId", description="スレッドID")
    created_at: str = Field(..., alias="createdAt", description="作成日時")
    creator: Dict[str, Any] = Field(..., description="作成者情報")
    modified_at: str = Field(..., alias="modifiedAt", description="更新日時")
    modifier: Dict[str, Any] = Field(..., description="更新者情報")


class AppCreationRequest(BaseModel):
    """アプリ作成リクエスト"""
    name: str = Field(..., description="アプリの名前")
    space: Optional[int] = Field(None, description="スペースID（オプション）")
    thread: Optional[int] = Field(None, description="スレッドID（オプション）")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """アプリ名のバリデーション"""
        if not v or len(v.strip()) == 0:
            raise ValueError("アプリ名は必須です")
        if len(v) > 64:
            raise ValueError("アプリ名は64文字以内で指定してください")
        return v.strip()


class AppDeployRequest(BaseModel):
    """アプリデプロイリクエスト"""
    apps: List[int] = Field(..., description="デプロイ対象のアプリID配列")
    
    @field_validator('apps')
    @classmethod
    def validate_apps(cls, v: List[int]) -> List[int]:
        """アプリIDリストのバリデーション"""
        if not v:
            raise ValueError("デプロイ対象のアプリIDを少なくとも1つ指定してください")
        if len(v) != len(set(v)):
            raise ValueError("重複するアプリIDが含まれています")
        return v


class DeployStatus(BaseModel):
    """デプロイ状態"""
    app: str = Field(..., description="アプリID")
    status: str = Field(..., description="デプロイ状態")


class FieldProperty(BaseModel):
    """フィールドプロパティの基底クラス"""
    type: str = Field(..., description="フィールドタイプ")
    code: str = Field(..., description="フィールドコード")
    label: str = Field(..., description="フィールドラベル")
    no_label: Optional[bool] = Field(None, alias="noLabel", description="ラベルを表示しない")
    required: Optional[bool] = Field(None, description="必須フィールド")
    
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


class FieldProperties(BaseModel):
    """フィールドプロパティのコレクション"""
    properties: Dict[str, FieldProperty] = Field(..., description="フィールドプロパティの辞書")
    revision: Optional[str] = Field(None, description="リビジョン番号")


class AppMoveRequest(BaseModel):
    """アプリ移動リクエスト"""
    app_id: int = Field(..., alias="appId", description="移動対象のアプリID")
    space_id: Optional[Union[str, int]] = Field(None, alias="spaceId", description="移動先のスペースID")
    
    @field_validator('app_id')
    @classmethod
    def validate_app_id(cls, v: int) -> int:
        """アプリIDのバリデーション"""
        if v <= 0:
            raise ValueError("アプリIDは正の整数で指定してください")
        return v 