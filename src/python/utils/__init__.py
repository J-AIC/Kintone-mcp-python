"""
Utilities Package

共通ユーティリティ関数
"""

from .layout_utils import (
    auto_correct_field_width,
    auto_correct_layout_widths,
    extract_fields_from_layout,
    validate_fields_in_layout,
    add_missing_fields_to_layout
)

__all__ = [
    'auto_correct_field_width',
    'auto_correct_layout_widths',
    'extract_fields_from_layout',
    'validate_fields_in_layout',
    'add_missing_fields_to_layout'
]

# utils package

from .exceptions import (
    KintoneBaseError,
    KintoneAPIError,
    KintoneAuthenticationError,
    KintonePermissionError,
    KintoneValidationError,
    NodeJSWrapperError,
    KintoneNetworkError,
    KintoneConfigurationError,
    parse_nodejs_error_response
)

from .error_handler import (
    ErrorHandler,
    handle_kintone_errors,
    validate_required_params,
    validate_param_types,
    MCPErrorResponse,
    MCPError,
    MCPErrorCode
)

__all__ = [
    # Exceptions
    'KintoneBaseError',
    'KintoneAPIError',
    'KintoneAuthenticationError',
    'KintonePermissionError',
    'KintoneValidationError',
    'NodeJSWrapperError',
    'KintoneNetworkError',
    'KintoneConfigurationError',
    'parse_nodejs_error_response',
    
    # Error Handler
    'ErrorHandler',
    'handle_kintone_errors',
    'validate_required_params',
    'validate_param_types',
    'MCPErrorResponse',
    
    # Legacy compatibility
    'MCPError',
    'MCPErrorCode',
] 