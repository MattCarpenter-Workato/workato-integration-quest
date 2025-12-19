"""
Database manager for multiplayer mode using MongoDB Atlas.
"""

import os
from datetime import datetime
from typing import Optional, Dict, Any, List

from pymongo import MongoClient, DESCENDING
from pymongo.errors import DuplicateKeyError


class DatabaseManager:
    """Manages all MongoDB operations for multiplayer mode"""

    def __init__(self):
        mongodb_uri = os.environ.get("MONGODB_URI")
        if not mongodb_uri:
            raise EnvironmentError("MONGODB_URI environment variable is required for multiplayer mode")

        self.client = MongoClient(mongodb_uri)
        self.db = self.client["integration_quest"]
        self.players = self.db["players"]
        self.game_sessions = self.db["game_sessions"]

        # Ensure indexes
        self.players.create_index("username", unique=True)
        self.game_sessions.create_index("player_email")

    # --- Player Operations ---

    def get_player(self, email: str) -> Optional[Dict[str, Any]]:
        """Get a player by email (case-insensitive)"""
        return self.players.find_one({"_id": email.lower()})

    def get_player_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get a player by username"""
        return self.players.find_one({"username": username})

    def create_player(self, email: str, username: str, token: str) -> Dict[str, Any]:
        """Create a new player profile"""
        now = datetime.utcnow()
        player_doc = {
            "_id": email.lower(),
            "username": username,
            "token": token,
            "token_created_at": now,
            "total_score": 0,
            "best_run_score": 0,
            "enemies_defeated": 0,
            "created_at": now,
            "last_active": now,
        }

        try:
            self.players.insert_one(player_doc)
            return player_doc
        except DuplicateKeyError as e:
            if "username" in str(e):
                raise ValueError(f"Username '{username}' is already taken")
            raise ValueError(f"Email '{email}' is already registered")

    def update_token(self, email: str, new_token: str) -> bool:
        """Update a player's authentication token"""
        result = self.players.update_one(
            {"_id": email.lower()},
            {
                "$set": {
                    "token": new_token,
                    "token_created_at": datetime.utcnow(),
                }
            }
        )
        return result.modified_count > 0

    def validate_token(self, email: str, token: str) -> bool:
        """Validate a player's token"""
        player = self.get_player(email)
        if not player:
            return False
        return player.get("token") == token

    def update_last_active(self, email: str) -> None:
        """Update player's last active timestamp"""
        self.players.update_one(
            {"_id": email.lower()},
            {"$set": {"last_active": datetime.utcnow()}}
        )

    # --- Score Operations ---

    def add_score(self, email: str, points: int) -> None:
        """Add points to a player's total score"""
        self.players.update_one(
            {"_id": email.lower()},
            {
                "$inc": {"total_score": points},
                "$set": {"last_active": datetime.utcnow()},
            }
        )

    def increment_enemies_defeated(self, email: str, count: int = 1) -> None:
        """Increment the enemies defeated counter"""
        self.players.update_one(
            {"_id": email.lower()},
            {"$inc": {"enemies_defeated": count}}
        )

    def finalize_run(self, email: str, run_score: int) -> None:
        """Finalize a run, updating best_run_score if needed"""
        player = self.get_player(email)
        if player and run_score > player.get("best_run_score", 0):
            self.players.update_one(
                {"_id": email.lower()},
                {"$set": {"best_run_score": run_score}}
            )

    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top players sorted by total score"""
        cursor = self.players.find(
            {},
            {"_id": 0, "username": 1, "total_score": 1, "enemies_defeated": 1}
        ).sort("total_score", DESCENDING).limit(limit)
        return list(cursor)

    def get_player_rank(self, email: str) -> int:
        """Get a player's rank (1-indexed)"""
        player = self.get_player(email)
        if not player:
            return -1

        # Count players with higher scores
        higher_count = self.players.count_documents({
            "total_score": {"$gt": player.get("total_score", 0)}
        })
        return higher_count + 1

    # --- Game Session Operations ---

    def save_game_session(self, email: str, game_state: Dict[str, Any], run_score: int) -> str:
        """Save a game session to MongoDB"""
        now = datetime.utcnow()
        session_doc = {
            "player_email": email.lower(),
            "game_state": game_state,
            "current_run_score": run_score,
            "created_at": now,
            "last_updated": now,
        }

        # Upsert - replace existing session for this player
        result = self.game_sessions.update_one(
            {"player_email": email.lower()},
            {"$set": session_doc},
            upsert=True
        )

        return str(result.upserted_id) if result.upserted_id else "updated"

    def load_game_session(self, email: str) -> Optional[Dict[str, Any]]:
        """Load a player's saved game session"""
        return self.game_sessions.find_one({"player_email": email.lower()})

    def delete_game_session(self, email: str) -> bool:
        """Delete a player's saved game session"""
        result = self.game_sessions.delete_one({"player_email": email.lower()})
        return result.deleted_count > 0
