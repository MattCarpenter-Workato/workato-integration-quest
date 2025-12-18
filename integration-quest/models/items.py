"""
Item models for weapons, armor, and consumables.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal


class Item(BaseModel):
    """Base item model"""
    id: str
    name: str
    description: str
    tier: Literal["common", "uncommon", "rare", "legendary", "epic"]
    item_type: Literal["weapon", "armor", "consumable"]


class Weapon(BaseModel):
    """Connector weapons"""
    id: str
    name: str
    description: str
    tier: Literal["common", "uncommon", "rare", "legendary", "epic"]
    damage_dice: str  # e.g., "2d6", "3d8"
    special_effect: Optional[str] = None
    drop_rate: float  # 0.0 to 1.0


class Armor(BaseModel):
    """Error handler armor"""
    id: str
    name: str
    description: str
    tier: Literal["common", "uncommon", "rare", "legendary", "epic"]
    protection: int
    special_effect: Optional[str] = None
    drop_rate: float  # 0.0 to 1.0


class Consumable(BaseModel):
    """Recipe component consumables"""
    id: str
    name: str
    description: str
    effect_type: Literal["heal_hp", "heal_mp", "cure_status", "reveal_info", "escape", "buff", "special"]
    effect_value: int | str  # Amount for heals, or string for special effects
    drop_rate: float  # 0.0 to 1.0
    single_use: bool = True


class EquipmentSlots(BaseModel):
    """Character equipment slots"""
    weapon: Optional[Weapon] = None
    armor: Optional[Armor] = None
    accessory: Optional[str] = None  # Future expansion


class InventoryItem(BaseModel):
    """Item in inventory with quantity"""
    item: Item | Weapon | Armor | Consumable
    quantity: int = 1
