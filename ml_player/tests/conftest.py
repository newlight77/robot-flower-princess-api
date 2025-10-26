"""Pytest configuration and fixtures for ML Player tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from hexagons.mlplayer.domain.core.value_objects.game_state import GameState
from hexagons.mlplayer.domain.core.value_objects import StrategyConfig
from hexagons.mlplayer.domain.ports.game_client import GameClientPort


@pytest.fixture
def default_strategy_config() -> StrategyConfig:
    """Create default strategy configuration."""
    return StrategyConfig.default()


@pytest.fixture
def mock_game_client() -> GameClientPort:
    """Create a mock game client."""
    client = AsyncMock(spec=GameClientPort)

    # Mock get_game_state response
    client.get_game_state.return_value = {
        "id": "test-game-123",
        "robot": {
            "position": {"row": 0, "col": 0},
            "orientation": "EAST",
            "flowers": {"held": 0, "capacity": 5},
        },
        "princess": {
            "position": {"row": 4, "col": 4},
            "flowers": {"delivered": 0, "required": 3},
        },
        "board": {"rows": 5, "cols": 5},
        "flowers": {"positions": [{"row": 1, "col": 1}, {"row": 2, "col": 2}]},
        "obstacles": {"positions": [{"row": 1, "col": 2}]},
        "status": "IN_PROGRESS",
    }

    # Mock execute_action response
    client.execute_action.return_value = {"success": True}

    return client


@pytest.fixture
def sample_game_state() -> dict:
    """Create a sample game state dictionary."""
    return {
        "id": "test-game-123",
        "robot": {
            "position": {"row": 0, "col": 0},
            "orientation": "EAST",
            "flowers": {"held": 0, "capacity": 5},
        },
        "princess": {
            "position": {"row": 4, "col": 4},
            "flowers": {"delivered": 0, "required": 3},
        },
        "board": {"rows": 5, "cols": 5},
        "flowers": {"positions": [{"row": 1, "col": 1}, {"row": 2, "col": 2}]},
        "obstacles": {"positions": [{"row": 1, "col": 2}]},
        "status": "IN_PROGRESS",
    }
