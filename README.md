# Integration Quest: The Workato RPG

*"Descend into the Legacy System Dungeons. Connect the disconnected. Automate the manual. Defeat the bugs that plague enterprise workflows."*

A Workato-themed text-based RPG implemented as a Python MCP (Model Context Protocol) server. Battle through legacy systems, API errors, and enterprise chaos as an Integration Hero!

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.0-green.svg)](https://github.com/jlowin/fastmcp)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🎮 What is Integration Quest?

Integration Quest transforms the daily challenges of integration engineering into an epic RPG adventure. Face off against **Bugs**, **Timeout Gremlins**, **Rate Limit Guardians**, and the dreaded **SAP Config Beast** while wielding **Connectors** as weapons and **Error Handlers** as armor.

Perfect for:
- **Workato users** wanting a fun way to learn integration concepts
- **RPG enthusiasts** interested in a unique technical theme
- **Developers** exploring MCP (Model Context Protocol) implementations
- **Teams** looking for an engaging way to teach integration patterns

## ✨ Key Features

- **🎭 4 Character Classes** - Integration Engineer, Recipe Builder, API Hacker, Support Engineer
- **👹 20+ Enemy Types** - From common Bugs to legendary Technical Debt Dragons
- **⚔️ 14 MCP Tools** - Full RPG functionality accessible through Claude or any MCP client
- **🏰 Procedural Dungeons** - Infinite exploration with boss battles every 5 levels
- **💾 Auto-Save System** - Automatically loads your latest progress
- **🎓 AI Game Guide** - LLM-powered tutorial for new players
- **🌐 3 Play Modes** - Terminal CLI, Local MCP, or Remote HTTP server

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/workato-integration-quest.git
cd workato-integration-quest/integration-quest

# Install dependencies with uv
uv sync

# Choose your adventure:
uv run python play.py              # Terminal mode
uv run python server.py            # Local MCP server
uv run python remote_server.py     # Remote HTTP server
```

## 📖 Documentation

- **[Full Game Guide](integration-quest/README.md)** - Complete documentation, gameplay, and features
- **[Quick Start Guide](integration-quest/QUICKSTART.md)** - Get up and running in 5 minutes
- **[Testing Guide](integration-quest/TESTING.md)** - Automated testing documentation
- **[AI Game Guide](integration-quest/game_guide_prompt.md)** - LLM prompt for guided gameplay
- **[Quick Guide](integration-quest/game_guide_prompt_short.md)** - Condensed tutorial prompt

## 🎯 Game Overview

### The Story

You are an **Integration Hero**, venturing into the depths of the Integration Dungeon where legacy systems lurk, APIs fail, and technical debt accumulates. Armed with your trusty HTTP Client and determination, you must connect the disconnected, transform the untransformed, and bring order to enterprise chaos.

### Character Classes

| Class | Role | Playstyle | Signature Ability |
|-------|------|-----------|-------------------|
| **⚔️ Warrior** | Integration Engineer | High damage, bulk operations | **Bulk Upsert** - Hit all enemies |
| **🔮 Mage** | Recipe Builder | Powerful transformations | **Formula Transform** - Rewrite logic |
| **🗡️ Rogue** | API Hacker | High agility, workarounds | **Custom Connector** - 3x damage |
| **✨ Cleric** | Support Engineer | Resilient, recovery | **Error Handler** - Auto-revive |

### Sample Enemies

- **🐛 Bug** - A crawling syntax error (Common)
- **⏱️ Timeout Gremlin** - Loves slow APIs (Common)
- **🚦 Rate Limit Guardian** - Inflicts Rate Limited status (Uncommon)
- **🏰 Undocumented API** - Immune until examined! (Rare)
- **👹 SAP Config Beast** - 47 mandatory fields (Boss)
- **💀 Technical Debt Dragon** - Every shortcut returns (Boss)

### Equipment & Loot

**Connectors (Weapons):**
- HTTP Client → Slack Webhook → Salesforce Connector → NetSuite Blade → SAP RFC Cannon → Workato SDK Staff

**Error Handlers (Armor):**
- Basic Logging → Try/Catch Vest → Retry Logic Armor → Circuit Breaker Shield → Observability Plate

**Consumables:**
- Job Retry Potion, API Credit Refill, Token Refresh Vial, API Documentation, Recipe Fragments

## 🎮 Play Modes

### Option 1: Terminal Mode (Interactive CLI)

Perfect for quick play sessions or development:

```bash
uv run python play.py
```

Interactive command-line interface with all 14 game commands available.

### Option 2: Claude Desktop (Local MCP)

Play through Claude Desktop with natural language:

1. Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "integration-quest": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/workato-integration-quest/integration-quest",
        "run",
        "python",
        "server.py"
      ]
    }
  }
}
```

2. Restart Claude Desktop
3. Interact with Claude to play the game!

### Option 3: Remote Server (HTTP)

Serve the game over HTTP for remote access or web integration:

```bash
uv run python remote_server.py
```

Connect via: `http://localhost:8000/mcp/v1`

Perfect for cloud deployment, multi-client scenarios, or web applications.

## 🎓 New Player Guide

First time playing? Use the **AI Game Guide** to learn the mechanics!

Copy the contents of [`game_guide_prompt.md`](integration-quest/game_guide_prompt.md) into your conversation with Claude when using the MCP server. The guide will:

- Teach you game mechanics step-by-step
- Explain Workato concepts in context
- Provide strategic advice tailored to your experience level
- Help you make the most of your Integration Quest adventure

## 🏗️ Project Structure

```
workato-integration-quest/
├── README.md                        # This file - Quick overview
└── integration-quest/               # Main game directory
    ├── README.md                    # Full game documentation
    ├── QUICKSTART.md                # Get started in 5 minutes
    ├── TESTING.md                   # Testing guide and results
    ├── server.py                    # FastMCP server (14 tools)
    ├── play.py                      # Terminal CLI mode
    ├── remote_server.py             # HTTP remote server
    ├── config.py                    # Game configuration
    ├── game_guide_prompt.md         # Full AI guide prompt
    ├── game_guide_prompt_short.md   # Quick guide prompt
    ├── test_all_functions.py        # Function validation tests
    ├── test_gameplay.py             # Automated gameplay tests
    ├── models/                      # Game data models (11 files)
    ├── systems/                     # Game systems (combat, generation, etc.)
    ├── data/                        # JSON game data
    ├── storage/saves/               # Save files
    └── logs/                        # Test logs
```

## 🛠️ Technical Details

### Built With

- **[FastMCP 2.0](https://github.com/jlowin/fastmcp)** - Python MCP server framework
- **[Pydantic](https://docs.pydantic.dev/)** - Data validation and settings management
- **Python 3.11+** - Modern Python features and type hints

### MCP Tools (14 Total)

| Tool | Description |
|------|-------------|
| `create_character` | Create your Integration Hero |
| `view_status` | View stats, inventory, and status |
| `explore` | Explore current room |
| `examine` | Examine enemies or items in detail |
| `move` | Navigate north/south/east/west |
| `attack` | Attack enemies with skills |
| `defend` | Take defensive stance |
| `use_item` | Use consumables |
| `pickup` | Pick up items |
| `equip` | Equip weapons and armor |
| `rest` | Recover HP/MP (20% encounter chance!) |
| `flee` | Attempt to escape combat |
| `save_game` | Create a checkpoint |
| `load_game` | Restore from checkpoint |

### Auto-Save Feature

Integration Quest automatically loads your most recent save file when you start the game in any mode. No more manual loading - just start playing where you left off!

## 📊 Game Stats (Workato Themed)

| Stat | Theme | Description |
|------|-------|-------------|
| **Uptime** | HP | Integration health (0 = system down) |
| **API Credits** | MP | Fuel for powerful skills |
| **Throughput** | STR | Records processed per action |
| **Formula Power** | INT | Transformation complexity |
| **Rate Agility** | DEX | Avoiding 429 errors |
| **Error Resilience** | CON | Recovery from failures |

## 🎯 Example Gameplay

```
> create_character(name="Alex", role="mage")
📜 Alex the Recipe Builder awakens in the Integration Dungeon...

> explore()
🏛️ THE SALESFORCE ANTECHAMBER
⚠️ Rate Limit Guardian blocks the path!

> examine("Rate Limit Guardian")
🔍 HP: 50/50 | Armor: 2
Special: Can inflict Rate Limited status

> attack("Rate Limit Guardian", skill="lookup_table_strike")
🔮 Lookup Table Strike: GUARANTEED HIT!
⚔️ 18 damage! Guardian: 32/50 HP

> attack("Rate Limit Guardian", skill="formula_transform")
🔮 FORMULA TRANSFORM!
✅ VICTORY! +35 XP, +20 gold
📦 Loot: Retry Logic Armor
```

## 🎉 Educational Value

Integration Quest teaches real integration concepts through gameplay:

- **API Rate Limiting** - Rate Limit Guardians and status effects
- **Error Handling** - Armor system and recovery mechanics
- **Retry Logic** - Rest and recovery with risk/reward
- **Bulk Operations** - Warrior class skills and strategies
- **Data Transformation** - Mage class formula mechanics
- **Graceful Degradation** - Flee system and fallback strategies
- **Observability** - Examine tool and status monitoring
- **Technical Debt** - Boss enemies that accumulate over time

## 🧪 Testing & Quality

Integration Quest includes comprehensive automated testing:

- **31/31 Function Tests Passing** - All game functions validated
- **Automated Gameplay Tests** - AI-driven gameplay simulation
- **Full Coverage** - Combat, progression, save/load, items, and more
- **Continuous Testing** - Run `test_all_functions.py` and `test_gameplay.py`

See [TESTING.md](integration-quest/TESTING.md) for full testing documentation.

## 🤝 Contributing

We welcome contributions! Whether it's:

- 🐛 Bug fixes
- ✨ New features (enemies, items, skills)
- 📝 Documentation improvements
- 🎨 Game balance adjustments
- 🌍 Translations

Please feel free to open an issue or submit a pull request!

## 📜 License

This project is built for the Workato community as an educational and entertaining demonstration of MCP server capabilities.

## 🙏 Credits

Created with:
- **FastMCP 2.0** - MCP server framework
- **Pydantic** - Data validation
- **Love for Integration** - The Workato spirit

Special thanks to the Workato community for inspiration and the integration challenges that became game mechanics!

## 🔗 Links

- **[Workato](https://www.workato.com/)** - The low-code integration platform that inspired this game
- **[Model Context Protocol](https://modelcontextprotocol.io/)** - The protocol powering the game's architecture
- **[FastMCP](https://github.com/jlowin/fastmcp)** - The framework that makes it all possible

---

*"Every successful integration is a dungeon conquered. Every bug fixed is a villain defeated. You are the hero the enterprise needs."*

**Now venture forth, Integration Hero, and may your APIs always return 200 OK!** ⚡
