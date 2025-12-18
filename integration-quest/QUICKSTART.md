# Integration Quest - Quick Start Guide 🚀

Get up and running with Integration Quest in 5 minutes!

## Step 1: Install uv (Recommended)

If you don't have uv installed:

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Or skip to **Option B** below to use pip instead.

## Step 2: Install Dependencies

### Option A: Using uv (Recommended)

```bash
cd integration-quest

# No installation needed! uv will install dependencies automatically when you run the server
# (Or optionally run 'uv sync' if you want a virtual environment - warnings are safe to ignore)
```

### Option B: Using pip

```bash
cd integration-quest
pip install -r requirements.txt
```

**Required packages:**
- fastmcp >= 2.0.0
- pydantic >= 2.0.0
- uvicorn >= 0.27.0

## Step 3: Test the Server

Verify everything is installed correctly:

```bash
# With uv (inline dependencies)
uv run --with fastmcp --with pydantic python -c "from server import mcp; print('✅ Server imports successfully!')"

# With pip
python -c "from server import mcp; print('✅ Server imports successfully!')"
```

## Step 4: Configure Claude Desktop

Add this to your `claude_desktop_config.json`:

### Windows
Location: `%APPDATA%\Claude\claude_desktop_config.json`

### Mac/Linux
Location: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Configuration:**

### If using uv (recommended):

```json
{
  "mcpServers": {
    "integration-quest": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/Users/YOUR_USERNAME/Documents/GitHub/workato-integration-quest/integration-quest",
        "run",
        "--with",
        "fastmcp",
        "--with",
        "pydantic",
        "--with",
        "uvicorn",
        "--with",
        "starlette",
        "python",
        "server.py"
      ]
    }
  }
}
```

### If using pip:

```json
{
  "mcpServers": {
    "integration-quest": {
      "command": "python",
      "args": [
        "C:/Users/YOUR_USERNAME/Documents/GitHub/workato-integration-quest/integration-quest/server.py"
      ]
    }
  }
}
```

**Important:** Update the path to match your actual installation location!

## Step 4: Restart Claude Desktop

Close and reopen Claude Desktop to load the MCP server.

## Step 5: Start Playing!

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
- With uv: Run `uv sync` to ensure dependencies are installed
- With pip: Check all dependencies are installed: `pip list | grep -E "fastmcp|pydantic"`

### Claude can't find the server
- Check the path in `claude_desktop_config.json` is correct
- Use absolute paths, not relative
- On Windows, use forward slashes `/` or escaped backslashes `\\`
- If using uv, make sure the `--directory` path points to the `integration-quest` folder
- Restart Claude Desktop after making config changes

### uv sync fails with package discovery error
This is expected! The project structure is intentionally flat for easier MCP server deployment. You can:
- Ignore the error and use pip instead: `pip install -r requirements.txt`
- Or run the server directly with: `uv run --with fastmcp --with pydantic python server.py`

### Import errors
- Ensure you're in the `integration-quest` directory
- All `__init__.py` files should be present in `models/`, `systems/`, and `tests/`
- If using uv, try: `uv run python server.py` instead of just `python server.py`

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
