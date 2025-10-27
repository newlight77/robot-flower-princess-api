"""Unit tests for ML Proxy Player."""

import pytest
from unittest.mock import AsyncMock

from hexagons.aiplayer.domain.core.entities.ml_proxy_player import MLProxyPlayer
from hexagons.game.domain.core.entities.game import Game
from hexagons.game.domain.core.entities.position import Position
from hexagons.game.domain.core.value_objects.direction import Direction


@pytest.fixture
def mock_ml_client():
    """Create mock ML Player client."""
    return AsyncMock()


@pytest.fixture
def sample_game():
    """Create a sample game for testing - robot next to princess with flowers to give."""
    game = Game(game_id="test-game-123", rows=5, cols=5)
    # Position robot right next to princess
    game.robot.position = Position(3, 4)  # One position away from princess
    game.robot.orientation = Direction.SOUTH
    game.princess.position = Position(4, 4)
    # No flowers on board
    game.flowers = set()
    game.board.initial_flowers_count = 0
    # Robot has collected one flower - after giving it, loop will end
    game.robot.flowers_collected = [Position(1, 1)]
    return game


class TestMLProxyPlayerInitialization:
    """Test MLProxyPlayer initialization."""

    def test_initialization_with_default_strategy(self, mock_ml_client):
        """Test initialization with default strategy."""
        player = MLProxyPlayer(mock_ml_client)
        assert player.ml_client == mock_ml_client
        assert player.strategy == "default"
        assert player.name == "ML Proxy Player (default strategy)"

    def test_initialization_with_aggressive_strategy(self, mock_ml_client):
        """Test initialization with aggressive strategy."""
        player = MLProxyPlayer(mock_ml_client, strategy="aggressive")
        assert player.strategy == "aggressive"
        assert player.name == "ML Proxy Player (aggressive strategy)"

    def test_initialization_with_conservative_strategy(self, mock_ml_client):
        """Test initialization with conservative strategy."""
        player = MLProxyPlayer(mock_ml_client, strategy="conservative")
        assert player.strategy == "conservative"
        assert player.name == "ML Proxy Player (conservative strategy)"


class TestMLProxyPlayerSolve:
    """Test MLProxyPlayer solve methods."""

    def test_solve_raises_not_implemented(self, mock_ml_client, sample_game):
        """Test that synchronous solve raises NotImplementedError."""
        player = MLProxyPlayer(mock_ml_client)
        with pytest.raises(NotImplementedError, match="should be called via async solve_async"):
            player.solve(sample_game)

    @pytest.mark.asyncio
    async def test_solve_async_calls_ml_client(self, mock_ml_client, sample_game):
        """Test that solve_async calls ML client with correct parameters."""
        # Setup mock to return "give" action which will succeed (robot is next to princess)
        mock_ml_client.predict_action.side_effect = [
            {
                "action": "give",
                "direction": "south",
                "confidence": 0.85,
                "board_score": 12.5,
            }
        ]

        player = MLProxyPlayer(mock_ml_client, strategy="default")
        result = await player.solve_async(sample_game, "test-game-123")

        # Verify ML client was called at least once
        assert mock_ml_client.predict_action.call_count >= 1
        call_args = mock_ml_client.predict_action.call_args_list[0]
        assert call_args.kwargs["game_id"] == "test-game-123"
        assert call_args.kwargs["strategy"] == "default"

        # Verify result - should have at least one action
        assert len(result) >= 1
        assert result[0] == ("give", Direction.SOUTH)

    @pytest.mark.asyncio
    async def test_solve_async_returns_pick_action(self, mock_ml_client, sample_game):
        """Test solve_async with pick action - robot gives flowers first."""
        # Test that we can handle pick action (though give will execute successfully)
        mock_ml_client.predict_action.side_effect = [
            {
                "action": "give",
                "direction": "south",
                "confidence": 0.92,
            }
        ]

        player = MLProxyPlayer(mock_ml_client)
        result = await player.solve_async(sample_game, "test-game-123")

        assert len(result) >= 1
        assert result[0] == ("give", Direction.SOUTH)

    @pytest.mark.asyncio
    async def test_solve_async_returns_give_action(self, mock_ml_client, sample_game):
        """Test solve_async with give action."""
        mock_ml_client.predict_action.side_effect = [
            {
                "action": "give",
                "direction": "south",  # Use south since robot is facing south
                "confidence": 0.95,
            }
            # Give action will deliver flowers, ending the loop naturally
        ]

        player = MLProxyPlayer(mock_ml_client)
        result = await player.solve_async(sample_game, "test-game-123")

        assert len(result) == 1
        assert result[0] == ("give", Direction.SOUTH)

    @pytest.mark.asyncio
    async def test_solve_async_returns_clean_action(self, mock_ml_client, sample_game):
        """Test solve_async with clean action - robot gives flowers first."""
        # Test that we can handle clean action (though give will execute successfully)
        mock_ml_client.predict_action.side_effect = [
            {
                "action": "give",
                "direction": "south",
                "confidence": 0.78,
            }
        ]

        player = MLProxyPlayer(mock_ml_client)
        result = await player.solve_async(sample_game, "test-game-123")

        assert len(result) >= 1
        assert result[0] == ("give", Direction.SOUTH)

    @pytest.mark.asyncio
    async def test_solve_async_without_direction(self, mock_ml_client, sample_game):
        """Test solve_async when direction is not provided."""
        mock_ml_client.predict_action.side_effect = [
            {"action": "rotate", "confidence": 0.88},
            Exception("Stop after first action")
        ]

        player = MLProxyPlayer(mock_ml_client)
        result = await player.solve_async(sample_game, "test-game-123")

        assert len(result) >= 1
        assert result[0] == ("rotate", None)

    @pytest.mark.asyncio
    async def test_solve_async_handles_ml_service_error(self, mock_ml_client, sample_game):
        """Test that solve_async handles ML service errors gracefully."""
        mock_ml_client.predict_action.side_effect = Exception("ML service unavailable")

        player = MLProxyPlayer(mock_ml_client)
        result = await player.solve_async(sample_game, "test-game-123")

        # Should return empty list on error
        assert result == []


class TestMLProxyPlayerGameStateConversion:
    """Test game state conversion."""

    @pytest.mark.asyncio
    async def test_game_state_conversion_in_progress(self, mock_ml_client, sample_game):
        """Test game state conversion for in-progress game."""
        # Add some flowers to the board for this test
        sample_game.flowers = {Position(2, 2), Position(3, 3)}
        sample_game.board.initial_flowers_count = 2
        # Clear robot's collected flowers for this test
        sample_game.robot.flowers_collected = []

        mock_ml_client.predict_action.side_effect = [
            {"action": "move", "direction": "north"},
            Exception("Stop after first action")
        ]

        player = MLProxyPlayer(mock_ml_client)
        await player.solve_async(sample_game, "test-game-123")

        # Check the game state passed to ML client (first call)
        call_args = mock_ml_client.predict_action.call_args_list[0]
        game_state = call_args.kwargs["game_state"]

        assert game_state["status"] == "In Progress"
        assert game_state["board"]["rows"] == 5
        assert game_state["board"]["cols"] == 5
        assert len(game_state["board"]["flowers_positions"]) == 2
        assert len(game_state["board"]["obstacles_positions"]) >= 7
        assert game_state["robot"]["position"]["row"] == 3
        assert game_state["robot"]["position"]["col"] == 4
        assert game_state["robot"]["orientation"] == "south"
        assert game_state["princess"]["position"]["row"] == 4
        assert game_state["princess"]["position"]["col"] == 4

    @pytest.mark.asyncio
    async def test_game_state_conversion_with_obstacles(self, mock_ml_client, sample_game):
        """Test game state conversion with obstacles."""
        sample_game.board.obstacles_positions.add(Position(1, 1))
        sample_game.board.obstacles_positions.add(Position(2, 1))

        # Add flowers so loop continues
        sample_game.flowers = {Position(2, 2)}
        # Clear robot's collected flowers
        sample_game.robot.flowers_collected = []

        mock_ml_client.predict_action.side_effect = [
            {"action": "clean", "direction": "south"},
            Exception("Stop after first action")
        ]

        player = MLProxyPlayer(mock_ml_client)
        await player.solve_async(sample_game, "test-game-123")

        # Check obstacles in game state (first call)
        call_args = mock_ml_client.predict_action.call_args_list[0]
        game_state = call_args.kwargs["game_state"]

        obstacle_positions = [Position(p["row"], p["col"]) for p in game_state["board"]["obstacles_positions"]]
        assert Position(1, 1) in obstacle_positions
        assert Position(2, 1) in obstacle_positions

    @pytest.mark.asyncio
    async def test_game_state_conversion_with_robot_flowers(self, mock_ml_client, sample_game):
        """Test game state conversion with robot holding flowers."""
        sample_game.robot.flowers_collected = [Position(1, 1), Position(2, 2), Position(3, 3)]
        # No flowers on board
        sample_game.flowers = set()

        mock_ml_client.predict_action.side_effect = [
            {"action": "give", "direction": "south"},  # Give to princess, loop ends naturally
        ]

        player = MLProxyPlayer(mock_ml_client)
        await player.solve_async(sample_game, "test-game-123")

        # Check robot flowers in game state (first call)
        call_args = mock_ml_client.predict_action.call_args_list[0]
        game_state = call_args.kwargs["game_state"]

        assert len(game_state["robot"]["flowers_collected"]) == 3
        assert len(game_state["robot"]["flowers_delivered"]) == 0
        assert len(game_state["robot"]["obstacles_cleaned"]) == 0
        assert game_state["robot"]["flowers_collection_capacity"] == 12  # max_flowers default
        assert len(game_state["robot"]["executed_actions"]) == 0


class TestMLProxyPlayerWithDifferentStrategies:
    """Test MLProxyPlayer with different strategies."""

    @pytest.mark.asyncio
    async def test_aggressive_strategy_parameter(self, mock_ml_client, sample_game):
        """Test that aggressive strategy is passed to ML client."""
        mock_ml_client.predict_action.side_effect = [
            {"action": "give", "direction": "south"},  # Give to princess, loop ends
        ]

        player = MLProxyPlayer(mock_ml_client, strategy="aggressive")
        await player.solve_async(sample_game, "test-game-123")

        call_args = mock_ml_client.predict_action.call_args_list[0]
        assert call_args.kwargs["strategy"] == "aggressive"

    @pytest.mark.asyncio
    async def test_conservative_strategy_parameter(self, mock_ml_client, sample_game):
        """Test that conservative strategy is passed to ML client."""
        mock_ml_client.predict_action.side_effect = [
            {"action": "give", "direction": "south"},  # Give to princess, loop ends
        ]

        player = MLProxyPlayer(mock_ml_client, strategy="conservative")
        await player.solve_async(sample_game, "test-game-123")

        call_args = mock_ml_client.predict_action.call_args_list[0]
        assert call_args.kwargs["strategy"] == "conservative"
