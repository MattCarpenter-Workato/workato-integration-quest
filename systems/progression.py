"""
Experience, leveling, and character progression system.
"""

import random
from typing import List, Tuple
from models.hero import Hero
from config import LEVEL_UP_MESSAGES


class ProgressionSystem:
    """Handles XP, leveling, and stat growth"""

    @staticmethod
    def xp_required_for_level(level: int) -> int:
        """Calculate XP required to reach a level"""
        # Formula: 100 * level^1.5
        return int(100 * (level ** 1.5))

    @staticmethod
    def add_experience(hero: Hero, xp: int) -> Tuple[bool, List[str]]:
        """
        Add XP to hero and check for level up.

        Returns:
            Tuple of (leveled_up, messages)
        """
        messages = []
        hero.xp += xp
        messages.append(f"📈 Gained {xp} XP! (Total: {hero.xp})")

        # Check for level up
        leveled_up = False
        while hero.xp >= ProgressionSystem.xp_required_for_level(hero.level + 1):
            hero.xp -= ProgressionSystem.xp_required_for_level(hero.level + 1)
            hero.level += 1
            leveled_up = True

            # Apply stat increases
            stat_messages = ProgressionSystem._apply_level_up(hero)
            messages.extend(stat_messages)

            # Level up message
            level_msg = random.choice(LEVEL_UP_MESSAGES).format(level=hero.level)
            messages.append(level_msg)

        return leveled_up, messages

    @staticmethod
    def _apply_level_up(hero: Hero) -> List[str]:
        """
        Apply stat increases on level up.

        Returns:
            List of stat increase messages
        """
        messages = []

        # Role-based stat growth
        if hero.role == "warrior":
            hero.throughput += 2
            hero.error_resilience += 1
            messages.append("💪 Throughput +2, Error Resilience +1")

        elif hero.role == "mage":
            hero.formula_power += 2
            hero.rate_agility += 1
            messages.append("🔮 Formula Power +2, Rate Agility +1")

        elif hero.role == "rogue":
            hero.rate_agility += 2
            hero.throughput += 1
            messages.append("🗡️ Rate Agility +2, Throughput +1")

        elif hero.role == "cleric":
            hero.error_resilience += 2
            hero.formula_power += 1
            messages.append("✨ Error Resilience +2, Formula Power +1")

        # Update max HP and MP
        old_max_hp = hero.max_uptime
        old_max_mp = hero.max_api_credits

        hero.max_uptime = hero.calculate_max_uptime()
        hero.max_api_credits = hero.calculate_max_api_credits()

        # Heal to full on level up
        hp_restored = hero.max_uptime - hero.uptime
        mp_restored = hero.max_api_credits - hero.api_credits

        hero.uptime = hero.max_uptime
        hero.api_credits = hero.max_api_credits

        messages.append(
            f"❤️ Max Uptime: {old_max_hp} → {hero.max_uptime} (fully restored)"
        )
        messages.append(
            f"💙 Max API Credits: {old_max_mp} → {hero.max_api_credits} (fully restored)"
        )

        # Unlock new skills every 5 levels
        if hero.level % 5 == 0:
            messages.append(f"🌟 New skill unlocked at level {hero.level}!")

        return messages

    @staticmethod
    def add_gold(hero: Hero, amount: int) -> None:
        """Add gold to hero"""
        hero.gold += amount

    @staticmethod
    def add_recipe_fragment(hero: Hero) -> Tuple[bool, str]:
        """
        Add a recipe fragment and check for bonus.

        Returns:
            Tuple of (bonus_applied, message)
        """
        hero.recipe_fragments += 1

        if hero.recipe_fragments % 3 == 0:
            # Apply bonus
            old_max = hero.max_uptime
            hero.max_uptime = hero.calculate_max_uptime()
            bonus = hero.max_uptime - old_max

            return True, (
                f"✨ Recipe Fragment collected! ({hero.recipe_fragments} total)\n"
                f"🎉 3 fragments combined! Max Uptime +{bonus} "
                f"({old_max} → {hero.max_uptime})"
            )
        else:
            remaining = 3 - (hero.recipe_fragments % 3)
            return False, (
                f"✨ Recipe Fragment collected! ({hero.recipe_fragments} total)\n"
                f"Collect {remaining} more for +5 max Uptime bonus"
            )
