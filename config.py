"""
Integration Quest Configuration

Game constants, class bonuses, and configuration settings.
"""

from typing import Dict, Any

# Class bonuses for character creation
CLASS_BONUSES: Dict[str, Dict[str, int]] = {
    "warrior": {
        "str": 4,
        "con": 2,
        "hp_mod": 20,
        "mp_mod": -10,
    },
    "mage": {
        "int": 4,
        "dex": 2,
        "hp_mod": -10,
        "mp_mod": 30,
    },
    "rogue": {
        "dex": 4,
        "str": 2,
        "hp_mod": 0,
        "mp_mod": 0,
    },
    "cleric": {
        "con": 4,
        "int": 2,
        "hp_mod": 10,
        "mp_mod": 15,
    },
}

# Base stats
BASE_STATS = {
    "hp": 100,
    "mp": 50,
    "str": 10,
    "int": 10,
    "dex": 10,
    "con": 10,
}

# Room type weights for generation
ROOM_WEIGHTS = {
    "corridor": 0.40,
    "chamber": 0.30,
    "treasure": 0.15,
    "trap": 0.10,
    "boss": 0.05,  # Only at depth % 5 == 0
}

# Error messages (in character)
ERRORS = {
    "no_game": "🚫 No active integration detected. Use create_character to initialize a new hero.",
    "invalid_target": "❓ Target '{target}' not found in current scope. Check your room's contents.",
    "not_in_combat": "😌 No active incidents. The system is peaceful... for now.",
    "inventory_full": "📦 Inventory buffer overflow! Drop something before picking up more.",
    "insufficient_credits": "💳 Insufficient API Credits! Rest or use a refill potion.",
    "invalid_direction": "🧱 Cannot move {direction}. No endpoint exists in that direction.",
    "item_not_found": "🔍 '{item}' not found in inventory. Check your loadout.",
    "already_equipped": "⚙️ '{item}' is already equipped in that slot.",
    "enemy_immune": "🛡️ The {enemy} is immune! Try using 'examine' first to find its weakness.",
}

# Victory messages
VICTORY_MESSAGES = [
    "✅ The bug is squashed! Your recipe runs green.",
    "🔗 Integration successful! Data flows freely once more.",
    "📡 The rate limiter falls! '200 OK' echoes through the dungeon.",
    "⚡ You've connected the disconnected. The workflow is complete.",
    "🏆 The legacy system acknowledges your authority. COBOL bows before you.",
    "🎉 Job completed successfully! 0 errors, 0 warnings.",
    "💾 The API responds with valid JSON. You've won... this time.",
]

# Game over messages
GAME_OVER_MESSAGES = [
    "💀 SYSTEM DOWN. Your integration has crashed. Jobs pile up eternally...",
    "❌ Error 500: Internal Hero Failure. Support tickets multiply in your absence.",
    "⏱️ Connection timeout. Your adventure has... timed out.",
    "🏚️ The Monolith consumes you. You become part of the legacy code. Forever.",
    "📉 Uptime: 0%. SLA breached. The on-call engineer is summoned... but it's too late.",
    "🔄 Infinite loop detected. Your consciousness spins forever in the void.",
]

# Level up messages
LEVEL_UP_MESSAGES = [
    "⬆️ LEVEL UP! Your integration skills grow stronger!",
    "🌟 New certification unlocked! Your hero advances to level {level}!",
    "📈 Experience processed! You've leveled up to {level}!",
    "🎓 Training complete! Welcome to level {level}, Integration Hero!",
]

# Game settings
MAX_INVENTORY_SIZE = 20
SAVE_DIRECTORY = "storage/saves"
REST_HP_RECOVERY = 0.5  # 50% of max HP
REST_MP_RECOVERY = 0.75  # 75% of max MP
REST_ENCOUNTER_CHANCE = 0.20  # 20% chance
FLEE_BASE_CHANCE = 0.50  # 50% base + DEX modifier
DEFENSE_DAMAGE_REDUCTION = 0.50  # 50% damage reduction when defending

# Multiplayer settings
MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 20
USERNAME_PATTERN = r'^[a-zA-Z0-9_]+$'
TOKEN_LENGTH = 32  # hex characters (16 bytes = 32 hex chars)
