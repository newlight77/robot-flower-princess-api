"""Unit tests for AIMLPlayer."""

import pytest

from hexagons.mlplayer.domain.core.entities import AIMLPlayer
from hexagons.mlplayer.domain.core.value_objects import GameState, StrategyConfig


def _create_game_state(
    robot_position=(0, 0),
    princess_position=(4, 4),
    flowers_positions=None,
    obstacles_positions=None,
    robot_flowers_collected=None,
    robot_flowers_delivered=None,
):
    """Helper to create a GameState for testing."""
    if flowers_positions is None:
        flowers_positions = []
    if obstacles_positions is None:
        obstacles_positions = []
    if robot_flowers_collected is None:
        robot_flowers_collected = []
    if robot_flowers_delivered is None:
        robot_flowers_delivered = []

    # Create a simple grid for testing
    grid = [["⬜" for _ in range(5)] for _ in range(5)]

    return GameState(
        game_id="test-game",
        board={
            "rows": 5,
            "cols": 5,
            "grid": grid,
            "flowers_positions": [{"row": f[0], "col": f[1]} for f in flowers_positions],
            "obstacles_positions": [{"row": o[0], "col": o[1]} for o in obstacles_positions],
            "initial_flowers_count": len(flowers_positions),
            "initial_obstacles_count": len(obstacles_positions),
        },
        robot={
            "position": {"row": robot_position[0], "col": robot_position[1]},
            "orientation": "EAST",
            "flowers_collected": [{"row": f[0], "col": f[1]} for f in robot_flowers_collected],
            "flowers_delivered": [{"row": f[0], "col": f[1]} for f in robot_flowers_delivered],
            "flowers_collection_capacity": 5,
            "obstacles_cleaned": [],
            "executed_actions": [],
        },
        princess={
            "position": {"row": princess_position[0], "col": princess_position[1]},
            "flowers_received": [{"row": f[0], "col": f[1]} for f in robot_flowers_delivered],
            "mood": "neutral",
        },
    )


def test_ai_ml_player_initialization():
    """Test AIMLPlayer can be initialized with default config."""
    player = AIMLPlayer()

    assert player.config is not None
    assert player.model is None
    assert isinstance(player.config, StrategyConfig)


def test_ai_ml_player_with_custom_config():
    """Test AIMLPlayer can be initialized with custom config."""
    config = StrategyConfig.aggressive()
    player = AIMLPlayer(config)

    assert player.config == config
    assert player.config.risk_aversion == 0.3


def test_evaluate_board_returns_score():
    """Test that evaluate_board returns a numeric score."""
    game_state = _create_game_state(flowers_positions=[(1, 1), (2, 2)], obstacles_positions=[(1, 2)])
    player = AIMLPlayer()
    score = player.evaluate_board(game_state)

    assert isinstance(score, float)


def test_select_action_returns_valid_action():
    """Test that select_action returns a valid action tuple."""
    game_state = _create_game_state(flowers_positions=[(1, 1), (2, 2)], obstacles_positions=[(1, 2)])
    player = AIMLPlayer()
    action, direction = player.select_action(game_state)

    assert isinstance(action, str)
    assert action in ["move", "pick", "drop", "give", "clean", "rotate"]

    if action in ["move", "rotate"]:
        assert direction in ["NORTH", "SOUTH", "EAST", "WEST"]
    elif action in ["pick", "give", "drop"]:
        assert direction is None


def test_select_action_pick_when_at_flower():
    """Test that player picks flower when standing on one."""
    game_state = _create_game_state(
        robot_position=(1, 1),
        flowers_positions=[(1, 1)],  # Robot is on this flower
    )

    player = AIMLPlayer()
    action, direction = player.select_action(game_state)

    assert action == "pick"
    assert direction is None


def test_select_action_give_when_at_princess():
    """Test that player gives flowers when at princess with flowers held."""
    game_state = _create_game_state(
        robot_position=(4, 3),  # Adjacent to princess
        princess_position=(4, 4),
        robot_flowers_delivered=[(1, 1), (2, 2)],  # Holding flowers
    )

    player = AIMLPlayer()
    action, direction = player.select_action(game_state)

    assert action == "give"
    assert direction is None


def test_plan_sequence_returns_action_list():
    """Test that plan_sequence returns a list of actions."""
    game_state = _create_game_state(flowers_positions=[(1, 1), (2, 2)], obstacles_positions=[(1, 2)])
    player = AIMLPlayer()
    actions = player.plan_sequence(game_state)

    assert isinstance(actions, list)
    assert len(actions) > 0

    for action, direction in actions:
        assert isinstance(action, str)


def test_get_config_returns_dict():
    """Test that get_config returns a dictionary."""
    player = AIMLPlayer()
    config_dict = player.get_config()

    assert isinstance(config_dict, dict)
    assert "distance_to_flower_weight" in config_dict
    assert "risk_aversion" in config_dict


def test_load_model_not_implemented():
    """Test that load_model raises NotImplementedError (future feature)."""
    player = AIMLPlayer()

    with pytest.raises(NotImplementedError):
        player.load_model("model.pkl")


def test_save_model_not_implemented():
    """Test that save_model raises NotImplementedError (future feature)."""
    player = AIMLPlayer()

    with pytest.raises(NotImplementedError):
        player.save_model("model.pkl")


def test_game_state_to_feature_vector():
    """Test that GameState can convert to feature vector."""
    game_state = _create_game_state(flowers_positions=[(1, 1), (2, 2)], obstacles_positions=[(1, 2)])
    features = game_state.to_feature_vector()

    assert isinstance(features, list)
    assert len(features) > 0
    assert all(isinstance(f, float) for f in features)


def test_game_state_distance_calculations():
    """Test GameState distance calculation methods."""
    game_state = _create_game_state(flowers_positions=[(1, 1), (2, 2)], obstacles_positions=[(1, 2)])
    princess_dist = game_state._distance_to_princess()
    flower_dist = game_state._closest_flower_distance()
    obstacle_density = game_state._obstacle_density()

    assert isinstance(princess_dist, float)
    assert isinstance(flower_dist, float)
    assert isinstance(obstacle_density, float)
    assert 0.0 <= obstacle_density <= 1.0


def test_different_strategies_produce_different_configs():
    """Test that different strategies have different configurations."""
    default = StrategyConfig.default()
    aggressive = StrategyConfig.aggressive()
    conservative = StrategyConfig.conservative()

    assert default.risk_aversion != aggressive.risk_aversion
    assert default.risk_aversion != conservative.risk_aversion
    assert aggressive.risk_aversion < conservative.risk_aversion
