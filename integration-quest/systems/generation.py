"""
Procedural dungeon and content generation.
"""

import random
import json
from pathlib import Path
from typing import List, Dict, Tuple
from models.world import Room
from models.combat import Enemy
from models.items import Weapon, Armor, Consumable
from config import ROOM_WEIGHTS


class DungeonGenerator:
    """Generates rooms, enemies, and loot"""

    def __init__(self):
        """Load game data from JSON files"""
        data_dir = Path(__file__).parent.parent / "data"

        # Load enemies
        with open(data_dir / "enemies.json", "r") as f:
            self.enemy_data = json.load(f)

        # Load items
        with open(data_dir / "items.json", "r") as f:
            self.item_data = json.load(f)

        # Load descriptions
        with open(data_dir / "descriptions.json", "r") as f:
            self.description_data = json.load(f)

    def generate_room(self, depth: int, room_type: str = None) -> Room:
        """
        Generate a procedural room.

        Args:
            depth: Dungeon depth (affects difficulty)
            room_type: Force specific room type, or None for random
        """

        # Determine room type
        if room_type is None:
            # Boss rooms every 5 levels
            if depth % 5 == 0:
                room_type = "boss"
            else:
                room_type = random.choices(
                    population=["corridor", "chamber", "treasure", "trap"],
                    weights=[0.40, 0.30, 0.15, 0.15],
                    k=1
                )[0]

        # Generate room ID
        room_id = f"{room_type}_{depth}_{random.randint(1000, 9999)}"

        # Get description
        description = random.choice(self.description_data[room_type])
        system_name = random.choice(self.description_data["system_names"][room_type])

        # Create room
        room = Room(
            id=room_id,
            room_type=room_type,
            system_name=system_name,
            description=description,
            depth=depth
        )

        # Populate room based on type
        if room_type in ["corridor", "chamber"]:
            room.enemies = self._generate_enemies(depth, room_type)
            room.items = self._generate_loot(depth, "common", quantity=random.randint(0, 2))

        elif room_type == "treasure":
            room.items = self._generate_loot(depth, "uncommon", quantity=random.randint(2, 4))

        elif room_type == "trap":
            room.enemies = self._generate_enemies(depth, room_type)
            # Traps have fewer items but more enemies

        elif room_type == "boss":
            room.enemies = self._generate_boss_enemy(depth)

        return room

    def _generate_enemies(self, depth: int, room_type: str) -> List[Enemy]:
        """Generate enemies for a room based on depth"""

        enemies = []

        # Determine enemy tier based on depth
        if depth <= 3:
            tier = "common"
            count = random.randint(1, 2)
        elif depth <= 6:
            tier = "uncommon"
            count = random.randint(1, 3)
        elif depth <= 9:
            tier = "rare"
            count = random.randint(1, 2)
        else:
            # Mix of tiers
            tier = random.choice(["uncommon", "rare"])
            count = random.randint(2, 3)

        # Generate enemies
        enemy_pool = self.enemy_data[tier]
        for i in range(count):
            enemy_template = random.choice(enemy_pool)
            enemy = Enemy(**enemy_template)

            # Scale HP based on depth
            hp_multiplier = 1.0 + (depth * 0.1)  # +10% HP per depth
            enemy.hp = int(enemy.hp * hp_multiplier)
            enemy.max_hp = enemy.hp

            enemies.append(enemy)

        return enemies

    def _generate_boss_enemy(self, depth: int) -> List[Enemy]:
        """Generate a boss enemy for the depth"""

        # Determine which boss based on depth
        boss_index = (depth // 5) - 1
        boss_pool = self.enemy_data["boss"]

        if boss_index >= len(boss_pool):
            boss_index = len(boss_pool) - 1  # Use final boss

        boss_template = boss_pool[boss_index]
        boss = Enemy(**boss_template)

        # Scale boss stats
        hp_multiplier = 1.0 + (depth * 0.05)
        boss.hp = int(boss.hp * hp_multiplier)
        boss.max_hp = boss.hp

        return [boss]

    def _generate_loot(self, depth: int, min_tier: str, quantity: int = 1) -> List[Weapon | Armor | Consumable]:
        """Generate random loot items"""

        loot = []

        for _ in range(quantity):
            # Randomly choose item type
            item_type = random.choice(["weapons", "armor", "consumables"])
            item_pool = self.item_data[item_type]

            # Filter by drop rate and tier
            available_items = [
                item for item in item_pool
                if random.random() < item.get("drop_rate", 1.0)
            ]

            if not available_items:
                continue

            item_data = random.choice(available_items)

            # Create appropriate item instance
            if item_type == "weapons":
                loot.append(Weapon(**item_data))
            elif item_type == "armor":
                loot.append(Armor(**item_data))
            else:
                loot.append(Consumable(**item_data))

        return loot

    def generate_dungeon_level(self, depth: int, room_count: int = 5) -> Dict[str, Room]:
        """
        Generate a connected dungeon level.

        Args:
            depth: Current depth
            room_count: Number of rooms to generate

        Returns:
            Dictionary of room_id -> Room
        """

        rooms = {}

        # Generate rooms
        for i in range(room_count):
            # Boss room only at end
            if i == room_count - 1 and depth % 5 == 0:
                room = self.generate_room(depth, room_type="boss")
            else:
                room = self.generate_room(depth)

            rooms[room.id] = room

        # Connect rooms linearly for now (can be enhanced later)
        room_ids = list(rooms.keys())
        for i in range(len(room_ids) - 1):
            current_room = rooms[room_ids[i]]
            next_room_id = room_ids[i + 1]

            # Add exits
            current_room.exits["north"] = next_room_id

        return rooms

    def create_starting_room(self) -> Room:
        """Create the initial starting room"""

        room = Room(
            id="start_0",
            room_type="corridor",
            system_name="Integration Hub Entrance",
            description=(
                "🏛️ **THE INTEGRATION HUB**\n\n"
                "You stand at the entrance to the Integration Dungeon. Ancient APIs hum in the distance. "
                "Somewhere deep below, legacy systems await connection. The air smells of stale JSON and "
                "broken promises.\n\n"
                "Your journey begins here, Integration Hero."
            ),
            depth=1,
            exits={"north": "generated"}  # Will be connected to first generated room
        )

        # Add starting items
        room.items = self._generate_loot(1, "common", quantity=2)

        return room
