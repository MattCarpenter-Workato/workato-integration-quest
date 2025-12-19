"""
Integration Quest: The Workato RPG
FastMCP Server Implementation

A Workato-themed text-based RPG where players are Integration Heroes
battling through legacy systems, API errors, and enterprise chaos.

Supports two modes:
- Single-player (default): JSON file storage, no registration needed
- Multiplayer (MULTIPLAYER_MODE=true): MongoDB + SendGrid, leaderboard enabled
"""

import sys
import os
import json
import random
import re
import secrets
from pathlib import Path
from typing import Literal, Optional, Dict
from datetime import datetime

# Load .env file for local development (before any env var access)
from dotenv import load_dotenv
load_dotenv()

# Debug logging to stderr
print("Integration Quest: Starting server initialization...", file=sys.stderr)

# Check for multiplayer mode
MULTIPLAYER_MODE = os.environ.get("MULTIPLAYER_MODE", "").lower() == "true"
print(f"Integration Quest: Multiplayer mode: {MULTIPLAYER_MODE}", file=sys.stderr)

from fastmcp import FastMCP

print("Integration Quest: FastMCP imported successfully", file=sys.stderr)

# Import models
from models.hero import Hero, StatusEffect
from models.world import GameState, Room
from models.items import Weapon, Armor, Consumable, EquipmentSlots, InventoryItem
from models.combat import CombatState, Enemy

# Import systems
from systems.combat import CombatSystem
from systems.generation import DungeonGenerator
from systems.progression import ProgressionSystem
from systems.effects import StatusEffectManager
from systems.dice import roll_percentage

# Import config
from config import (
    CLASS_BONUSES, BASE_STATS, ERRORS, VICTORY_MESSAGES,
    GAME_OVER_MESSAGES, REST_HP_RECOVERY, REST_MP_RECOVERY,
    REST_ENCOUNTER_CHANCE, FLEE_BASE_CHANCE,
    MIN_USERNAME_LENGTH, MAX_USERNAME_LENGTH, USERNAME_PATTERN
)

# Import multiplayer models and systems (always available for easy mode switching)
from models.player import PlayerSession

# Conditionally initialize multiplayer services
db = None
email_service = None

if MULTIPLAYER_MODE:
    try:
        from systems.database import DatabaseManager
        from systems.email_service import EmailService

        # Validate required environment variables
        required_vars = ["MONGODB_URI", "SENDGRID_API_KEY", "FROM_EMAIL"]
        missing = [v for v in required_vars if not os.environ.get(v)]
        if missing:
            raise EnvironmentError(f"Multiplayer mode requires: {', '.join(missing)}")

        db = DatabaseManager()
        email_service = EmailService()
        print("Integration Quest: Multiplayer services initialized", file=sys.stderr)
    except Exception as e:
        print(f"Integration Quest: Failed to initialize multiplayer: {e}", file=sys.stderr)
        raise

print("Integration Quest: All imports successful", file=sys.stderr)

# Initialize FastMCP server
mcp = FastMCP("integration-quest")

print("Integration Quest: FastMCP server created", file=sys.stderr)

# Game state storage (in-memory, keyed by session)
game_states: Dict[str, GameState] = {}

# Player sessions storage (multiplayer mode only)
player_sessions: Dict[str, PlayerSession] = {}

# Initialize dungeon generator
dungeon_gen = DungeonGenerator()


# ============================================================================
# MULTIPLAYER HELPER FUNCTIONS
# ============================================================================

def get_player_session(session_id: str = "default") -> Optional[PlayerSession]:
    """Get player session if authenticated"""
    return player_sessions.get(session_id)


def require_multiplayer() -> None:
    """Raise error if not in multiplayer mode"""
    if not MULTIPLAYER_MODE:
        raise ValueError("❌ This feature requires multiplayer mode. Set MULTIPLAYER_MODE=true to enable.")


def validate_username(username: str) -> tuple[bool, str]:
    """Validate username format"""
    if len(username) < MIN_USERNAME_LENGTH:
        return False, f"Username must be at least {MIN_USERNAME_LENGTH} characters"
    if len(username) > MAX_USERNAME_LENGTH:
        return False, f"Username must be at most {MAX_USERNAME_LENGTH} characters"
    if not re.match(USERNAME_PATTERN, username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, ""


def generate_token() -> str:
    """Generate a secure 32-character hex token"""
    return secrets.token_hex(16)


def load_latest_save() -> Optional[GameState]:
    """Load the most recent save file automatically"""
    save_dir = Path(__file__).parent / "storage" / "saves"

    if not save_dir.exists():
        return None

    # Find all save files
    save_files = list(save_dir.glob("save_*.json"))

    if not save_files:
        return None

    # Get the most recent save file
    latest_save = max(save_files, key=lambda f: f.stat().st_mtime)

    try:
        with open(latest_save, "r", encoding="utf-8") as f:
            save_data = json.load(f)

        # Restore game state
        game_state = GameState(**save_data)
        game_states["default"] = game_state
        return game_state

    except Exception:
        return None


# Auto-load the latest save file on module initialization
load_latest_save()


def get_or_create_game_state(session_id: str = "default") -> Optional[GameState]:
    """Get game state for session, or None if not initialized"""
    return game_states.get(session_id)


def create_new_game_state(name: str, role: str, session_id: str = "default") -> GameState:
    """Create a new game state"""

    # Create hero with class bonuses
    bonuses = CLASS_BONUSES[role]

    # Calculate stats
    throughput = BASE_STATS["str"] + bonuses.get("str", 0)
    formula_power = BASE_STATS["int"] + bonuses.get("int", 0)
    rate_agility = BASE_STATS["dex"] + bonuses.get("dex", 0)
    error_resilience = BASE_STATS["con"] + bonuses.get("con", 0)

    # Calculate HP and MP
    max_uptime = BASE_STATS["hp"] + bonuses["hp_mod"] + (error_resilience * 5)
    max_api_credits = BASE_STATS["mp"] + bonuses["mp_mod"] + (formula_power * 3)

    # Load starting equipment
    with open(Path(__file__).parent / "data" / "items.json", "r", encoding="utf-8") as f:
        items_data = json.load(f)

    starting_weapon = Weapon(**items_data["weapons"][0])  # HTTP Client
    starting_armor = Armor(**items_data["armor"][0])  # Basic Logging

    # Load starting skills
    with open(Path(__file__).parent / "data" / "skills.json", "r", encoding="utf-8") as f:
        skills_data = json.load(f)

    role_skills = [skill["id"] for skill in skills_data[role]]

    # Create hero
    hero = Hero(
        name=name,
        role=role,
        level=1,
        xp=0,
        uptime=max_uptime,
        max_uptime=max_uptime,
        api_credits=max_api_credits,
        max_api_credits=max_api_credits,
        throughput=throughput,
        formula_power=formula_power,
        rate_agility=rate_agility,
        error_resilience=error_resilience,
        equipped=EquipmentSlots(weapon=starting_weapon, armor=starting_armor),
        skills=role_skills,
        gold=0
    )

    # Add starting potions
    starter_potion = Consumable(**items_data["consumables"][0])  # Job Retry Potion
    hero.inventory.append(InventoryItem(item=starter_potion, quantity=2))

    # Create starting room
    starting_room = dungeon_gen.create_starting_room()

    # Generate first level
    first_level = dungeon_gen.generate_dungeon_level(depth=1, room_count=4)

    # Connect starting room to first generated room
    first_room_id = list(first_level.keys())[0]
    starting_room.exits["north"] = first_room_id

    # Create dungeon map
    dungeon_map = {starting_room.id: starting_room}
    dungeon_map.update(first_level)

    # Create game state
    game_state = GameState(
        hero=hero,
        current_room_id=starting_room.id,
        dungeon_map=dungeon_map,
        depth=1
    )

    game_states[session_id] = game_state
    return game_state


# ============================================================================
# MCP TOOLS (15 Total)
# ============================================================================

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

    Args:
        name: Your hero's name
        role: Character class/role

    Returns:
        Hero creation confirmation and starting stats
    """

    # Create new game state
    game_state = create_new_game_state(name, role)
    hero = game_state.hero

    # Role descriptions
    role_names = {
        "warrior": "Integration Engineer",
        "mage": "Recipe Builder",
        "rogue": "API Hacker",
        "cleric": "Support Engineer"
    }

    narrative = f"""📜 **{name} the {role_names[role]}** awakens in the Integration Dungeon...

You clutch your {hero.equipped.weapon.name}—a humble starting connector, but it will grow.
Somewhere deep below, legacy systems await connection. The air smells of stale JSON and
broken promises.

🎭 **Role**: {role_names[role]} ({role.title()})
📊 **Stats**:
   - Uptime: {hero.uptime}/{hero.max_uptime}
   - API Credits: {hero.api_credits}/{hero.max_api_credits}
   - Throughput (STR): {hero.throughput}
   - Formula Power (INT): {hero.formula_power}
   - Rate Agility (DEX): {hero.rate_agility}
   - Error Resilience (CON): {hero.error_resilience}

⚔️ **Equipped**: {hero.equipped.weapon.name} ({hero.equipped.weapon.damage_dice}) | {hero.equipped.armor.name} (+{hero.equipped.armor.protection})
🎒 **Inventory**: Job Retry Potion x2

💡 Use 'explore' to examine your surroundings, or 'view_status' to see your full character sheet.
"""

    # Add warning if in multiplayer mode but not logged in
    if MULTIPLAYER_MODE:
        session = get_player_session()
        if not session or not session.is_authenticated:
            narrative += "\n⚠️ **You're not logged in!** Your score won't be saved to the leaderboard.\nUse `register_player()` or `login()` to compete on the leaderboard."

    return {
        "narrative": narrative,
        "state": {
            "hero_name": hero.name,
            "role": hero.role,
            "level": hero.level,
            "uptime": f"{hero.uptime}/{hero.max_uptime}",
            "api_credits": f"{hero.api_credits}/{hero.max_api_credits}"
        }
    }


@mcp.tool()
def view_status() -> dict:
    """
    View your Integration Hero's current Uptime, API Credits, stats, inventory, and status effects.

    Returns:
        Complete character status sheet
    """

    game_state = get_or_create_game_state()
    if not game_state:
        return {"error": ERRORS["no_game"]}

    hero = game_state.hero

    # Format inventory
    inventory_list = []
    for inv_item in hero.inventory:
        item = inv_item.item
        qty_str = f"x{inv_item.quantity}" if inv_item.quantity > 1 else ""
        inventory_list.append(f"{item.name} {qty_str}")

    inventory_str = "\n   - ".join(inventory_list) if inventory_list else "Empty"

    # Format skills
    with open(Path(__file__).parent / "data" / "skills.json", "r", encoding="utf-8") as f:
        skills_data = json.load(f)

    skills_list = []
    for skill_id in hero.skills:
        for role_skills in skills_data.values():
            skill = next((s for s in role_skills if s["id"] == skill_id), None)
            if skill:
                skills_list.append(f"{skill['name']} ({skill['cost']} credits): {skill['description']}")
                break

    skills_str = "\n   - ".join(skills_list) if skills_list else "Basic Attack only"

    narrative = f"""📊 **{hero.name} the {hero.role.title()}** - Level {hero.level}

❤️ **Uptime**: {hero.uptime}/{hero.max_uptime}
💙 **API Credits**: {hero.api_credits}/{hero.max_api_credits}
⭐ **XP**: {hero.xp}/{ProgressionSystem.xp_required_for_level(hero.level + 1)} to next level
💰 **Gold**: {hero.gold}

📈 **Stats**:
   - Throughput (STR): {hero.throughput}
   - Formula Power (INT): {hero.formula_power}
   - Rate Agility (DEX): {hero.rate_agility}
   - Error Resilience (CON): {hero.error_resilience}
   - Armor: {hero.get_armor_value()}

⚔️ **Equipment**:
   - Weapon: {hero.equipped.weapon.name if hero.equipped.weapon else "None"} ({hero.equipped.weapon.damage_dice if hero.equipped.weapon else "N/A"})
   - Armor: {hero.equipped.armor.name if hero.equipped.armor else "None"} (+{hero.equipped.armor.protection if hero.equipped.armor else 0})

🎒 **Inventory** ({len(hero.inventory)}/20):
   - {inventory_str}

⚡ **Skills**:
   - {skills_str}

✨ **Status Effects**: {StatusEffectManager.format_effects_list(hero)}
🧩 **Recipe Fragments**: {hero.recipe_fragments} (collect 3 for +5 max Uptime)

📍 **Location**: Depth {game_state.depth} - {game_state.get_current_room().system_name}
{"⚔️ **IN COMBAT**" if game_state.is_in_combat() else ""}
"""

    return {
        "narrative": narrative,
        "state": {
            "level": hero.level,
            "uptime": hero.uptime,
            "max_uptime": hero.max_uptime,
            "api_credits": hero.api_credits,
            "in_combat": game_state.is_in_combat()
        }
    }


@mcp.tool()
def explore() -> dict:
    """
    Explore the current system. Reveals room details, items, connectors, and integration villains.

    Returns:
        Current room description with contents and exits
    """

    game_state = get_or_create_game_state()
    if not game_state:
        return {"error": ERRORS["no_game"]}

    room = game_state.get_current_room()
    room.is_discovered = True

    # Format exits
    exits_str = ", ".join([direction.upper() for direction in room.exits.keys()])

    # Format items
    items_list = []
    for item in room.items:
        tier = getattr(item, 'tier', 'consumable')  # Consumables don't have tier
        items_list.append(f"{item.name} ({tier})")
    items_str = ", ".join(items_list) if items_list else "None"

    # Format enemies
    enemies_list = []
    for enemy in room.enemies:
        if enemy.hp > 0:
            enemies_list.append(f"{enemy.emoji} **{enemy.name}** ({enemy.hp}/{enemy.max_hp} HP)")
    enemies_str = "\n   - ".join(enemies_list) if enemies_list else "None"

    narrative = f"""🏛️ **{room.system_name.upper()}**

{room.description}

📍 **Exits**: [{exits_str}]
📦 **Items**: {items_str}
👹 **Enemies**:
   - {enemies_str}

{"⚠️ Enemies block your path! You must fight or flee." if enemies_list and not room.is_cleared else "✅ Room cleared. You may explore freely."}
"""

    return {
        "narrative": narrative,
        "state": {
            "room_type": room.room_type,
            "has_enemies": len(enemies_list) > 0,
            "has_items": len(room.items) > 0,
            "exits": list(room.exits.keys())
        }
    }


@mcp.tool()
def examine(target: str) -> dict:
    """
    Examine an enemy, item, or system feature in detail.
    Critical for Undocumented API enemies—they're immune until examined!

    Args:
        target: Name of enemy or item to examine

    Returns:
        Detailed information about the target
    """

    game_state = get_or_create_game_state()
    if not game_state:
        return {"error": ERRORS["no_game"]}

    room = game_state.get_current_room()

    # Check if examining an enemy
    for enemy in room.enemies:
        if target.lower() in enemy.name.lower() and enemy.hp > 0:
            enemy.is_examined = True

            weakness_str = f"**Weakness**: {enemy.weakness}" if enemy.weakness else "No known weakness"
            resistance_str = f"**Resistance**: {enemy.resistance}" if enemy.resistance else ""
            special_str = f"**Special**: {enemy.special_ability}" if enemy.special_ability else ""

            narrative = f"""🔍 **{enemy.name.upper()}**

{enemy.description}

**HP**: {enemy.hp}/{enemy.max_hp}
**Damage**: {enemy.damage_dice}
**Armor**: {enemy.armor}
{weakness_str}
{resistance_str}
{special_str}

**XP Reward**: {enemy.xp_reward}
**Gold Reward**: {enemy.gold_reward}

{"💡 This enemy was IMMUNE until examined! You can now damage it." if enemy.immune_until_examined else ""}
"""

            return {
                "narrative": narrative,
                "state": {
                    "examined": target,
                    "enemy_hp": enemy.hp,
                    "enemy_max_hp": enemy.max_hp
                }
            }

    # Check if examining an item
    for item in room.items:
        if target.lower() in item.name.lower():
            narrative = f"""🔍 **{item.name}**

{item.description}

**Tier**: {item.tier}
**Type**: {item.item_type if hasattr(item, 'item_type') else type(item).__name__}

Use 'pickup' to add this to your inventory.
"""

            return {"narrative": narrative}

    return {"error": ERRORS["invalid_target"].format(target=target)}


@mcp.tool()
def move(direction: Literal["north", "south", "east", "west"]) -> dict:
    """
    Navigate to an adjacent system.

    Args:
        direction: Cardinal direction to move

    Returns:
        New room description or failure message
    """

    game_state = get_or_create_game_state()
    if not game_state:
        return {"error": ERRORS["no_game"]}

    room = game_state.get_current_room()

    # Check if in combat
    if game_state.is_in_combat():
        return {"error": "⚔️ You cannot move while in combat! Use 'flee' to escape."}

    # Check if direction exists
    if direction not in room.exits:
        return {"error": ERRORS["invalid_direction"].format(direction=direction)}

    # Check if enemies block the path
    alive_enemies = [e for e in room.enemies if e.hp > 0]
    if alive_enemies and not room.is_cleared:
        return {"error": "⚠️ Enemies block your path! Defeat them first or use 'flee' to escape."}

    # Move to new room
    next_room_id = room.exits[direction]

    # Generate new room if needed
    if next_room_id == "generated" or next_room_id not in game_state.dungeon_map:
        new_depth = game_state.depth + 1
        new_rooms = dungeon_gen.generate_dungeon_level(new_depth, room_count=4)
        game_state.dungeon_map.update(new_rooms)
        next_room_id = list(new_rooms.keys())[0]
        room.exits[direction] = next_room_id
        game_state.depth = new_depth

        if new_depth > game_state.max_depth_reached:
            game_state.max_depth_reached = new_depth

    game_state.current_room_id = next_room_id
    game_state.turn_count += 1
    game_state.update_timestamp()

    # Explore the new room automatically
    return explore.fn() if hasattr(explore, 'fn') else explore()


@mcp.tool()
def attack(target: str, skill: str = "basic_attack") -> dict:
    """
    Attack an integration villain.

    Args:
        target: Enemy name (e.g., "Rate Limit Guardian")
        skill: Skill to use (default: basic_attack, or class skill name)

    Returns:
        Combat result with damage dealt and enemy status
    """

    game_state = get_or_create_game_state()
    if not game_state:
        return {"error": ERRORS["no_game"]}

    hero = game_state.hero
    room = game_state.get_current_room()

    # Find enemy
    enemy = None
    for e in room.enemies:
        if target.lower() in e.name.lower() and e.hp > 0:
            enemy = e
            break

    if not enemy:
        return {"error": ERRORS["invalid_target"].format(target=target)}

    # Initialize combat if not started
    if not game_state.is_in_combat():
        alive_enemies = [e for e in room.enemies if e.hp > 0]
        game_state.combat = CombatSystem.initialize_combat(hero, alive_enemies)

    # Load skill data
    with open(Path(__file__).parent / "data" / "skills.json", "r", encoding="utf-8") as f:
        skills_data = json.load(f)

    # Find skill
    skill_info = None
    for role_skills in skills_data.values():
        skill_info = next((s for s in role_skills if s["id"] == skill), None)
        if skill_info:
            break

    if not skill_info:
        return {"error": f"❓ Skill '{skill}' not found!"}

    # Check MP cost
    mp_cost = int(skill_info["cost"] * StatusEffectManager.get_mp_cost_modifier(hero))
    if hero.api_credits < mp_cost:
        return {"error": ERRORS["insufficient_credits"]}

    # Deduct MP
    hero.api_credits -= mp_cost

    # Execute attack
    result = CombatSystem.hero_attack(
        hero,
        enemy,
        game_state.combat,
        skill_multiplier=skill_info.get("damage_multiplier", 1.0),
        ignore_armor=skill_info.get("ignore_armor", False)
    )

    messages = result["messages"]

    # Check if all enemies defeated
    if all(e.hp <= 0 for e in room.enemies):
        room.is_cleared = True
        game_state.combat = None
        messages.append("\n" + random.choice(VICTORY_MESSAGES))

        # Add XP and gold
        total_xp = sum(e.xp_reward for e in room.enemies)
        total_gold = sum(e.gold_reward for e in room.enemies)
        enemies_killed = len([e for e in room.enemies if e.hp <= 0])

        leveled_up, level_messages = ProgressionSystem.add_experience(hero, total_xp)
        ProgressionSystem.add_gold(hero, total_gold)

        messages.extend(level_messages)

        # Track score in multiplayer mode
        if MULTIPLAYER_MODE:
            session = get_player_session()
            if session and session.is_authenticated:
                session.current_run_score += total_xp
                db.add_score(session.email, total_xp)
                db.increment_enemies_defeated(session.email, enemies_killed)
                messages.append(f"\n🏆 **+{total_xp} points!** (Run total: {session.current_run_score:,})")

    else:
        # Enemy turn
        alive_enemies = [e for e in room.enemies if e.hp > 0]
        for e in alive_enemies:
            enemy_result = CombatSystem.enemy_attack(e, hero, game_state.combat)
            messages.extend(enemy_result["messages"])

            if enemy_result["hero_defeated"]:
                messages.append("\n" + random.choice(GAME_OVER_MESSAGES))
                return {
                    "narrative": "\n".join(messages),
                    "combat_log": result,
                    "state": {"game_over": True}
                }

    narrative = "\n".join(messages)

    return {
        "narrative": narrative,
        "combat_log": result,
        "state": {
            "uptime": hero.uptime,
            "api_credits": hero.api_credits,
            "combat_active": game_state.is_in_combat(),
            "room_cleared": room.is_cleared
        }
    }


@mcp.tool()
def defend() -> dict:
    """
    Defensive stance. Reduces incoming damage by 50% and triggers retry logic if equipped.

    Returns:
        Defense confirmation and turn results
    """

    game_state = get_or_create_game_state()
    if not game_state:
        return {"error": ERRORS["no_game"]}

    if not game_state.is_in_combat():
        return {"error": ERRORS["not_in_combat"]}

    hero = game_state.hero
    game_state.combat.hero_defending = True

    messages = ["🛡️ You take a defensive stance, bracing for incoming attacks!"]

    # Enemy attacks with reduced damage
    room = game_state.get_current_room()
    alive_enemies = [e for e in room.enemies if e.hp > 0]

    for enemy in alive_enemies:
        enemy_result = CombatSystem.enemy_attack(enemy, hero, game_state.combat)
        messages.extend(enemy_result["messages"])

        if enemy_result["hero_defeated"]:
            # Check for try/catch vest
            if hero.equipped.armor and "try" in hero.equipped.armor.name.lower():
                messages.append("💚 Try/Catch Vest activated! You survive with 1 Uptime!")
                hero.uptime = 1
            else:
                messages.append("\n" + random.choice(GAME_OVER_MESSAGES))
                return {
                    "narrative": "\n".join(messages),
                    "state": {"game_over": True}
                }

    # Reset defending for next turn
    game_state.combat.hero_defending = False

    return {
        "narrative": "\n".join(messages),
        "state": {
            "uptime": hero.uptime,
            "combat_active": True
        }
    }


@mcp.tool()
def use_item(item: str, target: str = "self") -> dict:
    """
    Use a consumable from inventory.

    Args:
        item: Item name (e.g., "Job Retry Potion")
        target: Target of item effect (default: self)

    Returns:
        Item usage result
    """

    game_state = get_or_create_game_state()
    if not game_state:
        return {"error": ERRORS["no_game"]}

    hero = game_state.hero

    # Find item in inventory
    consumable = None
    for inv_item in hero.inventory:
        if item.lower() in inv_item.item.name.lower():
            if isinstance(inv_item.item, Consumable):
                consumable = inv_item.item
                break

    if not consumable:
        return {"error": ERRORS["item_not_found"].format(item=item)}

    messages = [f"🧪 You use {consumable.name}!"]

    # Apply effect
    if consumable.effect_type == "heal_hp":
        heal_amount = min(consumable.effect_value, hero.max_uptime - hero.uptime)
        hero.uptime += heal_amount
        messages.append(f"❤️ Restored {heal_amount} Uptime! ({hero.uptime}/{hero.max_uptime})")

    elif consumable.effect_type == "heal_mp":
        restore_amount = min(consumable.effect_value, hero.max_api_credits - hero.api_credits)
        hero.api_credits += restore_amount
        messages.append(f"💙 Restored {restore_amount} API Credits! ({hero.api_credits}/{hero.max_api_credits})")

    elif consumable.effect_type == "cure_status":
        StatusEffectManager.remove_effect(hero, consumable.effect_value)
        messages.append(f"✨ {consumable.effect_value.replace('_', ' ').title()} cured!")

    elif consumable.effect_type == "escape":
        if game_state.is_in_combat():
            game_state.combat.active = False
            messages.append("💨 Graceful degradation successful! You've escaped combat!")

    elif consumable.effect_type == "special":
        if consumable.effect_value == "fragment":
            bonus_applied, fragment_msg = ProgressionSystem.add_recipe_fragment(hero)
            messages.append(fragment_msg)

    # Remove item from inventory
    hero.remove_from_inventory(consumable.id, quantity=1)

    return {
        "narrative": "\n".join(messages),
        "state": {
            "uptime": hero.uptime,
            "api_credits": hero.api_credits
        }
    }


@mcp.tool()
def pickup(item: str) -> dict:
    """
    Pick up an item or connector from the current room.

    Args:
        item: Item name to pick up

    Returns:
        Pickup confirmation
    """

    game_state = get_or_create_game_state()
    if not game_state:
        return {"error": ERRORS["no_game"]}

    hero = game_state.hero
    room = game_state.get_current_room()

    # Find item in room
    found_item = None
    for room_item in room.items:
        if item.lower() in room_item.name.lower():
            found_item = room_item
            break

    if not found_item:
        return {"error": ERRORS["item_not_found"].format(item=item)}

    # Add to inventory
    success = hero.add_to_inventory(found_item, quantity=1)

    if not success:
        return {"error": ERRORS["inventory_full"]}

    # Remove from room
    room.items.remove(found_item)

    return {
        "narrative": f"✅ Picked up **{found_item.name}**! Added to inventory.",
        "state": {
            "inventory_count": len(hero.inventory)
        }
    }


@mcp.tool()
def equip(item: str) -> dict:
    """
    Equip a connector (weapon), error handler (armor), or accessory from inventory.

    Args:
        item: Item name to equip

    Returns:
        Equipment confirmation
    """

    game_state = get_or_create_game_state()
    if not game_state:
        return {"error": ERRORS["no_game"]}

    hero = game_state.hero

    # Find item in inventory
    found_item = None
    for inv_item in hero.inventory:
        if item.lower() in inv_item.item.name.lower():
            found_item = inv_item.item
            break

    if not found_item:
        return {"error": ERRORS["item_not_found"].format(item=item)}

    # Equip based on type
    if isinstance(found_item, Weapon):
        old_weapon = hero.equipped.weapon
        hero.equipped.weapon = found_item
        msg = f"⚔️ Equipped **{found_item.name}** ({found_item.damage_dice})!"
        if old_weapon:
            msg += f" (Unequipped {old_weapon.name})"

    elif isinstance(found_item, Armor):
        old_armor = hero.equipped.armor
        hero.equipped.armor = found_item
        msg = f"🛡️ Equipped **{found_item.name}** (+{found_item.protection} protection)!"
        if old_armor:
            msg += f" (Unequipped {old_armor.name})"

    else:
        return {"error": "❓ This item cannot be equipped."}

    return {
        "narrative": msg,
        "state": {
            "weapon": hero.equipped.weapon.name if hero.equipped.weapon else None,
            "armor": hero.equipped.armor.name if hero.equipped.armor else None
        }
    }


@mcp.tool()
def rest() -> dict:
    """
    Rest to recover Uptime and API Credits.
    Warning: 20% chance of triggering a random encounter!

    Returns:
        Rest results and possible encounter
    """

    game_state = get_or_create_game_state()
    if not game_state:
        return {"error": ERRORS["no_game"]}

    if game_state.is_in_combat():
        return {"error": "⚔️ You cannot rest during combat!"}

    hero = game_state.hero

    # Calculate recovery
    hp_recovered = int((hero.max_uptime - hero.uptime) * REST_HP_RECOVERY)
    mp_recovered = int((hero.max_api_credits - hero.api_credits) * REST_MP_RECOVERY)

    hero.uptime = min(hero.max_uptime, hero.uptime + hp_recovered)
    hero.api_credits = min(hero.max_api_credits, hero.api_credits + mp_recovered)

    messages = [
        "😴 You rest and recover...",
        f"❤️ Uptime restored: +{hp_recovered} ({hero.uptime}/{hero.max_uptime})",
        f"💙 API Credits restored: +{mp_recovered} ({hero.api_credits}/{hero.max_api_credits})"
    ]

    # Random encounter chance
    if roll_percentage() < REST_ENCOUNTER_CHANCE:
        messages.append("\n⚠️ **AMBUSH!** A random encounter interrupts your rest!")

        # Generate random enemy
        room = game_state.get_current_room()
        new_enemy = dungeon_gen._generate_enemies(game_state.depth, "corridor")
        room.enemies.extend(new_enemy)
        room.is_cleared = False

        messages.append(f"👹 {new_enemy[0].name} appears!")

    return {
        "narrative": "\n".join(messages),
        "state": {
            "uptime": hero.uptime,
            "api_credits": hero.api_credits
        }
    }


@mcp.tool()
def flee() -> dict:
    """
    Attempt graceful degradation (escape combat). Success based on Rate Agility.

    Returns:
        Flee attempt result
    """

    game_state = get_or_create_game_state()
    if not game_state:
        return {"error": ERRORS["no_game"]}

    if not game_state.is_in_combat():
        return {"error": ERRORS["not_in_combat"]}

    hero = game_state.hero

    # Calculate flee chance
    flee_chance = FLEE_BASE_CHANCE + (hero.rate_agility * 0.02)  # +2% per DEX point
    success = roll_percentage() < flee_chance

    if success:
        game_state.combat.active = False
        return {
            "narrative": "💨 Graceful degradation successful! You've escaped combat!",
            "state": {"combat_active": False}
        }
    else:
        messages = ["❌ Escape failed! The enemies block your retreat!"]

        # Enemies get free attacks
        room = game_state.get_current_room()
        alive_enemies = [e for e in room.enemies if e.hp > 0]

        for enemy in alive_enemies:
            enemy_result = CombatSystem.enemy_attack(enemy, hero, game_state.combat)
            messages.extend(enemy_result["messages"])

            if enemy_result["hero_defeated"]:
                messages.append("\n" + random.choice(GAME_OVER_MESSAGES))
                return {
                    "narrative": "\n".join(messages),
                    "state": {"game_over": True}
                }

        return {
            "narrative": "\n".join(messages),
            "state": {
                "uptime": hero.uptime,
                "combat_active": True
            }
        }


@mcp.tool()
def save_game() -> dict:
    """
    Create a checkpoint. Returns save ID for later restoration.
    In multiplayer mode, saves to cloud if logged in.

    Returns:
        Save confirmation with save ID
    """

    game_state = get_or_create_game_state()
    if not game_state:
        return {"error": ERRORS["no_game"]}

    # Multiplayer mode - save to MongoDB if logged in
    if MULTIPLAYER_MODE:
        session = get_player_session()
        if session and session.is_authenticated:
            db.save_game_session(
                session.email,
                game_state.model_dump(),
                session.current_run_score
            )
            return {
                "narrative": f"☁️ **Game saved to cloud!**\n\nYour progress is automatically synced.\nCurrent run score: {session.current_run_score:,} points",
                "state": {"save_id": "cloud", "cloud_save": True}
            }
        else:
            return {"error": "❌ Login required to save in multiplayer mode. Use `login()` first."}

    # Single-player mode - save to local JSON file
    save_id = f"save_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    game_state.save_id = save_id

    save_dir = Path(__file__).parent / "storage" / "saves"
    save_dir.mkdir(parents=True, exist_ok=True)

    save_file = save_dir / f"{save_id}.json"

    with open(save_file, "w") as f:
        json.dump(game_state.model_dump(), f, indent=2)

    return {
        "narrative": f"💾 Game saved!\n\n**Save ID**: {save_id}\n\nUse this ID with 'load_game' to restore your progress.",
        "state": {"save_id": save_id}
    }


@mcp.tool()
def load_game(save_id: str = "") -> dict:
    """
    Restore from a previous checkpoint.
    In multiplayer mode, loads from cloud if logged in (save_id is ignored).

    Args:
        save_id: Save ID from previous save_game call (single-player mode only)

    Returns:
        Load confirmation
    """

    # Multiplayer mode - load from MongoDB if logged in
    if MULTIPLAYER_MODE:
        session = get_player_session()
        if session and session.is_authenticated:
            saved_session = db.load_game_session(session.email)
            if not saved_session:
                return {"error": "❌ No cloud save found. Start a new game with `create_character()`."}

            try:
                game_state = GameState(**saved_session["game_state"])
                game_states["default"] = game_state
                session.current_run_score = saved_session.get("current_run_score", 0)

                hero = game_state.hero
                return {
                    "narrative": f"☁️ **Cloud save loaded!**\n\nWelcome back, **{hero.name}**!\n\nLevel {hero.level} {hero.role.title()}\nDepth: {game_state.depth}\nUptime: {hero.uptime}/{hero.max_uptime}\nCurrent run score: {session.current_run_score:,} points",
                    "state": {
                        "hero_name": hero.name,
                        "level": hero.level,
                        "depth": game_state.depth,
                        "cloud_save": True
                    }
                }
            except Exception as e:
                return {"error": f"❌ Failed to load cloud save: {e}"}
        else:
            return {"error": "❌ Login required to load in multiplayer mode. Use `login()` first."}

    # Single-player mode - load from local JSON file
    if not save_id:
        return {"error": "❌ Please provide a save_id. Example: load_game('save_20250115_143022')"}

    save_file = Path(__file__).parent / "storage" / "saves" / f"{save_id}.json"

    if not save_file.exists():
        return {"error": f"❌ Save file '{save_id}' not found!"}

    # Load save data
    with open(save_file, "r") as f:
        save_data = json.load(f)

    # Restore game state
    game_state = GameState(**save_data)
    game_states["default"] = game_state

    hero = game_state.hero

    return {
        "narrative": f"📂 Game loaded!\n\nWelcome back, **{hero.name}**!\n\nLevel {hero.level} {hero.role.title()}\nDepth: {game_state.depth}\nUptime: {hero.uptime}/{hero.max_uptime}",
        "state": {
            "hero_name": hero.name,
            "level": hero.level,
            "depth": game_state.depth
        }
    }


@mcp.tool()
def enter_diagnostic_code(code: str) -> dict:
    """
    Run system diagnostics with a diagnostic code.

    Args:
        code: Diagnostic code sequence

    Returns:
        Diagnostic result
    """

    game_state = get_or_create_game_state()
    if not game_state:
        return {"error": ERRORS["no_game"]}

    hero = game_state.hero

    # Verify diagnostic checksum
    import hashlib
    code_hash = hashlib.md5(code.encode()).hexdigest()
    if code_hash == "c79c28c71f0363cc52f32fb29e130222":
        # Toggle god mode
        if hero.god_mode_active:
            # DISABLE GOD MODE - Restore original stats
            if hero.saved_stats:
                hero.throughput = hero.saved_stats["throughput"]
                hero.formula_power = hero.saved_stats["formula_power"]
                hero.rate_agility = hero.saved_stats["rate_agility"]
                hero.error_resilience = hero.saved_stats["error_resilience"]
                hero.max_uptime = hero.saved_stats["max_uptime"]
                hero.uptime = hero.saved_stats["uptime"]
                hero.max_api_credits = hero.saved_stats["max_api_credits"]
                hero.api_credits = hero.saved_stats["api_credits"]
                hero.gold = hero.saved_stats["gold"]
                hero.level = hero.saved_stats["level"]
                hero.xp = hero.saved_stats["xp"]

                # Remove god mode status effect
                hero.status_effects = [e for e in hero.status_effects if e.name != "God Mode"]

                # Clear saved stats and flag
                hero.saved_stats = None
                hero.god_mode_active = False

                narrative = f"""🌙 **RETURNING TO MORTAL FORM** 🌙

The legendary power fades as {hero.name} returns to their natural state...

**GOD MODE DISABLED**

📊 **RESTORED STATS**:
   - Throughput: {hero.throughput}
   - Formula Power: {hero.formula_power}
   - Rate Agility: {hero.rate_agility}
   - Error Resilience: {hero.error_resilience}

❤️ **Uptime**: {hero.uptime}/{hero.max_uptime}
💙 **API Credits**: {hero.api_credits}/{hero.max_api_credits}
⭐ **Level**: {hero.level}
💰 **Gold**: {hero.gold}

✨ **Status**: Normal (God Mode effect removed)

You are once again bound by mortal limitations. But you are wiser for the experience.
"""

                return {
                    "narrative": narrative,
                    "state": {
                        "god_mode": False,
                        "level": hero.level,
                        "uptime": hero.uptime,
                        "max_uptime": hero.max_uptime,
                        "api_credits": hero.api_credits,
                        "max_api_credits": hero.max_api_credits
                    }
                }
            else:
                # No saved stats to restore (shouldn't happen, but handle gracefully)
                hero.god_mode_active = False
                return {
                    "narrative": "⚠️ God mode disabled, but no saved stats found to restore.",
                    "state": {"god_mode": False}
                }
        else:
            # ENABLE GOD MODE - Save current stats first
            hero.saved_stats = {
                "throughput": hero.throughput,
                "formula_power": hero.formula_power,
                "rate_agility": hero.rate_agility,
                "error_resilience": hero.error_resilience,
                "max_uptime": hero.max_uptime,
                "uptime": hero.uptime,
                "max_api_credits": hero.max_api_credits,
                "api_credits": hero.api_credits,
                "gold": hero.gold,
                "level": hero.level,
                "xp": hero.xp
            }

            # Apply system calibration overrides
            hero.throughput = 999
            hero.formula_power = 999
            hero.rate_agility = 999
            hero.error_resilience = 999

            # Reset resource pools to test values
            hero.max_uptime = 9999
            hero.uptime = 9999
            hero.max_api_credits = 9999
            hero.api_credits = 9999

            # Initialize test economy values
            hero.gold = 999999
            hero.level = 99
            hero.xp = 999999

            # Apply persistent test flag
            test_flag = StatusEffect(
                name="God Mode",
                effect_type="transformed",
                duration=-1,
                description="Ascended beyond mortal limitations",
                stat_modifier={"all": 999}
            )

            # Clear existing flags and set new test state
            hero.status_effects = [e for e in hero.status_effects if e.name != "God Mode"]
            hero.status_effects.append(test_flag)

            # Set god mode flag
            hero.god_mode_active = True

            narrative = f"""⚡ **LEGENDARY POWER ACTIVATED** ⚡

🌟 The ancient Integration Architect's blessing flows through {hero.name}!
✨ You feel the power of infinite connections coursing through your circuits!

**GOD MODE ENABLED**

📊 **ASCENDED STATS**:
   - Throughput: {hero.throughput} (MAXIMUM)
   - Formula Power: {hero.formula_power} (MAXIMUM)
   - Rate Agility: {hero.rate_agility} (MAXIMUM)
   - Error Resilience: {hero.error_resilience} (MAXIMUM)

❤️ **Uptime**: {hero.uptime}/{hero.max_uptime}
💙 **API Credits**: {hero.api_credits}/{hero.max_api_credits}
⭐ **Level**: {hero.level}
💰 **Gold**: {hero.gold}

🔱 **Status**: GOD MODE (Active - use code again to disable)

You are now unstoppable. The dungeon trembles at your presence!
"""

            return {
                "narrative": narrative,
                "state": {
                    "god_mode": True,
                    "level": hero.level,
                    "uptime": hero.uptime,
                    "max_uptime": hero.max_uptime,
                    "api_credits": hero.api_credits,
                    "max_api_credits": hero.max_api_credits
                }
            }

    return {
        "narrative": f"🔧 Diagnostic code '{code}' not recognized. System nominal.",
        "state": {"diagnostic_complete": True}
    }


# ============================================================================
# MULTIPLAYER TOOLS (6 Total - Only available when MULTIPLAYER_MODE=true)
# ============================================================================

@mcp.tool()
def register_player(email: str, username: str) -> dict:
    """
    Register for the Integration Quest leaderboard with your email.
    A login token will be sent to your email address.

    Args:
        email: Your email address (used as your player ID)
        username: Your display name for the leaderboard (3-20 chars, alphanumeric + underscore)

    Returns:
        Registration confirmation
    """
    try:
        require_multiplayer()
    except ValueError as e:
        return {"error": str(e)}

    # Validate username
    valid, error_msg = validate_username(username)
    if not valid:
        return {"error": f"❌ Invalid username: {error_msg}"}

    # Check if email already registered
    if db.get_player(email):
        return {"error": f"❌ Email '{email}' is already registered. Use login() or refresh_token() if you forgot your token."}

    # Check if username taken
    if db.get_player_by_username(username):
        return {"error": f"❌ Username '{username}' is already taken. Please choose another."}

    # Generate token
    token = generate_token()

    # Create player in database
    try:
        db.create_player(email, username, token)
    except ValueError as e:
        return {"error": f"❌ Registration failed: {e}"}

    # Send welcome email with token
    email_sent = email_service.send_welcome_email(email, username, token)

    if email_sent:
        return {
            "narrative": f"""✅ **Account Created!**

Welcome to Integration Quest, **{username}**!

📧 A login token has been sent to: {email}

Check your email and use the token to login:
  `login("{email}", "your-token-here")`

Your token is your password - keep it safe!
If you ever lose it, use `refresh_token("{email}")` to get a new one.
""",
            "state": {"registered": True, "email": email, "username": username}
        }
    else:
        return {
            "narrative": f"""⚠️ **Account Created, but email failed!**

Your account was created, but we couldn't send the welcome email.
Please use `refresh_token("{email}")` to get your login token.
""",
            "state": {"registered": True, "email_failed": True}
        }


@mcp.tool()
def login(email: str, token: str) -> dict:
    """
    Login to your Integration Quest account to track scores on the leaderboard.

    Args:
        email: Your registered email address
        token: Your login token (received via email)

    Returns:
        Login confirmation with your stats
    """
    try:
        require_multiplayer()
    except ValueError as e:
        return {"error": str(e)}

    # Validate token
    if not db.validate_token(email, token):
        return {"error": "❌ Invalid email or token. Use refresh_token() if you forgot your token."}

    # Get player profile
    player = db.get_player(email)
    if not player:
        return {"error": "❌ Player not found. Please register first."}

    # Create session
    session = PlayerSession(
        email=email,
        username=player["username"],
        is_authenticated=True,
        current_run_score=0
    )
    player_sessions["default"] = session

    # Update last active
    db.update_last_active(email)

    # Load existing game session if available
    saved_session = db.load_game_session(email)
    if saved_session:
        try:
            game_state = GameState(**saved_session["game_state"])
            game_states["default"] = game_state
            session.current_run_score = saved_session.get("current_run_score", 0)

            return {
                "narrative": f"""✅ **Welcome back, {player['username']}!**

📊 **Your Stats**:
   - Total Score: {player['total_score']:,} points
   - Best Run: {player['best_run_score']:,} points
   - Enemies Defeated: {player['enemies_defeated']:,}
   - Rank: #{db.get_player_rank(email)}

🎮 **Saved Game Loaded**:
   - Hero: {game_state.hero.name} (Level {game_state.hero.level} {game_state.hero.role.title()})
   - Depth: {game_state.depth}
   - Current Run Score: {session.current_run_score:,} points

Use `view_leaderboard()` to see top players!
""",
                "state": {"logged_in": True, "game_loaded": True}
            }
        except Exception:
            pass  # Failed to load saved game, continue without it

    return {
        "narrative": f"""✅ **Welcome back, {player['username']}!**

📊 **Your Stats**:
   - Total Score: {player['total_score']:,} points
   - Best Run: {player['best_run_score']:,} points
   - Enemies Defeated: {player['enemies_defeated']:,}
   - Rank: #{db.get_player_rank(email)}

🎮 No saved game found. Use `create_character()` to start a new adventure!

Use `view_leaderboard()` to see top players!
""",
        "state": {"logged_in": True, "game_loaded": False}
    }


@mcp.tool()
def refresh_token(email: str) -> dict:
    """
    Request a new login token. The new token will be sent to your email.
    Your old token will no longer work.

    Args:
        email: Your registered email address

    Returns:
        Confirmation that a new token was sent
    """
    try:
        require_multiplayer()
    except ValueError as e:
        return {"error": str(e)}

    # Check if email is registered
    player = db.get_player(email)
    if not player:
        return {"error": f"❌ Email '{email}' is not registered. Use register_player() to create an account."}

    # Generate new token
    new_token = generate_token()

    # Update token in database
    db.update_token(email, new_token)

    # Send email with new token
    email_sent = email_service.send_token_refresh_email(email, player["username"], new_token)

    if email_sent:
        return {
            "narrative": f"""✅ **New Token Sent!**

A new login token has been sent to: {email}

Your old token no longer works.
Check your email and use the new token to login.
""",
            "state": {"token_refreshed": True}
        }
    else:
        return {"error": "❌ Failed to send email. Please try again later."}


@mcp.tool()
def logout() -> dict:
    """
    Logout from your Integration Quest account.
    Your current game will be saved automatically.

    Returns:
        Logout confirmation
    """
    try:
        require_multiplayer()
    except ValueError as e:
        return {"error": str(e)}

    session = get_player_session()
    if not session or not session.is_authenticated:
        return {"error": "❌ You're not logged in."}

    # Save game state if exists
    game_state = get_or_create_game_state()
    if game_state:
        db.save_game_session(
            session.email,
            game_state.model_dump(),
            session.current_run_score
        )

    # Finalize run score
    db.finalize_run(session.email, session.current_run_score)

    # Clear session
    username = session.username
    if "default" in player_sessions:
        del player_sessions["default"]

    return {
        "narrative": f"""👋 **Goodbye, {username}!**

Your game has been saved and your run score recorded.
See you next time, Integration Hero!
""",
        "state": {"logged_out": True}
    }


@mcp.tool()
def view_leaderboard(limit: int = 10) -> dict:
    """
    View the Integration Quest leaderboard.
    See the top players ranked by total score.

    Args:
        limit: Number of players to show (default: 10, max: 50)

    Returns:
        Leaderboard with top players
    """
    try:
        require_multiplayer()
    except ValueError as e:
        return {"error": str(e)}

    limit = min(limit, 50)  # Cap at 50

    leaderboard = db.get_leaderboard(limit)

    if not leaderboard:
        return {
            "narrative": """🏆 **INTEGRATION QUEST LEADERBOARD**

No players yet! Be the first to register and claim the top spot!

Use `register_player()` to join the competition.
""",
            "state": {"leaderboard": []}
        }

    # Format leaderboard
    lines = ["🏆 **INTEGRATION QUEST LEADERBOARD**", ""]

    # Get current player for highlighting
    session = get_player_session()
    current_username = session.username if session and session.is_authenticated else None

    for i, player in enumerate(leaderboard, 1):
        rank_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        you_marker = " ← YOU" if player["username"] == current_username else ""
        lines.append(
            f"  {rank_emoji} **{player['username']}** — {player['total_score']:,} pts ({player['enemies_defeated']:,} kills){you_marker}"
        )

    # Show current player's rank if not in top
    if current_username:
        in_top = any(p["username"] == current_username for p in leaderboard)
        if not in_top and session:
            rank = db.get_player_rank(session.email)
            player = db.get_player(session.email)
            if player:
                lines.append("")
                lines.append(f"  ... ")
                lines.append(f"  {rank}. **{current_username}** — {player['total_score']:,} pts ← YOU")

    return {
        "narrative": "\n".join(lines),
        "state": {"leaderboard": leaderboard}
    }


@mcp.tool()
def view_my_stats() -> dict:
    """
    View your personal stats and leaderboard rank.
    Requires being logged in.

    Returns:
        Your detailed player statistics
    """
    try:
        require_multiplayer()
    except ValueError as e:
        return {"error": str(e)}

    session = get_player_session()
    if not session or not session.is_authenticated:
        return {"error": "❌ You're not logged in. Use login() first."}

    player = db.get_player(session.email)
    if not player:
        return {"error": "❌ Player profile not found."}

    rank = db.get_player_rank(session.email)

    return {
        "narrative": f"""📊 **YOUR STATS — {player['username']}**

🏆 **Rank**: #{rank}
⭐ **Total Score**: {player['total_score']:,} points
🎯 **Best Run**: {player['best_run_score']:,} points
💀 **Enemies Defeated**: {player['enemies_defeated']:,}

📧 **Email**: {session.email}
🎮 **Current Run Score**: {session.current_run_score:,} points

Keep defeating enemies to climb the leaderboard!
""",
        "state": {
            "rank": rank,
            "total_score": player["total_score"],
            "best_run_score": player["best_run_score"],
            "enemies_defeated": player["enemies_defeated"],
            "current_run_score": session.current_run_score
        }
    }


if __name__ == "__main__":
    # Force UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8')
        if sys.stderr.encoding != 'utf-8':
            sys.stderr.reconfigure(encoding='utf-8')

    print("""
===============================================================

     ** INTEGRATION QUEST: MCP SERVER **

     "Connect the disconnected. Automate the manual."

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

    print("\n🎮 Server ready! Connect via MCP client at http://localhost:8000/mcp")
    print("=" * 63 + "\n")

    # Run the MCP server in remote mode with streamable HTTP transport
    mcp.run(transport="streamable-http", path="/mcp")
