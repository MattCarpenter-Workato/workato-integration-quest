"""
Unit tests for game models (Hero, Items, World, Combat).
"""

import pytest
from models.hero import Hero, StatusEffect
from models.items import Weapon, Armor, Consumable, EquipmentSlots, InventoryItem
from models.world import GameState, Room
from models.combat import Enemy, CombatState


# =============================================================================
# Hero Model Tests
# =============================================================================

class TestHeroModel:
    """Tests for Hero model"""

    def test_hero_creation(self, warrior_hero):
        """Test basic hero creation"""
        assert warrior_hero.name == "TestWarrior"
        assert warrior_hero.role == "warrior"
        assert warrior_hero.level == 1
        assert warrior_hero.uptime > 0
        assert warrior_hero.api_credits > 0

    def test_hero_armor_value(self, warrior_hero):
        """Test armor value calculation"""
        armor_value = warrior_hero.get_armor_value()
        assert armor_value >= 0
        assert armor_value == warrior_hero.equipped.armor.protection

    def test_hero_armor_value_no_armor(self, warrior_hero):
        """Test armor value when no armor equipped"""
        warrior_hero.equipped.armor = None
        assert warrior_hero.get_armor_value() == 0

    def test_hero_inventory_add(self, warrior_hero, healing_potion):
        """Test adding items to inventory"""
        initial_count = len(warrior_hero.inventory)
        success = warrior_hero.add_to_inventory(healing_potion)
        assert success
        assert len(warrior_hero.inventory) == initial_count + 1

    def test_hero_inventory_add_duplicate_stacks(self, warrior_hero, healing_potion):
        """Test that duplicate consumables stack"""
        warrior_hero.add_to_inventory(healing_potion)
        warrior_hero.add_to_inventory(healing_potion)

        # Find the item in inventory
        found = False
        for inv_item in warrior_hero.inventory:
            if inv_item.item.id == healing_potion.id:
                assert inv_item.quantity == 2
                found = True
                break
        assert found

    def test_hero_inventory_remove(self, warrior_hero, healing_potion):
        """Test removing items from inventory"""
        warrior_hero.add_to_inventory(healing_potion, quantity=3)
        success = warrior_hero.remove_from_inventory(healing_potion.id, quantity=2)
        assert success

        # Check remaining quantity
        for inv_item in warrior_hero.inventory:
            if inv_item.item.id == healing_potion.id:
                assert inv_item.quantity == 1
                break

    def test_hero_inventory_remove_all(self, warrior_hero, healing_potion):
        """Test removing all of an item from inventory"""
        warrior_hero.add_to_inventory(healing_potion, quantity=2)
        success = warrior_hero.remove_from_inventory(healing_potion.id, quantity=2)
        assert success

        # Item should be completely removed
        for inv_item in warrior_hero.inventory:
            assert inv_item.item.id != healing_potion.id

    def test_hero_inventory_full(self, warrior_hero, healing_potion):
        """Test inventory full condition"""
        from config import MAX_INVENTORY_SIZE

        # Fill inventory with different items
        for i in range(MAX_INVENTORY_SIZE):
            unique_potion = Consumable(
                id=f"test_potion_{i}",
                name=f"Test Potion {i}",
                description="Test",
                tier="common",
                effect_type="heal_hp",
                effect_value=10
            )
            warrior_hero.add_to_inventory(unique_potion)

        # Try to add one more
        overflow_potion = Consumable(
            id="overflow_potion",
            name="Overflow Potion",
            description="Test",
            tier="common",
            effect_type="heal_hp",
            effect_value=10
        )
        success = warrior_hero.add_to_inventory(overflow_potion)
        assert not success

    def test_hero_status_effects(self, warrior_hero):
        """Test adding and checking status effects"""
        effect = StatusEffect(
            name="Rate Limited",
            effect_type="debuff",
            duration=3,
            description="Slower actions"
        )
        warrior_hero.status_effects.append(effect)
        assert len(warrior_hero.status_effects) == 1
        assert warrior_hero.status_effects[0].name == "Rate Limited"


# =============================================================================
# Item Model Tests
# =============================================================================

class TestItemModels:
    """Tests for Item models"""

    def test_weapon_creation(self, basic_weapon):
        """Test weapon creation"""
        assert basic_weapon.name is not None
        assert basic_weapon.damage_dice is not None
        assert basic_weapon.tier in ["common", "uncommon", "rare", "legendary"]

    def test_armor_creation(self, basic_armor):
        """Test armor creation"""
        assert basic_armor.name is not None
        assert basic_armor.protection >= 0
        assert basic_armor.tier in ["common", "uncommon", "rare", "legendary"]

    def test_consumable_creation(self, healing_potion):
        """Test consumable creation"""
        assert healing_potion.name is not None
        assert healing_potion.effect_type in ["heal_hp", "heal_mp", "cure_status", "escape", "special"]
        assert healing_potion.effect_value >= 0

    def test_equipment_slots(self, basic_weapon, basic_armor):
        """Test equipment slots"""
        slots = EquipmentSlots(weapon=basic_weapon, armor=basic_armor)
        assert slots.weapon == basic_weapon
        assert slots.armor == basic_armor

    def test_equipment_slots_empty(self):
        """Test empty equipment slots"""
        slots = EquipmentSlots()
        assert slots.weapon is None
        assert slots.armor is None

    def test_inventory_item_quantity(self, healing_potion):
        """Test inventory item with quantity"""
        inv_item = InventoryItem(item=healing_potion, quantity=5)
        assert inv_item.quantity == 5
        assert inv_item.item == healing_potion


# =============================================================================
# Enemy Model Tests
# =============================================================================

class TestEnemyModel:
    """Tests for Enemy model"""

    def test_enemy_creation(self, common_enemy):
        """Test enemy creation"""
        assert common_enemy.name is not None
        assert common_enemy.hp > 0
        assert common_enemy.max_hp > 0
        assert common_enemy.damage_dice is not None

    def test_enemy_tiers(self, common_enemy, uncommon_enemy, rare_enemy, boss_enemy):
        """Test different enemy tiers"""
        assert common_enemy.tier == "common"
        assert uncommon_enemy.tier == "uncommon"
        assert rare_enemy.tier == "rare"
        assert boss_enemy.tier == "boss"

    def test_enemy_hp_scaling(self, common_enemy, boss_enemy):
        """Test that boss enemies have more HP"""
        assert boss_enemy.max_hp > common_enemy.max_hp

    def test_enemy_xp_scaling(self, common_enemy, boss_enemy):
        """Test that boss enemies give more XP"""
        assert boss_enemy.xp_reward > common_enemy.xp_reward

    def test_enemy_examine_flag(self, common_enemy):
        """Test enemy examine flag"""
        assert not common_enemy.is_examined
        common_enemy.is_examined = True
        assert common_enemy.is_examined


# =============================================================================
# Room Model Tests
# =============================================================================

class TestRoomModel:
    """Tests for Room model"""

    def test_room_creation(self, empty_room):
        """Test room creation"""
        assert empty_room.id is not None
        assert empty_room.system_name is not None
        assert empty_room.room_type in ["corridor", "chamber", "treasure", "trap", "boss"]

    def test_room_exits(self, empty_room):
        """Test room exits"""
        assert "north" in empty_room.exits

    def test_room_with_enemies(self, room_with_enemy):
        """Test room with enemies"""
        assert len(room_with_enemy.enemies) > 0
        assert not room_with_enemy.is_cleared

    def test_room_with_items(self, room_with_items):
        """Test room with items"""
        assert len(room_with_items.items) > 0

    def test_room_cleared_state(self, room_with_enemy):
        """Test room cleared state changes"""
        assert not room_with_enemy.is_cleared
        room_with_enemy.is_cleared = True
        assert room_with_enemy.is_cleared


# =============================================================================
# Game State Model Tests
# =============================================================================

class TestGameStateModel:
    """Tests for GameState model"""

    def test_game_state_creation(self, basic_game_state):
        """Test game state creation"""
        assert basic_game_state.hero is not None
        assert basic_game_state.current_room_id is not None
        assert len(basic_game_state.dungeon_map) > 0

    def test_game_state_get_current_room(self, basic_game_state, empty_room):
        """Test getting current room"""
        room = basic_game_state.get_current_room()
        assert room is not None
        assert room.id == empty_room.id

    def test_game_state_combat_check(self, basic_game_state, combat_game_state):
        """Test combat state checking"""
        assert not basic_game_state.is_in_combat()
        assert combat_game_state.is_in_combat()

    def test_game_state_depth(self, basic_game_state):
        """Test depth tracking"""
        assert basic_game_state.depth == 1
        basic_game_state.depth = 5
        assert basic_game_state.depth == 5

    def test_game_state_max_depth(self, basic_game_state):
        """Test max depth tracking"""
        basic_game_state.depth = 10
        basic_game_state.max_depth_reached = max(basic_game_state.max_depth_reached, basic_game_state.depth)
        assert basic_game_state.max_depth_reached == 10

    def test_game_state_turn_count(self, basic_game_state):
        """Test turn counting"""
        initial_turns = basic_game_state.turn_count
        basic_game_state.turn_count += 1
        assert basic_game_state.turn_count == initial_turns + 1

    def test_game_state_timestamp_update(self, basic_game_state):
        """Test timestamp updates"""
        old_timestamp = basic_game_state.updated_at
        basic_game_state.update_timestamp()
        assert basic_game_state.updated_at >= old_timestamp


# =============================================================================
# Combat State Model Tests
# =============================================================================

class TestCombatStateModel:
    """Tests for CombatState model"""

    def test_combat_state_creation(self, combat_state):
        """Test combat state creation"""
        assert combat_state.active
        assert len(combat_state.enemies) > 0
        assert combat_state.turn >= 1

    def test_combat_state_defending(self, combat_state):
        """Test defending flag"""
        assert not combat_state.hero_defending
        combat_state.hero_defending = True
        assert combat_state.hero_defending

    def test_combat_state_turn_increment(self, combat_state):
        """Test turn increment"""
        initial_turn = combat_state.turn
        combat_state.turn += 1
        assert combat_state.turn == initial_turn + 1
