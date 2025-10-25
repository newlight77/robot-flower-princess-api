"""Unit tests for HttpMLPlayerClient."""

import pytest
from unittest.mock import AsyncMock, patch

from hexagons.mlplayer.driven.adapters import HttpMLPlayerClient


@pytest.fixture
def ml_player_client():
    """Create HttpMLPlayerClient instance for testing."""
    return HttpMLPlayerClient(base_url="http://localhost:8001", timeout=30)


@pytest.fixture
def sample_game_state():
    """Create a sample game state for testing."""
    return {
        "status": "In Progress",
        "board": {"rows": 5, "cols": 5},
        "robot": {
            "position": {"row": 0, "col": 0},
            "orientation": "EAST",
            "flowers": {"held": 0, "capacity": 5},
        },
        "princess": {
            "position": {"row": 4, "col": 4},
            "flowers": {"delivered": 0, "required": 3},
        },
        "obstacles": {"positions": [{"row": 1, "col": 2}]},
        "flowers": {"positions": [{"row": 1, "col": 1}, {"row": 2, "col": 2}]},
    }


@pytest.mark.asyncio
async def test_predict_action_success(ml_player_client, sample_game_state):
    """Test successful action prediction."""
    mock_response = {
        "game_id": "test-game-123",
        "action": "move",
        "direction": "NORTH",
        "confidence": 0.85,
        "board_score": 12.5,
        "config_used": {"distance_to_flower_weight": -2.5},
    }

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=AsyncMock(
                raise_for_status=AsyncMock(),
                json=AsyncMock(return_value=mock_response)
            )
        )

        result = await ml_player_client.predict_action(
            game_id="test-game-123",
            strategy="default",
            game_state=sample_game_state
        )

        assert result["game_id"] == "test-game-123"
        assert result["action"] == "move"
        assert result["direction"] == "NORTH"
        assert result["confidence"] == 0.85


@pytest.mark.asyncio
async def test_predict_action_with_different_strategy(ml_player_client, sample_game_state):
    """Test action prediction with different strategy."""
    mock_response = {
        "game_id": "test-game-123",
        "action": "pick",
        "direction": None,
        "confidence": 0.9,
        "board_score": 15.0,
        "config_used": {"risk_aversion": 0.3},
    }

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=AsyncMock(
                raise_for_status=AsyncMock(),
                json=AsyncMock(return_value=mock_response)
            )
        )

        result = await ml_player_client.predict_action(
            game_id="test-game-123",
            strategy="aggressive",
            game_state=sample_game_state
        )

        assert result["action"] == "pick"
        assert result["confidence"] == 0.9


@pytest.mark.asyncio
async def test_get_strategies_success(ml_player_client):
    """Test getting list of strategies."""
    mock_response = [
        {
            "strategy_name": "default",
            "config": {"risk_aversion": 0.7, "exploration_factor": 0.3}
        },
        {
            "strategy_name": "aggressive",
            "config": {"risk_aversion": 0.3, "exploration_factor": 0.5}
        },
        {
            "strategy_name": "conservative",
            "config": {"risk_aversion": 0.9, "exploration_factor": 0.1}
        },
    ]

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=AsyncMock(
                raise_for_status=AsyncMock(),
                json=AsyncMock(return_value=mock_response)
            )
        )

        result = await ml_player_client.get_strategies()

        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0]["strategy_name"] == "default"
        assert result[1]["strategy_name"] == "aggressive"


@pytest.mark.asyncio
async def test_get_strategy_success(ml_player_client):
    """Test getting specific strategy configuration."""
    mock_response = {
        "strategy_name": "default",
        "config": {
            "distance_to_flower_weight": -2.5,
            "distance_to_princess_weight": -1.0,
            "risk_aversion": 0.7,
            "exploration_factor": 0.3,
        }
    }

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=AsyncMock(
                raise_for_status=AsyncMock(),
                json=AsyncMock(return_value=mock_response)
            )
        )

        result = await ml_player_client.get_strategy("default")

        assert result["strategy_name"] == "default"
        assert "config" in result
        assert result["config"]["risk_aversion"] == 0.7


@pytest.mark.asyncio
async def test_health_check_success(ml_player_client):
    """Test health check endpoint."""
    mock_response = {
        "status": "healthy",
        "service": "ML Player Service",
        "version": "0.1.0",
        "ml_enabled": False,
    }

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=AsyncMock(
                raise_for_status=AsyncMock(),
                json=AsyncMock(return_value=mock_response)
            )
        )

        result = await ml_player_client.health_check()

        assert result["status"] == "healthy"
        assert result["service"] == "ML Player Service"


@pytest.mark.asyncio
async def test_client_with_custom_timeout():
    """Test client initialization with custom timeout."""
    client = HttpMLPlayerClient(base_url="http://localhost:8001", timeout=60)

    assert client.base_url == "http://localhost:8001"
    assert client.timeout == 60


@pytest.mark.asyncio
async def test_client_strips_trailing_slash():
    """Test that base URL trailing slash is stripped."""
    client = HttpMLPlayerClient(base_url="http://localhost:8001/", timeout=30)

    assert client.base_url == "http://localhost:8001"


@pytest.mark.asyncio
async def test_predict_action_constructs_correct_payload(ml_player_client, sample_game_state):
    """Test that predict_action constructs the correct payload."""
    mock_response = {"game_id": "test", "action": "move"}

    with patch("httpx.AsyncClient") as mock_client:
        mock_post = AsyncMock(
            return_value=AsyncMock(
                raise_for_status=AsyncMock(),
                json=AsyncMock(return_value=mock_response)
            )
        )
        mock_client.return_value.__aenter__.return_value.post = mock_post

        await ml_player_client.predict_action(
            game_id="test-game-123",
            strategy="conservative",
            game_state=sample_game_state
        )

        # Verify the call was made with correct URL and payload
        call_args = mock_post.call_args
        assert "http://localhost:8001/api/ml-player/predict/test-game-123" in str(call_args)

        # Check payload structure
        payload = call_args.kwargs["json"]
        assert payload["strategy"] == "conservative"
        assert payload["game_id"] == "test-game-123"
        assert payload["board"] == sample_game_state["board"]
        assert payload["robot"] == sample_game_state["robot"]
