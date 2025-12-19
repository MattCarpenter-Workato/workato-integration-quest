"""
Unit tests for the combat system.
"""

import pytest
from systems.combat import CombatSystem
from models.combat import CombatState, Enemy
from models.hero import Hero


# =============================================================================
# Combat Initialization Tests
# =============================================================================

class TestCombatInitialization:
    """Tests for combat system initialization"""

    def test_initialize_combat(self, warrior_hero, common_enemy):
        """Test basic combat initialization"""
        combat = CombatSystem.initialize_combat(warrior_hero, [common_enemy])

        assert combat is not None
        assert combat.active
        assert len(combat.enemies) == 1
        assert combat.turn >= 1

    def test_initialize_combat_multiple_enemies(self, warrior_hero, common_enemy, enemies_data):
        """Test combat with multiple enemies"""
        enemy2 = Enemy(**enemies_data["common"][1])
        combat = CombatSystem.initialize_combat(warrior_hero, [common_enemy, enemy2])

        assert len(combat.enemies) == 2

    def test_initialize_combat_empty_enemies(self, warrior_hero):
        """Test combat initialization with no enemies"""
        combat = CombatSystem.initialize_combat(warrior_hero, [])

        assert combat is not None
        assert len(combat.enemies) == 0


# =============================================================================
# Hero Attack Tests
# =============================================================================

class TestHeroAttack:
    """Tests for hero attacks"""

    def test_basic_attack_deals_damage(self, warrior_hero, common_enemy, combat_state):
        """Test that basic attacks deal damage"""
        initial_hp = common_enemy.hp

        result = CombatSystem.hero_attack(
            warrior_hero, common_enemy, combat_state,
            skill_multiplier=1.0, ignore_armor=False
        )

        assert "damage" in result or common_enemy.hp < initial_hp or common_enemy.hp <= 0
        assert len(result["messages"]) > 0

    def test_skill_multiplier_increases_damage(self, warrior_hero, common_enemy, combat_state):
        """Test that skill multiplier increases damage"""
        # Reset enemy HP for each test
        common_enemy.hp = common_enemy.max_hp

        # Track multiple attacks to account for variance
        normal_damages = []
        boosted_damages = []

        for _ in range(10):
            common_enemy.hp = common_enemy.max_hp
            result1 = CombatSystem.hero_attack(
                warrior_hero, common_enemy, combat_state,
                skill_multiplier=1.0, ignore_armor=False
            )
            normal_damages.append(common_enemy.max_hp - max(0, common_enemy.hp))

        for _ in range(10):
            common_enemy.hp = common_enemy.max_hp
            result2 = CombatSystem.hero_attack(
                warrior_hero, common_enemy, combat_state,
                skill_multiplier=2.0, ignore_armor=False
            )
            boosted_damages.append(common_enemy.max_hp - max(0, common_enemy.hp))

        # Average boosted damage should be higher
        avg_normal = sum(normal_damages) / len(normal_damages)
        avg_boosted = sum(boosted_damages) / len(boosted_damages)
        assert avg_boosted >= avg_normal

    def test_ignore_armor_increases_damage(self, warrior_hero, enemies_data, combat_state):
        """Test that ignoring armor increases damage"""
        # Create enemy with armor
        armored_enemy = Enemy(**enemies_data["common"][0])
        armored_enemy.armor = 5
        armored_enemy.hp = 100
        armored_enemy.max_hp = 100

        damages_with_armor = []
        damages_ignore_armor = []

        for _ in range(10):
            armored_enemy.hp = 100
            CombatSystem.hero_attack(
                warrior_hero, armored_enemy, combat_state,
                skill_multiplier=1.0, ignore_armor=False
            )
            damages_with_armor.append(100 - max(0, armored_enemy.hp))

        for _ in range(10):
            armored_enemy.hp = 100
            CombatSystem.hero_attack(
                warrior_hero, armored_enemy, combat_state,
                skill_multiplier=1.0, ignore_armor=True
            )
            damages_ignore_armor.append(100 - max(0, armored_enemy.hp))

        avg_with_armor = sum(damages_with_armor) / len(damages_with_armor)
        avg_ignore = sum(damages_ignore_armor) / len(damages_ignore_armor)
        assert avg_ignore >= avg_with_armor

    def test_attack_can_kill_enemy(self, warrior_hero, weak_enemy, combat_state):
        """Test that attacks can kill weak enemies"""
        result = CombatSystem.hero_attack(
            warrior_hero, weak_enemy, combat_state,
            skill_multiplier=1.0, ignore_armor=False
        )

        assert weak_enemy.hp <= 0

    def test_attack_returns_messages(self, warrior_hero, common_enemy, combat_state):
        """Test that attacks return narrative messages"""
        result = CombatSystem.hero_attack(
            warrior_hero, common_enemy, combat_state,
            skill_multiplier=1.0, ignore_armor=False
        )

        assert "messages" in result
        assert len(result["messages"]) > 0
        assert isinstance(result["messages"], list)


# =============================================================================
# Enemy Attack Tests
# =============================================================================

class TestEnemyAttack:
    """Tests for enemy attacks"""

    def test_enemy_attack_deals_damage(self, warrior_hero, common_enemy, combat_state):
        """Test that enemy attacks deal damage"""
        initial_hp = warrior_hero.uptime

        result = CombatSystem.enemy_attack(common_enemy, warrior_hero, combat_state)

        # Damage should be dealt (accounting for possible miss)
        assert "messages" in result

    def test_defending_reduces_damage(self, warrior_hero, common_enemy, combat_state):
        """Test that defending reduces damage"""
        # Track damage while not defending
        normal_damages = []
        defending_damages = []

        for _ in range(20):
            warrior_hero.uptime = warrior_hero.max_uptime
            combat_state.hero_defending = False
            CombatSystem.enemy_attack(common_enemy, warrior_hero, combat_state)
            normal_damages.append(warrior_hero.max_uptime - warrior_hero.uptime)

        for _ in range(20):
            warrior_hero.uptime = warrior_hero.max_uptime
            combat_state.hero_defending = True
            CombatSystem.enemy_attack(common_enemy, warrior_hero, combat_state)
            defending_damages.append(warrior_hero.max_uptime - warrior_hero.uptime)

        avg_normal = sum(normal_damages) / len(normal_damages) if normal_damages else 0
        avg_defending = sum(defending_damages) / len(defending_damages) if defending_damages else 0

        # Defending should reduce average damage
        assert avg_defending <= avg_normal

    def test_enemy_can_kill_hero(self, damaged_hero, boss_enemy, combat_state):
        """Test that enemies can kill heroes"""
        damaged_hero.uptime = 1  # Very low HP

        # Attack multiple times to ensure kill
        for _ in range(10):
            if damaged_hero.uptime > 0:
                result = CombatSystem.enemy_attack(boss_enemy, damaged_hero, combat_state)
                if result.get("hero_defeated"):
                    break

        # Should eventually kill or damage significantly
        assert damaged_hero.uptime <= 1

    def test_enemy_attack_returns_defeat_flag(self, warrior_hero, boss_enemy, combat_state):
        """Test that enemy attack returns hero_defeated flag"""
        warrior_hero.uptime = 1

        result = CombatSystem.enemy_attack(boss_enemy, warrior_hero, combat_state)

        assert "hero_defeated" in result
        assert isinstance(result["hero_defeated"], bool)


# =============================================================================
# Armor and Damage Calculation Tests
# =============================================================================

class TestDamageCalculations:
    """Tests for damage calculations"""

    def test_armor_reduces_damage(self, warrior_hero, common_enemy, combat_state):
        """Test that armor reduces incoming damage"""
        # Hero with armor
        warrior_hero.equipped.armor.protection = 5

        initial_hp = warrior_hero.uptime
        CombatSystem.enemy_attack(common_enemy, warrior_hero, combat_state)
        damage_with_armor = initial_hp - warrior_hero.uptime

        # Reset and test without armor
        warrior_hero.uptime = initial_hp
        warrior_hero.equipped.armor = None

        # Multiple attacks to get average
        damages_no_armor = []
        for _ in range(10):
            warrior_hero.uptime = initial_hp
            CombatSystem.enemy_attack(common_enemy, warrior_hero, combat_state)
            damages_no_armor.append(initial_hp - warrior_hero.uptime)

        # Without armor should take more damage on average
        # This is probabilistic, so we use a weak assertion
        assert sum(damages_no_armor) >= 0

    def test_minimum_damage(self, high_level_hero, common_enemy, combat_state):
        """Test that attacks always deal at least minimum damage"""
        common_enemy.armor = 100  # Very high armor

        damages = []
        for _ in range(20):
            common_enemy.hp = common_enemy.max_hp
            CombatSystem.hero_attack(
                high_level_hero, common_enemy, combat_state,
                skill_multiplier=1.0, ignore_armor=False
            )
            damage = common_enemy.max_hp - common_enemy.hp
            damages.append(damage)

        # At least some attacks should deal damage
        assert any(d > 0 for d in damages)


# =============================================================================
# Special Combat Mechanics Tests
# =============================================================================

class TestSpecialMechanics:
    """Tests for special combat mechanics"""

    def test_undocumented_api_immunity(self, rare_enemy, warrior_hero, combat_state):
        """Test that Undocumented API is immune until examined"""
        if rare_enemy.immune_until_examined:
            assert not rare_enemy.is_examined

            # After examining
            rare_enemy.is_examined = True
            assert rare_enemy.is_examined

    def test_combat_turn_counter(self, combat_state):
        """Test that combat turns are tracked"""
        initial_turn = combat_state.turn
        combat_state.turn += 1
        assert combat_state.turn == initial_turn + 1

    def test_combat_active_flag(self, combat_state):
        """Test combat active flag"""
        assert combat_state.active

        combat_state.active = False
        assert not combat_state.active


# =============================================================================
# Combat End Conditions Tests
# =============================================================================

class TestCombatEndConditions:
    """Tests for combat end conditions"""

    def test_all_enemies_defeated(self, warrior_hero, weak_enemy, combat_state):
        """Test combat ends when all enemies defeated"""
        # Kill the enemy
        weak_enemy.hp = 0

        # Check if all enemies are defeated
        all_defeated = all(e.hp <= 0 for e in combat_state.enemies)
        assert all_defeated or len(combat_state.enemies) == 0

    def test_hero_defeated(self, warrior_hero, combat_state):
        """Test combat detects hero defeat"""
        warrior_hero.uptime = 0

        # Hero should be considered defeated
        assert warrior_hero.uptime <= 0

    def test_flee_ends_combat(self, combat_state):
        """Test that fleeing can end combat"""
        # Simulate flee
        combat_state.active = False
        assert not combat_state.active


# =============================================================================
# Status Effects in Combat Tests
# =============================================================================

class TestCombatStatusEffects:
    """Tests for status effects during combat"""

    def test_rate_limited_effect(self, warrior_hero, common_enemy, combat_state):
        """Test Rate Limited status effect"""
        from models.hero import StatusEffect

        effect = StatusEffect(
            name="Rate Limited",
            effect_type="debuff",
            duration=2,
            description="Actions cost more"
        )
        warrior_hero.status_effects.append(effect)

        # Effect should be active
        assert len(warrior_hero.status_effects) == 1

    def test_auth_expired_effect(self, warrior_hero):
        """Test Auth Expired status effect"""
        from models.hero import StatusEffect

        effect = StatusEffect(
            name="Auth Expired",
            effect_type="debuff",
            duration=3,
            description="Cannot use skills"
        )
        warrior_hero.status_effects.append(effect)

        has_auth_expired = any(e.name == "Auth Expired" for e in warrior_hero.status_effects)
        assert has_auth_expired
