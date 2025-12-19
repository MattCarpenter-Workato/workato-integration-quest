# Integration Quest: The Workato RPG 🎮⚔️

*"Descend into the Legacy System Dungeons. Connect the disconnected. Automate the manual. Defeat the bugs that plague enterprise workflows."*

A Workato-themed text-based RPG implemented as a Python MCP (Model Context Protocol) server. Battle through legacy systems, API errors, and enterprise chaos as an Integration Hero!

## 🎭 The Story

You are an **Integration Hero**, venturing into the depths of the Integration Dungeon where legacy systems lurk, APIs fail, and technical debt accumulates. Armed with your trusty HTTP Client and determination, you must connect the disconnected, transform the untransformed, and bring order to enterprise chaos.

Will you become a legendary Integration Engineer, mastering bulk operations? A powerful Recipe Builder, wielding formula transformations? A cunning API Hacker, finding workarounds for every obstacle? Or a resilient Support Engineer, recovering from any failure?

The choice is yours. The legacy systems await.

## 🚀 Installation

### Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) package manager

### Setup

1. **Install uv** (if not already installed):
   ```bash
   # On macOS and Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # On Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Clone and navigate to the project:**
   ```bash
   git clone https://github.com/MattCarpenter-Workato/workato-integration-quest.git
   cd workato-integration-quest
   ```

3. **Install dependencies:**
   ```bash
   uv sync  # Package discovery warnings are safe to ignore
   ```

4. **Choose your play mode:**
   ```bash
   # Option 1: Terminal Mode (Interactive CLI)
   uv run python play.py

   # Option 2: Local MCP Server (for Claude Desktop)
   uv run python server.py

   # Option 3: Remote MCP Server (HTTP)
   uv run python remote_server.py
   ```

## 🎮 Playing the Game

### 🎓 New Player Guide

**First time playing?** Use the AI Game Guide to learn the mechanics!

Copy the contents of [`game_guide_prompt.md`](game_guide_prompt.md) or [`game_guide_prompt_short.md`](game_guide_prompt_short.md) into your conversation with Claude when using the MCP server. The guide will:

- Teach you game mechanics step-by-step
- Explain Workato concepts in context
- Provide strategic advice tailored to your experience level
- Help you make the most of your Integration Quest adventure

**Quick Start with Guide:**
1. Open Claude Desktop
2. Paste the guide prompt at the start of your conversation
3. Let the guide walk you through character creation and your first steps
4. The guide adapts to your experience level - ask questions anytime!

### Option 1: Terminal Mode (Interactive CLI)

Play directly in your terminal with an interactive command-line interface!

```bash
uv run python play.py
```

**Features:**
- Full interactive gameplay in your terminal
- Text-based adventure interface
- All 14 game commands available
- Save/load functionality
- Perfect for quick play sessions or development

**Example Session:**
```
>>> explore
🏛️ THE INTEGRATION HUB
You stand at the entrance...

>>> attack bug
🎲 Rolled 1d4: [3] = 3
⚔️ You hit Bug for 3 damage!

>>> status
📊 Alex the Mage - Level 1
❤️ Uptime: 90/90
```

### Option 2: Via Claude Desktop (MCP Server)

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "integration-quest": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/workato-integration-quest",
        "run",
        "python",
        "server.py"
      ]
    }
  }
}
```

**Important:** Update the path to match your actual installation location!

Then restart Claude Desktop and interact with Claude to use the game tools!

### Option 3: Remote MCP Server (HTTP)

Run the game as a remote MCP server that can be accessed over HTTP using SSE (Server-Sent Events) transport:

```bash
uv run python remote_server.py
```

This starts an HTTP server (default port 8000) that serves the MCP protocol. Perfect for:
- Remote access to the game
- Integration with web applications
- Multi-client scenarios
- Cloud deployment

**Connecting to the Remote Server:**

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "integration-quest-remote": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://localhost:8000/sse"
      ]
    }
  }
}
```

Or connect from any MCP client using the SSE endpoint: `http://localhost:8000/sse`

**Configuration Options:**

You can customize the server by setting environment variables:
- `MCP_SERVER_PORT`: Change the port (default: 8000)
- `MCP_SERVER_HOST`: Change the host (default: 0.0.0.0)

### Available Commands (MCP Tools)

| Command | Description |
|---------|-------------|
| `create_character` | Create your Integration Hero |
| `view_status` | View stats, inventory, and status |
| `explore` | Explore current room |
| `examine` | Examine enemies or items in detail |
| `move` | Navigate north/south/east/west |
| `attack` | Attack an enemy with skills |
| `defend` | Take defensive stance |
| `use_item` | Use consumables from inventory |
| `pickup` | Pick up items from room |
| `equip` | Equip weapons and armor |
| `rest` | Recover HP/MP (20% encounter chance!) |
| `flee` | Attempt to escape combat |
| `save_game` | Create a checkpoint |
| `load_game` | Restore from checkpoint |

## 🎭 Character Classes

### 🗡️ Warrior (Integration Engineer)
**"Process more. Process faster."**

- **Primary Stat:** Throughput (STR)
- **HP:** High (+20)
- **MP:** Low (-10)
- **Skills:**
  - **Bulk Upsert:** Hit all enemies at once
  - **Force Sync:** Ignore armor completely
  - **Throughput Surge:** Take two actions per turn

### 🔮 Mage (Recipe Builder)
**"Everything is just a transformation away."**

- **Primary Stat:** Formula Power (INT)
- **HP:** Low (-10)
- **MP:** Very High (+30)
- **Skills:**
  - **Formula Transform:** Rewrite enemy logic
  - **Lookup Table Strike:** Guaranteed hit +50% damage
  - **Callable Recipe:** Summon automation ally

### 🗡️ Rogue (API Hacker)
**"There's always a workaround."**

- **Primary Stat:** Rate Agility (DEX)
- **HP:** Normal
- **MP:** Normal
- **Skills:**
  - **Workaround:** Bypass armor, double damage
  - **Rate Limit Dance:** Evade all attacks
  - **Custom Connector:** Exploit weaknesses for 3x damage

### ✨ Cleric (Support Engineer)
**"No system stays down on my watch."**

- **Primary Stat:** Error Resilience (CON)
- **HP:** High (+10)
- **MP:** High (+15)
- **Skills:**
  - **Error Handler:** Auto-revive from 0 HP (once per combat)
  - **Job Recovery:** Restore 40% max HP
  - **Escalation:** Call backup ally

## 👹 Enemies

### Common Enemies (Depth 1-3)
- 🐛 **Bug** - A crawling syntax error
- ⏱️ **Timeout Gremlin** - Loves slow APIs
- 🔐 **Auth Zombie** - Expired token, still walking
- 📋 **Null Pointer Specter** - Expected data, found void
- 📝 **Missing Field Imp** - Required field not provided!

### Uncommon Enemies (Depth 4-6)
- 🚦 **Rate Limit Guardian** - Inflicts Rate Limited status
- 🔀 **Data Mismatch Hydra** - Attacks with 3 heads
- 📉 **Schema Drift Phantom** - Randomizes stats
- 🕳️ **Pagination Void** - Steals inventory items
- 🔄 **Infinite Loop Serpent** - Attacks twice per turn

### Rare Enemies (Depth 7-9)
- 🏰 **Undocumented API** - Immune until examined!
- 🧊 **Frozen Job Golem** - 50% chance to skip turn
- 🔥 **Webhook Storm** - AOE damage
- 📜 **Legacy Code Lich** - Resurrects defeated enemies
- 🕸️ **Spaghetti Code Horror** - Tangles your skills

### Boss Enemies (Every 5th Depth)
- 👹 **SAP Config Beast** (Depth 5) - 47 mandatory fields
- 🏚️ **The Legacy Mainframe** (Depth 10) - Running since 1987
- 🐉 **The Monolith** (Depth 15) - All services in one
- 💀 **Technical Debt Dragon** (Depth 20) - Every shortcut returns

## ⚔️ Weapons (Connectors)

| Weapon | Tier | Damage | Special |
|--------|------|--------|---------|
| HTTP Client | Common | 1d4 | Starting weapon |
| Slack Webhook | Common | 1d6 | +2 vs Communication |
| Salesforce Connector | Uncommon | 2d6 | Bulk Mode: Hit all |
| NetSuite Blade | Rare | 3d6 | Ignores 50% armor |
| SAP RFC Cannon | Legendary | 4d8 | Stuns for 1 turn |
| Workato SDK Staff | Legendary | 3d10 | +5 all stats |

## 🛡️ Armor (Error Handlers)

| Armor | Tier | Protection | Effect |
|-------|------|------------|--------|
| Basic Logging | Common | +1 | See enemy HP |
| Try/Catch Vest | Common | +2 | Survive fatal hit once |
| Retry Logic Armor | Uncommon | +4 | Auto-retry defenses |
| Circuit Breaker Shield | Rare | +6 | Block cascading damage |
| Observability Plate | Legendary | +10 | See all enemy stats |

## 🧪 Consumables

- 💊 **Job Retry Potion** - Restore 50 Uptime
- 💙 **API Credit Refill** - Restore 30 API Credits
- 🔐 **Token Refresh Vial** - Cure "Auth Expired" status
- 📚 **API Documentation** - Reveal enemy weakness
- 💨 **Graceful Degradation Bomb** - Guaranteed escape
- 📜 **Bulk Operation Scroll** - Next attack hits all
- 🧩 **Recipe Fragment** - Collect 3 for +5 max HP bonus
- 🎫 **Golden Ticket** - Skip to next boss room

## 📊 Game Stats (Workato Themed)

| Stat | Theme | Description |
|------|-------|-------------|
| **Uptime** | HP | Integration health (0 = system down) |
| **API Credits** | MP | Fuel for powerful skills |
| **Throughput** | STR | Records processed per action |
| **Formula Power** | INT | Transformation complexity |
| **Rate Agility** | DEX | Avoiding 429 errors |
| **Error Resilience** | CON | Recovery from failures |

## 🗺️ Room Types

- 🔗 **Corridor (Pipeline)** - Data flows through cables
- 🏛️ **Chamber (App Hub)** - Vast application instances
- 💎 **Treasure (Data Lake)** - Perfectly normalized JSON!
- ⚠️ **Trap (Legacy System)** - SOAP envelopes and XML namespaces
- 👹 **Boss (Core System)** - Face the ultimate integrations

## 🎯 Example Gameplay Session

```
> create_character(name="Alex", role="mage")

📜 Alex the Recipe Builder awakens in the Integration Dungeon...

🎭 Role: Recipe Builder (Mage)
📊 Stats: Uptime 90 | API Credits 80 | Formula Power 14

> explore()

🏛️ THE SALESFORCE ANTECHAMBER

Opportunity objects drift lazily through the air...
📦 Items: API Documentation Scroll, Slack Webhook
⚠️ Rate Limit Guardian blocks the path!

> examine("Rate Limit Guardian")

🔍 RATE LIMIT GUARDIAN
HP: 50/50 | Armor: 2
Special: Can inflict Rate Limited status

> attack("Rate Limit Guardian", skill="lookup_table_strike")

🔮 Lookup Table Strike: GUARANTEED HIT!
⚔️ 18 damage! Guardian: 32/50 HP

> attack("Rate Limit Guardian", skill="formula_transform")

🔮 FORMULA TRANSFORM!
✅ VICTORY! +35 XP, +20 gold
📦 Loot: Retry Logic Armor
```

## 🏗️ Project Structure

```
workato-integration-quest/
├── server.py                    # FastMCP server + all 14 tools
├── play.py                      # Terminal mode CLI interface
├── remote_server.py             # Remote MCP server (HTTP/SSE)
├── config.py                    # Game configuration and constants
├── pyproject.toml               # Python project configuration
├── requirements.txt             # Python dependencies
├── uv.lock                      # uv lock file
├── README.md                    # This file - Full documentation
├── TESTING.md                   # Testing guide and results
├── game_guide_prompt.md         # Full AI guide system prompt
├── game_guide_prompt_short.md   # Condensed guide prompt
├── test_all_functions.py        # Function validation tests (31 tests)
├── models/
│   ├── __init__.py              # Model exports
│   ├── hero.py                  # Hero, stats, inventory
│   ├── combat.py                # Combat state, enemies
│   ├── world.py                 # Room, dungeon map
│   └── items.py                 # Weapons, armor, consumables
├── systems/
│   ├── __init__.py              # System exports
│   ├── combat.py                # Damage calc, turn order
│   ├── generation.py            # Procedural dungeon generation
│   ├── progression.py           # XP, leveling, skill unlocks
│   ├── effects.py               # Status effect processing
│   └── dice.py                  # Dice rolling utilities
├── data/
│   ├── enemies.json             # 20+ enemy definitions
│   ├── items.json               # Weapons, armor, consumables
│   ├── descriptions.json        # Room templates
│   └── skills.json              # Class skills
├── tests/
│   ├── __init__.py              # Test package init
│   ├── test_dice.py             # Dice rolling unit tests
│   └── test_progression.py      # Progression system tests
└── logs/                        # Test logs (git ignored)
```

## 🎮 Game Features

✅ **14 MCP Tools** - Full RPG functionality via Claude
✅ **4 Character Classes** - Unique skills and playstyles
✅ **20+ Enemy Types** - Across 4 difficulty tiers
✅ **Boss Battles** - Epic encounters every 5 levels
✅ **Procedural Dungeons** - Infinite exploration
✅ **Loot System** - 10+ weapons, 5+ armor, 9+ consumables
✅ **Save/Load** - Persistent game state with auto-load
✅ **Status Effects** - Rate Limited, Auth Expired, Buffered, etc.
✅ **Progression** - Level up, gain stats, unlock skills
✅ **Narrative Combat** - Rich storytelling throughout
✅ **AI Game Guide** - LLM-powered tutorial system for new players
✅ **3 Play Modes** - Terminal CLI, Local MCP, Remote HTTP server
✅ **Comprehensive Testing** - 31 function tests + unit tests

## 🛠️ Development

### Running Tests

Integration Quest includes comprehensive automated testing:

```bash
# Run all function tests (31 tests - validates all game functions)
uv run python test_all_functions.py

# Run unit tests with pytest
uv run pytest tests/
```

**Test Results:**
- ✅ 31/31 function tests passing (100%)
- ✅ Full coverage: combat, progression, save/load, items, status effects

See [TESTING.md](TESTING.md) for complete testing documentation.

### Adding New Content

- **New Enemies:** Edit `data/enemies.json`
- **New Items:** Edit `data/items.json`
- **New Skills:** Edit `data/skills.json`
- **New Rooms:** Edit `data/descriptions.json`

## 📜 License

This project is built for the Workato community as an educational and entertaining demonstration of MCP server capabilities.

## 🎉 Credits

Built with:
- **FastMCP 2.0** - Python MCP server framework
- **Pydantic** - Data validation
- **Love for Integration** - The Workato spirit

---

*"Every successful integration is a dungeon conquered. Every bug fixed is a villain defeated. You are the hero the enterprise needs."*

**Now venture forth, Integration Hero, and may your APIs always return 200 OK!** ⚡
