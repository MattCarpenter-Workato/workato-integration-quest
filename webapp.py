#!/usr/bin/env python3
"""
Integration Quest: PWA Web Application
FastAPI REST server wrapping the game tools for mobile/web play.

Usage:
    uv run uvicorn webapp:app --host 0.0.0.0 --port 8000
"""

import uuid
from typing import Optional
from pathlib import Path

from fastapi import FastAPI, Request, Response, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import game functions from server (same pattern as play.py)
import server

create_character_fn = server.create_character.fn
view_status_fn = server.view_status.fn
explore_fn = server.explore.fn
examine_fn = server.examine.fn
move_fn = server.move.fn
attack_fn = server.attack.fn
defend_fn = server.defend.fn
use_item_fn = server.use_item.fn
pickup_fn = server.pickup.fn
equip_fn = server.equip.fn
rest_fn = server.rest.fn
flee_fn = server.flee.fn
save_game_fn = server.save_game.fn
load_game_fn = server.load_game.fn
game_states = server.game_states

# Create FastAPI app
app = FastAPI(
    title="Integration Quest",
    description="A Workato-themed RPG - Battle through legacy systems and API chaos!",
    version="1.0.0"
)

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session management
SESSION_COOKIE_NAME = "iq_session"


def get_or_create_session(session_id: Optional[str]) -> str:
    """Get existing session or create new one."""
    if session_id and session_id in game_states:
        return session_id
    # For now, use "default" session for simplicity (single player)
    return "default"


def set_session_cookie(response: Response, session_id: str):
    """Set session cookie on response."""
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        max_age=60 * 60 * 24 * 30,  # 30 days
        httponly=True,
        samesite="lax"
    )


# Request/Response models
class CreateCharacterRequest(BaseModel):
    name: str
    role: str  # warrior, mage, rogue, cleric


class ExamineRequest(BaseModel):
    target: str


class MoveRequest(BaseModel):
    direction: str  # north, south, east, west


class AttackRequest(BaseModel):
    target: str
    skill: str = "basic_attack"


class UseItemRequest(BaseModel):
    item: str
    target: str = "self"


class PickupRequest(BaseModel):
    item: str


class EquipRequest(BaseModel):
    item: str


class LoadGameRequest(BaseModel):
    save_id: str


# API Routes

@app.get("/api/status")
async def api_status(session_id: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME)):
    """Get hero status."""
    session = get_or_create_session(session_id)
    result = view_status_fn()
    return JSONResponse(content=result)


@app.post("/api/create_character")
async def api_create_character(
    request: CreateCharacterRequest,
    response: Response,
    session_id: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME)
):
    """Create a new character."""
    session = get_or_create_session(session_id)
    set_session_cookie(response, session)
    result = create_character_fn(request.name, request.role)
    return JSONResponse(content=result)


@app.get("/api/explore")
async def api_explore(session_id: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME)):
    """Explore current room."""
    session = get_or_create_session(session_id)
    result = explore_fn()
    return JSONResponse(content=result)


@app.post("/api/examine")
async def api_examine(
    request: ExamineRequest,
    session_id: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME)
):
    """Examine a target."""
    session = get_or_create_session(session_id)
    result = examine_fn(request.target)
    return JSONResponse(content=result)


@app.post("/api/move")
async def api_move(
    request: MoveRequest,
    session_id: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME)
):
    """Move in a direction."""
    session = get_or_create_session(session_id)
    result = move_fn(request.direction)
    return JSONResponse(content=result)


@app.post("/api/attack")
async def api_attack(
    request: AttackRequest,
    session_id: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME)
):
    """Attack a target."""
    session = get_or_create_session(session_id)
    result = attack_fn(request.target, request.skill)
    return JSONResponse(content=result)


@app.post("/api/defend")
async def api_defend(session_id: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME)):
    """Take defensive stance."""
    session = get_or_create_session(session_id)
    result = defend_fn()
    return JSONResponse(content=result)


@app.post("/api/use_item")
async def api_use_item(
    request: UseItemRequest,
    session_id: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME)
):
    """Use an item."""
    session = get_or_create_session(session_id)
    result = use_item_fn(request.item, request.target)
    return JSONResponse(content=result)


@app.post("/api/pickup")
async def api_pickup(
    request: PickupRequest,
    session_id: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME)
):
    """Pick up an item."""
    session = get_or_create_session(session_id)
    result = pickup_fn(request.item)
    return JSONResponse(content=result)


@app.post("/api/equip")
async def api_equip(
    request: EquipRequest,
    session_id: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME)
):
    """Equip an item."""
    session = get_or_create_session(session_id)
    result = equip_fn(request.item)
    return JSONResponse(content=result)


@app.post("/api/rest")
async def api_rest(session_id: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME)):
    """Rest to recover."""
    session = get_or_create_session(session_id)
    result = rest_fn()
    return JSONResponse(content=result)


@app.post("/api/flee")
async def api_flee(session_id: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME)):
    """Attempt to flee combat."""
    session = get_or_create_session(session_id)
    result = flee_fn()
    return JSONResponse(content=result)


@app.post("/api/save")
async def api_save(session_id: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME)):
    """Save the game."""
    session = get_or_create_session(session_id)
    result = save_game_fn()
    return JSONResponse(content=result)


@app.post("/api/load")
async def api_load(
    request: LoadGameRequest,
    session_id: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME)
):
    """Load a saved game."""
    session = get_or_create_session(session_id)
    result = load_game_fn(request.save_id)
    return JSONResponse(content=result)


@app.get("/api/game_state")
async def api_game_state(session_id: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME)):
    """Get current game state for UI updates."""
    session = get_or_create_session(session_id)
    game_state = server.get_or_create_game_state(session)

    if not game_state:
        return JSONResponse(content={
            "has_character": False,
            "in_combat": False
        })

    hero = game_state.hero
    room = game_state.get_current_room()

    # Get alive enemies
    enemies = []
    for e in room.enemies:
        if e.hp > 0:
            enemies.append({
                "name": e.name,
                "hp": e.hp,
                "max_hp": e.max_hp,
                "emoji": e.emoji
            })

    # Get available exits
    exits = list(room.exits.keys())

    # Get room items
    items = [{"name": item.name, "tier": getattr(item, 'tier', 'consumable')} for item in room.items]

    # Get inventory
    inventory = []
    for inv_item in hero.inventory:
        inventory.append({
            "name": inv_item.item.name,
            "quantity": inv_item.quantity,
            "type": type(inv_item.item).__name__
        })

    return JSONResponse(content={
        "has_character": True,
        "hero": {
            "name": hero.name,
            "role": hero.role,
            "level": hero.level,
            "hp": hero.uptime,
            "max_hp": hero.max_uptime,
            "mp": hero.api_credits,
            "max_mp": hero.max_api_credits,
            "xp": hero.xp,
            "gold": hero.gold
        },
        "room": {
            "name": room.system_name,
            "cleared": room.is_cleared,
            "exits": exits,
            "items": items,
            "enemies": enemies
        },
        "in_combat": game_state.is_in_combat(),
        "depth": game_state.depth
    })


# Serve static files
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=static_path), name="static")


# Serve index.html at root
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main game page."""
    index_path = Path(__file__).parent / "static" / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Integration Quest</h1><p>Static files not found. Run from project root.</p>")


# Health check
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "game": "Integration Quest"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
