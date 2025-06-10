"""
Tool Definitions

すべてのツール定義を統合
"""

from .app_tool_definitions import APP_TOOL_DEFINITIONS
from .field_tool_definitions import FIELD_TOOL_DEFINITIONS
from .layout_tool_definitions import LAYOUT_TOOL_DEFINITIONS
from .file_tools_definitions import FILE_TOOLS_DEFINITIONS
from .record_tools_definitions import get_record_tools_definitions
from .user_tools_definitions import USER_TOOLS_DEFINITIONS
from .documentation_tools_definitions import get_documentation_tools_definitions
from .logging_tools_definitions import LOGGING_TOOL_DEFINITIONS

# すべてのツール定義を統合
ALL_TOOL_DEFINITIONS = [
    *APP_TOOL_DEFINITIONS,
    *FIELD_TOOL_DEFINITIONS,
    *LAYOUT_TOOL_DEFINITIONS,
    *FILE_TOOLS_DEFINITIONS,
    *get_record_tools_definitions(),
    *USER_TOOLS_DEFINITIONS,
    *get_documentation_tools_definitions(),
    *LOGGING_TOOL_DEFINITIONS,
]

__all__ = [
    "APP_TOOL_DEFINITIONS",
    "FIELD_TOOL_DEFINITIONS",
    "LAYOUT_TOOL_DEFINITIONS",
    "FILE_TOOLS_DEFINITIONS",
    "get_record_tools_definitions",
    "USER_TOOLS_DEFINITIONS",
    "get_documentation_tools_definitions",
    "LOGGING_TOOL_DEFINITIONS",
    "ALL_TOOL_DEFINITIONS"
]
