<p align="center">
  <img src="Integration-Quest-Logo.png" alt="Integration Quest Logo" width="400">
</p>

# Integration Quest: The Workato RPG

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

> Descend into the Legacy System Dungeons. Connect the disconnected. Automate the manual. Defeat the bugs that plague enterprise workflows.

A Workato-themed text-based RPG implemented as a Python MCP (Model Context Protocol) server. Battle through legacy systems, API errors, and enterprise chaos as an Integration Hero!

## Table of Contents

- [The Story](#the-story)
- [Installation](#installation)
- [Playing the Game](#playing-the-game)
- [Character Classes](#character-classes)
- [Enemies](#enemies)
- [Items](#items)
- [Game Mechanics](#game-mechanics)
- [Project Structure](#project-structure)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)

## The Story

You are an **Integration Hero**, venturing into the depths of the Integration Dungeon where legacy systems lurk, APIs fail, and technical debt accumulates. Armed with your trusty HTTP Client and determination, you must connect the disconnected, transform the untransformed, and bring order to enterprise chaos.

Will you become a legendary **Integration Engineer**, mastering bulk operations? A powerful **Recipe Builder**, wielding formula transformations? A cunning **API Hacker**, finding workarounds for every obstacle? Or a resilient **Support Engineer**, recovering from any failure?

The choice is yours. The legacy systems await.

## Installation

### Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) package manager

### Setup

1. **Install uv** (if not already installed):

   ```bash
   # macOS and Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Clone the repository:**

   ```bash
   git clone https://github.com/MattCarpenter-Workato/workato-integration-quest.git
   cd workato-integration-quest
   ```

3. **Install dependencies:**

   ```bash
   uv sync
   ```

   > Note: Package discovery warnings are safe to ignore.

## Playing the Game

### Quick Start

Choose your preferred play mode:

```bash
# Terminal Mode (Interactive CLI)
uv run python play.py

# Local MCP Server (for Claude Desktop)
uv run python server.py

# Remote MCP Server (HTTP/SSE)
uv run python remote_server.py
```

### New Player Guide

First time playing? Use the AI Game Guide to learn the mechanics. Copy the contents of [`game_guide_prompt.md`](game_guide_prompt.md) into your conversation with Claude when using the MCP server. The guide will teach you game mechanics, explain Workato concepts in context, and provide strategic advice tailored to your experience level.

### Play Modes

#### Terminal Mode

Play directly in your terminal with an interactive command-line interface:

```bash
uv run python play.py
```

Example session:

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

#### Claude Desktop (MCP Server)

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

> **Important:** Update the path to match your actual installation location.

#### Claude Code (CLI)

Add the MCP server to your Claude Code configuration:

```bash
claude mcp add integration-quest -- uv --directory /path/to/workato-integration-quest run python server.py
```

Or manually edit `~/.claude/settings.json`:

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

After configuration, restart Claude Code and the game tools will be available.

#### Remote MCP Server

Run the game as a remote MCP server accessible over HTTP:

```bash
uv run python remote_server.py
```

Connect via Claude Desktop:

```json
{
  "mcpServers": {
    "integration-quest-remote": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:8000/sse"]
    }
  }
}
```

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_SERVER_PORT` | `8000` | Server port |
| `MCP_SERVER_HOST` | `0.0.0.0` | Server host |

### Available Commands

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
| `rest` | Recover HP/MP (20% encounter chance) |
| `flee` | Attempt to escape combat |
| `save_game` | Create a checkpoint |
| `load_game` | Restore from checkpoint |

## Character Classes

### Warrior (Integration Engineer)

*"Process more. Process faster."*

| Attribute | Value |
|-----------|-------|
| Primary Stat | Throughput (STR) |
| HP Modifier | +20 |
| MP Modifier | -10 |

**Skills:**

- **Bulk Upsert** — Hit all enemies at once
- **Force Sync** — Ignore armor completely
- **Throughput Surge** — Take two actions per turn

### Mage (Recipe Builder)

*"Everything is just a transformation away."*

| Attribute | Value |
|-----------|-------|
| Primary Stat | Formula Power (INT) |
| HP Modifier | -10 |
| MP Modifier | +30 |

**Skills:**

- **Formula Transform** — Rewrite enemy logic
- **Lookup Table Strike** — Guaranteed hit +50% damage
- **Callable Recipe** — Summon automation ally

### Rogue (API Hacker)

*"There's always a workaround."*

| Attribute | Value |
|-----------|-------|
| Primary Stat | Rate Agility (DEX) |
| HP Modifier | 0 |
| MP Modifier | 0 |

**Skills:**

- **Workaround** — Bypass armor, double damage
- **Rate Limit Dance** — Evade all attacks
- **Custom Connector** — Exploit weaknesses for 3x damage

### Cleric (Support Engineer)

*"No system stays down on my watch."*

| Attribute | Value |
|-----------|-------|
| Primary Stat | Error Resilience (CON) |
| HP Modifier | +10 |
| MP Modifier | +15 |

**Skills:**

- **Error Handler** — Auto-revive from 0 HP (once per combat)
- **Job Recovery** — Restore 40% max HP
- **Escalation** — Call backup ally

## Enemies

### Common (Depth 1-3)

| Enemy | Description |
|-------|-------------|
| Bug | A crawling syntax error |
| Timeout Gremlin | Loves slow APIs |
| Auth Zombie | Expired token, still walking |
| Null Pointer Specter | Expected data, found void |
| Missing Field Imp | Required field not provided |

### Uncommon (Depth 4-6)

| Enemy | Description |
|-------|-------------|
| Rate Limit Guardian | Inflicts Rate Limited status |
| Data Mismatch Hydra | Attacks with 3 heads |
| Schema Drift Phantom | Randomizes stats |
| Pagination Void | Steals inventory items |
| Infinite Loop Serpent | Attacks twice per turn |

### Rare (Depth 7-9)

| Enemy | Description |
|-------|-------------|
| Undocumented API | Immune until examined |
| Frozen Job Golem | 50% chance to skip turn |
| Webhook Storm | AOE damage |
| Legacy Code Lich | Resurrects defeated enemies |
| Spaghetti Code Horror | Tangles your skills |

### Bosses (Every 5th Depth)

| Boss | Depth | Description |
|------|-------|-------------|
| SAP Config Beast | 5 | 47 mandatory fields |
| The Legacy Mainframe | 10 | Running since 1987 |
| The Monolith | 15 | All services in one |
| Technical Debt Dragon | 20 | Every shortcut returns |

## Items

### Weapons (Connectors)

| Weapon | Tier | Damage | Special |
|--------|------|--------|---------|
| HTTP Client | Common | 1d4 | Starting weapon |
| Slack Webhook | Common | 1d6 | +2 vs Communication |
| Salesforce Connector | Uncommon | 2d6 | Bulk Mode: Hit all |
| NetSuite Blade | Rare | 3d6 | Ignores 50% armor |
| SAP RFC Cannon | Legendary | 4d8 | Stuns for 1 turn |
| Workato SDK Staff | Legendary | 3d10 | +5 all stats |

### Armor (Error Handlers)

| Armor | Tier | Protection | Effect |
|-------|------|------------|--------|
| Basic Logging | Common | +1 | See enemy HP |
| Try/Catch Vest | Common | +2 | Survive fatal hit once |
| Retry Logic Armor | Uncommon | +4 | Auto-retry defenses |
| Circuit Breaker Shield | Rare | +6 | Block cascading damage |
| Observability Plate | Legendary | +10 | See all enemy stats |

### Consumables

| Item | Effect |
|------|--------|
| Job Retry Potion | Restore 50 Uptime |
| API Credit Refill | Restore 30 API Credits |
| Token Refresh Vial | Cure "Auth Expired" status |
| API Documentation | Reveal enemy weakness |
| Graceful Degradation Bomb | Guaranteed escape |
| Bulk Operation Scroll | Next attack hits all |
| Recipe Fragment | Collect 3 for +5 max HP |
| Golden Ticket | Skip to next boss room |

## Game Mechanics

### Stats (Workato Themed)

| Stat | Theme | Description |
|------|-------|-------------|
| Uptime | HP | Integration health (0 = system down) |
| API Credits | MP | Fuel for powerful skills |
| Throughput | STR | Records processed per action |
| Formula Power | INT | Transformation complexity |
| Rate Agility | DEX | Avoiding 429 errors |
| Error Resilience | CON | Recovery from failures |

### Room Types

| Type | Theme | Description |
|------|-------|-------------|
| Corridor | Pipeline | Data flows through cables |
| Chamber | App Hub | Vast application instances |
| Treasure | Data Lake | Perfectly normalized JSON |
| Trap | Legacy System | SOAP envelopes and XML namespaces |
| Boss | Core System | Ultimate integrations |

## Project Structure

```
workato-integration-quest/
├── server.py                 # FastMCP server + all 14 tools
├── play.py                   # Terminal mode CLI interface
├── remote_server.py          # Remote MCP server (HTTP/SSE)
├── config.py                 # Game configuration and constants
├── pyproject.toml            # Python project configuration
├── requirements.txt          # Python dependencies
├── game_guide_prompt.md      # Full AI guide system prompt
├── game_guide_prompt_short.md # Condensed guide prompt
├── models/
│   ├── hero.py               # Hero, stats, inventory
│   ├── combat.py             # Combat state, enemies
│   ├── world.py              # Room, dungeon map
│   └── items.py              # Weapons, armor, consumables
├── systems/
│   ├── combat.py             # Damage calc, turn order
│   ├── generation.py         # Procedural dungeon generation
│   ├── progression.py        # XP, leveling, skill unlocks
│   ├── effects.py            # Status effect processing
│   └── dice.py               # Dice rolling utilities
├── data/
│   ├── enemies.json          # 20+ enemy definitions
│   ├── items.json            # Weapons, armor, consumables
│   ├── descriptions.json     # Room templates
│   └── skills.json           # Class skills
└── tests/
    ├── test_dice.py          # Dice rolling unit tests
    └── test_progression.py   # Progression system tests
```

## Development

### Running Tests

```bash
# Run all function tests (31 tests)
uv run python test_all_functions.py

# Run unit tests with pytest
uv run pytest tests/
```

### Adding Content

| Content Type | File |
|--------------|------|
| Enemies | `data/enemies.json` |
| Items | `data/items.json` |
| Skills | `data/skills.json` |
| Room Descriptions | `data/descriptions.json` |

## Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Guidelines

- Follow existing code style and conventions
- Add tests for new features
- Update documentation as needed
- Keep commits focused and atomic

### Ideas for Contributions

- New enemy types with unique mechanics
- Additional character classes
- New weapons, armor, and consumables
- Quality of life improvements
- Bug fixes and optimizations

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Matt Carpenter

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Credits

Built with:

- [FastMCP 2.0](https://github.com/jlowin/fastmcp) — Python MCP server framework
- [Pydantic](https://docs.pydantic.dev/) — Data validation
- [uv](https://docs.astral.sh/uv/) — Fast Python package manager

---

<p align="center">
  <i>"Every successful integration is a dungeon conquered. Every bug fixed is a villain defeated. You are the hero the enterprise needs."</i>
  <br><br>
  <b>Now venture forth, Integration Hero, and may your APIs always return 200 OK!</b>
</p>
