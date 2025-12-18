#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Quest: Automated Gameplay Testing Script

This script automates gameplay testing by simulating player actions
and logging every move, game state change, and outcome to a log file.

Usage:
    uv run python test_gameplay.py [--class CLASSNAME] [--depth TARGET_DEPTH]
"""

import sys
import os
import json
import argparse
from datetime import datetime
from pathlib import Path
import random

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')

# Import game functions
import server

# Extract functions from FastMCP wrapped tools
create_character = server.create_character.fn
view_status = server.view_status.fn
explore = server.explore.fn
examine = server.examine.fn
move = server.move.fn
attack = server.attack.fn
defend = server.defend.fn
use_item = server.use_item.fn
pickup = server.pickup.fn
equip = server.equip.fn
rest = server.rest.fn
flee = server.flee.fn
save_game = server.save_game.fn
load_game = server.load_game.fn
game_states = server.game_states


class GameplayLogger:
    """Logs all gameplay actions and outcomes"""

    def __init__(self, log_file: str = None):
        """Initialize the logger"""
        if log_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = f"test_gameplay_{timestamp}.log"

        self.log_dir = Path(__file__).parent / "logs"
        self.log_dir.mkdir(exist_ok=True)
        self.log_path = self.log_dir / log_file

        self.session_start = datetime.now()
        self.action_count = 0

        # Initialize log file
        with open(self.log_path, 'w', encoding='utf-8') as f:
            f.write(f"{'='*80}\n")
            f.write(f"INTEGRATION QUEST - AUTOMATED GAMEPLAY TEST\n")
            f.write(f"Session Started: {self.session_start}\n")
            f.write(f"{'='*80}\n\n")

    def log(self, message: str, level: str = "INFO"):
        """Log a message to the log file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}\n"

        # Write to file
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(log_line)

        # Also print to console
        print(log_line.strip())

    def log_action(self, action: str, params: dict = None):
        """Log a game action"""
        self.action_count += 1
        self.log(f"Action #{self.action_count}: {action}", "ACTION")
        if params:
            self.log(f"  Parameters: {json.dumps(params, indent=2)}", "ACTION")

    def log_result(self, result: dict):
        """Log the result of an action"""
        if isinstance(result, dict):
            # Log narrative if present
            if "narrative" in result:
                self.log(f"  Narrative: {result['narrative']}", "RESULT")

            # Log error if present
            if "error" in result:
                self.log(f"  ERROR: {result['error']}", "ERROR")

            # Log full result as JSON
            self.log(f"  Full Result: {json.dumps(result, indent=2, default=str)}", "RESULT")
        else:
            self.log(f"  Result: {result}", "RESULT")

    def log_game_state(self, session_id: str = "default"):
        """Log current game state"""
        if session_id in game_states:
            state = game_states[session_id]
            state_dict = state.model_dump() if hasattr(state, 'model_dump') else vars(state)
            self.log(f"Game State: {json.dumps(state_dict, indent=2, default=str)}", "STATE")

    def log_separator(self):
        """Log a separator line"""
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(f"\n{'-'*80}\n\n")

    def log_summary(self, success: bool, reason: str = ""):
        """Log final test summary"""
        duration = datetime.now() - self.session_start

        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"TEST SUMMARY\n")
            f.write(f"{'='*80}\n")
            f.write(f"Status: {'SUCCESS' if success else 'FAILED'}\n")
            if reason:
                f.write(f"Reason: {reason}\n")
            f.write(f"Total Actions: {self.action_count}\n")
            f.write(f"Duration: {duration}\n")
            f.write(f"Session Ended: {datetime.now()}\n")
            f.write(f"{'='*80}\n")

        self.log(f"Test {'SUCCEEDED' if success else 'FAILED'}: {reason}", "SUMMARY")


class AutomatedPlayer:
    """Simulates automated gameplay"""

    def __init__(self, logger: GameplayLogger, target_depth: int = 5):
        self.logger = logger
        self.target_depth = target_depth
        self.session_id = "default"
        self.max_actions = 500  # Prevent infinite loops
        self.actions_taken = 0

    def get_current_state(self):
        """Get current game state"""
        return game_states.get(self.session_id)

    def run_test(self, hero_name: str = "TestHero", hero_class: str = "warrior"):
        """Run automated gameplay test"""
        try:
            # Create character
            self.logger.log_separator()
            self.logger.log_action("create_character", {"name": hero_name, "role": hero_class})
            result = create_character(name=hero_name, role=hero_class)
            self.logger.log_result(result)
            self.logger.log_game_state()

            # Main gameplay loop
            while self.actions_taken < self.max_actions:
                state = self.get_current_state()

                if not state:
                    self.logger.log_summary(False, "Game state lost")
                    return False

                # Check if we've reached target depth
                if state.depth >= self.target_depth:
                    self.logger.log_summary(True, f"Reached target depth {self.target_depth}")
                    return True

                # Check if hero is dead
                if state.hero.uptime <= 0:
                    self.logger.log_summary(False, "Hero died")
                    return False

                # Decide next action based on game state
                action_taken = self.take_intelligent_action(state)

                if not action_taken:
                    self.logger.log_summary(False, "No valid actions available")
                    return False

                self.actions_taken += 1
                self.logger.log_separator()

            self.logger.log_summary(False, f"Exceeded max actions ({self.max_actions})")
            return False

        except Exception as e:
            self.logger.log(f"Test failed with exception: {str(e)}", "ERROR")
            self.logger.log_summary(False, f"Exception: {str(e)}")
            return False

    def take_intelligent_action(self, state) -> bool:
        """Decide and take the next intelligent action based on game state"""

        # Priority 1: Heal if low HP
        if state.hero.uptime < state.hero.max_uptime * 0.3:
            if self.try_use_healing_item(state):
                return True
            if not state.combat and self.try_rest(state):
                return True

        # Priority 2: Handle combat
        if state.combat:
            return self.handle_combat(state)

        # Priority 3: Explore and interact with room
        return self.explore_and_advance(state)

    def try_use_healing_item(self, state) -> bool:
        """Try to use a healing item"""
        # Find healing item in inventory
        for inv_item in state.hero.inventory:
            item_name = inv_item.item.name
            # Check if it's a healing item
            if any(word in item_name.lower() for word in ['potion', 'retry', 'heal']):
                self.logger.log_action("use_item", {"item": item_name})
                result = use_item(item=item_name)
                self.logger.log_result(result)
                return "error" not in result
        return False

    def try_rest(self, state) -> bool:
        """Try to rest and recover"""
        self.logger.log_action("rest", {})
        result = rest()
        self.logger.log_result(result)
        return "error" not in result

    def handle_combat(self, state) -> bool:
        """Handle combat situation"""
        combat = state.combat
        enemy_name = combat.enemy.name

        # Check if we should flee (very low HP)
        if state.hero.uptime < state.hero.max_uptime * 0.2:
            self.logger.log_action("flee", {})
            result = flee()
            self.logger.log_result(result)
            return True

        # Examine enemy if we haven't yet
        if not hasattr(self, '_examined_enemies'):
            self._examined_enemies = set()

        if enemy_name not in self._examined_enemies:
            self.logger.log_action("examine", {"target": enemy_name})
            result = examine(target=enemy_name)
            self.logger.log_result(result)
            self._examined_enemies.add(enemy_name)
            return True

        # Try to use a skill or basic attack
        if state.hero.skills and state.hero.api_credits > 20:
            # Use first available skill
            skill = state.hero.skills[0]
            self.logger.log_action("attack", {"target": enemy_name, "skill": skill})
            result = attack(target=enemy_name, skill=skill)
            self.logger.log_result(result)
        else:
            # Basic attack
            self.logger.log_action("attack", {"target": enemy_name})
            result = attack(target=enemy_name)
            self.logger.log_result(result)

        return True

    def explore_and_advance(self, state) -> bool:
        """Explore room and try to advance deeper"""
        try:
            # Get current room from dungeon map
            current_room = state.dungeon_map.get(state.current_room_id)

            if not current_room:
                return False

            # First, explore the room
            self.logger.log_action("explore", {})
            result = explore()
            self.logger.log_result(result)

            # Pick up any valuable items
            if hasattr(current_room, 'items') and current_room.items:
                items_to_pickup = list(current_room.items)[:2]  # Convert to list first
                for item in items_to_pickup:
                    try:
                        item_name = getattr(item, 'name', str(item))
                        self.logger.log_action("pickup", {"item": item_name})
                        result = pickup(item=item_name)
                        self.logger.log_result(result)

                        # Try to equip if it's equipment (has damage_dice for weapons or protection for armor)
                        if hasattr(item, 'damage_dice') or hasattr(item, 'protection'):
                            self.logger.log_action("equip", {"item": item_name})
                            result = equip(item=item_name)
                            self.logger.log_result(result)
                    except Exception as e:
                        self.logger.log(f"Error handling item: {e}", "ERROR")

            # Move to next room (prefer going deeper)
            direction_priority = ['down', 'north', 'east', 'south', 'west']
            for direction in direction_priority:
                if direction in current_room.exits:
                    self.logger.log_action("move", {"direction": direction})
                    result = move(direction=direction)
                    self.logger.log_result(result)
                    return True

            # No exits available
            return False

        except Exception as e:
            self.logger.log(f"Error in explore_and_advance: {e}", "ERROR")
            return False


def main():
    """Main entry point for automated testing"""
    parser = argparse.ArgumentParser(description='Integration Quest - Automated Gameplay Testing')
    parser.add_argument('--class', dest='hero_class', default='warrior',
                        choices=['warrior', 'mage', 'rogue', 'cleric'],
                        help='Hero class to test with')
    parser.add_argument('--depth', type=int, default=5,
                        help='Target depth to reach (default: 5)')
    parser.add_argument('--name', default='TestHero',
                        help='Hero name (default: TestHero)')
    parser.add_argument('--log', default=None,
                        help='Log file name (default: auto-generated timestamp)')

    args = parser.parse_args()

    # Initialize logger
    logger = GameplayLogger(log_file=args.log)
    logger.log(f"Starting automated gameplay test", "INFO")
    logger.log(f"Hero Class: {args.hero_class}", "INFO")
    logger.log(f"Target Depth: {args.depth}", "INFO")
    logger.log(f"Hero Name: {args.name}", "INFO")

    # Create automated player
    player = AutomatedPlayer(logger, target_depth=args.depth)

    # Run test
    success = player.run_test(hero_name=args.name, hero_class=args.hero_class)

    logger.log(f"Log file saved to: {logger.log_path}", "INFO")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
