"""
Parameter Validation Models

Node.jsラッパーへのパラメータバリデーション用Pydanticモデル
"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum


class LanguageCode(str, Enum):
    """言語コード"""
    JAPANESE = "ja"
    ENGLISH = "en"
    CHINESE = "zh"


class EntityType(str, Enum):
    """エンティティタイプ"""
    USER = "USER"
    GROUP = "GROUP"
    ORGANIZATION = "ORGANIZATION"


class IconType(str, Enum):
    """アイコンタイプ"""
    FILE = "FILE"
    PRESET = "PRESET"


class AppTheme(str, Enum):
    """アプリテーマ"""
    WHITE = "WHITE"
    CLIPBOARD = "CLIPBOARD"
    BINDER = "BINDER"
    PENCIL = "PENCIL"
    CLIPS = "CLIPS"


# 基本バリデーションモデル
class BaseKintoneRequest(BaseModel):
    """基本リクエストモデル"""
    domain: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    apiToken: Optional[str] = None

    @model_validator(mode='after')
    def validate_auth(self):
        """認証情報のバリデーション"""
        if not self.apiToken and (not self.username or not self.password):
            raise ValueError('APIトークンまたはユーザー名・パスワードが必要です')
        
        return self


# レコード操作関連
class GetRecordRequest(BaseKintoneRequest):
    """レコード取得リクエスト"""
    appId: Union[str, int] = Field(..., description="アプリID")
    recordId: Union[str, int] = Field(..., description="レコードID")

    @field_validator('appId', 'recordId')
    @classmethod
    def validate_positive_id(cls, v):
        """正の数値IDのバリデーション"""
        try:
            num_val = int(v)
            if num_val <= 0:
                raise ValueError("IDは正の数値である必要があります")
            return num_val
        except (ValueError, TypeError):
            raise ValueError("IDは数値である必要があります")


class GetRecordsRequest(BaseKintoneRequest):
    """レコード一覧取得リクエスト"""
    appId: Union[str, int] = Field(..., description="アプリID")
    query: Optional[str] = Field(None, description="クエリ文字列")
    fields: Optional[List[str]] = Field(None, description="取得フィールド")
    totalCount: Optional[bool] = Field(None, description="総件数取得フラグ")

    @field_validator('appId')
    @classmethod
    def validate_app_id(cls, v):
        """アプリIDのバリデーション"""
        try:
            num_val = int(v)
            if num_val <= 0:
                raise ValueError("アプリIDは正の数値である必要があります")
            return num_val
        except (ValueError, TypeError):
            raise ValueError("アプリIDは数値である必要があります")

    @field_validator('fields')
    @classmethod
    def validate_fields(cls, v):
        """フィールドリストのバリデーション"""
        if v is not None and len(v) == 0:
            return None
        return v


class CreateRecordRequest(BaseKintoneRequest):
    """レコード作成リクエスト"""
    appId: Union[str, int] = Field(..., description="アプリID")
    record: Dict[str, Any] = Field(..., description="レコードデータ")

    @field_validator('appId')
    @classmethod
    def validate_app_id(cls, v):
        try:
            num_val = int(v)
            if num_val <= 0:
                raise ValueError("アプリIDは正の数値である必要があります")
            return num_val
        except (ValueError, TypeError):
            raise ValueError("アプリIDは数値である必要があります")

    @field_validator('record')
    @classmethod
    def validate_record(cls, v):
        """レコードデータのバリデーション"""
        if not v or len(v) == 0:
            raise ValueError("レコードデータは空にできません")
        return v


class UpdateRecordRequest(BaseKintoneRequest):
    """レコード更新リクエスト"""
    appId: Union[str, int] = Field(..., description="アプリID")
    recordId: Union[str, int] = Field(..., description="レコードID")
    record: Dict[str, Any] = Field(..., description="更新データ")
    revision: Optional[Union[str, int]] = Field(None, description="リビジョン")

    @field_validator('appId', 'recordId')
    @classmethod
    def validate_positive_id(cls, v):
        try:
            num_val = int(v)
            if num_val <= 0:
                raise ValueError("IDは正の数値である必要があります")
            return num_val
        except (ValueError, TypeError):
            raise ValueError("IDは数値である必要があります")

    @field_validator('record')
    @classmethod
    def validate_record(cls, v):
        if not v or len(v) == 0:
            raise ValueError("更新データは空にできません")
        return v


class UpdateRecordByKeyRequest(BaseKintoneRequest):
    """キーによるレコード更新リクエスト"""
    appId: Union[str, int] = Field(..., description="アプリID")
    keyField: str = Field(..., min_length=1, description="キーフィールド")
    keyValue: Union[str, int] = Field(..., description="キー値")
    record: Dict[str, Any] = Field(..., description="更新データ")
    revision: Optional[Union[str, int]] = Field(None, description="リビジョン")

    @field_validator('appId')
    @classmethod
    def validate_app_id(cls, v):
        try:
            num_val = int(v)
            if num_val <= 0:
                raise ValueError("アプリIDは正の数値である必要があります")
            return num_val
        except (ValueError, TypeError):
            raise ValueError("アプリIDは数値である必要があります")

    @field_validator('record')
    @classmethod
    def validate_record(cls, v):
        if not v or len(v) == 0:
            raise ValueError("更新データは空にできません")
        return v


class MentionEntity(BaseModel):
    """メンション対象エンティティ"""
    code: str = Field(..., min_length=1, description="エンティティコード")
    type: EntityType = Field(..., description="エンティティタイプ")


class AddRecordCommentRequest(BaseKintoneRequest):
    """レコードコメント追加リクエスト"""
    appId: Union[str, int] = Field(..., description="アプリID")
    recordId: Union[str, int] = Field(..., description="レコードID")
    text: str = Field(..., min_length=1, description="コメントテキスト")
    mentions: Optional[List[MentionEntity]] = Field(None, description="メンション")

    @field_validator('appId', 'recordId')
    @classmethod
    def validate_positive_id(cls, v):
        try:
            num_val = int(v)
            if num_val <= 0:
                raise ValueError("IDは正の数値である必要があります")
            return num_val
        except (ValueError, TypeError):
            raise ValueError("IDは数値である必要があります")


# アプリ操作関連
class CreateAppRequest(BaseKintoneRequest):
    """アプリ作成リクエスト"""
    name: str = Field(..., min_length=1, max_length=64, description="アプリ名")
    space: Optional[Union[str, int]] = Field(None, description="スペースID")
    thread: Optional[Union[str, int]] = Field(None, description="スレッドID")


class AppDeployInfo(BaseModel):
    """アプリデプロイ情報"""
    app: Union[str, int] = Field(..., description="アプリID")
    revision: Optional[Union[str, int]] = Field(None, description="リビジョン")

    @field_validator('app')
    @classmethod
    def validate_app_id(cls, v):
        try:
            num_val = int(v)
            if num_val <= 0:
                raise ValueError("アプリIDは正の数値である必要があります")
            return num_val
        except (ValueError, TypeError):
            raise ValueError("アプリIDは数値である必要があります")


class DeployAppRequest(BaseKintoneRequest):
    """アプリデプロイリクエスト"""
    apps: List[AppDeployInfo] = Field(..., min_length=1, description="デプロイ対象アプリ")


class GetDeployStatusRequest(BaseKintoneRequest):
    """デプロイステータス取得リクエスト"""
    apps: List[Union[str, int]] = Field(..., min_length=1, description="アプリIDリスト")

    @field_validator('apps')
    @classmethod
    def validate_app_ids(cls, v):
        """アプリIDリストのバリデーション"""
        validated_ids = []
        for app_id in v:
            try:
                num_val = int(app_id)
                if num_val <= 0:
                    raise ValueError(f"アプリID {app_id} は正の数値である必要があります")
                validated_ids.append(num_val)
            except (ValueError, TypeError):
                raise ValueError(f"アプリID {app_id} は数値である必要があります")
        return validated_ids


class GetAppFormFieldsRequest(BaseKintoneRequest):
    """アプリフォームフィールド取得リクエスト"""
    appId: Union[str, int] = Field(..., description="アプリID")
    lang: Optional[LanguageCode] = Field(None, description="言語コード")

    @field_validator('appId')
    @classmethod
    def validate_app_id(cls, v):
        try:
            num_val = int(v)
            if num_val <= 0:
                raise ValueError("アプリIDは正の数値である必要があります")
            return num_val
        except (ValueError, TypeError):
            raise ValueError("アプリIDは数値である必要があります")


# アプリ設定関連
class AppIconFile(BaseModel):
    """アプリアイコンファイル"""
    fileKey: str = Field(..., min_length=1, description="ファイルキー")


class AppIcon(BaseModel):
    """アプリアイコン"""
    type: IconType = Field(..., description="アイコンタイプ")
    file: Optional[AppIconFile] = Field(None, description="ファイル情報")
    preset: Optional[str] = Field(None, description="プリセット名")

    @model_validator(mode='after')
    def validate_icon_config(self):
        """アイコン設定のバリデーション"""
        if self.type == IconType.FILE and not self.file:
            raise ValueError("ファイルタイプの場合、ファイル情報が必要です")
        elif self.type == IconType.PRESET and not self.preset:
            raise ValueError("プリセットタイプの場合、プリセット名が必要です")
        
        return self


class AppSettingsData(BaseModel):
    """アプリ設定データ"""
    name: Optional[str] = Field(None, min_length=1, max_length=64, description="アプリ名")
    description: Optional[str] = Field(None, max_length=10000, description="アプリ説明")
    icon: Optional[AppIcon] = Field(None, description="アプリアイコン")
    theme: Optional[AppTheme] = Field(None, description="アプリテーマ")

    @model_validator(mode='after')
    def validate_settings(self):
        """設定データのバリデーション"""
        if not any([self.name, self.description, self.icon, self.theme]):
            raise ValueError("少なくとも1つの設定項目が必要です")
        return self


class UpdateAppSettingsRequest(BaseKintoneRequest):
    """アプリ設定更新リクエスト"""
    appId: Union[str, int] = Field(..., description="アプリID")
    settings: AppSettingsData = Field(..., description="設定データ")
    revision: Optional[Union[str, int]] = Field(None, description="リビジョン")

    @field_validator('appId')
    @classmethod
    def validate_app_id(cls, v):
        try:
            num_val = int(v)
            if num_val <= 0:
                raise ValueError("アプリIDは正の数値である必要があります")
            return num_val
        except (ValueError, TypeError):
            raise ValueError("アプリIDは数値である必要があります")


# 権限設定関連
class PermissionEntity(BaseModel):
    """権限エンティティ"""
    type: EntityType = Field(..., description="エンティティタイプ")
    code: str = Field(..., min_length=1, description="エンティティコード")


class AppPermissionRight(BaseModel):
    """アプリ権限設定"""
    entity: PermissionEntity = Field(..., description="対象エンティティ")
    appEditable: bool = Field(..., description="アプリ編集権限")
    recordViewable: bool = Field(..., description="レコード閲覧権限")
    recordAddable: bool = Field(..., description="レコード追加権限")
    recordEditable: bool = Field(..., description="レコード編集権限")
    recordDeletable: bool = Field(..., description="レコード削除権限")
    recordImportable: bool = Field(..., description="レコードインポート権限")
    recordExportable: bool = Field(..., description="レコードエクスポート権限")


class UpdateAppAclRequest(BaseKintoneRequest):
    """アプリ権限更新リクエスト"""
    appId: Union[str, int] = Field(..., description="アプリID")
    rights: List[AppPermissionRight] = Field(..., min_length=1, description="権限設定")
    revision: Optional[Union[str, int]] = Field(None, description="リビジョン")

    @field_validator('appId')
    @classmethod
    def validate_app_id(cls, v):
        try:
            num_val = int(v)
            if num_val <= 0:
                raise ValueError("アプリIDは正の数値である必要があります")
            return num_val
        except (ValueError, TypeError):
            raise ValueError("アプリIDは数値である必要があります")


# ファイル操作関連
class FileUploadInfo(BaseModel):
    """ファイルアップロード情報"""
    fileName: str = Field(..., min_length=1, description="ファイル名")
    fileData: str = Field(..., min_length=1, description="ファイルデータ（Base64）")
    contentType: Optional[str] = Field(None, description="コンテンツタイプ")


class UploadFileRequest(BaseKintoneRequest):
    """ファイルアップロードリクエスト"""
    fileName: str = Field(..., min_length=1, description="ファイル名")
    fileData: str = Field(..., min_length=1, description="ファイルデータ（Base64）")
    contentType: Optional[str] = Field(None, description="コンテンツタイプ")


class UploadMultipleFilesRequest(BaseKintoneRequest):
    """複数ファイルアップロードリクエスト"""
    files: List[FileUploadInfo] = Field(
        ..., 
        min_length=1, 
        max_length=100, 
        description="アップロードファイル（最大100個）"
    )


class DownloadFileRequest(BaseKintoneRequest):
    """ファイルダウンロードリクエスト"""
    fileKey: str = Field(..., min_length=1, description="ファイルキー")


class GetFileInfoRequest(BaseKintoneRequest):
    """ファイル情報取得リクエスト"""
    fileKey: str = Field(..., min_length=1, description="ファイルキー")


class DeleteFileRequest(BaseKintoneRequest):
    """ファイル削除リクエスト"""
    fileKey: str = Field(..., min_length=1, description="ファイルキー")


# フィールド設定関連
class AddFormFieldsRequest(BaseKintoneRequest):
    """フォームフィールド追加リクエスト"""
    appId: Union[str, int] = Field(..., description="アプリID")
    properties: Dict[str, Any] = Field(..., description="フィールドプロパティ")
    revision: Optional[Union[str, int]] = Field(None, description="リビジョン")

    @field_validator('appId')
    @classmethod
    def validate_app_id(cls, v):
        try:
            num_val = int(v)
            if num_val <= 0:
                raise ValueError("アプリIDは正の数値である必要があります")
            return num_val
        except (ValueError, TypeError):
            raise ValueError("アプリIDは数値である必要があります")

    @field_validator('properties')
    @classmethod
    def validate_properties(cls, v):
        if not v or len(v) == 0:
            raise ValueError("フィールドプロパティは必須です")
        return v


class UpdateFormFieldsRequest(BaseKintoneRequest):
    """フォームフィールド更新リクエスト"""
    appId: Union[str, int] = Field(..., description="アプリID")
    properties: Dict[str, Any] = Field(..., description="フィールドプロパティ")
    revision: Optional[Union[str, int]] = Field(None, description="リビジョン")

    @field_validator('appId')
    @classmethod
    def validate_app_id(cls, v):
        try:
            num_val = int(v)
            if num_val <= 0:
                raise ValueError("アプリIDは正の数値である必要があります")
            return num_val
        except (ValueError, TypeError):
            raise ValueError("アプリIDは数値である必要があります")

    @field_validator('properties')
    @classmethod
    def validate_properties(cls, v):
        if not v or len(v) == 0:
            raise ValueError("フィールドプロパティは必須です")
        return v


class DeleteFormFieldsRequest(BaseKintoneRequest):
    """フォームフィールド削除リクエスト"""
    appId: Union[str, int] = Field(..., description="アプリID")
    fields: List[str] = Field(..., min_length=1, description="削除フィールド")
    revision: Optional[Union[str, int]] = Field(None, description="リビジョン")

    @field_validator('appId')
    @classmethod
    def validate_app_id(cls, v):
        try:
            num_val = int(v)
            if num_val <= 0:
                raise ValueError("アプリIDは正の数値である必要があります")
            return num_val
        except (ValueError, TypeError):
            raise ValueError("アプリIDは数値である必要があります")


# プロセス管理関連
class UpdateProcessManagementRequest(BaseKintoneRequest):
    """プロセス管理更新リクエスト"""
    appId: Union[str, int] = Field(..., description="アプリID")
    states: Dict[str, Any] = Field(..., description="ステータス設定")
    actions: List[Any] = Field(..., min_length=1, description="アクション設定")
    revision: Optional[Union[str, int]] = Field(None, description="リビジョン")

    @field_validator('appId')
    @classmethod
    def validate_app_id(cls, v):
        try:
            num_val = int(v)
            if num_val <= 0:
                raise ValueError("アプリIDは正の数値である必要があります")
            return num_val
        except (ValueError, TypeError):
            raise ValueError("アプリIDは数値である必要があります")

    @field_validator('states')
    @classmethod
    def validate_states(cls, v):
        if not v or len(v) == 0:
            raise ValueError("ステータス設定は必須です")
        return v 