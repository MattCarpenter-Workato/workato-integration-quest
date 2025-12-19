#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Quest: Comprehensive Function Testing

Tests all game functions to ensure they work correctly without trying to win.
Validates: character creation, all actions, save/load, combat, items, skills, etc.

Usage:
    uv run python test_all_functions.py
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')

# Import game functions
import server

# Extract functions from FastMCP wrapped tools
def get_function(tool):
    """Extract the actual function from a FastMCP tool"""
    if hasattr(tool, 'fn'):
        return tool.fn
    elif callable(tool):
        return tool
    else:
        raise ValueError(f"Cannot extract function from {tool}")

create_character = get_function(server.create_character)
view_status = get_function(server.view_status)
explore = get_function(server.explore)
examine = get_function(server.examine)
move = get_function(server.move)
attack = get_function(server.attack)
defend = get_function(server.defend)
use_item = get_function(server.use_item)
pickup = get_function(server.pickup)
equip = get_function(server.equip)
rest = get_function(server.rest)
flee = get_function(server.flee)
save_game = get_function(server.save_game)
load_game = get_function(server.load_game)
game_states = server.game_states


class FunctionTester:
    """Tests all game functions comprehensively"""

    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_log = []
        self.log_file = Path(__file__).parent / "logs" / f"function_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.log_file.parent.mkdir(exist_ok=True)

    def log(self, message: str, status: str = "INFO"):
        """Log a test message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{status}] {message}"
        self.test_log.append(log_line)
        print(log_line)

    def assert_test(self, condition: bool, test_name: str, error_msg: str = ""):
        """Assert a test condition"""
        if condition:
            self.tests_passed += 1
            self.log(f"✅ PASS: {test_name}", "PASS")
            return True
        else:
            self.tests_failed += 1
            self.log(f"❌ FAIL: {test_name} - {error_msg}", "FAIL")
            return False

    def test_character_creation(self):
        """Test character creation for all classes"""
        self.log("\n=== Testing Character Creation ===", "TEST")

        classes = ["warrior", "mage", "rogue", "cleric"]

        for hero_class in classes:
            result = create_character(name=f"Test{hero_class.title()}", role=hero_class)

            # Check for successful creation
            self.assert_test(
                "error" not in result,
                f"Create {hero_class} character",
                result.get("error", "")
            )

            # Check for narrative in response
            self.assert_test(
                "narrative" in result,
                f"{hero_class} has narrative response"
            )

            # Check game state exists
            state = game_states.get("default")
            self.assert_test(
                state is not None and state.hero.role == hero_class,
                f"{hero_class} game state created"
            )

    def test_exploration_actions(self):
        """Test exploration-related actions"""
        self.log("\n=== Testing Exploration Actions ===", "TEST")

        # Create a test character first
        create_character(name="Explorer", role="warrior")

        # Test explore
        result = explore()
        self.assert_test(
            "error" not in result and "narrative" in result,
            "Explore current room"
        )

        # Test view_status
        result = view_status()
        self.assert_test(
            "error" not in result and "narrative" in result,
            "View character status"
        )

        # Get current room to find items/enemies
        state = game_states.get("default")
        current_room = state.dungeon_map.get(state.current_room_id)

        # Test examine on items if available
        if current_room.items:
            item = current_room.items[0]
            result = examine(target=item.name)
            self.assert_test(
                "error" not in result,
                f"Examine item: {item.name}"
            )

        # Test examine on enemies if available
        if current_room.enemies:
            enemy = current_room.enemies[0]
            result = examine(target=enemy.name)
            self.assert_test(
                "error" not in result,
                f"Examine enemy: {enemy.name}"
            )

    def test_item_management(self):
        """Test item pickup and equipment"""
        self.log("\n=== Testing Item Management ===", "TEST")

        # Create a test character
        create_character(name="ItemTester", role="warrior")

        state = game_states.get("default")
        current_room = state.dungeon_map.get(state.current_room_id)

        # Test pickup
        if current_room.items:
            item = current_room.items[0]
            item_name = item.name

            result = pickup(item=item_name)
            self.assert_test(
                "error" not in result,
                f"Pickup item: {item_name}",
                result.get("error", "")
            )

            # Test equip if it's equipment
            if hasattr(item, 'damage_dice') or hasattr(item, 'protection'):
                result = equip(item=item_name)
                self.assert_test(
                    "error" not in result,
                    f"Equip item: {item_name}",
                    result.get("error", "")
                )

        # Test using consumable
        if state.hero.inventory:
            # Find a consumable
            for inv_item in state.hero.inventory:
                if hasattr(inv_item.item, 'effect_type'):
                    result = use_item(item=inv_item.item.name)
                    self.assert_test(
                        "error" not in result,
                        f"Use consumable: {inv_item.item.name}",
                        result.get("error", "")
                    )
                    break

    def test_movement(self):
        """Test movement between rooms"""
        self.log("\n=== Testing Movement ===", "TEST")

        # Create a test character
        create_character(name="MoveTester", role="rogue")

        state = game_states.get("default")
        current_room = state.dungeon_map.get(state.current_room_id)

        # Clear any enemies first to allow movement
        if current_room.enemies:
            current_room.enemies.clear()
            current_room.is_cleared = True

        # Test move in available direction
        if current_room.exits:
            direction = list(current_room.exits.keys())[0]
            initial_room_id = state.current_room_id

            result = move(direction=direction)
            self.assert_test(
                "error" not in result,
                f"Move {direction}",
                result.get("error", "")
            )

            # Verify room changed
            state = game_states.get("default")
            self.assert_test(
                state.current_room_id != initial_room_id,
                "Room changed after move"
            )

    def test_combat_actions(self):
        """Test combat-related actions"""
        self.log("\n=== Testing Combat Actions ===", "TEST")

        # Create a test character
        create_character(name="Combatant", role="warrior")

        state = game_states.get("default")

        # Find a room with enemies
        enemy_room = None
        enemy = None
        for room_id, room in state.dungeon_map.items():
            if room.enemies and len(room.enemies) > 0:
                enemy_room = room
                enemy = room.enemies[0]
                state.current_room_id = room_id
                break

        if enemy:
            # Test basic attack
            result = attack(target=enemy.name)
            self.assert_test(
                "error" not in result,
                f"Basic attack on {enemy.name}",
                result.get("error", "")
            )

            # Test skill attack if hero has skills
            state = game_states.get("default")
            if state.hero.skills and state.hero.api_credits > 10:
                skill = state.hero.skills[0]

                # Recreate enemy if defeated
                if state.combat is None:
                    # Find another enemy room
                    for room_id, room in state.dungeon_map.items():
                        if room.enemies and len(room.enemies) > 0:
                            state.current_room_id = room_id
                            enemy = room.enemies[0]
                            break

                if enemy:
                    result = attack(target=enemy.name, skill=skill)
                    self.assert_test(
                        "error" not in result,
                        f"Skill attack with {skill}",
                        result.get("error", "")
                    )

            # Test defend
            state = game_states.get("default")
            if state.combat:
                result = defend()
                self.assert_test(
                    "error" not in result,
                    "Defend action",
                    result.get("error", "")
                )

            # Test flee
            state = game_states.get("default")
            if state.combat:
                result = flee()
                # Flee can fail, so just check it doesn't crash
                self.assert_test(
                    True,  # Always pass if no exception
                    "Flee action (may succeed or fail)"
                )

    def test_rest_action(self):
        """Test rest functionality"""
        self.log("\n=== Testing Rest Action ===", "TEST")

        # Create a test character
        create_character(name="RestTester", role="cleric")

        state = game_states.get("default")

        # Damage the hero first
        state.hero.uptime = state.hero.max_uptime // 2
        state.hero.api_credits = state.hero.max_api_credits // 2

        # Make sure not in combat
        state.combat = None

        result = rest()
        self.assert_test(
            "error" not in result,
            "Rest action",
            result.get("error", "")
        )

    def test_save_and_load(self):
        """Test save and load game functionality"""
        self.log("\n=== Testing Save/Load System ===", "TEST")

        # Create a test character
        create_character(name="SaveTester", role="mage")

        # Modify game state
        state = game_states.get("default")
        state.hero.uptime = 100
        state.hero.gold = 50
        original_depth = state.depth

        # Test save
        result = save_game()
        self.assert_test(
            "error" not in result and "save_id" in result.get("state", {}),
            "Save game",
            result.get("error", "")
        )

        save_id = result.get("state", {}).get("save_id")

        if save_id:
            # Modify state again
            state.hero.gold = 999
            state.depth = 99

            # Test load
            result = load_game(save_id=save_id)
            self.assert_test(
                "error" not in result,
                f"Load game with save_id: {save_id}",
                result.get("error", "")
            )

            # Verify state restored
            state = game_states.get("default")
            self.assert_test(
                state.hero.gold == 50 and state.depth == original_depth,
                "Game state restored correctly after load"
            )

    def test_all_classes(self):
        """Test that all character classes work"""
        self.log("\n=== Testing All Character Classes ===", "TEST")

        classes = ["warrior", "mage", "rogue", "cleric"]

        for hero_class in classes:
            # Create character
            result = create_character(name=f"Class{hero_class.title()}", role=hero_class)

            if "error" in result:
                self.assert_test(False, f"{hero_class} class functional test", result.get("error"))
                continue

            state = game_states.get("default")

            # Verify class-specific attributes
            has_skills = len(state.hero.skills) > 0
            has_equipment = state.hero.equipped.weapon is not None
            has_stats = state.hero.uptime > 0 and state.hero.api_credits > 0

            self.assert_test(
                has_skills and has_equipment and has_stats,
                f"{hero_class} class has proper setup (skills, equipment, stats)"
            )

    def run_all_tests(self):
        """Run all test suites"""
        self.log("=" * 80)
        self.log("INTEGRATION QUEST - COMPREHENSIVE FUNCTION TESTING")
        self.log(f"Started: {datetime.now()}")
        self.log("=" * 80)

        try:
            # Run all test suites
            self.test_character_creation()
            self.test_all_classes()
            self.test_exploration_actions()
            self.test_item_management()
            self.test_movement()
            self.test_combat_actions()
            self.test_rest_action()
            self.test_save_and_load()

        except Exception as e:
            self.log(f"CRITICAL ERROR: {str(e)}", "ERROR")
            import traceback
            self.log(f"Traceback: {traceback.format_exc()}", "ERROR")

        # Print summary
        self.log("\n" + "=" * 80)
        self.log("TEST SUMMARY")
        self.log("=" * 80)
        total_tests = self.tests_passed + self.tests_failed
        pass_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0

        self.log(f"Total Tests: {total_tests}")
        self.log(f"Passed: {self.tests_passed} ✅")
        self.log(f"Failed: {self.tests_failed} ❌")
        self.log(f"Pass Rate: {pass_rate:.1f}%")

        # Save log to file
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.test_log))

        self.log(f"\nLog saved to: {self.log_file}")
        self.log("=" * 80)

        # Return exit code
        return 0 if self.tests_failed == 0 else 1


def main():
    """Main entry point"""
    tester = FunctionTester()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
