# Integration Quest - Quick Start Guide 🚀

Get up and running with Integration Quest in 5 minutes!

## Step 1: Install uv

If you don't have uv installed:

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Step 2: Install Dependencies

```bash
cd integration-quest
uv sync  # Package discovery warnings are safe to ignore
```

**Required packages:**
- fastmcp >= 2.0.0
- pydantic >= 2.0.0
- uvicorn >= 0.27.0

## Step 3: Test the Server

Verify everything is installed correctly:

```bash
uv run python -c "from server import mcp; print('✅ Server imports successfully!')"
```

## Step 4: Configure Claude Desktop

Add this to your `claude_desktop_config.json`:

### Windows
Location: `%APPDATA%\Claude\claude_desktop_config.json`

### Mac/Linux
Location: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Configuration:**

```json
{
  "mcpServers": {
    "integration-quest": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/Users/YOUR_USERNAME/Documents/GitHub/workato-integration-quest/integration-quest",
        "run",
        "python",
        "server.py"
      ]
    }
  }
}
```

**Important:** Update the path to match your actual installation location!

## Step 5: Choose Your Play Mode

### Option A: Terminal Mode (Quick & Easy!)

Play directly in your terminal - no Claude Desktop needed:

```bash
uv run python play.py
```

This launches an interactive CLI where you can type commands like:
- `explore` - Look around
- `attack bug` - Fight enemies
- `status` - Check your stats
- `help` - See all commands

### Option B: Claude Desktop (MCP Server)

1. **Restart Claude Desktop** to load the MCP server
2. **Start playing** by asking Claude to interact with the game

## Step 6: Start Playing!

In Claude Desktop, try these commands:

```
Can you help me create a character in Integration Quest? I want to be a mage named "Alex"
```

Claude will use the `create_character` tool and your adventure begins!

## 🎮 First Session Commands

Here's a sample gameplay flow:

1. **Create Character:**
   ```
   Create a warrior character named "Morgan"
   ```

2. **Check Status:**
   ```
   Show me my character status in Integration Quest
   ```

3. **Explore:**
   ```
   Explore the current room
   ```

4. **Pick Up Items:**
   ```
   Pick up the Slack Webhook
   ```

5. **Move Forward:**
   ```
   Move north
   ```

6. **Combat:**
   ```
   Attack the Bug with basic_attack
   ```

7. **Save Progress:**
   ```
   Save my game
   ```

## 🐛 Troubleshooting

### Server won't start
- Verify Python 3.11+ is installed: `python --version`
- Run `uv sync` to ensure dependencies are installed
- Check that you're in the `integration-quest` directory

### Claude can't find the server
- Check the path in `claude_desktop_config.json` is correct
- Use absolute paths, not relative
- On Windows, use forward slashes `/` or escaped backslashes `\\`
- Make sure the `--directory` path points to the `integration-quest` folder
- Restart Claude Desktop after making config changes

### uv sync fails with package discovery error
This is expected! The project structure is intentionally flat for easier MCP server deployment.
- The warnings are safe to ignore - just run `uv run python server.py` or `uv run python play.py`

### Import errors
- Ensure you're in the `integration-quest` directory
- All `__init__.py` files should be present in `models/`, `systems/`, and `tests/`
- Try: `uv run python server.py` instead of just `python server.py`

## 📚 Next Steps

Once you're up and running:

1. **Read the [README.md](README.md)** for full game mechanics
2. **Explore different classes** - Try warrior, mage, rogue, and cleric
3. **Reach depth 5** to face your first boss!
4. **Collect rare loot** and build the ultimate Integration Hero

## 🎯 Pro Tips

- **Examine enemies** before fighting - especially Undocumented APIs!
- **Save often** - Use `save_game` before boss battles
- **Collect Recipe Fragments** - Every 3 gives +5 max HP
- **Match skills to enemies** - Use class abilities strategically
- **Rest carefully** - 20% chance of random encounters!

---

**Ready to become a legendary Integration Hero?** ⚔️

*May your APIs always return 200 OK!*
