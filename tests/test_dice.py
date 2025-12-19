"""
Test dice rolling system.
"""

import pytest
from systems.dice import roll_dice, roll_d20, roll_percentage


def test_roll_dice_simple():
    """Test basic dice rolling"""
    total, rolls = roll_dice("2d6")
    assert 2 <= total <= 12
    assert len(rolls) == 2
    assert all(1 <= r <= 6 for r in rolls)


def test_roll_dice_with_modifier():
    """Test dice with modifiers"""
    total, rolls = roll_dice("1d6+3")
    assert 4 <= total <= 9
    assert len(rolls) == 1


def test_roll_dice_negative_modifier():
    """Test dice with negative modifiers"""
    total, rolls = roll_dice("1d8-2")
    assert 0 <= total <= 6  # max(0, 1-2) to max(0, 8-2)


def test_roll_d20():
    """Test d20 rolls"""
    for _ in range(10):
        result = roll_d20()
        assert 1 <= result <= 20


def test_roll_percentage():
    """Test percentage rolls"""
    for _ in range(10):
        result = roll_percentage()
        assert 0.0 <= result <= 1.0
