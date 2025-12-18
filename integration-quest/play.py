#!/usr/bin/env python3
"""
Integration Quest: Terminal Play Mode
Run the game directly in your terminal!

Usage:
    uv run python play.py
"""

import sys
from pathlib import Path

# Import all the game tools from server
from server import (
    create_character, view_status, explore, examine, move, attack,
    defend, use_item, pickup, equip, rest, flee, save_game, load_game,
    game_states
)


def print_banner():
    """Print the game banner"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     ⚡ INTEGRATION QUEST: THE WORKATO RPG ⚡                 ║
║                                                               ║
║     "Connect the disconnected. Automate the manual.          ║
║      Defeat the bugs that plague enterprise workflows."      ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
""")


def print_separator():
    """Print a separator line"""
    print("\n" + "=" * 65 + "\n")


def print_narrative(result):
    """Print the narrative response from a tool"""
    if isinstance(result, dict):
        if "narrative" in result:
            print(result["narrative"])
        elif "error" in result:
            print(f"\n❌ ERROR: {result['error']}")
        else:
            print(result)
    else:
        print(result)


def show_help():
    """Show available commands"""
    print("""
📜 AVAILABLE COMMANDS:

Character & Status:
  status              - View your hero's stats, inventory, and status

Exploration:
  explore             - Explore the current room
  examine <target>    - Examine an enemy or item in detail
  move <direction>    - Move north, south, east, or west

Combat:
  attack <enemy>      - Attack an enemy with basic attack
  attack <enemy> <skill> - Use a class skill (e.g., bulk_upsert)
  defend              - Take defensive stance
  flee                - Attempt to escape combat

Inventory:
  pickup <item>       - Pick up an item from the room
  equip <item>        - Equip a weapon or armor
  use <item>          - Use a consumable item

Utility:
  rest                - Rest to recover HP/MP (20% encounter chance!)
  save                - Save your game
  load <save_id>      - Load a saved game

Meta:
  help                - Show this help message
  quit / exit         - Exit the game

💡 TIP: You don't need to type full names - partial matches work!
    Example: "attack bug" instead of "attack Bug"
""")


def get_input(prompt=">>> "):
    """Get user input with a prompt"""
    try:
        return input(prompt).strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\n👋 Thanks for playing Integration Quest!")
        sys.exit(0)


def parse_command(command_str):
    """Parse user command into action and arguments"""
    parts = command_str.strip().split(maxsplit=2)

    if not parts:
        return None, []

    action = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []

    return action, args


def main():
    """Main game loop"""
    print_banner()

    # Check if there's an existing game
    if game_states.get("default"):
        response = get_input("🎮 Continue existing game? (y/n): ")
        if response.lower() != 'y':
            game_states.clear()

    # Create new character if needed
    if not game_states.get("default"):
        print("\n🎭 CREATE YOUR INTEGRATION HERO\n")
        print("Choose your class:")
        print("  1. Warrior (Integration Engineer) - High Throughput, bulk operations")
        print("  2. Mage (Recipe Builder) - Formula Power, transformations")
        print("  3. Rogue (API Hacker) - Rate Agility, workarounds")
        print("  4. Cleric (Support Engineer) - Error Resilience, recovery")

        role_map = {
            "1": "warrior", "warrior": "warrior",
            "2": "mage", "mage": "mage",
            "3": "rogue", "rogue": "rogue",
            "4": "cleric", "cleric": "cleric"
        }

        while True:
            role_input = get_input("\nSelect class (1-4 or name): ").lower()
            if role_input in role_map:
                role = role_map[role_input]
                break
            print("❌ Invalid choice. Please choose 1-4 or class name.")

        name = get_input("Enter your hero's name: ").strip()
        if not name:
            name = "Hero"

        print_separator()
        result = create_character(name, role)
        print_narrative(result)

    print_separator()
    print("💡 Type 'help' for available commands, or 'explore' to begin!")
    print_separator()

    # Main game loop
    while True:
        command_str = get_input()

        if not command_str:
            continue

        action, args = parse_command(command_str)

        # Handle commands
        if action in ["quit", "exit", "q"]:
            response = get_input("\n💾 Save before quitting? (y/n): ")
            if response.lower() == 'y':
                result = save_game()
                print_narrative(result)
            print("\n👋 Thanks for playing Integration Quest!")
            print("May your APIs always return 200 OK! ⚡\n")
            break

        elif action in ["help", "h", "?"]:
            show_help()

        elif action == "status":
            result = view_status()
            print_narrative(result)

        elif action == "explore":
            result = explore()
            print_narrative(result)

        elif action == "examine" or action == "inspect":
            if not args:
                print("❌ Usage: examine <target>")
                continue
            target = " ".join(args)
            result = examine(target)
            print_narrative(result)

        elif action in ["move", "go"]:
            if not args:
                print("❌ Usage: move <north|south|east|west>")
                continue
            direction = args[0].lower()
            if direction not in ["north", "south", "east", "west"]:
                print("❌ Invalid direction. Use: north, south, east, or west")
                continue
            result = move(direction)
            print_narrative(result)

        elif action == "attack":
            if not args:
                print("❌ Usage: attack <enemy> [skill]")
                continue

            # Parse target and optional skill
            if len(args) == 1:
                target = args[0]
                skill = "basic_attack"
            else:
                # Everything except last word is target, last word might be skill
                # Or if 2+ words, first is target, rest is skill
                target = args[0]
                skill = args[1] if len(args) > 1 else "basic_attack"

            result = attack(target, skill)
            print_narrative(result)

        elif action == "defend":
            result = defend()
            print_narrative(result)

        elif action == "flee" or action == "escape":
            result = flee()
            print_narrative(result)

        elif action == "pickup" or action == "take" or action == "get":
            if not args:
                print("❌ Usage: pickup <item>")
                continue
            item = " ".join(args)
            result = pickup(item)
            print_narrative(result)

        elif action == "equip" or action == "wear":
            if not args:
                print("❌ Usage: equip <item>")
                continue
            item = " ".join(args)
            result = equip(item)
            print_narrative(result)

        elif action == "use":
            if not args:
                print("❌ Usage: use <item>")
                continue
            item = " ".join(args)
            result = use_item(item)
            print_narrative(result)

        elif action == "rest" or action == "sleep":
            result = rest()
            print_narrative(result)

        elif action == "save":
            result = save_game()
            print_narrative(result)

        elif action == "load":
            if not args:
                print("❌ Usage: load <save_id>")
                continue
            save_id = args[0]
            result = load_game(save_id)
            print_narrative(result)

        else:
            print(f"❓ Unknown command: '{action}'. Type 'help' for available commands.")

        print()  # Extra newline for readability


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for playing Integration Quest!")
        sys.exit(0)
