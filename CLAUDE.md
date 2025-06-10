# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Kintone MCP Server** that provides 47 specialized tools for Kintone (Japanese business application platform) integration through Claude Desktop. The project uses a hybrid Python + Node.js architecture where Python handles MCP protocol communication and Node.js executes Kintone API calls using the official `@kintone/rest-api-client`.

## Development Commands

### Setup and Installation
```bash
# Python dependencies
cd src/python
pip install -r requirements.txt

# Node.js dependencies
cd src/nodejs
npm install

# Environment setup
cp .env.example .env
# Edit .env with Kintone credentials
```

### Running the Server
```bash
# Primary entry point (hybrid clean version)
python src/python/main.py

# Alternative FastAPI-based server
python src/python/mcp_main.py

# Development testing
python tests/integration/test_mcp_client.py
```

### Development Tools
```bash
# Code quality
cd src/python
mypy .
flake8 .
black .
isort .

# Debug tools
python tools/debug/count_tools.py        # Count available tools (should show 47)
python tools/debug/check_tool_duplicates.py  # Check for duplicate tools
```

### Testing
```bash
# Integration tests
python tests/integration/test_complete_nodejs_migration.py
python tests/integration/test_mcp_client.py

# Python test framework
pytest tests/
```

## Architecture

### Hybrid Design Pattern
```
Claude Desktop → Python MCP Server → Node.js Wrapper → Kintone API
```

### Core Components
- **Python MCP Server** (`src/python/`): Handles MCP protocol, tool definitions, validation
- **Node.js API Wrapper** (`src/nodejs/wrapper.mjs`): Executes actual Kintone API calls
- **Tool System**: 47 tools organized by category (records, apps, fields, layout, files, users)

### Key Entry Points
- `src/python/main.py`: Primary production server (hybrid clean version)
- `src/python/mcp_main.py`: FastAPI-based alternative with HTTP/SSE support
- `src/nodejs/wrapper.mjs`: Node.js API wrapper using @kintone/rest-api-client

### Tool Categories
- **Records**: search_records, get_record, create_record, update_record, add_record_comment
- **Apps**: get_apps_info, create_app, deploy_app, get_deploy_status, update_app_settings (+ 8 more)
- **Fields**: add_fields, update_fields, delete_fields, get_form_fields, create_lookup_field
- **Layout**: get_form_layout, update_form_layout, create_layout_element (+ 9 more)
- **Files**: upload_file, download_file
- **Users**: get_users, get_groups, get_group_users, add_guests
- **System**: Documentation and logging tools

## Configuration

### Environment Variables
Required in `src/python/.env`:
```env
# Option 1: Username/Password
KINTONE_DOMAIN=your-domain.cybozu.com
KINTONE_USERNAME=your-username
KINTONE_PASSWORD=your-password

# Option 2: API Token
KINTONE_DOMAIN=your-domain.cybozu.com
KINTONE_API_TOKEN=your-api-token
```

### Claude Desktop Integration
Use configuration files in `config/claude-desktop/`:
- `recommended.json`: Production configuration
- `debug.json`: Development configuration with logging

## Code Patterns

### Repository Pattern
All data access follows repository pattern in `src/python/repositories/`:
- Inherit from `base.py` for consistent error handling
- Use Node.js wrapper for all API calls via `nodejs_wrapper_interface.py`

### Tool Implementation
1. **Definition**: Define in `src/python/server/tools/definitions/`
2. **Implementation**: Implement in `src/python/server/tools/implementations/`
3. **Validation**: Use Pydantic models in `src/python/models/`

### Error Handling
- All tools return consistent error responses through base repository
- Character encoding issues (mojibake) are handled automatically
- Comprehensive logging via structlog

## Important Notes

### Node.js Migration
- **ALL 47 tools execute via Node.js wrapper** - do not create direct Python API calls
- Use `nodejs_wrapper_interface.py` for all Kintone API interactions
- Maintain consistency with existing tool patterns

### Japanese Text Handling
- The system includes comprehensive mojibake (character corruption) fixes
- Character encoding normalization is handled automatically
- Test with Japanese text when making changes

### Tool Development
- Always implement both tool definition and implementation
- Follow existing patterns for parameter validation
- Use structured logging for debugging
- Maintain the 47-tool count unless explicitly adding new functionality

When adding new tools or modifying existing ones, ensure you maintain the hybrid architecture pattern and use the Node.js wrapper for all Kintone API calls.