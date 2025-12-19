"""
Player profile and session models for multiplayer mode.
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class PlayerProfile(BaseModel):
    """Persistent player identity stored in MongoDB"""
    email: EmailStr  # Primary identifier (stored as _id in MongoDB)
    username: str  # Display name (3-20 chars, alphanumeric + underscore)
    token: str  # 32-char hex authentication token
    token_created_at: datetime
    total_score: int = 0  # Lifetime points from enemies defeated
    best_run_score: int = 0  # Highest single-run score
    enemies_defeated: int = 0  # Total enemies killed
    created_at: datetime
    last_active: datetime


class PlayerSession(BaseModel):
    """Tracks authenticated player in current game session"""
    email: str
    username: str
    is_authenticated: bool = False
    current_run_score: int = 0  # Points earned in current game session
