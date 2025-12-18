# Integration Quest: The Workato RPG
## MCP Server Specification

*"Descend into the Legacy System Dungeons. Connect the disconnected. Automate the manual. Defeat the bugs that plague enterprise workflows."*

---

## Overview

Build a Workato-themed text-based RPG as a Python MCP server. Players are **Integration Heroes** battling through legacy systems, API errors, and enterprise chaos.

## Technical Stack

```
Python 3.11+
mcp[cli] >= 1.9.0
uvicorn / starlette
pydantic
```

## Server Configuration

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("integration-quest")

# Run with: python server.py
if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
```

### Client Config (claude_desktop_config.json)

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

## 🎭 Character Classes (Integration Roles)

| Class | Role | Primary | HP Mod | MP Mod | Abilities |
|-------|------|---------|--------|--------|-----------|
| **Warrior** | Integration Engineer | Throughput | +20 | -10 | Bulk Upsert, Force Sync, Throughput Surge |
| **Mage** | Recipe Builder | Formula Power | -10 | +30 | Formula Transform, Lookup Strike, Callable Recipe |
| **Rogue** | API Hacker | Rate Evasion | +0 | +0 | Workaround, Rate Limit Dance, Custom Connector |
| **Cleric** | Support Engineer | Resilience | +10 | +15 | Error Handler, Job Recovery, Escalation |

---

## 📊 Stats (Workato Themed)

| Stat | Theme | Base | Description |
|------|-------|------|-------------|
| HP | **Uptime** | 100 + (CON×5) | Integration health (0 = system down) |
| MP | **API Credits** | 50 + (INT×3) | Fuel for powerful actions |
| STR | **Throughput** | 10 | Records processed per action |
| INT | **Formula Power** | 10 | Transformation complexity |
| DEX | **Rate Agility** | 10 | Avoiding 429 errors |
| CON | **Error Resilience** | 10 | Recovery from failures |

### Class Bonuses

```python
CLASS_BONUSES = {
    "warrior": {"str": 4, "con": 2, "hp_mod": 20, "mp_mod": -10},
    "mage": {"int": 4, "dex": 2, "hp_mod": -10, "mp_mod": 30},
    "rogue": {"dex": 4, "str": 2, "hp_mod": 0, "mp_mod": 0},
    "cleric": {"con": 4, "int": 2, "hp_mod": 10, "mp_mod": 15},
}
```

---

## 👹 Enemies (Integration Villains)

### Common (Depth 1-3)

| Enemy | HP | Damage | Description |
|-------|-----|--------|-------------|
| 🐛 Bug | 20 | 1d6 | "A crawling syntax error" |
| ⏱️ Timeout Gremlin | 25 | 1d8 | "Loves slow APIs" |
| 🔐 Auth Zombie | 22 | 1d6 | "Expired token, still walking" |
| 📋 Null Pointer Specter | 18 | 2d4 | "Expected data, found void" |
| 📝 Missing Field Imp | 15 | 1d4 | "Required field not provided!" |

### Uncommon (Depth 4-6)

| Enemy | HP | Damage | Special |
|-------|-----|--------|---------|
| 🚦 Rate Limit Guardian | 50 | 2d6 | Inflicts "Rate Limited" (skip turn) |
| 🔀 Data Mismatch Hydra | 60 | 2d8 | 3 heads, each attacks |
| 📉 Schema Drift Phantom | 45 | 2d6 | Randomizes your stats each turn |
| 🕳️ Pagination Void | 40 | 1d10 | Absorbs items from inventory |
| 🔄 Infinite Loop Serpent | 55 | 1d6 | Attacks twice per turn |

### Rare (Depth 7-9)

| Enemy | HP | Damage | Special |
|-------|-----|--------|---------|
| 🏰 Undocumented API | 80 | 3d6 | Immune until "examined" |
| 🧊 Frozen Job Golem | 90 | 2d10 | 50% chance to skip its turn |
| 🔥 Webhook Storm | 70 | 3d8 | Hits all party members |
| 📜 Legacy Code Lich | 85 | 2d8 | Resurrects defeated enemies |
| 🕸️ Spaghetti Code Horror | 75 | 2d6 | Tangles your skills (random skill used) |

### Bosses (Every 5th Depth)

| Boss | Depth | HP | Description |
|------|-------|-----|-------------|
| 👹 **SAP Config Beast** | 5 | 150 | "47 mandatory custom fields protect its core" |
| 🏚️ **The Legacy Mainframe** | 10 | 250 | "RUNNING SINCE 1987. YOU SHALL NOT PASS." |
| 🐉 **The Monolith** | 15 | 400 | "All services in one. None shall escape." |
| 💀 **Technical Debt Dragon** | 20 | 500 | "Every shortcut returns to haunt you" |

---

## ⚔️ Weapons (Connectors)

| Weapon | Tier | Damage | Special | Drop Rate |
|--------|------|--------|---------|-----------|
| HTTP Client | Common | 1d4 | - | Starting |
| Slack Webhook | Common | 1d6 | +2 vs Communication enemies | 60% |
| Gmail Connector | Common | 1d6 | Can attack multiple targets | 55% |
| Jira Blade | Uncommon | 2d4 | Tracks damage dealt | 25% |
| Salesforce Connector | Uncommon | 2d6 | *Bulk Mode*: Hit all enemies | 20% |
| NetSuite Blade | Rare | 3d6 | Ignores 50% armor | 12% |
| ServiceNow Hammer | Rare | 2d10 | Stuns on crit | 10% |
| SAP RFC Cannon | Legendary | 4d8 | Stuns for 1 turn | 3% |
| Custom Connector | Epic | 2d10 | Configurable damage type | 2% |
| Workato SDK Staff | Legendary | 3d10 | +5 to all stats while equipped | 1% |

---

## 🛡️ Armor (Error Handlers)

| Armor | Tier | Protection | Effect |
|-------|------|------------|--------|
| Basic Logging | Common | +1 | See enemy HP |
| Try/Catch Vest | Common | +2 | Survive one fatal hit per room |
| Retry Logic Armor | Uncommon | +4 | Auto-retry failed defenses (3x) |
| Circuit Breaker Shield | Rare | +6 | Blocks cascading damage |
| Observability Plate | Legendary | +10 | See all enemy stats and intents |

---

## 🧪 Consumables (Recipe Components)

| Item | Effect | Drop Rate |
|------|--------|-----------|
| Job Retry Potion | Restore 50 Uptime | 40% |
| API Credit Refill | Restore 30 Credits | 35% |
| Token Refresh Vial | Cure "Auth Expired" status | 25% |
| API Documentation | Reveal enemy weakness | 20% |
| Graceful Degradation Bomb | Escape combat safely | 15% |
| Bulk Operation Scroll | Next attack hits all enemies | 10% |
| Webhook Trigger | Summon random ally for 3 turns | 8% |
| Recipe Fragment | Combine 3 for permanent +5 max Uptime | 5% |
| Golden Ticket | Skip to next boss room | 2% |

---

## 🗺️ Room Types (Systems)

| Type | Weight | Description Template |
|------|--------|---------------------|
| Corridor (Pipeline) | 40% | Data flows through fiber optic cables... |
| Chamber (App Hub) | 30% | A vast application instance hums with activity... |
| Treasure (Data Lake) | 15% | Perfectly normalized JSON awaits... |
| Trap (Legacy System) | 10% | SOAP envelopes rain from above... |
| Boss (Core System) | 5%* | The ERP awakens... |

*Boss rooms only appear at depth % 5 == 0

---

## 📜 Room Descriptions

```python
ROOM_DESCRIPTIONS = {
    "corridor": [
        "Packets of data stream past through fiber optic cables embedded in the walls. A faint '200 OK' echoes in the distance.",
        "A narrow REST endpoint stretches before you. Rate limit warnings flicker on overhead monitors.",
        "The webhook tunnel echoes with incoming payloads. Each footstep triggers a new event.",
        "JSON objects float past like tumbleweeds. You're deep in the data pipeline now.",
        "Logs scroll endlessly on wall-mounted screens. Somewhere, a job just failed.",
    ],
    "chamber": [
        "You enter a vast Salesforce org. Opportunity objects drift like fireflies, their Stage fields glowing softly.",
        "The NetSuite chamber hums with subsidiary records. Custom fields cover every surface like moss.",
        "A Slack workspace materializes around you. Channels branch in every direction. Notifications ping constantly.",
        "The ServiceNow hall stretches endlessly. Ticket queues line the walls like ancient scrolls.",
        "You've entered the HubSpot domain. Contact records swirl in a CRM vortex overhead.",
    ],
    "treasure": [
        "A pristine Data Lake spreads before you. The JSON is perfectly nested. Not a null in sight.",
        "The Clean Data Vault! Normalized tables gleam like gold. Primary keys align in perfect harmony.",
        "You've found the Schema Registry. Every field is documented. Every type is correct. It's beautiful.",
        "An API Response Cache glitters with pre-fetched data. No latency here—pure, instant access.",
        "The Golden Pipeline! Every transformation succeeds. Every record maps perfectly. You weep with joy.",
    ],
    "trap": [
        "SOAP envelopes rain from the ceiling! XML namespaces tangle around your feet!",
        "The floor is littered with deprecated API versions. One wrong step triggers a breaking change!",
        "A legacy FTP server blocks your path. The credentials are written in COBOL on a sticky note.",
        "You've stumbled into the CSV Parsing Pit! Unescaped commas everywhere! Encodings shift randomly!",
        "The OAuth1.0 Chamber! Signature base strings must be constructed BY HAND. There is no escape.",
    ],
    "boss": [
        "The SAP Configuration Beast awakens! Its body is armored with 47 mandatory custom fields. Each must be filled correctly to proceed.",
        "THE LEGACY MAINFRAME SPEAKS: 'I HAVE RUN SINCE 1987. MY BATCH JOBS TAKE 6 HOURS. YOU. SHALL. NOT. PASS.'",
        "The Monolith rises—a single codebase containing ALL business logic. Microservices cry out in terror.",
        "Technical Debt Dragon unfurls its wings. Every shortcut, every TODO, every 'we'll fix it later' has manifest into THIS.",
        "The Enterprise Service Bus ROARS. Hundreds of point-to-point integrations pulse through its corrupted core.",
    ],
}
```

---

## ⚡ Skills by Class

### Integration Engineer (Warrior)

| Skill | Cost | Effect |
|-------|------|--------|
| Bulk Upsert | 15 Credits | Hit all enemies for weapon damage |
| Force Sync | 20 Credits | Ignore enemy armor completely |
| Throughput Surge | 10 Credits | Take two actions this turn |

### Recipe Builder (Mage)

| Skill | Cost | Effect |
|-------|------|--------|
| Formula Transform | 12 Credits | Change enemy weakness type |
| Lookup Table Strike | 8 Credits | Guaranteed hit, +50% damage |
| Callable Recipe | 25 Credits | Summon automation ally for 3 turns |

### API Hacker (Rogue)

| Skill | Cost | Effect |
|-------|------|--------|
| Workaround | 10 Credits | Bypass armor, +100% damage |
| Rate Limit Dance | 15 Credits | Evade all attacks this turn |
| Custom Connector | 20 Credits | Exploit weakness for 3x damage |

### Support Engineer (Cleric)

| Skill | Cost | Effect |
|-------|------|--------|
| Error Handler | 30 Credits | Auto-revive from 0 Uptime (once per combat) |
| Job Recovery | 20 Credits | Restore 40% of max Uptime |
| Escalation | 25 Credits | Call backup (+1 ally for combat) |

---

## 🎮 MCP Tools (14 Total)

### 1. `create_character`

```python
@mcp.tool()
def create_character(
    name: str, 
    role: Literal["warrior", "mage", "rogue", "cleric"]
) -> dict:
    """
    Create an Integration Hero and begin your quest.
    
    Roles:
    - warrior (Integration Engineer): High Throughput, bulk operations
    - mage (Recipe Builder): Formula Power, transformations  
    - rogue (API Hacker): Rate Agility, workarounds
    - cleric (Support Engineer): Error Resilience, recovery
    """
```

### 2. `view_status`

```python
@mcp.tool()
def view_status() -> dict:
    """View your Integration Hero's current Uptime, API Credits, stats, inventory, and status effects."""
```

### 3. `explore`

```python
@mcp.tool()
def explore() -> dict:
    """Explore the current system. Reveals room details, items, connectors, and integration villains."""
```

### 4. `examine`

```python
@mcp.tool()
def examine(target: str) -> dict:
    """
    Examine an enemy, item, or system feature in detail.
    Critical for Undocumented API enemies—they're immune until examined!
    """
```

### 5. `move`

```python
@mcp.tool()
def move(direction: Literal["north", "south", "east", "west"]) -> dict:
    """Navigate to an adjacent system. Returns new room description or failure."""
```

### 6. `attack`

```python
@mcp.tool()
def attack(target: str, skill: str = "basic_attack") -> dict:
    """
    Attack an integration villain.
    
    Args:
        target: Enemy name (e.g., "Rate Limit Guardian")
        skill: Skill to use (default: basic_attack, or class skill name)
    """
```

### 7. `defend`

```python
@mcp.tool()
def defend() -> dict:
    """Defensive stance. Reduces incoming damage by 50% and triggers retry logic if equipped."""
```

### 8. `use_item`

```python
@mcp.tool()
def use_item(item: str, target: str = "self") -> dict:
    """
    Use a consumable from inventory.
    
    Args:
        item: Item name (e.g., "Job Retry Potion")
        target: Target of item effect (default: self)
    """
```

### 9. `pickup`

```python
@mcp.tool()
def pickup(item: str) -> dict:
    """Pick up an item or connector from the current room."""
```

### 10. `equip`

```python
@mcp.tool()
def equip(item: str) -> dict:
    """Equip a connector (weapon), error handler (armor), or accessory from inventory."""
```

### 11. `rest`

```python
@mcp.tool()
def rest() -> dict:
    """
    Rest to recover Uptime and API Credits.
    Warning: 20% chance of triggering a random encounter!
    """
```

### 12. `flee`

```python
@mcp.tool()
def flee() -> dict:
    """Attempt graceful degradation (escape combat). Success based on Rate Agility."""
```

### 13. `save_game`

```python
@mcp.tool()
def save_game() -> dict:
    """Create a checkpoint. Returns save ID for later restoration."""
```

### 14. `load_game`

```python
@mcp.tool()
def load_game(save_id: str) -> dict:
    """Restore from a previous checkpoint."""
```

---

## 📦 Game State Schema

```python
from pydantic import BaseModel
from typing import Optional, Literal

class GameState(BaseModel):
    hero: Hero
    current_room: Room
    dungeon_map: dict[str, Room]
    combat: Optional[CombatState]
    depth: int
    turn_count: int
    recipe_fragments: int  # Collect 3 for +5 max Uptime
    flags: dict[str, any]

class Hero(BaseModel):
    name: str
    role: str
    level: int
    xp: int
    uptime: int          # HP
    max_uptime: int
    api_credits: int     # MP
    max_api_credits: int
    throughput: int      # STR
    formula_power: int   # INT
    rate_agility: int    # DEX
    error_resilience: int # CON
    inventory: list[Item]
    equipped: EquipmentSlots
    status_effects: list[StatusEffect]
    gold: int
    skills: list[str]

class Room(BaseModel):
    id: str
    room_type: Literal["corridor", "chamber", "treasure", "trap", "boss"]
    system_name: str  # e.g., "Salesforce Org", "Legacy FTP"
    description: str
    exits: dict[str, str]
    items: list[Item]
    enemies: list[Enemy]
    is_cleared: bool
    is_discovered: bool

class Enemy(BaseModel):
    id: str
    name: str
    hp: int
    max_hp: int
    damage: str  # dice notation
    armor: int
    weakness: Optional[str]
    special_ability: Optional[str]
    xp_reward: int
    loot_table: str

class CombatState(BaseModel):
    active: bool
    enemies: list[Enemy]
    turn_order: list[str]
    current_turn: int
    round_num: int
    hero_defending: bool
```

---

## 🎭 Status Effects

| Effect | Duration | Description |
|--------|----------|-------------|
| Rate Limited | 1 turn | Skip next turn |
| Auth Expired | Until cured | -50% damage dealt |
| Transformed | 3 turns | Random stat swap |
| Buffered | 3 turns | +25% damage |
| Cached | 3 turns | +3 armor |
| Debugging | Combat | Can see enemy HP/intent |
| Throttled | 2 turns | Half API Credit costs |

---

## 💬 Message Templates

### Victory Messages

```python
VICTORY_MESSAGES = [
    "✅ The bug is squashed! Your recipe runs green.",
    "🔗 Integration successful! Data flows freely once more.",
    "📡 The rate limiter falls! '200 OK' echoes through the dungeon.",
    "⚡ You've connected the disconnected. The workflow is complete.",
    "🏆 The legacy system acknowledges your authority. COBOL bows before you.",
    "🎉 Job completed successfully! 0 errors, 0 warnings.",
    "💾 The API responds with valid JSON. You've won... this time.",
]
```

### Game Over Messages

```python
GAME_OVER_MESSAGES = [
    "💀 SYSTEM DOWN. Your integration has crashed. Jobs pile up eternally...",
    "❌ Error 500: Internal Hero Failure. Support tickets multiply in your absence.",
    "⏱️ Connection timeout. Your adventure has... timed out.",
    "🏚️ The Monolith consumes you. You become part of the legacy code. Forever.",
    "📉 Uptime: 0%. SLA breached. The on-call engineer is summoned... but it's too late.",
    "🔄 Infinite loop detected. Your consciousness spins forever in the void.",
]
```

### Level Up Messages

```python
LEVEL_UP_MESSAGES = [
    "⬆️ LEVEL UP! Your integration skills grow stronger!",
    "🌟 New certification unlocked! Your hero advances to level {level}!",
    "📈 Experience processed! You've leveled up to {level}!",
    "🎓 Training complete! Welcome to level {level}, Integration Hero!",
]
```

---

## 🔧 Response Format

All tool responses follow this structure:

```json
{
  "narrative": "Immersive description of what happened",
  "combat_log": {
    "action": "attack",
    "damage_dealt": 24,
    "damage_received": 8,
    "enemy_status": "Bug: 0/20 HP (defeated)",
    "xp_gained": 15
  },
  "state": {
    "uptime": 82,
    "max_uptime": 100,
    "api_credits": 65,
    "combat_active": false,
    "room_cleared": true
  },
  "loot": ["Job Retry Potion", "15 gold"],
  "hint": "The north passage leads deeper into the dungeon..."
}
```

---

## ⚠️ Error Messages (In Character)

```python
ERRORS = {
    "no_game": "🚫 No active integration detected. Use create_character to initialize a new hero.",
    "invalid_target": "❓ Target '{target}' not found in current scope. Check your room's contents.",
    "not_in_combat": "😌 No active incidents. The system is peaceful... for now.",
    "inventory_full": "📦 Inventory buffer overflow! Drop something before picking up more.",
    "insufficient_credits": "💳 Insufficient API Credits! Rest or use a refill potion.",
    "invalid_direction": "🧱 Cannot move {direction}. No endpoint exists in that direction.",
    "item_not_found": "🔍 '{item}' not found in inventory. Check your loadout.",
    "already_equipped": "⚙️ '{item}' is already equipped in that slot.",
    "enemy_immune": "🛡️ The {enemy} is immune! Try using 'examine' first to find its weakness.",
}
```

---

## 📁 Project Structure

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

## ✅ Delivery Checklist

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
- [ ] README with lore and setup instructions

---

## 🎮 Example Session

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
hundreds of them, some still undefined. A faint humming suggests an API call 
in progress somewhere nearby.

The floor is littered with old Apex triggers. Step carefully.

📍 Exits: [north, east]
📦 Items: [API Documentation Scroll, Slack Webhook]
⚠️ **Rate Limit Guardian** blocks the northern passage!

---

> examine(target="Rate Limit Guardian")

🔍 **RATE LIMIT GUARDIAN**

A towering construct of HTTP 429 responses stacked impossibly high. Red 
warning lights pulse where eyes should be. Its body shifts between states—
sometimes solid, sometimes rate-limited itself.

HP: 50/50 | Armor: 2 | Weakness: Patience (attacks after waiting deal +50%)
Special: "Too Many Requests" - Can inflict Rate Limited status (skip turn)
XP Reward: 35

💡 Its rate limiting works both ways—if you can wait it out...

---

> attack(target="Rate Limit Guardian", skill="Lookup Table Strike")

🔮 You channel Formula Power through your HTTP Client!

Your Lookup Table Strike bypasses the queue entirely—cached data from a 
previous successful call! The Guardian staggers as valid responses pierce 
its defenses!

⚔️ Combat Log:
- Lookup Table Strike: GUARANTEED HIT
- Damage: 18 (6 base × 1.5 skill bonus × 2 weakness)
- Guardian: 32/50 HP
- Cost: 8 API Credits (72 remaining)

The Guardian retaliates: "429 - TOO MANY REQUESTS"
- Damage to you: 12
- Uptime: 78/90
- ⚡ Status Inflicted: Rate Limited (skip next turn)

🎯 Combat continues... Guardian looks weakened.
💡 You're rate limited! Consider using 'defend' or an item next turn.

---

> use_item(item="Token Refresh Vial")

🧪 You consume the Token Refresh Vial!

Fresh OAuth tokens flood your system. The Rate Limited status dissolves 
as your credentials renew. You feel... authorized.

✅ Status Removed: Rate Limited
📦 Inventory: Job Retry Potion x2 (Token Refresh Vial consumed)

The Guardian attacks during your recovery!
- Damage: 10
- Uptime: 68/90

💡 You can act next turn! One more solid hit should finish it.

---

> attack(target="Rate Limit Guardian", skill="Formula Transform")

🔮 FORMULA TRANSFORM!

You rewrite the Guardian's very nature—transforming its rate limiting 
logic into a self-destruct sequence!

"workato.transform(guardian.core, 'deprecated')"

The Guardian's warning lights turn green, then fade entirely. It crumbles 
into a pile of successful response codes.

✅ **VICTORY!**

⚔️ Final Blow: 24 damage (Guardian: 0/50 HP)
🏆 XP Gained: 35 (Total: 35/100)
💰 Gold: +20 (Total: 20)
📦 Loot Dropped: [Retry Logic Armor (+4 protection)]

The northern passage is now clear. Deeper systems await...
```

---

*Spec Version: 2.0 | Theme: Workato Integration Quest | MCP SDK: 1.9+*
