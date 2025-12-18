"""
Dice rolling utilities for damage and random checks.
"""

import random
import re
from typing import Tuple


def roll_dice(notation: str) -> Tuple[int, list[int]]:
    """
    Roll dice using standard notation (e.g., "2d6", "1d8+2", "3d10-1").

    Returns:
        Tuple of (total, individual_rolls)

    Examples:
        roll_dice("2d6") -> (9, [4, 5])
        roll_dice("1d8+2") -> (7, [5])
        roll_dice("3d4-1") -> (7, [3, 2, 3])
    """
    # Parse dice notation: XdY+Z or XdY-Z or XdY
    match = re.match(r'(\d+)d(\d+)([+-]\d+)?', notation.lower().strip())

    if not match:
        # If not dice notation, try to parse as a simple number
        try:
            return int(notation), []
        except ValueError:
            return 0, []

    num_dice = int(match.group(1))
    die_size = int(match.group(2))
    modifier = int(match.group(3)) if match.group(3) else 0

    # Roll the dice
    rolls = [random.randint(1, die_size) for _ in range(num_dice)]
    total = sum(rolls) + modifier

    return max(0, total), rolls  # Ensure non-negative result


def roll_d20() -> int:
    """Roll a single d20 for skill checks"""
    return random.randint(1, 20)


def roll_percentage() -> float:
    """Roll a percentage (0.0 to 1.0) for chance checks"""
    return random.random()


def critical_hit_check() -> bool:
    """Check for critical hit (5% chance)"""
    return random.randint(1, 20) == 20


def critical_fail_check() -> bool:
    """Check for critical fail (5% chance)"""
    return random.randint(1, 20) == 1
