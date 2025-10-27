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
    """Create a sample game for testing."""
    game = Game(game_id="test-game-123", rows=5, cols=5)
    # Override default positions
    game.robot.position = Position(0, 0)
    game.robot.orientation = Direction.NORTH
    game.princess.position = Position(4, 4)
    # Add some flowers
    game.flowers = {Position(2, 2), Position(3, 3)}
    game.board.initial_flowers_count = len(game.flowers)
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
        # Setup mock response
        mock_ml_client.predict_action.return_value = {
            "action": "move",
            "direction": "north",
            "confidence": 0.85,
            "board_score": 12.5,
        }

        player = MLProxyPlayer(mock_ml_client, strategy="default")
        result = await player.solve_async(sample_game, "test-game-123")

        # Verify ML client was called
        mock_ml_client.predict_action.assert_called_once()
        call_args = mock_ml_client.predict_action.call_args
        assert call_args.kwargs["game_id"] == "test-game-123"
        assert call_args.kwargs["strategy"] == "default"

        # Verify result
        assert len(result) == 1
        assert result[0] == ("move", Direction.NORTH)

    @pytest.mark.asyncio
    async def test_solve_async_returns_pick_action(self, mock_ml_client, sample_game):
        """Test solve_async with pick action."""
        mock_ml_client.predict_action.return_value = {
            "action": "pick",
            "direction": "south",
            "confidence": 0.92,
        }

        player = MLProxyPlayer(mock_ml_client)
        result = await player.solve_async(sample_game, "test-game-123")

        assert len(result) == 1
        assert result[0] == ("pick", Direction.SOUTH)

    @pytest.mark.asyncio
    async def test_solve_async_returns_give_action(self, mock_ml_client, sample_game):
        """Test solve_async with give action."""
        mock_ml_client.predict_action.return_value = {
            "action": "give",
            "direction": "east",
            "confidence": 0.95,
        }

        player = MLProxyPlayer(mock_ml_client)
        result = await player.solve_async(sample_game, "test-game-123")

        assert len(result) == 1
        assert result[0] == ("give", Direction.EAST)

    @pytest.mark.asyncio
    async def test_solve_async_returns_clean_action(self, mock_ml_client, sample_game):
        """Test solve_async with clean action."""
        mock_ml_client.predict_action.return_value = {
            "action": "clean",
            "direction": "west",
            "confidence": 0.78,
        }

        player = MLProxyPlayer(mock_ml_client)
        result = await player.solve_async(sample_game, "test-game-123")

        assert len(result) == 1
        assert result[0] == ("clean", Direction.WEST)

    @pytest.mark.asyncio
    async def test_solve_async_without_direction(self, mock_ml_client, sample_game):
        """Test solve_async when direction is not provided."""
        mock_ml_client.predict_action.return_value = {"action": "rotate", "confidence": 0.88}

        player = MLProxyPlayer(mock_ml_client)
        result = await player.solve_async(sample_game, "test-game-123")

        assert len(result) == 1
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
        mock_ml_client.predict_action.return_value = {"action": "move", "direction": "north"}

        player = MLProxyPlayer(mock_ml_client)
        await player.solve_async(sample_game, "test-game-123")

        # Check the game state passed to ML client
        call_args = mock_ml_client.predict_action.call_args
        game_state = call_args.kwargs["game_state"]

        assert game_state["status"] == "In Progress"
        assert game_state["board"]["rows"] == 5
        assert game_state["board"]["cols"] == 5
        assert len(game_state["board"]["flowers_positions"]) == 2
        assert len(game_state["board"]["obstacles_positions"]) == 7
        assert game_state["robot"]["position"]["row"] == 0
        assert game_state["robot"]["position"]["col"] == 0
        assert game_state["robot"]["orientation"] == "north"
        assert game_state["princess"]["position"]["row"] == 4
        assert game_state["princess"]["position"]["col"] == 4

    @pytest.mark.asyncio
    async def test_game_state_conversion_with_obstacles(self, mock_ml_client, sample_game):
        """Test game state conversion with obstacles."""
        sample_game.board.obstacles_positions.add(Position(1, 1))
        sample_game.board.obstacles_positions.add(Position(2, 1))

        mock_ml_client.predict_action.return_value = {"action": "clean", "direction": "south"}

        player = MLProxyPlayer(mock_ml_client)
        await player.solve_async(sample_game, "test-game-123")

        # Check obstacles in game state
        call_args = mock_ml_client.predict_action.call_args
        game_state = call_args.kwargs["game_state"]

        # assert len(game_state["board"]["obstacles_positions"]) == sample_game.board.initial_obstacles_count
        obstacle_positions = [Position(p["row"], p["col"]) for p in game_state["board"]["obstacles_positions"]]
        assert Position(1, 1) in obstacle_positions
        assert Position(2, 1) in obstacle_positions

    @pytest.mark.asyncio
    async def test_game_state_conversion_with_robot_flowers(self, mock_ml_client, sample_game):
        """Test game state conversion with robot holding flowers."""
        sample_game.robot.flowers_collected = [Position(1, 1), Position(2, 2), Position(3, 3)]

        mock_ml_client.predict_action.return_value = {"action": "give", "direction": "north"}

        player = MLProxyPlayer(mock_ml_client)
        await player.solve_async(sample_game, "test-game-123")

        # Check robot flowers in game state
        call_args = mock_ml_client.predict_action.call_args
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
        mock_ml_client.predict_action.return_value = {"action": "move", "direction": "north"}

        player = MLProxyPlayer(mock_ml_client, strategy="aggressive")
        await player.solve_async(sample_game, "test-game-123")

        call_args = mock_ml_client.predict_action.call_args
        assert call_args.kwargs["strategy"] == "aggressive"

    @pytest.mark.asyncio
    async def test_conservative_strategy_parameter(self, mock_ml_client, sample_game):
        """Test that conservative strategy is passed to ML client."""
        mock_ml_client.predict_action.return_value = {"action": "pick", "direction": "south"}

        player = MLProxyPlayer(mock_ml_client, strategy="conservative")
        await player.solve_async(sample_game, "test-game-123")

        call_args = mock_ml_client.predict_action.call_args
        assert call_args.kwargs["strategy"] == "conservative"
