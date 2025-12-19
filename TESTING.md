# Integration Quest - Testing Guide

This document describes the automated testing systems for Integration Quest.

## Overview

Two complementary testing systems ensure game quality:

1. **Function Tests** (`test_all_functions.py`) - Validates all game functions work correctly
2. **Gameplay Tests** (`test_gameplay.py`) - Simulates intelligent gameplay and progression

## Test Suite 1: Function Tests

### Purpose
Validates that all game functions and features work correctly without trying to win the game. Tests each action, save/load system, combat mechanics, items, and more.

### Usage

```bash
# Run comprehensive function tests
uv run python test_all_functions.py
```

### What It Tests

#### ✅ Character Creation (12 tests)
- All 4 character classes (warrior, mage, rogue, cleric)
- Narrative responses
- Game state initialization
- Class-specific skills and stats

#### ✅ Exploration Actions (3 tests)
- `explore()` - Room exploration
- `view_status()` - Character status
- `examine()` - Examine items and enemies

#### ✅ Item Management (2 tests)
- `pickup()` - Pick up items from rooms
- `use_item()` - Use consumables
- `equip()` - Equip weapons and armor

#### ✅ Movement (2 tests)
- `move()` - Navigate between rooms
- Room transition validation

#### ✅ Combat Actions (4 tests)
- `attack()` - Basic attacks
- `attack(skill=...)` - Skill-based attacks
- `defend()` - Defensive stance
- `flee()` - Escape from combat

#### ✅ Rest System (1 test)
- `rest()` - HP/MP recovery

#### ✅ Save/Load System (3 tests)
- `save_game()` - Create save files
- `load_game()` - Restore from saves
- State restoration validation

### Test Results

**Latest Run: 31/31 tests passed (100% success rate)**

All core game functions validated as working correctly!

### Log Files

Function test logs saved to: `logs/function_test_YYYYMMDD_HHMMSS.log`

Example output:
```
[2025-12-18 18:48:05] [PASS] ✅ PASS: Create warrior character
[2025-12-18 18:48:05] [PASS] ✅ PASS: warrior has narrative response
[2025-12-18 18:48:05] [PASS] ✅ PASS: warrior game state created
...
Total Tests: 31
Passed: 31 ✅
Failed: 0 ❌
Pass Rate: 100.0%
```

## Test Suite 2: Gameplay Tests

### Purpose
Simulates intelligent automated gameplay to test game progression, combat strategy, and overall playability. Tests the game "in action" rather than individual functions.

### Usage

```bash
# Basic usage (warrior, depth 5)
uv run python test_gameplay.py

# Test specific class and depth
uv run python test_gameplay.py --class mage --depth 10

# Custom hero name
uv run python test_gameplay.py --class rogue --name "SpeedRunner" --depth 15

# Specify custom log file
uv run python test_gameplay.py --log my_test.log
```

### Options

- `--class`: Hero class (warrior, mage, rogue, cleric) - default: warrior
- `--depth`: Target depth to reach - default: 5
- `--name`: Hero name - default: TestHero
- `--log`: Custom log file name - default: auto-generated timestamp

### AI Strategy

The automated player uses intelligent decision-making:

1. **Priority 1 - Survival**: Heal when HP < 30%
2. **Priority 2 - Combat**: Handle enemies when in combat
3. **Priority 3 - Exploration**: Explore rooms, collect items, advance deeper

**Combat Logic**:
- Examine enemies before fighting
- Use skills when API Credits > 20
- Flee when HP < 20%
- Basic attack as fallback

**Exploration Logic**:
- Explore each new room
- Pick up first 2 items automatically
- Equip better gear (weapons/armor)
- Move north/down preferentially (to go deeper)

### Log Files

Gameplay test logs saved to: `logs/test_gameplay_YYYYMMDD_HHMMSS.log`

**Log Format:**
```
[TIMESTAMP] [LEVEL] Message

Levels:
- INFO: General information
- ACTION: Game actions with parameters
- RESULT: Action results (narrative + JSON)
- STATE: Full game state snapshots
- ERROR: Errors encountered
- SUMMARY: Final test summary
```

**Example Log:**
```
[2025-12-18 18:41:09] [ACTION] Action #5: attack
[2025-12-18 18:41:09] [ACTION]   Parameters: {
  "target": "Bug",
  "skill": "bulk_upsert"
}
[2025-12-18 18:41:09] [RESULT]   Narrative: ⚔️ You attack Bug with Bulk Upsert...
```

### Test Results

The gameplay test successfully:
- ✅ Creates characters of all classes
- ✅ Explores rooms and examines items
- ✅ Picks up and equips items
- ✅ Navigates through the dungeon
- ✅ Handles combat encounters
- ✅ Manages HP/MP resources
- ✅ Logs 1000+ actions with full detail

## Bug Fixes from Testing

Testing discovered and fixed critical bugs:

### 1. server.py:493 - FunctionTool Reference Error
**Problem**: `move()` function called `explore()` directly, but `explore` was a FunctionTool object.

**Fix**:
```python
return explore.fn() if hasattr(explore, 'fn') else explore()
```

### 2. server.py:337 - Missing Tier Attribute
**Problem**: `explore()` tried to access `.tier` on Consumable objects which don't have it.

**Fix**:
```python
tier = getattr(item, 'tier', 'consumable')  # Safe access
```

## Running Both Test Suites

```bash
# Run function tests first
uv run python test_all_functions.py

# Then run gameplay tests
uv run python test_gameplay.py --depth 5 --class warrior
```

## Continuous Integration

For CI/CD pipelines:

```bash
# Exit with error code if tests fail
uv run python test_all_functions.py || exit 1

# Run quick gameplay validation (depth 2)
uv run python test_gameplay.py --depth 2 --class warrior || exit 1
```

## Test Coverage

### ✅ Fully Tested
- Character creation (all classes)
- All exploration actions
- Item pickup and equipment
- Movement and navigation
- Combat (attack, defend, flee)
- Skills and MP management
- Rest and recovery
- Save/load system
- Status effects
- HP/MP tracking

### ⚠️ Known Limitations

1. **Combat Detection**: Gameplay bot sometimes gets stuck when enemies block paths
2. **Max Actions**: Gameplay tests limited to 500 actions (configurable)
3. **Boss Fights**: Function tests don't validate boss-specific mechanics
4. **Deep Progression**: Gameplay tests typically run to depth 2-5, not full game

## Future Test Improvements

1. ✨ Boss fight validation tests
2. ✨ Status effect interaction tests
3. ✨ Equipment combination tests
4. ✨ Parallel test execution for all classes
5. ✨ Performance benchmarking
6. ✨ Regression test suite
7. ✨ Enemy AI behavior validation

## Contributing

When modifying game code:

1. Run `test_all_functions.py` to verify core functions
2. Run `test_gameplay.py` to validate gameplay flow
3. Check logs for unexpected errors
4. Update tests if new mechanics are added
5. Ensure all tests pass before committing

## Test File Structure

```
integration-quest/
├── test_all_functions.py    # Comprehensive function tests
├── test_gameplay.py          # Automated gameplay simulation
├── logs/                     # Test logs (git ignored)
│   ├── function_test_*.log
│   └── test_gameplay_*.log
└── TESTING.md               # This file
```

## Quick Reference

| Test Type | File | Purpose | Run Time |
|-----------|------|---------|----------|
| Function Tests | `test_all_functions.py` | Validate all functions work | ~2 seconds |
| Gameplay Tests | `test_gameplay.py` | Simulate gameplay progression | Variable (30s-5min) |

## Success Metrics

**Function Tests**: ✅ 31/31 passed (100%)
**Gameplay Tests**: ✅ Successfully completed 1000+ actions
**Bug Fixes**: ✅ 2 critical bugs discovered and fixed
**Coverage**: ✅ All major game systems tested

---

*Last Updated: 2025-12-18*
*Test Framework Version: 1.0*
