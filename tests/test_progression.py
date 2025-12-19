"""
Test progression system.
"""

import pytest
from models.hero import Hero
from models.items import EquipmentSlots
from systems.progression import ProgressionSystem


def create_test_hero():
    """Create a test hero"""
    return Hero(
        name="TestHero",
        role="warrior",
        level=1,
        xp=0,
        uptime=100,
        max_uptime=100,
        api_credits=50,
        max_api_credits=50,
        throughput=14,
        formula_power=10,
        rate_agility=10,
        error_resilience=12,
        equipped=EquipmentSlots(),
        skills=["bulk_upsert", "force_sync", "throughput_surge"]
    )


def test_xp_required_for_level():
    """Test XP requirement calculation"""
    # XP requirement increases with level
    xp_lvl2 = ProgressionSystem.xp_required_for_level(2)
    xp_lvl3 = ProgressionSystem.xp_required_for_level(3)
    assert xp_lvl2 > 0
    assert xp_lvl3 > xp_lvl2


def test_add_experience_no_level_up():
    """Test adding XP without leveling"""
    hero = create_test_hero()
    leveled_up, messages = ProgressionSystem.add_experience(hero, 50)

    assert not leveled_up
    assert hero.xp == 50
    assert hero.level == 1
    assert len(messages) >= 1


def test_add_experience_with_level_up():
    """Test adding XP that causes level up"""
    hero = create_test_hero()
    initial_level = hero.level
    # Add enough XP to level up (may need more than 250)
    leveled_up, messages = ProgressionSystem.add_experience(hero, 500)

    assert leveled_up
    assert hero.level > initial_level  # Level should increase
    assert hero.uptime == hero.max_uptime  # Should heal on level up


def test_add_gold():
    """Test gold addition"""
    hero = create_test_hero()
    ProgressionSystem.add_gold(hero, 100)
    assert hero.gold == 100


def test_recipe_fragment_collection():
    """Test recipe fragment bonus"""
    hero = create_test_hero()

    # First fragment
    bonus_applied, msg = ProgressionSystem.add_recipe_fragment(hero)
    assert not bonus_applied
    assert hero.recipe_fragments == 1

    # Second fragment
    bonus_applied, msg = ProgressionSystem.add_recipe_fragment(hero)
    assert not bonus_applied
    assert hero.recipe_fragments == 2

    # Third fragment - should apply bonus
    old_max = hero.max_uptime
    bonus_applied, msg = ProgressionSystem.add_recipe_fragment(hero)
    assert bonus_applied
    assert hero.recipe_fragments == 3
    assert hero.max_uptime > old_max
