"""
Repository Layer Package

Kintone REST APIとの通信を担うリポジトリ層
"""

from .base import BaseKintoneRepository
# Note: KintoneAPIError is now imported from utils.exceptions
from ..utils.exceptions import KintoneAPIError  # Use the standard exception class
from .nodejs_kintone_client import NodeJSKintoneClient

# Node.js クライアントを既定のKintoneClientとしてエクスポート
KintoneClient = NodeJSKintoneClient
from .record_repository import KintoneRecordRepository
from .kintone_app_repository import KintoneAppRepository
from .file_repository import KintoneFileRepository
from .space_repository import SpaceRepository
from .user_repository import KintoneUserRepository
from .kintone_repository import KintoneRepository

__all__ = [
    "BaseKintoneRepository",
    "KintoneClient", 
    "KintoneAPIError",
    "KintoneRecordRepository",
    "KintoneAppRepository",
    "KintoneFileRepository",
    "SpaceRepository",
    "KintoneUserRepository",
    "KintoneRepository"
] 