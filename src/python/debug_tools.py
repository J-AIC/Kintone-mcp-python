#!/usr/bin/env python3
"""
ツール設定診断スクリプト
"""

import sys
from pathlib import Path

# 現在のファイルの場所から main.py をインポート
sys.path.insert(0, str(Path(__file__).parent))

# Python実装のツールクラスをインポートテスト
print("=== Python実装インポートテスト ===")
try:
    from config import get_settings
    print("✅ config import success")
except ImportError as e:
    print(f"❌ config import failed: {e}")

try:
    from server.tools.definitions import ALL_TOOL_DEFINITIONS
    print(f"✅ ALL_TOOL_DEFINITIONS import success - {len(ALL_TOOL_DEFINITIONS)} tools")
except ImportError as e:
    print(f"❌ ALL_TOOL_DEFINITIONS import failed: {e}")

try:
    from server.tools.handler import ToolHandler
    print("✅ ToolHandler import success")
except ImportError as e:
    print(f"❌ ToolHandler import failed: {e}")

from main import KintoneMCPServer

def diagnose_tools():
    """ツール設定を診断"""
    print("\n=== Kintone MCP Server ツール診断 ===")
    
    server = KintoneMCPServer()
    
    print(f"1. Node.js wrapper path: {server.nodejs_wrapper_path}")
    print(f"2. Node.js wrapper exists: {server.nodejs_wrapper_path.exists()}")
    
    tools = server.available_tools
    print(f"3. Available tools count: {len(tools)}")
    
    print(f"4. Python tools available: {server.python_tool_handler is not None}")
    print(f"5. Node.js tools count: {len(server.nodejs_tools)}")
    
    print("\n=== Tool List ===")
    for i, tool in enumerate(tools, 1):
        print(f"{i:2d}. {tool['name']} - {tool['description'][:50]}...")
    
    if len(tools) == 5:
        print("\n⚠️  WARNING: Only 5 tools detected - using basic tools fallback!")
        print("This means either:")
        print("- Python tool definitions are not being loaded")
        print("- Import errors are occurring")
        print("- Path issues preventing full tool loading")

if __name__ == "__main__":
    diagnose_tools() 