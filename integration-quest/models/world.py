"""
World, room, and game state models.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Literal
from .hero import Hero
from .combat import CombatState, Enemy
from .items import Weapon, Armor, Consumable


class Room(BaseModel):
    """A room/area in the dungeon"""
    id: str
    room_type: Literal["corridor", "chamber", "treasure", "trap", "boss"]
    system_name: str  # e.g., "Salesforce Org", "Legacy FTP"
    description: str

    # Navigation
    exits: Dict[str, str] = Field(default_factory=dict)  # {"north": "room_id_2", "east": "room_id_3"}

    # Contents
    items: List[Weapon | Armor | Consumable] = Field(default_factory=list)
    enemies: List[Enemy] = Field(default_factory=list)

    # State
    is_cleared: bool = False
    is_discovered: bool = False
    depth: int = 1  # How deep in the dungeon


class GameState(BaseModel):
    """Complete game state for a player"""

    # Player character
    hero: Hero

    # World state
    current_room_id: str
    dungeon_map: Dict[str, Room] = Field(default_factory=dict)

    # Combat
    combat: Optional[CombatState] = None

    # Progress
    depth: int = 1
    turn_count: int = 0
    max_depth_reached: int = 1

    # Flags for story/progression
    flags: Dict[str, any] = Field(default_factory=dict)

    # Meta
    save_id: Optional[str] = None
    created_at: str = Field(default_factory=lambda: __import__("datetime").datetime.now().isoformat())
    last_updated: str = Field(default_factory=lambda: __import__("datetime").datetime.now().isoformat())

    def get_current_room(self) -> Room:
        """Get the room the hero is currently in"""
        return self.dungeon_map[self.current_room_id]

    def is_in_combat(self) -> bool:
        """Check if currently in combat"""
        return self.combat is not None and self.combat.active

    def update_timestamp(self):
        """Update the last_updated timestamp"""
        self.last_updated = __import__("datetime").datetime.now().isoformat()
