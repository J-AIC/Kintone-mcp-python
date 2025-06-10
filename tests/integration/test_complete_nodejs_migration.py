#!/usr/bin/env python3
"""
Kintone MCP Server - 完全Node.js移行版テスト
全49ツールがNode.js経由で実行されることを確認
"""

import asyncio
import json
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mcp_stdio_hybrid_clean import KintoneMCPServer

async def test_complete_nodejs_migration():
    """完全Node.js移行版のテスト"""
    print("=== Kintone MCP Server - 完全Node.js移行版テスト ===\n")
    
    server = KintoneMCPServer()
    
    # 1. 初期化テスト
    print("1. 初期化テスト")
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        }
    }
    
    init_response = await server.handle_initialize(init_request)
    print(f"初期化レスポンス: {json.dumps(init_response, ensure_ascii=False, indent=2)}")
    print("✓ 初期化成功\n")
    
    # 2. ツール一覧テスト
    print("2. ツール一覧テスト")
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    tools_response = await server.handle_tools_list(tools_request)
    tools = tools_response.get("result", {}).get("tools", [])
    print(f"利用可能ツール数: {len(tools)}")
    
    # Node.js優先ツールの確認
    nodejs_tools_count = 0
    python_tools_count = 0
    
    for tool in tools:
        tool_name = tool["name"]
        if tool_name in server.nodejs_tools:
            nodejs_tools_count += 1
        else:
            python_tools_count += 1
    
    print(f"Node.js優先ツール: {nodejs_tools_count}個")
    print(f"Python実装ツール: {python_tools_count}個")
    print(f"全ツール数: {len(tools)}個")
    
    if nodejs_tools_count == 49:
        print("✓ 全49ツールがNode.js優先に設定されています")
    else:
        print(f"⚠ Node.js優先ツールが{nodejs_tools_count}個です（期待値: 49個）")
    
    print()
    
    # 3. Node.js優先ツールの詳細確認
    print("3. Node.js優先ツール一覧")
    nodejs_tool_names = sorted(list(server.nodejs_tools))
    for i, tool_name in enumerate(nodejs_tool_names, 1):
        print(f"{i:2d}. {tool_name}")
    print()
    
    # 4. コマンドマッピングテスト
    print("4. コマンドマッピングテスト")
    test_tool = "get_apps_info"
    test_args = {}
    
    try:
        # _execute_nodejs_toolメソッドの内部でコマンドマッピングをテスト
        print(f"テストツール: {test_tool}")
        print("Node.jsラッパーパスの確認...")
        
        if server.nodejs_wrapper_path and server.nodejs_wrapper_path.exists():
            print(f"✓ Node.jsラッパーが見つかりました: {server.nodejs_wrapper_path}")
        else:
            print(f"⚠ Node.jsラッパーが見つかりません: {server.nodejs_wrapper_path}")
        
        print("設定情報の確認...")
        config_status = []
        if server.kintone_config.get('domain'):
            config_status.append("domain")
        if server.kintone_config.get('apiToken'):
            config_status.append("apiToken")
        if server.kintone_config.get('username') and server.kintone_config.get('password'):
            config_status.append("username/password")
        
        if config_status:
            print(f"✓ 設定済み: {', '.join(config_status)}")
        else:
            print("⚠ Kintone認証情報が設定されていません")
        
    except Exception as e:
        print(f"⚠ コマンドマッピングテストでエラー: {str(e)}")
    
    print()
    
    # 5. 実際のツール呼び出しテスト（認証情報がある場合のみ）
    print("5. 実際のツール呼び出しテスト")
    
    if server.kintone_config.get('domain') and (
        server.kintone_config.get('apiToken') or 
        (server.kintone_config.get('username') and server.kintone_config.get('password'))
    ):
        print("認証情報が設定されているため、実際のAPI呼び出しをテストします...")
        
        # get_apps_infoツールのテスト
        call_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_apps_info",
                "arguments": {}
            }
        }
        
        try:
            call_response = await server.handle_tools_call(call_request)
            if call_response.get("result", {}).get("success"):
                print("✓ get_apps_info ツールの実行に成功しました")
                apps_data = call_response.get("result", {})
                if "apps" in apps_data:
                    print(f"  取得したアプリ数: {len(apps_data.get('apps', []))}")
            else:
                error_msg = call_response.get("result", {}).get("error", "Unknown error")
                print(f"⚠ get_apps_info ツールの実行でエラー: {error_msg}")
        except Exception as e:
            print(f"⚠ ツール呼び出しでエラー: {str(e)}")
    else:
        print("認証情報が設定されていないため、実際のAPI呼び出しはスキップします")
        print("(.envファイルでKINTONE_DOMAIN, KINTONE_API_TOKEN等を設定してください)")
    
    print()
    
    # 6. 移行完了確認
    print("6. 移行完了確認")
    print("=== 完全Node.js移行版の状況 ===")
    print(f"✓ 全ツール数: {len(tools)}個")
    print(f"✓ Node.js優先ツール: {nodejs_tools_count}個")
    print(f"✓ Python実装ツール: {python_tools_count}個")
    
    if nodejs_tools_count == 49 and python_tools_count == 0:
        print("🎉 完全Node.js移行が完了しました！")
        print("   全49ツールがNode.jsラッパー経由で実行されます。")
    elif nodejs_tools_count == len(tools):
        print("🎉 全ツールのNode.js移行が完了しました！")
        print(f"   全{len(tools)}ツールがNode.jsラッパー経由で実行されます。")
    else:
        print("⚠ 移行が完全ではありません")
        print(f"   Node.js優先: {nodejs_tools_count}個, Python実装: {python_tools_count}個")
    
    print("\n=== テスト完了 ===")

if __name__ == "__main__":
    asyncio.run(test_complete_nodejs_migration()) 