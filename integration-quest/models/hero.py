"""
Hero character model with stats, inventory, and equipment.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from .items import EquipmentSlots, InventoryItem, Weapon, Armor, Consumable


class StatusEffect(BaseModel):
    """Active status effect on character"""
    name: str
    effect_type: Literal["rate_limited", "auth_expired", "transformed", "buffered", "cached", "debugging", "throttled"]
    duration: int  # Turns remaining, -1 for permanent
    description: str
    stat_modifier: Optional[dict[str, int]] = None


class Hero(BaseModel):
    """Integration Hero character"""

    # Identity
    name: str
    role: Literal["warrior", "mage", "rogue", "cleric"]
    level: int = 1
    xp: int = 0

    # Core resources (themed as Workato concepts)
    uptime: int = Field(default=100, description="HP - Integration health")
    max_uptime: int = Field(default=100, description="Max HP")
    api_credits: int = Field(default=50, description="MP - Fuel for skills")
    max_api_credits: int = Field(default=50, description="Max MP")

    # Stats (Workato themed)
    throughput: int = Field(default=10, description="STR - Records processed")
    formula_power: int = Field(default=10, description="INT - Transformation complexity")
    rate_agility: int = Field(default=10, description="DEX - Avoiding 429 errors")
    error_resilience: int = Field(default=10, description="CON - Recovery from failures")

    # Inventory & Equipment
    inventory: List[InventoryItem] = Field(default_factory=list)
    equipped: EquipmentSlots = Field(default_factory=EquipmentSlots)

    # Status & Progression
    status_effects: List[StatusEffect] = Field(default_factory=list)
    gold: int = 0
    skills: List[str] = Field(default_factory=list)

    # Meta
    recipe_fragments: int = Field(default=0, description="Collect 3 for +5 max Uptime")

    def calculate_max_uptime(self) -> int:
        """Calculate max HP based on CON and class"""
        from config import BASE_STATS, CLASS_BONUSES
        base_hp = BASE_STATS["hp"]
        class_mod = CLASS_BONUSES[self.role]["hp_mod"]
        con_bonus = self.error_resilience * 5
        fragment_bonus = (self.recipe_fragments // 3) * 5
        return base_hp + class_mod + con_bonus + fragment_bonus

    def calculate_max_api_credits(self) -> int:
        """Calculate max MP based on INT and class"""
        from config import BASE_STATS, CLASS_BONUSES
        base_mp = BASE_STATS["mp"]
        class_mod = CLASS_BONUSES[self.role]["mp_mod"]
        int_bonus = self.formula_power * 3
        return base_mp + class_mod + int_bonus

    def has_status(self, status_name: str) -> bool:
        """Check if hero has a specific status effect"""
        return any(effect.name == status_name for effect in self.status_effects)

    def add_to_inventory(self, item: Weapon | Armor | Consumable, quantity: int = 1) -> bool:
        """Add item to inventory, returns False if full"""
        from config import MAX_INVENTORY_SIZE

        # Check if item already exists in inventory
        for inv_item in self.inventory:
            if inv_item.item.id == item.id:
                inv_item.quantity += quantity
                return True

        # Check inventory space
        if len(self.inventory) >= MAX_INVENTORY_SIZE:
            return False

        # Add new item
        self.inventory.append(InventoryItem(item=item, quantity=quantity))
        return True

    def remove_from_inventory(self, item_id: str, quantity: int = 1) -> bool:
        """Remove item from inventory, returns False if not found"""
        for i, inv_item in enumerate(self.inventory):
            if inv_item.item.id == item_id:
                inv_item.quantity -= quantity
                if inv_item.quantity <= 0:
                    self.inventory.pop(i)
                return True
        return False

    def get_armor_value(self) -> int:
        """Get total armor/protection value"""
        base_armor = self.equipped.armor.protection if self.equipped.armor else 0
        # Add any status effect bonuses
        for effect in self.status_effects:
            if effect.effect_type == "cached":
                base_armor += 3
        return base_armor
