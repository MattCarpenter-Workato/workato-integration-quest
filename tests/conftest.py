"""
Shared pytest fixtures for Integration Quest tests.
"""

import pytest
import json
from pathlib import Path
from typing import Generator

from models.hero import Hero, StatusEffect
from models.items import Weapon, Armor, Consumable, EquipmentSlots, InventoryItem
from models.world import GameState, Room
from models.combat import Enemy, CombatState
from models.player import PlayerProfile, PlayerSession

from systems.combat import CombatSystem
from systems.generation import DungeonGenerator
from systems.progression import ProgressionSystem


# =============================================================================
# Path Fixtures
# =============================================================================

@pytest.fixture
def project_root() -> Path:
    """Get the project root directory"""
    return Path(__file__).parent.parent


@pytest.fixture
def data_dir(project_root) -> Path:
    """Get the data directory"""
    return project_root / "data"


# =============================================================================
# Data Loading Fixtures
# =============================================================================

@pytest.fixture
def items_data(data_dir) -> dict:
    """Load items.json data"""
    with open(data_dir / "items.json", "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def enemies_data(data_dir) -> dict:
    """Load enemies.json data"""
    with open(data_dir / "enemies.json", "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def skills_data(data_dir) -> dict:
    """Load skills.json data"""
    with open(data_dir / "skills.json", "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def descriptions_data(data_dir) -> dict:
    """Load descriptions.json data"""
    with open(data_dir / "descriptions.json", "r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# Item Fixtures
# =============================================================================

@pytest.fixture
def basic_weapon(items_data) -> Weapon:
    """Create a basic weapon (HTTP Client)"""
    return Weapon(**items_data["weapons"][0])


@pytest.fixture
def uncommon_weapon(items_data) -> Weapon:
    """Create an uncommon weapon (Salesforce Connector)"""
    return Weapon(**items_data["weapons"][2])


@pytest.fixture
def basic_armor(items_data) -> Armor:
    """Create basic armor (Basic Logging)"""
    return Armor(**items_data["armor"][0])


@pytest.fixture
def uncommon_armor(items_data) -> Armor:
    """Create uncommon armor (Retry Logic Armor)"""
    return Armor(**items_data["armor"][2])


@pytest.fixture
def healing_potion(items_data) -> Consumable:
    """Create a healing potion (Job Retry Potion)"""
    return Consumable(**items_data["consumables"][0])


@pytest.fixture
def mp_potion(items_data) -> Consumable:
    """Create an MP potion (API Credit Refill)"""
    return Consumable(**items_data["consumables"][1])


# =============================================================================
# Hero Fixtures
# =============================================================================

@pytest.fixture
def warrior_hero(basic_weapon, basic_armor) -> Hero:
    """Create a warrior hero with basic equipment"""
    return Hero(
        name="TestWarrior",
        role="warrior",
        level=1,
        xp=0,
        uptime=120,
        max_uptime=120,
        api_credits=40,
        max_api_credits=40,
        throughput=14,
        formula_power=10,
        rate_agility=10,
        error_resilience=12,
        equipped=EquipmentSlots(weapon=basic_weapon, armor=basic_armor),
        skills=["bulk_upsert", "force_sync", "throughput_surge"],
        gold=0
    )


@pytest.fixture
def mage_hero(basic_weapon, basic_armor) -> Hero:
    """Create a mage hero with basic equipment"""
    return Hero(
        name="TestMage",
        role="mage",
        level=1,
        xp=0,
        uptime=90,
        max_uptime=90,
        api_credits=80,
        max_api_credits=80,
        throughput=10,
        formula_power=14,
        rate_agility=10,
        error_resilience=10,
        equipped=EquipmentSlots(weapon=basic_weapon, armor=basic_armor),
        skills=["formula_transform", "lookup_table_strike", "callable_recipe"],
        gold=0
    )


@pytest.fixture
def rogue_hero(basic_weapon, basic_armor) -> Hero:
    """Create a rogue hero with basic equipment"""
    return Hero(
        name="TestRogue",
        role="rogue",
        level=1,
        xp=0,
        uptime=100,
        max_uptime=100,
        api_credits=50,
        max_api_credits=50,
        throughput=10,
        formula_power=10,
        rate_agility=14,
        error_resilience=10,
        equipped=EquipmentSlots(weapon=basic_weapon, armor=basic_armor),
        skills=["workaround", "rate_limit_dance", "custom_connector"],
        gold=0
    )


@pytest.fixture
def cleric_hero(basic_weapon, basic_armor) -> Hero:
    """Create a cleric hero with basic equipment"""
    return Hero(
        name="TestCleric",
        role="cleric",
        level=1,
        xp=0,
        uptime=110,
        max_uptime=110,
        api_credits=65,
        max_api_credits=65,
        throughput=10,
        formula_power=10,
        rate_agility=10,
        error_resilience=14,
        equipped=EquipmentSlots(weapon=basic_weapon, armor=basic_armor),
        skills=["error_handler", "job_recovery", "escalation"],
        gold=0
    )


@pytest.fixture
def damaged_hero(warrior_hero) -> Hero:
    """Create a hero with reduced HP and MP"""
    warrior_hero.uptime = warrior_hero.max_uptime // 2
    warrior_hero.api_credits = warrior_hero.max_api_credits // 2
    return warrior_hero


@pytest.fixture
def high_level_hero(warrior_hero) -> Hero:
    """Create a level 5 hero with improved stats"""
    warrior_hero.level = 5
    warrior_hero.xp = 1000
    warrior_hero.throughput = 20
    warrior_hero.formula_power = 15
    warrior_hero.rate_agility = 15
    warrior_hero.error_resilience = 18
    warrior_hero.max_uptime = 200
    warrior_hero.uptime = 200
    warrior_hero.max_api_credits = 80
    warrior_hero.api_credits = 80
    warrior_hero.gold = 500
    return warrior_hero


# =============================================================================
# Enemy Fixtures
# =============================================================================

@pytest.fixture
def common_enemy(enemies_data) -> Enemy:
    """Create a common enemy (Bug)"""
    return Enemy(**enemies_data["common"][0])


@pytest.fixture
def uncommon_enemy(enemies_data) -> Enemy:
    """Create an uncommon enemy (Rate Limit Guardian)"""
    return Enemy(**enemies_data["uncommon"][0])


@pytest.fixture
def rare_enemy(enemies_data) -> Enemy:
    """Create a rare enemy (Undocumented API)"""
    return Enemy(**enemies_data["rare"][0])


@pytest.fixture
def boss_enemy(enemies_data) -> Enemy:
    """Create a boss enemy (SAP Config Beast)"""
    return Enemy(**enemies_data["boss"][0])


@pytest.fixture
def weak_enemy() -> Enemy:
    """Create a very weak enemy for testing kills"""
    return Enemy(
        id="test_weak_enemy",
        name="Test Weak Enemy",
        description="A test enemy",
        hp=1,
        max_hp=1,
        damage_dice="1d1",
        armor=0,
        xp_reward=10,
        gold_reward=5,
        tier="common",
        emoji="🧪",
        loot_table="common"
    )


# =============================================================================
# Room Fixtures
# =============================================================================

@pytest.fixture
def empty_room() -> Room:
    """Create an empty room"""
    return Room(
        id="test_empty_room",
        system_name="Test Empty Chamber",
        room_type="chamber",
        description="An empty test room.",
        exits={"north": "test_next_room"},
        enemies=[],
        items=[],
        is_cleared=True,
        is_discovered=True
    )


@pytest.fixture
def room_with_enemy(common_enemy) -> Room:
    """Create a room with one enemy"""
    return Room(
        id="test_enemy_room",
        system_name="Test Combat Room",
        room_type="corridor",
        description="A room with a test enemy.",
        exits={"north": "test_next_room", "south": "test_prev_room"},
        enemies=[common_enemy],
        items=[],
        is_cleared=False,
        is_discovered=True
    )


@pytest.fixture
def room_with_items(healing_potion, basic_weapon) -> Room:
    """Create a room with items"""
    return Room(
        id="test_item_room",
        system_name="Test Treasure Room",
        room_type="treasure",
        description="A room with test items.",
        exits={"south": "test_prev_room"},
        enemies=[],
        items=[healing_potion, basic_weapon],
        is_cleared=True,
        is_discovered=True
    )


# =============================================================================
# Game State Fixtures
# =============================================================================

@pytest.fixture
def basic_game_state(warrior_hero, empty_room) -> GameState:
    """Create a basic game state"""
    return GameState(
        hero=warrior_hero,
        current_room_id=empty_room.id,
        dungeon_map={empty_room.id: empty_room},
        depth=1
    )


@pytest.fixture
def combat_game_state(warrior_hero, room_with_enemy, common_enemy) -> GameState:
    """Create a game state in combat"""
    game_state = GameState(
        hero=warrior_hero,
        current_room_id=room_with_enemy.id,
        dungeon_map={room_with_enemy.id: room_with_enemy},
        depth=1
    )
    game_state.combat = CombatSystem.initialize_combat(warrior_hero, [common_enemy])
    return game_state


# =============================================================================
# Combat Fixtures
# =============================================================================

@pytest.fixture
def combat_state(warrior_hero, common_enemy) -> CombatState:
    """Create an active combat state"""
    return CombatSystem.initialize_combat(warrior_hero, [common_enemy])


# =============================================================================
# System Fixtures
# =============================================================================

@pytest.fixture
def dungeon_generator() -> DungeonGenerator:
    """Create a dungeon generator"""
    return DungeonGenerator()


# =============================================================================
# Multiplayer Fixtures
# =============================================================================

@pytest.fixture
def player_session() -> PlayerSession:
    """Create an authenticated player session"""
    return PlayerSession(
        email="test@example.com",
        username="TestPlayer",
        is_authenticated=True,
        current_run_score=0
    )


@pytest.fixture
def unauthenticated_session() -> PlayerSession:
    """Create an unauthenticated player session"""
    return PlayerSession(
        email="test@example.com",
        username="TestPlayer",
        is_authenticated=False,
        current_run_score=0
    )
