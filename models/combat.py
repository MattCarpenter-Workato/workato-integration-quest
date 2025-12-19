"""
Combat and enemy models.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class Enemy(BaseModel):
    """Integration villain enemy"""
    id: str
    name: str
    emoji: str = "👹"
    description: str

    # Combat stats
    hp: int
    max_hp: int
    damage_dice: str  # e.g., "2d6", "1d8"
    armor: int = 0

    # Special properties
    weakness: Optional[str] = None
    resistance: Optional[str] = None
    special_ability: Optional[str] = None
    immune_until_examined: bool = False

    # Rewards
    xp_reward: int
    gold_reward: int
    loot_table: str  # Tier name for loot generation

    # Enemy tier
    tier: Literal["common", "uncommon", "rare", "boss"]

    # Runtime state
    is_examined: bool = False
    status_effects: List[str] = Field(default_factory=list)


class CombatState(BaseModel):
    """Active combat session"""
    active: bool = True
    enemies: List[Enemy]
    turn_order: List[str] = Field(default_factory=list)  # ["hero", "enemy_0", "enemy_1"]
    current_turn_index: int = 0
    round_num: int = 1
    hero_defending: bool = False

    # Combat flags
    hero_used_error_handler: bool = False  # Cleric auto-revive
    enemies_defeated: int = 0

    def get_current_turn(self) -> str:
        """Get whose turn it is"""
        if not self.turn_order:
            return "hero"
        return self.turn_order[self.current_turn_index % len(self.turn_order)]

    def next_turn(self):
        """Advance to next turn"""
        self.current_turn_index += 1
        if self.current_turn_index >= len(self.turn_order):
            self.current_turn_index = 0
            self.round_num += 1

    def get_alive_enemies(self) -> List[Enemy]:
        """Get list of enemies still alive"""
        return [e for e in self.enemies if e.hp > 0]

    def is_combat_over(self) -> bool:
        """Check if combat has ended"""
        return len(self.get_alive_enemies()) == 0 or not self.active
