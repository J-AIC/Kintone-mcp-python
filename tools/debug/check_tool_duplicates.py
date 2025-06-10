#!/usr/bin/env python3
"""
ツール名の重複を検出
"""

from src.server.tools.definitions import ALL_TOOL_DEFINITIONS
from collections import Counter

def main():
    tool_names = [tool['name'] for tool in ALL_TOOL_DEFINITIONS]
    
    print(f"Total tools defined: {len(tool_names)}")
    print(f"Unique tools: {len(set(tool_names))}")
    
    # 重複を検出
    name_counts = Counter(tool_names)
    duplicates = {name: count for name, count in name_counts.items() if count > 1}
    
    if duplicates:
        print(f"\n🚨 重複するツール名が見つかりました:")
        for name, count in duplicates.items():
            print(f"  - '{name}': {count}回定義されています")
            
        print(f"\n重複除去後のツール数: {len(set(tool_names))}")
        print(f"Claude Desktopで表示される数: {len(set(tool_names))}")
    else:
        print("\n✅ 重複するツール名はありません")
        print("他の原因を調査する必要があります")

if __name__ == "__main__":
    main() 