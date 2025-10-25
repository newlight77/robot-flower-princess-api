"""Unit tests for AIMLPlayer."""

import pytest

from hexagons.mlplayer.domain.core.entities import AIMLPlayer, BoardState
from hexagons.mlplayer.domain.core.value_objects import StrategyConfig


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


def test_evaluate_board_returns_score(sample_board_state):
    """Test that evaluate_board returns a numeric score."""
    player = AIMLPlayer()
    score = player.evaluate_board(sample_board_state)

    assert isinstance(score, float)


def test_select_action_returns_valid_action(sample_board_state):
    """Test that select_action returns a valid action tuple."""
    player = AIMLPlayer()
    action, direction = player.select_action(sample_board_state)

    assert isinstance(action, str)
    assert action in ["move", "pick", "drop", "give", "clean", "rotate"]

    if action in ["move", "rotate"]:
        assert direction in ["NORTH", "SOUTH", "EAST", "WEST"]
    elif action in ["pick", "give", "drop"]:
        assert direction is None


def test_select_action_pick_when_at_flower():
    """Test that player picks flower when standing on one."""
    board_state = BoardState(
        rows=5,
        cols=5,
        robot_position=(1, 1),  # Same as flower
        robot_orientation="EAST",
        robot_flowers_held=0,
        robot_max_capacity=5,
        princess_position=(4, 4),
        flowers=[(1, 1)],  # Robot is on this flower
        obstacles=[],
        flowers_delivered=0,
    )

    player = AIMLPlayer()
    action, direction = player.select_action(board_state)

    assert action == "pick"
    assert direction is None


def test_select_action_give_when_at_princess():
    """Test that player gives flowers when at princess with flowers held."""
    board_state = BoardState(
        rows=5,
        cols=5,
        robot_position=(4, 4),  # Same as princess
        robot_orientation="EAST",
        robot_flowers_held=2,  # Holding flowers
        robot_max_capacity=5,
        princess_position=(4, 4),
        flowers=[],
        obstacles=[],
        flowers_delivered=0,
    )

    player = AIMLPlayer()
    action, direction = player.select_action(board_state)

    assert action == "give"
    assert direction is None


def test_plan_sequence_returns_action_list(sample_board_state):
    """Test that plan_sequence returns a list of actions."""
    player = AIMLPlayer()
    actions = player.plan_sequence(sample_board_state)

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


def test_board_state_to_feature_vector(sample_board_state):
    """Test that BoardState can convert to feature vector."""
    features = sample_board_state.to_feature_vector()

    assert isinstance(features, list)
    assert len(features) > 0
    assert all(isinstance(f, float) for f in features)


def test_board_state_distance_calculations(sample_board_state):
    """Test BoardState distance calculation methods."""
    princess_dist = sample_board_state._distance_to_princess()
    flower_dist = sample_board_state._closest_flower_distance()
    obstacle_density = sample_board_state._obstacle_density()

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
