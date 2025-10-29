"""Integration tests for gameplay data collection."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


@pytest.fixture
def enable_data_collection(monkeypatch):
    """Enable data collection for tests."""
    # Clear the lru_cache before enabling to ensure fresh instance
    from configurator.dependencies import get_gameplay_data_collector

    get_gameplay_data_collector.cache_clear()

    monkeypatch.setenv("ENABLE_DATA_COLLECTION", "true")
    yield

    # Clear cache after test
    get_gameplay_data_collector.cache_clear()


@pytest.fixture
def mock_ml_player_http():
    """Mock HTTP calls to ML Player service."""
    with patch("hexagons.game.driven.adapters.gameplay_data_collector.httpx.Client") as mock_client:
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "message": "Data collected", "samples_collected": 1}
        mock_response.raise_for_status.return_value = None  # Mock raise_for_status
        mock_instance.post.return_value = mock_response
        mock_instance.__enter__.return_value = mock_instance
        mock_instance.__exit__.return_value = None
        mock_client.return_value = mock_instance
        yield mock_instance


def test_data_collection_disabled_by_default(client: TestClient, create_game, mock_ml_player_http, monkeypatch):
    """Test that data collection can be disabled via environment variable."""
    # Clear cache to ensure fresh instance
    from configurator.dependencies import get_gameplay_data_collector

    # Disable data collection via environment variable
    monkeypatch.setenv("ENABLE_DATA_COLLECTION", "false")
    get_gameplay_data_collector.cache_clear()

    # GIVEN
    game_id = create_game(rows=5, cols=5)
    action = {"action": "move", "direction": "SOUTH"}

    # WHEN
    response = client.post(
        f"/api/games/{game_id}/action",
        json=action,
    )

    # THEN
    assert response.status_code == 200
    # Verify NO HTTP call was made to ML Player (collection is disabled)
    mock_ml_player_http.post.assert_not_called()

    # Clear cache after test
    get_gameplay_data_collector.cache_clear()


def test_data_collection_enabled(client: TestClient, create_game, enable_data_collection, mock_ml_player_http):
    """Test that data is collected when enabled."""
    # GIVEN
    game_id = create_game(rows=5, cols=5)
    action = {"action": "move", "direction": "SOUTH"}

    # WHEN
    response = client.post(
        f"/api/games/{game_id}/action",
        json=action,
    )

    # THEN
    assert response.status_code == 200
    # Note: Move might fail if robot hits boundary or obstacle - that's OK for data collection test
    # We just want to verify data was collected regardless of action success

    # Verify HTTP call was made to ML Training hexagon
    mock_ml_player_http.post.assert_called_once()
    call_args = mock_ml_player_http.post.call_args

    # Verify the URL
    assert "/api/ml-training/collect" in call_args[0][0]

    # Verify the payload structure
    payload = call_args[1]["json"]
    assert "game_id" in payload
    assert payload["game_id"] == game_id
    assert "timestamp" in payload
    assert "game_state" in payload
    assert "action" in payload
    assert payload["action"] == "move"
    assert "direction" in payload
    assert payload["direction"].upper() == "SOUTH"
    assert "outcome" in payload
    assert "success" in payload["outcome"]  # Outcome can be True or False - both are valid for testing data collection


def test_data_collection_multiple_actions(client: TestClient, create_game, enable_data_collection, mock_ml_player_http):
    """Test that multiple actions are collected correctly."""
    # GIVEN
    game_id = create_game(rows=5, cols=5)
    actions = [
        {"action": "move", "direction": "SOUTH"},
        {"action": "rotate", "direction": "EAST"},
        {"action": "move", "direction": "EAST"},
    ]

    # WHEN
    for action in actions:
        response = client.post(
            f"/api/games/{game_id}/action",
            json=action,
        )
        assert response.status_code == 200

    # THEN
    # Verify HTTP call was made 3 times to ML Player
    assert mock_ml_player_http.post.call_count == 3

    # Verify each call had the correct action
    for call_index, expected_action in enumerate(actions):
        call_args = mock_ml_player_http.post.call_args_list[call_index]
        payload = call_args[1]["json"]

        assert payload["game_id"] == game_id
        # Map action names
        action_map = {"move": "move", "rotate": "rotate", "pickFlower": "pick"}
        expected_action_name = action_map.get(expected_action["action"], expected_action["action"])
        assert payload["action"] == expected_action_name
        assert payload["direction"].upper() == expected_action["direction"].upper()


def test_data_collection_format_compatible_with_ml_player(
    client: TestClient, create_game, enable_data_collection, mock_ml_player_http
):
    """Test that collected data format is compatible with ML Player."""
    # GIVEN
    game_id = create_game(rows=5, cols=5)
    action = {"action": "move", "direction": "SOUTH"}

    # WHEN
    response = client.post(
        f"/api/games/{game_id}/action",
        json=action,
    )

    # THEN
    assert response.status_code == 200

    # Verify HTTP call was made
    mock_ml_player_http.post.assert_called_once()
    call_args = mock_ml_player_http.post.call_args
    payload = call_args[1]["json"]

    # Verify ML Player compatible structure
    assert "game_state" in payload
    game_state = payload["game_state"]

    # Check required fields for ML Player
    assert "board" in game_state
    assert "robot" in game_state
    assert "princess" in game_state

    board = game_state["board"]
    assert "rows" in board
    assert "cols" in board
    assert "robot_position" in board
    assert "princess_position" in board
    assert "flowers_positions" in board
    assert "obstacles_positions" in board

    robot = game_state["robot"]
    assert "position" in robot
    assert "orientation" in robot
    assert "flowers_collected" in robot

    # Check action format
    assert payload["action"] in ["move", "rotate", "pick", "drop", "give", "clean"]
    # Direction can be uppercase or lowercase (depends on where it's converted)
    assert payload["direction"].upper() in ["NORTH", "SOUTH", "EAST", "WEST"]
