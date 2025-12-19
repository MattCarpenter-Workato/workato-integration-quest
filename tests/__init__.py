"""
Integration Quest Test Suite

This package contains comprehensive tests for the Integration Quest game:

- test_models.py: Unit tests for data models (Hero, Items, World, Combat)
- test_systems.py: Unit tests for game systems (Dice, Progression, Effects, Generation)
- test_combat.py: Unit tests for the combat system
- test_game_tools.py: Integration tests for MCP game tools
- test_dice.py: Legacy dice tests (kept for backwards compatibility)
- test_progression.py: Legacy progression tests (kept for backwards compatibility)

Run all tests with:
    uv run pytest tests/ -v

Run specific test file:
    uv run pytest tests/test_models.py -v

Run with coverage:
    uv run pytest tests/ --cov=. --cov-report=html
"""
