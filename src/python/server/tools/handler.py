"""
Tool Handler - 全てのツール実装を統合するハンドラー
"""

from .implementations.app_tools import handle_app_tools
from .implementations.record_tools import handle_record_tools
from .implementations.field_tools import handle_field_tools
from .implementations.layout_tools import handle_layout_tools
from .implementations.file_tools import handle_file_tools
from .implementations.user_tools import handle_user_tools
from .implementations.space_tools import handle_space_tools
from .implementations.system_tools import handle_system_tools
from .implementations.documentation_tools import handle_documentation_tools
from .implementations.logging_tools import handle_logging_tools

from ....repositories.kintone_app_repository import KintoneAppRepository
from ....repositories.record_repository import KintoneRecordRepository
from ....repositories.user_repository import KintoneUserRepository
from ....repositories.file_repository import KintoneFileRepository
from ....repositories.space_repository import SpaceRepository
from ....repositories import KintoneClient


class ToolHandler:
    """全てのツール実装を統合するハンドラー"""
    
    def __init__(self, credentials):
        self.credentials = credentials
        
        # システムツール用のKintoneClient
        self.kintone_client = KintoneClient(credentials)
        
        # 各リポジトリを初期化
        self.app_repository = KintoneAppRepository(credentials)
        self.record_repository = KintoneRecordRepository(credentials)
        self.user_repository = KintoneUserRepository(credentials)
        self.file_repository = KintoneFileRepository(credentials)
        self.space_repository = SpaceRepository(credentials)
        
        # ツール名とカテゴリのマッピング
        self.tool_category_mapping = {
            # App Tools
            "get_process_management": "app",
            "get_apps_info": "app",
            "create_app": "app", 
            "deploy_app": "app",
            "get_deploy_status": "app",
            "update_app_settings": "app",
            "get_form_layout": "layout",
            "update_form_layout": "layout",
            "move_app_to_space": "app",
            "move_app_from_space": "app",
            "get_preview_app_settings": "app",
            "get_preview_form_fields": "app",
            "get_preview_form_layout": "app",
            "get_app_actions": "app",
            "get_app_plugins": "app",
            
            # Record Tools
            "search_records": "record",
            "get_record": "record",
            "create_record": "record",
            "update_record": "record",
            "delete_record": "record",
            "get_record_comments": "record",
            "add_record_comment": "record",
            "delete_record_comment": "record",
            "update_record_assignees": "record",
            "update_record_status": "record",
            
            # Field Tools
            "add_fields": "field",
            "update_fields": "field",
            "delete_fields": "field",
            "get_form_fields": "field",
            "create_lookup_field": "field",
            
            # Layout Tools
            "get_form_layout": "layout",
            "update_form_layout": "layout",
            "create_layout_element": "layout",
            "add_fields_to_layout": "layout",
            "remove_fields_from_layout": "layout",
            
            # File Tools
            "upload_file": "file",
            "download_file": "file",
            
            # User Tools
            "get_users": "user",
            "get_groups": "user",
            "get_user_organizations": "user",
            "get_organization_users": "user",
            
            # Space Tools
            "get_space": "space",
            "update_space": "space",
            "get_space_members": "space",
            "update_space_members": "space",
            "get_space_thread": "space",
            "update_space_thread": "space",
            
            # System Tools
            "get_kintone_domain": "system",
            "get_kintone_username": "system",
            
            # Documentation Tools
            "get_field_type_documentation": "documentation",
            "get_available_field_types": "documentation",
            "get_documentation_tool_description": "documentation",
            "get_field_creation_tool_description": "documentation",
            "get_group_element_structure": "documentation",
            
            # Logging Tools
            "get_recent_logs": "logging",
            "clear_logs": "logging",
            "logging_set_level": "logging",
            "logging_get_level": "logging",
            "logging_send_message": "logging",
            "get_log_stats": "logging",
        }
    
    async def handle_tool_call(self, tool_name: str, arguments: dict):
        """ツール呼び出しを処理"""
        if tool_name not in self.tool_category_mapping:
            raise Exception(f"Unknown tool: {tool_name}")
        
        category = self.tool_category_mapping[tool_name]
        
        # カテゴリに応じて適切なハンドラーを呼び出し
        if category == "app":
            return await handle_app_tools(tool_name, arguments, self.app_repository)
        elif category == "record":
            return await handle_record_tools(tool_name, arguments, self.record_repository)
        elif category == "field":
            return await handle_field_tools(tool_name, arguments, self.app_repository)
        elif category == "layout":
            return await handle_layout_tools(tool_name, arguments, self.app_repository)
        elif category == "file":
            return await handle_file_tools(tool_name, arguments, self.file_repository)
        elif category == "user":
            return await handle_user_tools(tool_name, arguments, self.user_repository)
        elif category == "space":
            return await handle_space_tools(tool_name, arguments, self.space_repository)
        elif category == "system":
            return await handle_system_tools(tool_name, arguments, self.kintone_client)
        elif category == "documentation":
            return await handle_documentation_tools(tool_name, arguments, None)
        elif category == "logging":
            return await handle_logging_tools(tool_name, arguments, None)
        else:
            raise Exception(f"Unknown tool category: {category}") 