"""
Integration Quest: The Workato RPG
FastMCP Server Implementation

A Workato-themed text-based RPG where players are Integration Heroes
battling through legacy systems, API errors, and enterprise chaos.
"""

import json
import random
from pathlib import Path
from typing import Literal, Optional, Dict
from datetime import datetime

from fastmcp import FastMCP

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
    REST_ENCOUNTER_CHANCE, FLEE_BASE_CHANCE
)

# Initialize FastMCP server
mcp = FastMCP("integration-quest")

# Game state storage (in-memory, keyed by session)
game_states: Dict[str, GameState] = {}

# Initialize dungeon generator
dungeon_gen = DungeonGenerator()


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
# MCP TOOLS (14 Total)
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
        items_list.append(f"{item.name} ({item.tier})")
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
    return explore()


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

        leveled_up, level_messages = ProgressionSystem.add_experience(hero, total_xp)
        ProgressionSystem.add_gold(hero, total_gold)

        messages.extend(level_messages)

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

    Returns:
        Save confirmation with save ID
    """

    game_state = get_or_create_game_state()
    if not game_state:
        return {"error": ERRORS["no_game"]}

    # Generate save ID
    save_id = f"save_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    game_state.save_id = save_id

    # Save to file
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
def load_game(save_id: str) -> dict:
    """
    Restore from a previous checkpoint.

    Args:
        save_id: Save ID from previous save_game call

    Returns:
        Load confirmation
    """

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


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
