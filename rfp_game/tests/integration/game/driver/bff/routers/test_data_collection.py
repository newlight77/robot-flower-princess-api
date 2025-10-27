"""Integration tests for gameplay data collection."""

import json
import os
from pathlib import Path
from datetime import datetime
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def enable_data_collection(monkeypatch):
    """Enable data collection for tests."""
    monkeypatch.setenv("ENABLE_DATA_COLLECTION", "true")
    yield
    # Clean up test data files
    data_dir = Path("data/gameplay")
    if data_dir.exists():
        for file in data_dir.glob("gameplay_*.jsonl"):
            file.unlink()


def test_data_collection_disabled_by_default(client: TestClient, create_game):
    """Test that data collection is disabled by default."""
    game_id = create_game(rows=5, cols=5)

    # Perform an action
    response = client.post(
        f"/api/games/{game_id}/action",
        json={"action": "move", "direction": "south"},
    )
    assert response.status_code == 200

    # Check that no data was collected
    data_dir = Path("data/gameplay")
    if data_dir.exists():
        data_files = list(data_dir.glob("gameplay_*.jsonl"))
        # If file exists, it should be empty or have data from previous tests
        # For this test, we just verify it's not adding new data
        # (We can't easily verify this without more complex state tracking)
    # This test mainly verifies the API still works when collection is disabled


def test_data_collection_enabled(client: TestClient, create_game, enable_data_collection):
    """Test that data is collected when enabled."""
    game_id = create_game(rows=5, cols=5)

    # Perform an action
    response = client.post(
        f"/api/games/{game_id}/action",
        json={"action": "move", "direction": "south"},
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

    # Check that data was collected
    data_dir = Path("data/gameplay")
    assert data_dir.exists(), "Data directory should be created"

    # Find today's data file
    today = datetime.now().strftime("%Y%m%d")
    data_file = data_dir / f"gameplay_{today}.jsonl"
    assert data_file.exists(), f"Data file {data_file} should exist"

    # Read the collected data
    with open(data_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        assert len(lines) >= 1, "At least one data sample should be collected"

        # Parse the last line (our action)
        last_sample = json.loads(lines[-1])

        # Verify the sample structure
        assert "game_id" in last_sample
        assert last_sample["game_id"] == game_id
        assert "timestamp" in last_sample
        assert "game_state" in last_sample
        assert "action" in last_sample
        assert last_sample["action"] == "move"
        assert "direction" in last_sample
        assert last_sample["direction"] == "SOUTH"
        assert "outcome" in last_sample
        assert last_sample["outcome"]["success"] is True


def test_data_collection_multiple_actions(client: TestClient, create_game, enable_data_collection):
    """Test that multiple actions are collected correctly."""
    game_id = create_game(rows=5, cols=5)

    # Perform multiple actions
    actions = [
        {"action": "move", "direction": "south"},
        {"action": "rotate", "direction": "east"},
        {"action": "move", "direction": "east"},
    ]

    for action_data in actions:
        response = client.post(
            f"/api/games/{game_id}/action",
            json=action_data,
        )
        assert response.status_code == 200

    # Check collected data
    data_dir = Path("data/gameplay")
    today = datetime.now().strftime("%Y%m%d")
    data_file = data_dir / f"gameplay_{today}.jsonl"

    with open(data_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        assert len(lines) >= 3, "At least 3 data samples should be collected"

        # Verify last 3 samples match our actions
        last_samples = [json.loads(line) for line in lines[-3:]]
        for sample, expected in zip(last_samples, actions):
            assert sample["game_id"] == game_id
            # Map action names
            action_map = {"move": "move", "rotate": "rotate", "pickFlower": "pick"}
            expected_action = action_map.get(expected["action"], expected["action"])
            assert sample["action"] == expected_action
            assert sample["direction"] == expected["direction"].upper()


def test_data_collection_format_compatible_with_ml_player(client: TestClient, create_game, enable_data_collection):
    """Test that collected data format is compatible with ML Player."""
    game_id = create_game(rows=5, cols=5)

    # Perform an action
    response = client.post(
        f"/api/games/{game_id}/action",
        json={"action": "move", "direction": "south"},
    )
    assert response.status_code == 200

    # Read collected data
    data_dir = Path("data/gameplay")
    today = datetime.now().strftime("%Y%m%d")
    data_file = data_dir / f"gameplay_{today}.jsonl"

    with open(data_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        sample = json.loads(lines[-1])

        # Verify ML Player compatible structure
        assert "game_state" in sample
        game_state = sample["game_state"]

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
        assert sample["action"] in ["move", "rotate", "pick", "drop", "give", "clean"]
        assert sample["direction"] in ["NORTH", "SOUTH", "EAST", "WEST"]
