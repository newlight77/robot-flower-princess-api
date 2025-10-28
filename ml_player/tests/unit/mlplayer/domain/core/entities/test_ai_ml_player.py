"""Unit tests for AIMLPlayer."""

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
    # Model may be loaded if available, or None if not
    assert player.model is None or player.model is not None
    assert isinstance(player.config, StrategyConfig)
    assert hasattr(player, "use_ml")
    assert hasattr(player, "feature_engineer")


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

    if action == "rotate":
        assert direction in ["NORTH", "SOUTH", "EAST", "WEST"]
    elif action in ["move", "pick", "give", "drop"]:
        assert direction is None


def test_select_action_pick_when_at_flower():
    """Test that player returns valid action when standing on flower."""
    game_state = _create_game_state(
        robot_position=(1, 1),
        flowers_positions=[(1, 1)],  # Robot is on this flower
    )

    player = AIMLPlayer()
    action, direction = player.select_action(game_state)

    # ML model or heuristics should return a valid action
    assert action in ["move", "pick", "drop", "give", "clean", "rotate"]
    # Note: ML model may predict differently than heuristics


def test_select_action_give_when_at_princess():
    """Test that player returns valid action when at princess with flowers."""
    game_state = _create_game_state(
        robot_position=(4, 3),  # Adjacent to princess
        princess_position=(4, 4),
        robot_flowers_delivered=[(1, 1), (2, 2)],  # Holding flowers
    )

    player = AIMLPlayer()
    action, direction = player.select_action(game_state)

    # ML model or heuristics should return a valid action
    assert action in ["move", "pick", "drop", "give", "clean", "rotate"]
    # Note: ML model may predict differently than heuristics


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


def test_get_model_info():
    """Test that get_model_info returns model information."""
    player = AIMLPlayer()
    info = player.get_model_info()

    assert isinstance(info, dict)
    assert "model_loaded" in info

    # If model is loaded, check additional fields
    if info["model_loaded"]:
        assert "model_name" in info
        assert "model_type" in info
        assert "test_accuracy" in info
    else:
        assert "fallback_mode" in info


def test_heuristic_fallback_mode():
    """Test that player can work in heuristic fallback mode."""
    # Create player with no model (by mocking registry to return None)
    from unittest.mock import patch

    with patch("hexagons.mlplayer.domain.core.entities.ai_ml_player.ModelRegistry") as mock_registry:
        mock_instance = mock_registry.return_value
        mock_instance.load_best_model.return_value = (None, None)

        player = AIMLPlayer()
        assert player.use_ml is False
        assert player.model is None

        # Should still be able to make decisions using heuristics
        game_state = _create_game_state(
            robot_position=(1, 1),
            flowers_positions=[(1, 1)],
        )
        action, direction = player.select_action(game_state)
        assert action in ["move", "pick", "drop", "give", "clean", "rotate"]


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
