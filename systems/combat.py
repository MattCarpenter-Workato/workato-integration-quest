"""
Combat system - damage calculation, turn order, enemy AI.
"""

import random
from typing import Tuple, List, Optional
from models.hero import Hero
from models.combat import CombatState, Enemy
from models.items import Weapon
from systems.dice import roll_dice, critical_hit_check, roll_percentage
from systems.effects import StatusEffectManager
from config import DEFENSE_DAMAGE_REDUCTION


class CombatSystem:
    """Handles all combat logic"""

    @staticmethod
    def initialize_combat(hero: Hero, enemies: List[Enemy]) -> CombatState:
        """Start a new combat encounter"""

        # Generate turn order (based on DEX/agility)
        turn_order = ["hero"]
        for i, enemy in enumerate(enemies):
            turn_order.append(f"enemy_{i}")

        # Shuffle to add variety (could weight by DEX later)
        random.shuffle(turn_order)

        return CombatState(
            active=True,
            enemies=enemies,
            turn_order=turn_order,
            current_turn_index=0,
            round_num=1,
            hero_defending=False
        )

    @staticmethod
    def calculate_damage(
        attacker_stats: dict,
        weapon: Optional[Weapon],
        target: Enemy | Hero,
        skill_multiplier: float = 1.0,
        ignore_armor: bool = False
    ) -> Tuple[int, bool, List[str]]:
        """
        Calculate damage dealt.

        Returns:
            Tuple of (damage, is_critical, combat_log_messages)
        """
        messages = []

        # Base damage from weapon
        if weapon:
            base_damage, rolls = roll_dice(weapon.damage_dice)
            messages.append(f"🎲 Rolled {weapon.damage_dice}: {rolls} = {base_damage}")
        else:
            base_damage = 1  # Unarmed/basic
            messages.append(f"🎲 Basic attack: 1 damage")

        # Apply STR/throughput bonus
        str_bonus = attacker_stats.get("throughput", 10) // 5  # +1 per 5 STR
        base_damage += str_bonus

        # Apply skill multiplier
        base_damage = int(base_damage * skill_multiplier)

        # Critical hit check
        is_critical = critical_hit_check()
        if is_critical:
            base_damage *= 2
            messages.append("💥 CRITICAL HIT!")

        # Apply armor
        final_damage = base_damage
        if not ignore_armor:
            if isinstance(target, Enemy):
                armor = target.armor
            else:
                armor = target.get_armor_value()

            damage_reduction = armor
            final_damage = max(1, base_damage - damage_reduction)  # Minimum 1 damage

            if armor > 0:
                messages.append(f"🛡️ Armor reduced damage by {damage_reduction}")

        return final_damage, is_critical, messages

    @staticmethod
    def hero_attack(
        hero: Hero,
        target: Enemy,
        combat_state: CombatState,
        skill_multiplier: float = 1.0,
        ignore_armor: bool = False
    ) -> dict:
        """
        Hero attacks an enemy.

        Returns:
            Combat result dictionary
        """
        result = {
            "success": True,
            "messages": [],
            "damage_dealt": 0,
            "enemy_defeated": False,
            "xp_gained": 0,
            "gold_gained": 0
        }

        # Check if enemy is immune
        if target.immune_until_examined and not target.is_examined:
            result["success"] = False
            result["messages"].append(
                f"🛡️ The {target.name} is IMMUNE! Its defenses are impenetrable. "
                f"Try using 'examine' to find its weakness."
            )
            return result

        # Calculate damage
        attacker_stats = {
            "throughput": hero.throughput,
            "formula_power": hero.formula_power
        }

        damage, is_crit, damage_messages = CombatSystem.calculate_damage(
            attacker_stats=attacker_stats,
            weapon=hero.equipped.weapon,
            target=target,
            skill_multiplier=skill_multiplier,
            ignore_armor=ignore_armor
        )

        # Apply status effect modifiers
        damage_mod = StatusEffectManager.get_damage_modifier(hero)
        damage = int(damage * damage_mod)

        result["damage_dealt"] = damage
        result["messages"].extend(damage_messages)

        # Apply damage to enemy
        target.hp -= damage
        result["messages"].append(
            f"⚔️ You hit {target.name} for {damage} damage! ({target.hp}/{target.max_hp} HP remaining)"
        )

        # Check if enemy defeated
        if target.hp <= 0:
            target.hp = 0
            result["enemy_defeated"] = True
            result["xp_gained"] = target.xp_reward
            result["gold_gained"] = target.gold_reward
            combat_state.enemies_defeated += 1

            result["messages"].append(
                f"✅ {target.name} defeated! +{target.xp_reward} XP, +{target.gold_reward} gold"
            )

        return result

    @staticmethod
    def enemy_attack(enemy: Enemy, hero: Hero, combat_state: CombatState) -> dict:
        """
        Enemy attacks the hero.

        Returns:
            Combat result dictionary
        """
        result = {
            "messages": [],
            "damage_dealt": 0,
            "hero_defeated": False
        }

        # Calculate damage
        base_damage, rolls = roll_dice(enemy.damage_dice)
        damage = base_damage

        result["messages"].append(
            f"{enemy.emoji} {enemy.name} attacks! Rolled {enemy.damage_dice}: {rolls} = {base_damage}"
        )

        # Apply defense reduction if hero is defending
        if combat_state.hero_defending:
            damage = int(damage * (1 - DEFENSE_DAMAGE_REDUCTION))
            result["messages"].append(f"🛡️ Defensive stance reduced damage by 50%!")

        # Apply armor
        armor = hero.get_armor_value()
        if armor > 0:
            damage = max(1, damage - armor)
            result["messages"].append(f"🛡️ Your armor blocked {armor} damage")

        result["damage_dealt"] = damage

        # Apply damage to hero
        hero.uptime -= damage
        result["messages"].append(
            f"💔 You took {damage} damage! Uptime: {hero.uptime}/{hero.max_uptime}"
        )

        # Check if hero defeated
        if hero.uptime <= 0:
            hero.uptime = 0
            result["hero_defeated"] = True
            result["messages"].append("💀 Your uptime has reached 0...")

        return result

    @staticmethod
    def check_special_abilities(enemy: Enemy) -> Optional[dict]:
        """
        Check and execute enemy special abilities.

        Returns:
            Special ability info or None
        """
        if not enemy.special_ability:
            return None

        # Handle specific abilities
        if enemy.special_ability == "skip_turn_50":
            if roll_percentage() < 0.5:
                return {
                    "name": "Frozen",
                    "description": f"{enemy.name} is frozen and skips its turn!"
                }

        elif enemy.special_ability == "double_attack":
            return {
                "name": "Double Attack",
                "description": f"{enemy.name} attacks twice this turn!"
            }

        elif enemy.special_ability == "rate_limited_inflict":
            if roll_percentage() < 0.3:  # 30% chance
                return {
                    "name": "Rate Limited",
                    "description": f"{enemy.name} inflicts Rate Limited status!",
                    "status_effect": "rate_limited"
                }

        return None
