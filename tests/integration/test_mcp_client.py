#!/usr/bin/env python3
"""
MCP クライアントテストスクリプト（改良版）

複数のKintone MCPサーバーをテストし、実際のツール機能も確認
"""

import json
import asyncio
import subprocess
import sys
from pathlib import Path


async def test_mcp_server(script_path, server_name):
    """MCPサーバーをテストする"""
    print(f"\n{'='*60}")
    print(f"Testing {server_name} ({script_path})")
    print(f"{'='*60}")
    
    try:
        # サーバープロセスを開始
        process = await asyncio.create_subprocess_exec(
            sys.executable, script_path,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=Path(script_path).parent
        )
        
        # initializeリクエストをテスト
        print("1. Testing initialize request...")
        initialize_request = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        request_line = json.dumps(initialize_request) + "\n"
        process.stdin.write(request_line.encode())
        await process.stdin.drain()
        
        # レスポンスを読み取り
        response_line = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
        if response_line:
            response = json.loads(response_line.decode().strip())
            print(f"✓ Initialize response: {response}")
            
            # initialized notificationを送信
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            notification_line = json.dumps(initialized_notification) + "\n"
            process.stdin.write(notification_line.encode())
            await process.stdin.drain()
            
        else:
            print("✗ No initialize response received")
            return False
        
        # tools/listリクエストをテスト
        print("2. Testing tools/list request...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        request_line = json.dumps(tools_request) + "\n"
        process.stdin.write(request_line.encode())
        await process.stdin.drain()
        
        # レスポンスを読み取り
        response_line = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
        if response_line:
            response = json.loads(response_line.decode().strip())
            print(f"✓ Tools list response: {response}")
            
            # ツール一覧を表示
            tools = response.get("result", {}).get("tools", [])
            print(f"  Available tools: {len(tools)}")
            for tool in tools:
                name = tool.get("name", "Unknown")
                description = tool.get("description", "No description")
                print(f"    - {name}: {description}")
        else:
            print("✗ No tools/list response received")
            return False
            
        # search_recordsツールをテスト（改良版のみ）
        if "final_fix" in script_path.lower() or "hybrid_clean" in script_path.lower():
            print("3. Testing search_records tool...")
            search_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "search_records",
                    "arguments": {
                        "app_id": 1,
                        "query": "limit 10",
                        "total_count": True
                    }
                }
            }
            
            request_line = json.dumps(search_request) + "\n"
            process.stdin.write(request_line.encode())
            await process.stdin.drain()
            
            # レスポンスを読み取り
            response_line = await asyncio.wait_for(process.stdout.readline(), timeout=10.0)
            if response_line:
                response = json.loads(response_line.decode().strip())
                print(f"✓ Search records response: {response}")
            else:
                print("✗ No search_records response received")
        
        # プロセスを終了
        process.stdin.close()
        await process.wait()
        
        print(f"✓ {server_name} test completed successfully")
        return True
        
    except asyncio.TimeoutError:
        print(f"✗ Timeout while testing {server_name}")
        if 'process' in locals():
            process.terminate()
            await process.wait()
        return False
    except Exception as e:
        print(f"✗ Error testing {server_name}: {e}")
        if 'process' in locals():
            process.terminate()
            await process.wait()
        return False


async def main():
    """メイン関数"""
    print("Kintone MCP Server Test Suite")
    print("Testing multiple MCP server implementations...")
    
    base_dir = Path(__file__).parent
    
    # テスト対象のサーバーリスト
    servers_to_test = [
        ("mcp_stdio_hybrid_clean.py", "Complete Node.js Migration Version (完全Node.js移行版)"),
        ("mcp_stdio_final_fix.py", "Final Fix Version (実際のKintone API連携)"),
        ("test_simple_mcp.py", "Simple Test Version")
    ]
    
    results = {}
    
    for script_name, server_name in servers_to_test:
        script_path = base_dir / script_name
        if script_path.exists():
            success = await test_mcp_server(str(script_path), server_name)
            results[server_name] = success
        else:
            print(f"\n⚠️  Skipping {server_name} - file not found: {script_path}")
            results[server_name] = False
    
    # 結果サマリー
    print(f"\n{'='*60}")
    print("TEST RESULTS SUMMARY")
    print(f"{'='*60}")
    
    for server_name, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status} {server_name}")
    
    print(f"\nTotal: {sum(results.values())}/{len(results)} tests passed")
    
    # 推奨設定の表示
    success_servers = [name for name, success in results.items() if success]
    if success_servers:
        print(f"\n📋 Claude Desktop推奨設定: {success_servers[0]}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test suite failed: {e}")
        sys.exit(1) 