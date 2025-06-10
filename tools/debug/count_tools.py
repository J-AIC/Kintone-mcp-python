#!/usr/bin/env python3
"""
ツール数をカウントして差異を調査
"""

from src.server.tools.definitions import ALL_TOOL_DEFINITIONS

def main():
    print(f"Total tools: {len(ALL_TOOL_DEFINITIONS)}")
    print("\nTool list:")
    
    for i, tool in enumerate(ALL_TOOL_DEFINITIONS, 1):
        print(f"{i:2d}. {tool['name']}")
    
    print(f"\nExpected: 49 tools")
    print(f"Actual:   {len(ALL_TOOL_DEFINITIONS)} tools")
    print(f"Difference: {49 - len(ALL_TOOL_DEFINITIONS)}")

if __name__ == "__main__":
    main() 