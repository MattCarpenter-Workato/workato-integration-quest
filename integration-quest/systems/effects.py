"""
Status effect management system.
"""

from typing import List, Optional
from models.hero import Hero, StatusEffect


class StatusEffectManager:
    """Manages status effects on characters"""

    @staticmethod
    def apply_effect(hero: Hero, effect_type: str, duration: int, description: str) -> None:
        """Apply a status effect to the hero"""

        # Check if effect already exists
        for effect in hero.status_effects:
            if effect.effect_type == effect_type:
                # Refresh duration if longer
                if duration > effect.duration:
                    effect.duration = duration
                return

        # Add new effect
        effect = StatusEffect(
            name=effect_type.replace("_", " ").title(),
            effect_type=effect_type,
            duration=duration,
            description=description
        )
        hero.status_effects.append(effect)

    @staticmethod
    def remove_effect(hero: Hero, effect_type: str) -> bool:
        """Remove a specific status effect"""
        for i, effect in enumerate(hero.status_effects):
            if effect.effect_type == effect_type:
                hero.status_effects.pop(i)
                return True
        return False

    @staticmethod
    def process_turn_effects(hero: Hero) -> List[str]:
        """Process status effects at the start of a turn"""
        messages = []
        effects_to_remove = []

        for effect in hero.status_effects:
            # Skip permanent effects (-1 duration)
            if effect.duration == -1:
                continue

            # Decrement duration
            effect.duration -= 1

            # Check if effect expired
            if effect.duration <= 0:
                effects_to_remove.append(effect.effect_type)
                messages.append(f"✨ {effect.name} has worn off!")

        # Remove expired effects
        for effect_type in effects_to_remove:
            StatusEffectManager.remove_effect(hero, effect_type)

        return messages

    @staticmethod
    def get_damage_modifier(hero: Hero) -> float:
        """Get damage multiplier from status effects"""
        modifier = 1.0

        for effect in hero.status_effects:
            if effect.effect_type == "buffered":
                modifier *= 1.25
            elif effect.effect_type == "auth_expired":
                modifier *= 0.5
            elif effect.effect_type == "throttled":
                # Throttled doesn't affect damage, just MP costs
                pass

        return modifier

    @staticmethod
    def get_mp_cost_modifier(hero: Hero) -> float:
        """Get MP cost multiplier from status effects"""
        modifier = 1.0

        for effect in hero.status_effects:
            if effect.effect_type == "throttled":
                modifier *= 0.5  # Half MP costs

        return modifier

    @staticmethod
    def can_act(hero: Hero) -> Tuple[bool, Optional[str]]:
        """Check if hero can act this turn"""
        for effect in hero.status_effects:
            if effect.effect_type == "rate_limited":
                return False, "⏱️ Rate Limited! You must skip this turn."

        return True, None

    @staticmethod
    def format_effects_list(hero: Hero) -> str:
        """Format active status effects for display"""
        if not hero.status_effects:
            return "None"

        effects_str = []
        for effect in hero.status_effects:
            duration_str = f"{effect.duration} turns" if effect.duration > 0 else "Permanent"
            effects_str.append(f"{effect.name} ({duration_str})")

        return ", ".join(effects_str)


from typing import Tuple
