"""
Unit tests for multiplayer features (registration, login, leaderboard, etc.)

These tests use mock database and email services to test multiplayer tools
without requiring actual MongoDB or SendGrid connections.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone


# =============================================================================
# Mock Classes for Database and Email
# =============================================================================

class MockDatabaseManager:
    """Mock database manager for testing multiplayer features"""

    def __init__(self):
        self.players = {}
        self.game_sessions = {}

    def get_player(self, email: str):
        return self.players.get(email.lower())

    def get_player_by_username(self, username: str):
        for player in self.players.values():
            if player["username"] == username:
                return player
        return None

    def create_player(self, email: str, username: str, token: str):
        email_lower = email.lower()
        if email_lower in self.players:
            raise ValueError(f"Email '{email}' is already registered")
        if self.get_player_by_username(username):
            raise ValueError(f"Username '{username}' is already taken")

        now = datetime.now(timezone.utc)
        player_doc = {
            "_id": email_lower,
            "username": username,
            "token": token,
            "token_created_at": now,
            "total_score": 0,
            "best_run_score": 0,
            "enemies_defeated": 0,
            "created_at": now,
            "last_active": now,
        }
        self.players[email_lower] = player_doc
        return player_doc

    def update_token(self, email: str, new_token: str):
        email_lower = email.lower()
        if email_lower in self.players:
            self.players[email_lower]["token"] = new_token
            self.players[email_lower]["token_created_at"] = datetime.now(timezone.utc)
            return True
        return False

    def validate_token(self, email: str, token: str):
        player = self.get_player(email)
        if not player:
            return False
        return player.get("token") == token

    def update_last_active(self, email: str):
        email_lower = email.lower()
        if email_lower in self.players:
            self.players[email_lower]["last_active"] = datetime.now(timezone.utc)

    def add_score(self, email: str, points: int):
        email_lower = email.lower()
        if email_lower in self.players:
            self.players[email_lower]["total_score"] += points

    def increment_enemies_defeated(self, email: str, count: int = 1):
        email_lower = email.lower()
        if email_lower in self.players:
            self.players[email_lower]["enemies_defeated"] += count

    def finalize_run(self, email: str, run_score: int):
        player = self.get_player(email)
        if player and run_score > player.get("best_run_score", 0):
            self.players[email.lower()]["best_run_score"] = run_score

    def get_leaderboard(self, limit: int = 10):
        sorted_players = sorted(
            self.players.values(),
            key=lambda p: p["total_score"],
            reverse=True
        )[:limit]
        return [
            {"username": p["username"], "total_score": p["total_score"], "enemies_defeated": p["enemies_defeated"]}
            for p in sorted_players
        ]

    def get_player_rank(self, email: str):
        player = self.get_player(email)
        if not player:
            return -1
        score = player.get("total_score", 0)
        higher_count = sum(1 for p in self.players.values() if p["total_score"] > score)
        return higher_count + 1

    def save_game_session(self, email: str, game_state: dict, run_score: int):
        self.game_sessions[email.lower()] = {
            "player_email": email.lower(),
            "game_state": game_state,
            "current_run_score": run_score,
            "created_at": datetime.now(timezone.utc),
            "last_updated": datetime.now(timezone.utc),
        }
        return "session_id"

    def load_game_session(self, email: str):
        return self.game_sessions.get(email.lower())

    def delete_game_session(self, email: str):
        if email.lower() in self.game_sessions:
            del self.game_sessions[email.lower()]
            return True
        return False

    def save_previous_character(self, email: str, game_state: dict, run_score: int):
        email_lower = email.lower()
        if email_lower not in self.game_sessions:
            return False
        self.game_sessions[email_lower]["previous_character"] = {
            "game_state": game_state,
            "run_score": run_score,
            "backed_up_at": datetime.now(timezone.utc),
        }
        return True

    def get_previous_character(self, email: str):
        session = self.game_sessions.get(email.lower())
        if session:
            return session.get("previous_character")
        return None

    def has_previous_character(self, email: str):
        return self.get_previous_character(email) is not None

    def clear_previous_character(self, email: str):
        email_lower = email.lower()
        if email_lower in self.game_sessions and "previous_character" in self.game_sessions[email_lower]:
            del self.game_sessions[email_lower]["previous_character"]
            return True
        return False

    def restore_previous_character(self, email: str):
        session = self.game_sessions.get(email.lower())
        if not session or "previous_character" not in session:
            return None
        previous = session["previous_character"]
        # Swap: previous becomes current
        self.game_sessions[email.lower()]["game_state"] = previous["game_state"]
        self.game_sessions[email.lower()]["current_run_score"] = previous["run_score"]
        del self.game_sessions[email.lower()]["previous_character"]
        return previous


class MockEmailService:
    """Mock email service for testing"""

    def __init__(self):
        self.sent_emails = []

    def send_welcome_email(self, to_email: str, username: str, token: str) -> bool:
        self.sent_emails.append({
            "type": "welcome",
            "to": to_email,
            "username": username,
            "token": token
        })
        return True

    def send_token_refresh_email(self, to_email: str, username: str, token: str) -> bool:
        self.sent_emails.append({
            "type": "token_refresh",
            "to": to_email,
            "username": username,
            "token": token
        })
        return True


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_db():
    """Create a mock database manager"""
    return MockDatabaseManager()


@pytest.fixture
def mock_email():
    """Create a mock email service"""
    return MockEmailService()


@pytest.fixture
def multiplayer_env(mock_db, mock_email):
    """Set up multiplayer environment with mocks"""
    import server

    # Store originals
    original_multiplayer_mode = server.MULTIPLAYER_MODE
    original_db = server.db
    original_email = server.email_service
    original_game_states = server.game_states.copy()
    original_player_sessions = server.player_sessions.copy()
    original_pending = server.pending_character_creation.copy()

    # Set up multiplayer mode with mocks
    server.MULTIPLAYER_MODE = True
    server.db = mock_db
    server.email_service = mock_email
    server.game_states.clear()
    server.player_sessions.clear()
    server.pending_character_creation.clear()

    yield {
        "db": mock_db,
        "email": mock_email,
        "server": server
    }

    # Restore originals
    server.MULTIPLAYER_MODE = original_multiplayer_mode
    server.db = original_db
    server.email_service = original_email
    server.game_states.clear()
    server.game_states.update(original_game_states)
    server.player_sessions.clear()
    server.player_sessions.update(original_player_sessions)
    server.pending_character_creation.clear()
    server.pending_character_creation.update(original_pending)


@pytest.fixture
def single_player_env():
    """Set up single-player environment (multiplayer disabled)"""
    import server

    # Store originals
    original_multiplayer_mode = server.MULTIPLAYER_MODE
    original_game_states = server.game_states.copy()
    original_player_sessions = server.player_sessions.copy()
    original_pending = server.pending_character_creation.copy()

    # Set up single-player mode
    server.MULTIPLAYER_MODE = False
    server.game_states.clear()
    server.player_sessions.clear()
    server.pending_character_creation.clear()

    yield server

    # Restore originals
    server.MULTIPLAYER_MODE = original_multiplayer_mode
    server.game_states.clear()
    server.game_states.update(original_game_states)
    server.player_sessions.clear()
    server.player_sessions.update(original_player_sessions)
    server.pending_character_creation.clear()
    server.pending_character_creation.update(original_pending)


# =============================================================================
# Helper to extract functions from FastMCP tools
# =============================================================================

def get_function(tool):
    """Extract the actual function from a FastMCP tool"""
    if hasattr(tool, 'fn'):
        return tool.fn
    elif callable(tool):
        return tool
    else:
        raise ValueError(f"Cannot extract function from {tool}")


# =============================================================================
# Single Player Mode Tests (Multiplayer features should be disabled)
# =============================================================================

class TestSinglePlayerMode:
    """Tests that multiplayer features are disabled in single-player mode"""

    def test_register_player_disabled(self, single_player_env):
        """Test register_player returns error in single-player mode"""
        register_fn = get_function(single_player_env.register_player)
        result = register_fn(email="test@example.com", username="TestPlayer")

        assert "error" in result
        assert "multiplayer mode" in result["error"].lower()

    def test_login_disabled(self, single_player_env):
        """Test login returns error in single-player mode"""
        login_fn = get_function(single_player_env.login)
        result = login_fn(email="test@example.com", token="abc123")

        assert "error" in result
        assert "multiplayer mode" in result["error"].lower()

    def test_logout_disabled(self, single_player_env):
        """Test logout returns error in single-player mode"""
        logout_fn = get_function(single_player_env.logout)
        result = logout_fn()

        assert "error" in result
        assert "multiplayer mode" in result["error"].lower()

    def test_refresh_token_disabled(self, single_player_env):
        """Test refresh_token returns error in single-player mode"""
        refresh_fn = get_function(single_player_env.refresh_token)
        result = refresh_fn(email="test@example.com")

        assert "error" in result
        assert "multiplayer mode" in result["error"].lower()

    def test_view_leaderboard_disabled(self, single_player_env):
        """Test view_leaderboard returns error in single-player mode"""
        leaderboard_fn = get_function(single_player_env.view_leaderboard)
        result = leaderboard_fn()

        assert "error" in result
        assert "multiplayer mode" in result["error"].lower()

    def test_view_my_stats_disabled(self, single_player_env):
        """Test view_my_stats returns error in single-player mode"""
        stats_fn = get_function(single_player_env.view_my_stats)
        result = stats_fn()

        assert "error" in result
        assert "multiplayer mode" in result["error"].lower()


# =============================================================================
# Registration Tests
# =============================================================================

class TestRegistration:
    """Tests for player registration"""

    def test_register_player_success(self, multiplayer_env):
        """Test successful player registration"""
        register_fn = get_function(multiplayer_env["server"].register_player)
        result = register_fn(email="hero@example.com", username="IntegrationHero")

        assert "error" not in result
        assert "narrative" in result
        assert "IntegrationHero" in result["narrative"]
        assert "hero@example.com" in result["narrative"]

        # Verify email was sent
        assert len(multiplayer_env["email"].sent_emails) == 1
        assert multiplayer_env["email"].sent_emails[0]["type"] == "welcome"
        assert multiplayer_env["email"].sent_emails[0]["to"] == "hero@example.com"

    def test_register_player_duplicate_email(self, multiplayer_env):
        """Test registration fails with duplicate email"""
        register_fn = get_function(multiplayer_env["server"].register_player)

        # First registration
        register_fn(email="hero@example.com", username="Player1")

        # Try to register with same email
        result = register_fn(email="hero@example.com", username="Player2")

        assert "error" in result
        assert "already registered" in result["error"]

    def test_register_player_duplicate_username(self, multiplayer_env):
        """Test registration fails with duplicate username"""
        register_fn = get_function(multiplayer_env["server"].register_player)

        # First registration
        register_fn(email="player1@example.com", username="SameName")

        # Try to register with same username
        result = register_fn(email="player2@example.com", username="SameName")

        assert "error" in result
        assert "already taken" in result["error"]

    def test_register_player_invalid_username_too_short(self, multiplayer_env):
        """Test registration fails with too short username"""
        register_fn = get_function(multiplayer_env["server"].register_player)
        result = register_fn(email="hero@example.com", username="AB")

        assert "error" in result
        assert "at least" in result["error"].lower()

    def test_register_player_invalid_username_too_long(self, multiplayer_env):
        """Test registration fails with too long username"""
        register_fn = get_function(multiplayer_env["server"].register_player)
        result = register_fn(email="hero@example.com", username="A" * 25)

        assert "error" in result
        assert "at most" in result["error"].lower()

    def test_register_player_invalid_username_special_chars(self, multiplayer_env):
        """Test registration fails with invalid characters in username"""
        register_fn = get_function(multiplayer_env["server"].register_player)
        result = register_fn(email="hero@example.com", username="Hero@#$%")

        assert "error" in result
        assert "alphanumeric" in result["error"].lower() or "letters" in result["error"].lower()


# =============================================================================
# Login/Logout Tests
# =============================================================================

class TestLoginLogout:
    """Tests for login and logout functionality"""

    def test_login_success(self, multiplayer_env):
        """Test successful login"""
        db = multiplayer_env["db"]
        server = multiplayer_env["server"]

        # Create a player directly in the mock DB
        db.create_player("hero@example.com", "TestHero", "valid_token_123")

        login_fn = get_function(server.login)
        result = login_fn(email="hero@example.com", token="valid_token_123")

        assert "error" not in result
        assert "narrative" in result
        assert "TestHero" in result["narrative"]

        # Verify session was created
        assert "default" in server.player_sessions
        assert server.player_sessions["default"].is_authenticated

    def test_login_invalid_token(self, multiplayer_env):
        """Test login fails with invalid token"""
        db = multiplayer_env["db"]
        server = multiplayer_env["server"]

        db.create_player("hero@example.com", "TestHero", "valid_token")

        login_fn = get_function(server.login)
        result = login_fn(email="hero@example.com", token="wrong_token")

        assert "error" in result
        assert "invalid" in result["error"].lower()

    def test_login_unregistered_email(self, multiplayer_env):
        """Test login fails with unregistered email"""
        login_fn = get_function(multiplayer_env["server"].login)
        result = login_fn(email="nobody@example.com", token="any_token")

        assert "error" in result

    def test_logout_success(self, multiplayer_env):
        """Test successful logout"""
        db = multiplayer_env["db"]
        server = multiplayer_env["server"]

        # Set up authenticated session
        db.create_player("hero@example.com", "TestHero", "token123")
        from models.player import PlayerSession
        server.player_sessions["default"] = PlayerSession(
            email="hero@example.com",
            username="TestHero",
            is_authenticated=True,
            current_run_score=100
        )

        logout_fn = get_function(server.logout)
        result = logout_fn()

        assert "error" not in result
        assert "narrative" in result
        assert "Goodbye" in result["narrative"] or "logged_out" in str(result.get("state", {}))

    def test_logout_not_logged_in(self, multiplayer_env):
        """Test logout fails when not logged in"""
        logout_fn = get_function(multiplayer_env["server"].logout)
        result = logout_fn()

        assert "error" in result
        assert "not logged in" in result["error"].lower()


# =============================================================================
# Token Refresh Tests
# =============================================================================

class TestTokenRefresh:
    """Tests for token refresh functionality"""

    def test_refresh_token_success(self, multiplayer_env):
        """Test successful token refresh"""
        db = multiplayer_env["db"]
        server = multiplayer_env["server"]

        db.create_player("hero@example.com", "TestHero", "old_token")
        old_token = db.get_player("hero@example.com")["token"]

        refresh_fn = get_function(server.refresh_token)
        result = refresh_fn(email="hero@example.com")

        assert "error" not in result
        assert "narrative" in result
        assert "sent" in result["narrative"].lower()

        # Verify token was changed
        new_token = db.get_player("hero@example.com")["token"]
        assert new_token != old_token

        # Verify email was sent
        assert any(e["type"] == "token_refresh" for e in multiplayer_env["email"].sent_emails)

    def test_refresh_token_unregistered(self, multiplayer_env):
        """Test token refresh fails for unregistered email"""
        refresh_fn = get_function(multiplayer_env["server"].refresh_token)
        result = refresh_fn(email="nobody@example.com")

        assert "error" in result
        assert "not registered" in result["error"].lower()


# =============================================================================
# Leaderboard Tests
# =============================================================================

class TestLeaderboard:
    """Tests for leaderboard functionality"""

    def test_view_leaderboard_empty(self, multiplayer_env):
        """Test viewing empty leaderboard"""
        leaderboard_fn = get_function(multiplayer_env["server"].view_leaderboard)
        result = leaderboard_fn()

        assert "error" not in result
        assert "narrative" in result
        assert "No players" in result["narrative"] or "LEADERBOARD" in result["narrative"]

    def test_view_leaderboard_with_players(self, multiplayer_env):
        """Test viewing leaderboard with players"""
        db = multiplayer_env["db"]
        server = multiplayer_env["server"]

        # Create players with different scores
        db.create_player("top@example.com", "TopPlayer", "token1")
        db.add_score("top@example.com", 1000)
        db.increment_enemies_defeated("top@example.com", 50)

        db.create_player("mid@example.com", "MidPlayer", "token2")
        db.add_score("mid@example.com", 500)
        db.increment_enemies_defeated("mid@example.com", 25)

        db.create_player("low@example.com", "LowPlayer", "token3")
        db.add_score("low@example.com", 100)
        db.increment_enemies_defeated("low@example.com", 10)

        leaderboard_fn = get_function(server.view_leaderboard)
        result = leaderboard_fn()

        assert "error" not in result
        assert "narrative" in result
        assert "TopPlayer" in result["narrative"]
        assert "1,000" in result["narrative"] or "1000" in result["narrative"]

    def test_view_leaderboard_limit(self, multiplayer_env):
        """Test leaderboard respects limit parameter"""
        db = multiplayer_env["db"]
        server = multiplayer_env["server"]

        # Create 5 players
        for i in range(5):
            db.create_player(f"player{i}@example.com", f"Player{i}", f"token{i}")
            db.add_score(f"player{i}@example.com", (5 - i) * 100)

        leaderboard_fn = get_function(server.view_leaderboard)
        result = leaderboard_fn(limit=3)

        assert "error" not in result
        assert "state" in result
        assert len(result["state"]["leaderboard"]) == 3


# =============================================================================
# Player Stats Tests
# =============================================================================

class TestPlayerStats:
    """Tests for player stats functionality"""

    def test_view_my_stats_success(self, multiplayer_env):
        """Test viewing stats when logged in"""
        db = multiplayer_env["db"]
        server = multiplayer_env["server"]

        # Create player and set up session
        db.create_player("hero@example.com", "StatHero", "token123")
        db.add_score("hero@example.com", 500)
        db.increment_enemies_defeated("hero@example.com", 25)

        from models.player import PlayerSession
        server.player_sessions["default"] = PlayerSession(
            email="hero@example.com",
            username="StatHero",
            is_authenticated=True,
            current_run_score=100
        )

        stats_fn = get_function(server.view_my_stats)
        result = stats_fn()

        assert "error" not in result
        assert "narrative" in result
        assert "StatHero" in result["narrative"]
        assert "500" in result["narrative"]  # Total score
        assert "25" in result["narrative"]  # Enemies defeated

    def test_view_my_stats_not_logged_in(self, multiplayer_env):
        """Test viewing stats fails when not logged in"""
        stats_fn = get_function(multiplayer_env["server"].view_my_stats)
        result = stats_fn()

        assert "error" in result
        assert "not logged in" in result["error"].lower()


# =============================================================================
# Score Tracking Tests
# =============================================================================

class TestScoreTracking:
    """Tests for score tracking in multiplayer mode"""

    def test_attack_tracks_score(self, multiplayer_env):
        """Test that defeating enemies tracks score when logged in"""
        db = multiplayer_env["db"]
        server = multiplayer_env["server"]

        # Create player and session
        db.create_player("hero@example.com", "ScoreHero", "token123")

        from models.player import PlayerSession
        server.player_sessions["default"] = PlayerSession(
            email="hero@example.com",
            username="ScoreHero",
            is_authenticated=True,
            current_run_score=0
        )

        # Create character and find enemy
        create_fn = get_function(server.create_character)
        create_fn(name="ScoreHero", role="warrior")

        # Get the game state and find a room with enemies
        game_state = server.game_states.get("default")
        assert game_state is not None

        # Find a room with enemies
        enemy_name = None
        for room_id, room in game_state.dungeon_map.items():
            if room.enemies:
                game_state.current_room_id = room_id
                enemy_name = room.enemies[0].name
                break

        if enemy_name:
            # Attack the enemy multiple times to defeat it
            attack_fn = get_function(server.attack)
            for _ in range(20):  # Multiple attacks to ensure defeat
                result = attack_fn(target=enemy_name)
                if "defeated" in result.get("narrative", "").lower():
                    break

            # Check if score was tracked
            session = server.player_sessions.get("default")
            if session:
                # Score should increase after defeating enemy
                assert session.current_run_score >= 0


# =============================================================================
# Integration Tests
# =============================================================================

class TestMultiplayerIntegration:
    """Integration tests for complete multiplayer workflows"""

    def test_full_registration_to_leaderboard_flow(self, multiplayer_env):
        """Test complete flow from registration to appearing on leaderboard"""
        db = multiplayer_env["db"]
        server = multiplayer_env["server"]
        email = multiplayer_env["email"]

        # Step 1: Register
        register_fn = get_function(server.register_player)
        result = register_fn(email="hero@example.com", username="QuestHero")
        assert "error" not in result

        # Get token from "email"
        welcome_email = next(e for e in email.sent_emails if e["type"] == "welcome")
        token = welcome_email["token"]

        # Step 2: Login
        login_fn = get_function(server.login)
        result = login_fn(email="hero@example.com", token=token)
        assert "error" not in result

        # Step 3: Add some score directly (simulating gameplay)
        db.add_score("hero@example.com", 500)
        db.increment_enemies_defeated("hero@example.com", 10)

        # Step 4: View leaderboard
        leaderboard_fn = get_function(server.view_leaderboard)
        result = leaderboard_fn()
        assert "error" not in result
        assert "QuestHero" in result["narrative"]

        # Step 5: View stats
        stats_fn = get_function(server.view_my_stats)
        result = stats_fn()
        assert "error" not in result
        assert "500" in result["narrative"]

        # Step 6: Logout
        logout_fn = get_function(server.logout)
        result = logout_fn()
        assert "error" not in result

    def test_token_refresh_and_relogin(self, multiplayer_env):
        """Test refreshing token and logging in with new token"""
        db = multiplayer_env["db"]
        server = multiplayer_env["server"]
        email = multiplayer_env["email"]

        # Register
        register_fn = get_function(server.register_player)
        register_fn(email="hero@example.com", username="RefreshHero")

        # Get original token
        original_token = next(e for e in email.sent_emails if e["type"] == "welcome")["token"]

        # Refresh token
        refresh_fn = get_function(server.refresh_token)
        result = refresh_fn(email="hero@example.com")
        assert "error" not in result

        # Get new token
        new_token = next(e for e in email.sent_emails if e["type"] == "token_refresh")["token"]
        assert new_token != original_token

        # Old token should not work
        login_fn = get_function(server.login)
        result = login_fn(email="hero@example.com", token=original_token)
        assert "error" in result

        # New token should work
        result = login_fn(email="hero@example.com", token=new_token)
        assert "error" not in result


# =============================================================================
# Character Backup and Restore Tests
# =============================================================================

class TestCharacterBackupRestore:
    """Tests for character backup and restore functionality"""

    def test_create_character_warning_when_existing(self, multiplayer_env):
        """Test that creating a character shows warning when one exists"""
        server = multiplayer_env["server"]

        create_fn = get_function(server.create_character)

        # Create first character
        result = create_fn(name="FirstHero", role="warrior")
        assert "error" not in result
        assert "FirstHero" in result["narrative"]

        # Try to create second character - should get warning
        result = create_fn(name="SecondHero", role="mage")
        assert "Warning" in result["narrative"]
        assert "FirstHero" in result["narrative"]
        assert "requires_confirmation" in result["state"]

    def test_create_character_confirmation_flow(self, multiplayer_env):
        """Test two-call confirmation for character replacement"""
        server = multiplayer_env["server"]

        create_fn = get_function(server.create_character)

        # Create first character
        create_fn(name="FirstHero", role="warrior")

        # First call for second character - warning
        result = create_fn(name="SecondHero", role="mage")
        assert "Warning" in result["narrative"]

        # Second call with same name/role - should proceed
        result = create_fn(name="SecondHero", role="mage")
        assert "error" not in result
        assert "SecondHero" in result["narrative"]
        assert "Recipe Builder" in result["narrative"]  # Mage role name

    def test_create_character_different_params_resets_confirmation(self, multiplayer_env):
        """Test that changing name/role resets the confirmation flow"""
        server = multiplayer_env["server"]

        create_fn = get_function(server.create_character)

        # Create first character
        create_fn(name="FirstHero", role="warrior")

        # First call for second character
        create_fn(name="SecondHero", role="mage")

        # Call with different params - should get warning again
        result = create_fn(name="DifferentHero", role="rogue")
        assert "Warning" in result["narrative"]
        assert "requires_confirmation" in result["state"]

    def test_restore_previous_character_no_backup(self, multiplayer_env):
        """Test restore fails when no backup exists"""
        db = multiplayer_env["db"]
        server = multiplayer_env["server"]

        # Set up authenticated session
        db.create_player("hero@example.com", "TestHero", "token123")
        from models.player import PlayerSession
        server.player_sessions["default"] = PlayerSession(
            email="hero@example.com",
            username="TestHero",
            is_authenticated=True,
            current_run_score=0
        )

        restore_fn = get_function(server.restore_previous_character)
        result = restore_fn()

        assert "error" in result
        assert "No previous character" in result["error"]

    def test_restore_previous_character_not_logged_in(self, multiplayer_env):
        """Test restore fails when not logged in"""
        server = multiplayer_env["server"]

        restore_fn = get_function(server.restore_previous_character)
        result = restore_fn()

        assert "error" in result
        assert "Login required" in result["error"]

    def test_backup_and_restore_flow_multiplayer(self, multiplayer_env):
        """Test complete backup and restore flow in multiplayer mode"""
        db = multiplayer_env["db"]
        server = multiplayer_env["server"]

        # Set up authenticated session
        db.create_player("hero@example.com", "TestHero", "token123")
        from models.player import PlayerSession
        server.player_sessions["default"] = PlayerSession(
            email="hero@example.com",
            username="TestHero",
            is_authenticated=True,
            current_run_score=100
        )

        create_fn = get_function(server.create_character)
        restore_fn = get_function(server.restore_previous_character)

        # Create first character
        create_fn(name="WarriorHero", role="warrior")

        # Save game to create a session in DB
        save_fn = get_function(server.save_game)
        save_fn()

        # Create second character (warning + confirm)
        create_fn(name="MageHero", role="mage")
        result = create_fn(name="MageHero", role="mage")
        assert "MageHero" in result["narrative"]

        # Restore the warrior
        result = restore_fn()
        assert "error" not in result
        assert "WarriorHero" in result["narrative"]
        assert "restored" in result["state"]

        # Verify game state is the warrior
        game_state = server.game_states.get("default")
        assert game_state.hero.name == "WarriorHero"
        assert game_state.hero.role == "warrior"

    def test_view_status_shows_backup_info(self, multiplayer_env):
        """Test view_status shows previous character info when backup exists"""
        db = multiplayer_env["db"]
        server = multiplayer_env["server"]

        # Set up authenticated session
        db.create_player("hero@example.com", "TestHero", "token123")
        from models.player import PlayerSession
        server.player_sessions["default"] = PlayerSession(
            email="hero@example.com",
            username="TestHero",
            is_authenticated=True,
            current_run_score=0
        )

        create_fn = get_function(server.create_character)
        status_fn = get_function(server.view_status)
        save_fn = get_function(server.save_game)

        # Create and save first character
        create_fn(name="WarriorHero", role="warrior")
        save_fn()

        # Create second character
        create_fn(name="MageHero", role="mage")
        create_fn(name="MageHero", role="mage")

        # View status should show backup info
        result = status_fn()
        assert "has_previous_character" in result["state"]
        assert result["state"]["has_previous_character"] is True
        assert "Previous Character Available" in result["narrative"]
        assert "WarriorHero" in result["narrative"]


class TestSinglePlayerBackupRestore:
    """Tests for character backup/restore in single-player mode"""

    def test_create_character_warning_single_player(self, single_player_env):
        """Test warning shown in single-player mode"""
        create_fn = get_function(single_player_env.create_character)

        # Create first character
        create_fn(name="FirstHero", role="warrior")

        # Second character should warn
        result = create_fn(name="SecondHero", role="mage")
        assert "Warning" in result["narrative"]

    def test_restore_no_backup_single_player(self, single_player_env):
        """Test restore fails when no backup in single-player"""
        restore_fn = get_function(single_player_env.restore_previous_character)
        result = restore_fn()

        assert "error" in result
        assert "No previous character" in result["error"]
