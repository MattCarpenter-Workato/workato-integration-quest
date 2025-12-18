#!/usr/bin/env python3
"""
Quick start script for Integration Quest MCP Server
"""

if __name__ == "__main__":
    print("🎮 Starting Integration Quest: The Workato RPG MCP Server...")
    print("=" * 60)
    print()
    print("Server will start on STDIO transport for MCP clients.")
    print("Configure your Claude Desktop to connect!")
    print()
    print("=" * 60)

    from server import mcp
    mcp.run()
