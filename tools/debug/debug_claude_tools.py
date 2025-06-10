#!/usr/bin/env python3
"""
Claude Desktop向けツール登録のデバッグ
"""

import sys
import asyncio
from src.server.tools.definitions import ALL_TOOL_DEFINITIONS

async def debug_tools():
    """ツール登録をシミュレートしてエラーを検出"""
    
    print(f"Total tools defined: {len(ALL_TOOL_DEFINITIONS)}")
    
    valid_tools = []
    invalid_tools = []
    duplicate_names = set()
    seen_names = set()
    
    for i, tool in enumerate(ALL_TOOL_DEFINITIONS, 1):
        tool_name = tool.get('name', f'unknown_{i}')
        
        # 重複チェック
        if tool_name in seen_names:
            duplicate_names.add(tool_name)
            print(f"🚨 重複ツール: {tool_name}")
            continue
        
        seen_names.add(tool_name)
        
        # 基本的な検証
        try:
            if not tool_name:
                raise ValueError("ツール名が空です")
            if not tool.get('description'):
                raise ValueError("説明がありません")
            if 'inputSchema' not in tool:
                raise ValueError("inputSchemaがありません")
                
            valid_tools.append(tool_name)
            
        except Exception as e:
            invalid_tools.append((tool_name, str(e)))
            print(f"❌ 無効なツール: {tool_name} - {e}")
    
    print(f"\n📊 結果:")
    print(f"  定義されたツール: {len(ALL_TOOL_DEFINITIONS)}")
    print(f"  重複ツール: {len(duplicate_names)} ({', '.join(duplicate_names)})")
    print(f"  無効なツール: {len(invalid_tools)}")
    print(f"  有効なツール: {len(valid_tools)}")
    
    expected_claude_tools = len(valid_tools)
    print(f"\n🎯 Claude Desktopで期待される数: {expected_claude_tools}")
    print(f"   実際にClaude Desktopで表示: 45")
    print(f"   差異: {expected_claude_tools - 45}")
    
    if invalid_tools:
        print(f"\n❌ 無効なツール詳細:")
        for name, error in invalid_tools:
            print(f"  - {name}: {error}")

if __name__ == "__main__":
    asyncio.run(debug_tools()) 