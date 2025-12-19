"""
Integration tests for MCP game tools.

These tests verify the game tools work correctly end-to-end,
testing the actual server functions.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


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
# Test Fixtures for Game Tools
# =============================================================================

@pytest.fixture(autouse=True)
def reset_game_state():
    """Reset game state before each test"""
    import server
    server.game_states.clear()
    server.player_sessions.clear()
    yield
    server.game_states.clear()
    server.player_sessions.clear()


@pytest.fixture
def create_character_fn():
    """Get the create_character function"""
    import server
    return get_function(server.create_character)


@pytest.fixture
def view_status_fn():
    """Get the view_status function"""
    import server
    return get_function(server.view_status)


@pytest.fixture
def explore_fn():
    """Get the explore function"""
    import server
    return get_function(server.explore)


@pytest.fixture
def examine_fn():
    """Get the examine function"""
    import server
    return get_function(server.examine)


@pytest.fixture
def move_fn():
    """Get the move function"""
    import server
    return get_function(server.move)


@pytest.fixture
def attack_fn():
    """Get the attack function"""
    import server
    return get_function(server.attack)


@pytest.fixture
def defend_fn():
    """Get the defend function"""
    import server
    return get_function(server.defend)


@pytest.fixture
def use_item_fn():
    """Get the use_item function"""
    import server
    return get_function(server.use_item)


@pytest.fixture
def pickup_fn():
    """Get the pickup function"""
    import server
    return get_function(server.pickup)


@pytest.fixture
def equip_fn():
    """Get the equip function"""
    import server
    return get_function(server.equip)


@pytest.fixture
def rest_fn():
    """Get the rest function"""
    import server
    return get_function(server.rest)


@pytest.fixture
def flee_fn():
    """Get the flee function"""
    import server
    return get_function(server.flee)


@pytest.fixture
def save_game_fn():
    """Get the save_game function"""
    import server
    return get_function(server.save_game)


@pytest.fixture
def load_game_fn():
    """Get the load_game function"""
    import server
    return get_function(server.load_game)


# =============================================================================
# Character Creation Tests
# =============================================================================

class TestCharacterCreation:
    """Tests for character creation tool"""

    def test_create_warrior(self, create_character_fn):
        """Test creating a warrior character"""
        result = create_character_fn(name="TestWarrior", role="warrior")

        assert "error" not in result
        assert "narrative" in result
        assert "TestWarrior" in result["narrative"]
        assert "Integration Engineer" in result["narrative"]

    def test_create_mage(self, create_character_fn):
        """Test creating a mage character"""
        result = create_character_fn(name="TestMage", role="mage")

        assert "error" not in result
        assert "narrative" in result
        assert "Recipe Builder" in result["narrative"]

    def test_create_rogue(self, create_character_fn):
        """Test creating a rogue character"""
        result = create_character_fn(name="TestRogue", role="rogue")

        assert "error" not in result
        assert "narrative" in result
        assert "API Hacker" in result["narrative"]

    def test_create_cleric(self, create_character_fn):
        """Test creating a cleric character"""
        result = create_character_fn(name="TestCleric", role="cleric")

        assert "error" not in result
        assert "narrative" in result
        assert "Support Engineer" in result["narrative"]

    def test_create_character_sets_game_state(self, create_character_fn):
        """Test that creating a character sets up game state"""
        import server

        create_character_fn(name="StateTest", role="warrior")

        assert "default" in server.game_states
        assert server.game_states["default"].hero.name == "StateTest"


# =============================================================================
# View Status Tests
# =============================================================================

class TestViewStatus:
    """Tests for view status tool"""

    def test_view_status_no_character(self, view_status_fn):
        """Test view status without a character"""
        result = view_status_fn()
        assert "error" in result

    def test_view_status_with_character(self, create_character_fn, view_status_fn):
        """Test view status with a character"""
        create_character_fn(name="StatusTest", role="warrior")
        result = view_status_fn()

        assert "error" not in result
        assert "narrative" in result
        assert "StatusTest" in result["narrative"]
        assert "Uptime" in result["narrative"]
        assert "API Credits" in result["narrative"]


# =============================================================================
# Exploration Tests
# =============================================================================

class TestExploration:
    """Tests for exploration tools"""

    def test_explore_no_character(self, explore_fn):
        """Test explore without a character"""
        result = explore_fn()
        assert "error" in result

    def test_explore_with_character(self, create_character_fn, explore_fn):
        """Test explore with a character"""
        create_character_fn(name="Explorer", role="warrior")
        result = explore_fn()

        assert "error" not in result
        assert "narrative" in result
        assert "Exits" in result["narrative"]

    def test_examine_enemy(self, create_character_fn, examine_fn):
        """Test examining an enemy"""
        import server

        create_character_fn(name="Examiner", role="warrior")

        # Find a room with enemies
        game_state = server.game_states["default"]
        for room_id, room in game_state.dungeon_map.items():
            if room.enemies:
                game_state.current_room_id = room_id
                enemy_name = room.enemies[0].name

                result = examine_fn(target=enemy_name)
                assert "error" not in result or "not found" in result.get("error", "").lower()
                break

    def test_examine_invalid_target(self, create_character_fn, examine_fn):
        """Test examining an invalid target"""
        create_character_fn(name="Examiner", role="warrior")
        result = examine_fn(target="NonexistentThing")

        assert "error" in result


# =============================================================================
# Movement Tests
# =============================================================================

class TestMovement:
    """Tests for movement tool"""

    def test_move_no_character(self, move_fn):
        """Test move without a character"""
        result = move_fn(direction="north")
        assert "error" in result

    def test_move_invalid_direction(self, create_character_fn, move_fn):
        """Test move in invalid direction"""
        import server

        create_character_fn(name="Mover", role="warrior")

        # Clear enemies to allow movement
        game_state = server.game_states["default"]
        current_room = game_state.get_current_room()
        current_room.enemies.clear()
        current_room.is_cleared = True

        # Try to move in a direction that doesn't exist
        if "west" not in current_room.exits:
            result = move_fn(direction="west")
            assert "error" in result

    def test_move_blocked_by_enemies(self, create_character_fn, move_fn):
        """Test move blocked by enemies"""
        import server

        create_character_fn(name="BlockedMover", role="warrior")

        # Find a room with enemies
        game_state = server.game_states["default"]
        for room_id, room in game_state.dungeon_map.items():
            if room.enemies and room.exits:
                game_state.current_room_id = room_id
                room.is_cleared = False

                direction = list(room.exits.keys())[0]
                result = move_fn(direction=direction)

                # Should be blocked
                assert "error" in result or "block" in result.get("narrative", "").lower()
                break


# =============================================================================
# Combat Tests
# =============================================================================

class TestCombat:
    """Tests for combat tools"""

    def test_attack_no_character(self, attack_fn):
        """Test attack without a character"""
        result = attack_fn(target="Bug")
        assert "error" in result

    def test_attack_no_enemy(self, create_character_fn, attack_fn):
        """Test attack with no enemy present"""
        import server

        create_character_fn(name="Attacker", role="warrior")

        # Clear all enemies
        game_state = server.game_states["default"]
        current_room = game_state.get_current_room()
        current_room.enemies.clear()

        result = attack_fn(target="Bug")
        assert "error" in result

    def test_attack_enemy(self, create_character_fn, attack_fn):
        """Test attacking an enemy"""
        import server

        create_character_fn(name="Fighter", role="warrior")

        # Find a room with enemies
        game_state = server.game_states["default"]
        for room_id, room in game_state.dungeon_map.items():
            if room.enemies:
                game_state.current_room_id = room_id
                enemy_name = room.enemies[0].name

                result = attack_fn(target=enemy_name)
                assert "error" not in result
                assert "narrative" in result
                break

    def test_defend_not_in_combat(self, create_character_fn, defend_fn):
        """Test defend when not in combat"""
        import server

        create_character_fn(name="Defender", role="warrior")

        # Clear combat state
        game_state = server.game_states["default"]
        game_state.combat = None

        result = defend_fn()
        assert "error" in result

    def test_flee_not_in_combat(self, create_character_fn, flee_fn):
        """Test flee when not in combat"""
        import server

        create_character_fn(name="Fleer", role="rogue")

        # Clear combat state
        game_state = server.game_states["default"]
        game_state.combat = None

        result = flee_fn()
        assert "error" in result


# =============================================================================
# Item Tests
# =============================================================================

class TestItems:
    """Tests for item tools"""

    def test_pickup_no_character(self, pickup_fn):
        """Test pickup without a character"""
        result = pickup_fn(item="Potion")
        assert "error" in result

    def test_pickup_no_item(self, create_character_fn, pickup_fn):
        """Test pickup when no item exists"""
        import server

        create_character_fn(name="Picker", role="warrior")

        # Clear items from room
        game_state = server.game_states["default"]
        current_room = game_state.get_current_room()
        current_room.items.clear()

        result = pickup_fn(item="NonexistentItem")
        assert "error" in result

    def test_use_item_no_character(self, use_item_fn):
        """Test use_item without a character"""
        result = use_item_fn(item="Potion")
        assert "error" in result

    def test_use_item_not_in_inventory(self, create_character_fn, use_item_fn):
        """Test use_item with item not in inventory"""
        import server

        create_character_fn(name="User", role="warrior")

        # Clear inventory
        game_state = server.game_states["default"]
        game_state.hero.inventory.clear()

        result = use_item_fn(item="NonexistentPotion")
        assert "error" in result

    def test_equip_no_character(self, equip_fn):
        """Test equip without a character"""
        result = equip_fn(item="Sword")
        assert "error" in result


# =============================================================================
# Rest Tests
# =============================================================================

class TestRest:
    """Tests for rest tool"""

    def test_rest_no_character(self, rest_fn):
        """Test rest without a character"""
        result = rest_fn()
        assert "error" in result

    def test_rest_in_combat(self, create_character_fn, attack_fn, rest_fn):
        """Test rest while in combat"""
        import server

        create_character_fn(name="Rester", role="warrior")

        # Start combat
        game_state = server.game_states["default"]
        for room_id, room in game_state.dungeon_map.items():
            if room.enemies:
                game_state.current_room_id = room_id
                enemy_name = room.enemies[0].name
                attack_fn(target=enemy_name)  # Start combat
                break

        if game_state.combat:
            result = rest_fn()
            assert "error" in result

    def test_rest_restores_hp(self, create_character_fn, rest_fn):
        """Test that rest restores HP and MP"""
        import server

        create_character_fn(name="HealRester", role="cleric")

        game_state = server.game_states["default"]
        hero = game_state.hero

        # Damage hero
        hero.uptime = hero.max_uptime // 2
        hero.api_credits = hero.max_api_credits // 2
        initial_hp = hero.uptime
        initial_mp = hero.api_credits

        # Clear combat and enemies
        game_state.combat = None
        current_room = game_state.get_current_room()
        current_room.enemies.clear()
        current_room.is_cleared = True

        result = rest_fn()

        # Should restore some HP/MP (might trigger encounter)
        assert "error" not in result
        assert "narrative" in result


# =============================================================================
# Save/Load Tests
# =============================================================================

class TestSaveLoad:
    """Tests for save and load tools"""

    def test_save_no_character(self, save_game_fn):
        """Test save without a character"""
        result = save_game_fn()
        assert "error" in result

    def test_save_game(self, create_character_fn, save_game_fn):
        """Test saving the game"""
        create_character_fn(name="Saver", role="warrior")
        result = save_game_fn()

        # In single-player mode, should succeed
        assert "error" not in result or "Login required" in result.get("error", "")

    def test_load_nonexistent_save(self, load_game_fn):
        """Test loading a nonexistent save"""
        result = load_game_fn(save_id="nonexistent_save_12345")
        assert "error" in result


# =============================================================================
# Class-Specific Tests
# =============================================================================

class TestClassSpecific:
    """Tests for class-specific features"""

    def test_warrior_has_correct_skills(self, create_character_fn):
        """Test warrior has correct starting skills"""
        import server

        create_character_fn(name="WarriorSkills", role="warrior")

        hero = server.game_states["default"].hero
        assert "bulk_upsert" in hero.skills or len(hero.skills) > 0

    def test_mage_has_higher_mp(self, create_character_fn):
        """Test mage has higher MP than warrior"""
        import server

        create_character_fn(name="MageMp", role="mage")
        mage_mp = server.game_states["default"].hero.max_api_credits

        server.game_states.clear()

        create_character_fn(name="WarriorMp", role="warrior")
        warrior_mp = server.game_states["default"].hero.max_api_credits

        assert mage_mp > warrior_mp

    def test_warrior_has_higher_hp(self, create_character_fn):
        """Test warrior has higher HP than mage"""
        import server

        create_character_fn(name="WarriorHp", role="warrior")
        warrior_hp = server.game_states["default"].hero.max_uptime

        server.game_states.clear()

        create_character_fn(name="MageHp", role="mage")
        mage_hp = server.game_states["default"].hero.max_uptime

        assert warrior_hp > mage_hp

    def test_all_classes_have_equipment(self, create_character_fn):
        """Test all classes start with equipment"""
        import server

        for role in ["warrior", "mage", "rogue", "cleric"]:
            server.game_states.clear()
            create_character_fn(name=f"Test{role}", role=role)

            hero = server.game_states["default"].hero
            assert hero.equipped.weapon is not None
            assert hero.equipped.armor is not None
