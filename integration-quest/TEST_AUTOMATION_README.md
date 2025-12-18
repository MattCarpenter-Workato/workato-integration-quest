# Integration Quest - Automated Testing

This document describes the automated gameplay testing system for Integration Quest.

## Overview

The automated testing system simulates intelligent gameplay, logs every action, and validates game mechanics without manual intervention.

## Files Created

1. **test_gameplay.py** - Main automated testing script
2. **logs/** - Directory containing test run logs (git ignored)
3. **.gitignore** - Updated to exclude log files

## Bug Fixes Applied

During test development, the following bugs in the game server were discovered and fixed:

### 1. server.py Line 493: FunctionTool Reference Error
**Problem**: The `move()` function called `explore()` directly, but `explore` was a FunctionTool object, not a callable function.

**Fix**: Changed `return explore()` to `return explore.fn() if hasattr(explore, 'fn') else explore()`

### 2. server.py Line 337: Missing Tier Attribute on Consumables
**Problem**: The `explore()` function tried to access `.tier` attribute on all items, but Consumable objects don't have this attribute.

**Fix**: Changed `items_list.append(f"{item.name} ({item.tier})")` to use `getattr(item, 'tier', 'consumable')` for safe access.

## Usage

### Basic Usage

```bash
# Run with default settings (warrior, depth 5)
uv run python test_gameplay.py

# Run with specific class and depth
uv run python test_gameplay.py --class mage --depth 10

# Run with custom name
uv run python test_gameplay.py --class rogue --name "SpeedRunner" --depth 15

# Specify custom log file name
uv run python test_gameplay.py --log my_test.log
```

### Available Options

- `--class`: Hero class (warrior, mage, rogue, cleric) - default: warrior
- `--depth`: Target depth to reach - default: 5
- `--name`: Hero name - default: TestHero
- `--log`: Custom log file name - default: auto-generated timestamp

## How It Works

### GameplayLogger Class

Logs all game actions and state changes to timestamped log files in the `logs/` directory.

**Features**:
- Action logging with parameters
- Full game state snapshots
- Result logging (narrative + JSON)
- Automatic timestamping
- Final test summary with success/failure status

### AutomatedPlayer Class

Simulates intelligent gameplay with strategic decision-making.

**AI Strategy**:
1. **Priority 1 - Survival**: Heal when HP < 30%
2. **Priority 2 - Combat**: Handle enemies when in combat
3. **Priority 3 - Exploration**: Explore rooms, collect items, advance deeper

**Combat Logic**:
- Examine enemies before fighting (especially Undocumented API)
- Use skills when API Credits > 20
- Flee when HP < 20%
- Basic attack as fallback

**Exploration Logic**:
- Explore each new room
- Pick up first 2 items automatically
- Equip better gear (weapons/armor)
- Move north/down preferentially (to go deeper)

## Log Files

All test runs create detailed log files in `logs/test_gameplay_YYYYMMDD_HHMMSS.log`

### Log Format

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

### Example Log Snippet

```
[2025-12-18 18:41:09] [ACTION] Action #5: attack
[2025-12-18 18:41:09] [ACTION]   Parameters: {
  "target": "Bug",
  "skill": "bulk_upsert"
}
[2025-12-18 18:41:09] [RESULT]   Narrative: ⚔️ You attack Bug with Bulk Upsert...
[2025-12-18 18:41:09] [RESULT]   Full Result: {...}
```

## Test Results

The automated test successfully:
- ✅ Creates characters of all classes
- ✅ Explores rooms and examines items
- ✅ Picks up and equips items
- ✅ Navigates through the dungeon
- ✅ Handles combat encounters
- ✅ Manages HP/MP resources
- ✅ Logs every action with full detail

## Known Limitations

1. **Combat Detection**: The bot sometimes gets stuck in rooms with enemies blocking exits, repeatedly trying to move instead of fighting. This needs improved logic to detect "enemies blocking path" errors and trigger combat.

2. **Max Actions Limit**: Tests are limited to 500 actions to prevent infinite loops. For deep dungeon runs, this may need to be increased.

3. **Static Strategy**: The AI uses a simple priority-based strategy. More sophisticated tactical decisions could improve performance.

## Future Improvements

1. Detect "enemies blocking path" messages and trigger combat
2. Better skill selection based on enemy weaknesses
3. Resource management (rest when safe, not mid-combat)
4. Boss preparation (save before depth 5, 10, 15, 20)
5. Parallel test runs for different classes
6. Performance metrics (time to depth, combat win rate, etc.)
7. Regression testing suite for game balance changes

## Contributing

When modifying the game server:
1. Run the automated tests to validate changes
2. Check log files for unexpected errors
3. Update test logic if new game mechanics are added
4. Ensure backwards compatibility with existing saves
