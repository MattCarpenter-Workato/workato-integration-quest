#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Quest: Remote MCP Server
Serve the game over HTTP using FastMCP's remote server capabilities

Usage:
    uv run python remote_server.py
"""

import sys

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')

# Import the FastMCP server and game state from server.py
# Note: server.py automatically loads the latest save on import
from server import mcp, game_states


if __name__ == "__main__":
    print("""
===============================================================

     ** INTEGRATION QUEST: REMOTE MCP SERVER **

     "Serving Integration Quest over HTTP"

     Server starting...

===============================================================
""")

    # Check if a save was loaded
    if game_states.get("default"):
        hero = game_states["default"].hero
        print(f"✅ Auto-loaded save: {hero.name} (Level {hero.level} {hero.role.title()})")
        print(f"   Depth: {game_states['default'].depth} | Uptime: {hero.uptime}/{hero.max_uptime}")
    else:
        print("No save found. Create a character to begin your quest!")

    print("\n🎮 Server ready! Connect via MCP client at http://localhost:8000/sse")
    print("=" * 63 + "\n")

    # Run the MCP server in remote mode with SSE transport
    # This will start an HTTP server that clients can connect to
    mcp.run(transport="sse")
