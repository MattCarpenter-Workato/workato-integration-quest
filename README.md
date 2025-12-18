# Integration Quest: The Workato RPG

*"Descend into the Legacy System Dungeons. Connect the disconnected. Automate the manual. Defeat the bugs that plague enterprise workflows."*

A Workato-themed text-based RPG built as a Python MCP (Model Context Protocol) server. Play as an Integration Hero battling through legacy systems, API errors, and enterprise chaos.

---

## Overview

Integration Quest is an interactive RPG where you embody one of four Integration Hero classes, each with unique abilities and playstyles. Navigate through procedurally generated dungeons filled with integration villains, collect powerful connectors (weapons), implement error handlers (armor), and overcome the challenges of enterprise software integration—all through a narrative-driven MCP interface.

## Features

- **4 Character Classes**: Warrior (Integration Engineer), Mage (Recipe Builder), Rogue (API Hacker), Cleric (Support Engineer)
- **20+ Enemy Types**: From humble Bugs to legendary bosses like the Technical Debt Dragon
- **15+ Weapons (Connectors)**: HTTP Client, Salesforce Connector, SAP RFC Cannon, Workato SDK Staff
- **10+ Armor (Error Handlers)**: Try/Catch Vest, Circuit Breaker Shield, Observability Plate
- **15+ Consumables**: Job Retry Potions, API Credit Refills, Webhook Triggers
- **Procedural Dungeon Generation**: Corridors, chambers, treasure rooms, traps, and boss encounters
- **Class-Specific Skills**: Unique abilities like Bulk Upsert, Formula Transform, Workaround, and Error Handler
- **Save/Load System**: Persistent game state with checkpoint restoration
- **Rich Narrative**: Workato-themed descriptions, combat logs, and victory messages

---

## Technical Stack

```
Python 3.11+
mcp[cli] >= 1.9.0
uvicorn / starlette
pydantic
```

---

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/workato-integration-quest.git
cd workato-integration-quest
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the MCP server:
```bash
python server.py
```

The server will start on `http://localhost:8000`.

---

## Configuration

### MCP Client Setup (claude_desktop_config.json)

Add this to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "integration-quest": {
      "url": "http://localhost:8000/mcp",
      "transport": "streamable-http",
      "headers": {
        "Authorization": "Bearer your-secret-token"
      }
    }
  }
}
```

---

## Character Classes

| Class | Role | Primary Focus | HP | MP | Abilities |
|-------|------|---------------|-----|-----|-----------|
| **Warrior** | Integration Engineer | Throughput | +20 | -10 | Bulk Upsert, Force Sync, Throughput Surge |
| **Mage** | Recipe Builder | Formula Power | -10 | +30 | Formula Transform, Lookup Strike, Callable Recipe |
| **Rogue** | API Hacker | Rate Evasion | +0 | +0 | Workaround, Rate Limit Dance, Custom Connector |
| **Cleric** | Support Engineer | Resilience | +10 | +15 | Error Handler, Job Recovery, Escalation |

---

## Stats (Workato Themed)

| Stat | Theme | Description |
|------|-------|-------------|
| **HP** | Uptime | Integration health (0 = system down) |
| **MP** | API Credits | Fuel for powerful actions |
| **STR** | Throughput | Records processed per action |
| **INT** | Formula Power | Transformation complexity |
| **DEX** | Rate Agility | Avoiding 429 errors |
| **CON** | Error Resilience | Recovery from failures |

---

## Game Mechanics

### Combat System
- Turn-based combat with heroes and enemies taking actions
- Damage calculated using dice notation (e.g., 2d6 = roll two 6-sided dice)
- Armor reduces incoming damage
- Status effects can buff, debuff, or disable combatants
- Enemies have special abilities and weaknesses

### Exploration
- Procedurally generated dungeon with interconnected rooms
- Multiple room types: Corridors, Chambers, Treasure, Traps, Boss rooms
- Items and enemies populate rooms dynamically
- Boss encounters every 5 depth levels

### Progression
- Gain XP by defeating enemies
- Level up to increase stats
- Collect Recipe Fragments (3 = +5 max Uptime permanently)
- Find increasingly powerful connectors and error handlers

### Inventory Management
- Collect weapons (connectors), armor (error handlers), and consumables
- Equipment slots: Weapon, Armor, Accessory
- Consumables provide healing, buffs, or utility effects

---

## MCP Tools (14 Available Commands)

| Tool | Description |
|------|-------------|
| `create_character` | Create an Integration Hero and begin your quest |
| `view_status` | View your hero's stats, inventory, and status effects |
| `explore` | Explore the current system, revealing items and enemies |
| `examine` | Examine an enemy, item, or feature in detail |
| `move` | Navigate to an adjacent system (north/south/east/west) |
| `attack` | Attack an integration villain with weapon or skill |
| `defend` | Take a defensive stance, reducing damage by 50% |
| `use_item` | Use a consumable from inventory |
| `pickup` | Pick up an item or connector from the room |
| `equip` | Equip a weapon, armor, or accessory |
| `rest` | Recover Uptime and API Credits (20% encounter chance) |
| `flee` | Attempt to escape combat (success based on Rate Agility) |
| `save_game` | Create a checkpoint for later restoration |
| `load_game` | Restore from a previous checkpoint |

---

## Enemy Gallery

### Common Enemies (Depth 1-3)
- 🐛 **Bug**: A crawling syntax error (20 HP, 1d6 damage)
- ⏱️ **Timeout Gremlin**: Loves slow APIs (25 HP, 1d8 damage)
- 🔐 **Auth Zombie**: Expired token, still walking (22 HP, 1d6 damage)
- 📋 **Null Pointer Specter**: Expected data, found void (18 HP, 2d4 damage)

### Uncommon Enemies (Depth 4-6)
- 🚦 **Rate Limit Guardian**: Inflicts "Rate Limited" status (50 HP, 2d6 damage)
- 🔀 **Data Mismatch Hydra**: 3 heads, each attacks (60 HP, 2d8 damage)
- 📉 **Schema Drift Phantom**: Randomizes your stats each turn (45 HP, 2d6 damage)

### Rare Enemies (Depth 7-9)
- 🏰 **Undocumented API**: Immune until examined (80 HP, 3d6 damage)
- 🔥 **Webhook Storm**: Hits all party members (70 HP, 3d8 damage)
- 📜 **Legacy Code Lich**: Resurrects defeated enemies (85 HP, 2d8 damage)

### Bosses (Every 5th Depth)
- 👹 **SAP Config Beast** (Depth 5): 47 mandatory custom fields (150 HP)
- 🏚️ **The Legacy Mainframe** (Depth 10): Running since 1987 (250 HP)
- 🐉 **The Monolith** (Depth 15): All services in one (400 HP)
- 💀 **Technical Debt Dragon** (Depth 20): Every shortcut returns (500 HP)

---

## Example Session

```
> create_character(name="Matt", role="mage")

📜 **Matt the Recipe Builder** awakens in the Integration Dungeon...

You clutch your Workato SDK prototype—a humble HTTP Client for now, but it
will grow. Somewhere deep below, legacy systems await connection. The air
smells of stale JSON and broken promises.

🎭 Role: Recipe Builder (Mage)
📊 Stats: Uptime 90 | API Credits 80 | Formula Power 14 | Rate Agility 12
⚔️ Equipped: HTTP Client (1d4) | Basic Logging (+1)
🎒 Inventory: Job Retry Potion x2, Token Refresh Vial

💡 Use 'explore' to examine your surroundings.

---

> explore()

🏛️ **THE SALESFORCE ANTECHAMBER**

Opportunity objects drift lazily through the air, their Stage fields glowing
softly in the dim light. Custom fields cover the walls like ancient runes—
hundreds of them, some still undefined.

📍 Exits: [north, east]
📦 Items: [API Documentation Scroll, Slack Webhook]
⚠️ **Rate Limit Guardian** blocks the northern passage!

---

> attack(target="Rate Limit Guardian", skill="Lookup Table Strike")

🔮 You channel Formula Power through your HTTP Client!

⚔️ Combat Log:
- Lookup Table Strike: GUARANTEED HIT
- Damage: 18 (6 base × 1.5 skill bonus × 2 weakness)
- Guardian: 32/50 HP
- Cost: 8 API Credits (72 remaining)

The Guardian retaliates: "429 - TOO MANY REQUESTS"
- Damage to you: 12
- Uptime: 78/90

🎯 Combat continues... Guardian looks weakened.
```

---

## Project Structure

```
integration-quest/
├── server.py              # FastMCP server + tools
├── models/
│   ├── hero.py            # Hero, stats, inventory
│   ├── combat.py          # Combat state, enemies
│   ├── world.py           # Room, dungeon map
│   └── items.py           # Connectors, handlers, consumables
├── systems/
│   ├── combat.py          # Damage calc, turn order, AI
│   ├── generation.py      # Procedural rooms, loot, enemies
│   ├── progression.py     # XP, leveling, skill unlocks
│   └── effects.py         # Status effect processing
├── data/
│   ├── enemies.json       # Enemy definitions by tier
│   ├── items.json         # All item definitions
│   ├── descriptions.json  # Room description templates
│   ├── skills.json        # Class skills
│   └── dialogue.json      # Victory/defeat/level messages
├── storage/
│   └── saves/             # Saved game files (JSON)
├── tests/
│   ├── test_combat.py
│   ├── test_generation.py
│   └── test_progression.py
├── requirements.txt
└── README.md
```

---

## Development Status

### Delivery Checklist

- [ ] All 14 tools implemented with docstrings
- [ ] Token authentication working
- [ ] Session-isolated game state
- [ ] 4 character classes with unique skills
- [ ] 20+ enemy types across 4 tiers
- [ ] 4 boss encounters
- [ ] 15+ weapons (connectors)
- [ ] 10+ armor pieces (error handlers)
- [ ] 15+ consumables
- [ ] 25+ room description templates
- [ ] Balanced progression levels 1-20
- [ ] Save/load persistence
- [ ] No soft-lock scenarios

---

## Lore

In the depths of the enterprise software ecosystem, where legacy systems lurk and API calls echo through endless corridors, Integration Heroes venture forth to connect the disconnected. Armed with connectors forged from REST APIs and protected by error handlers woven from retry logic, these brave souls face down bugs, timeouts, and the dreaded 429 Rate Limit Guardian.

Your quest: Navigate the procedurally generated Integration Dungeon, defeat integration villains, collect powerful Workato connectors, and ultimately face the Technical Debt Dragon—a beast born from every shortcut, every TODO, every "we'll fix it later" that has ever haunted a codebase.

Will you bulk upsert your way to victory? Transform data with formula magic? Dance around rate limits with API hacker finesse? Or heal your team with support engineer resilience?

**The dungeon awaits. The integrations must flow.**

---

## Contributing

Contributions welcome! Please feel free to submit pull requests or open issues for bugs, features, or improvements.

## License

MIT License - See LICENSE file for details

---

*Spec Version: 2.0 | Built with MCP SDK 1.9+ | Powered by Workato lore*
