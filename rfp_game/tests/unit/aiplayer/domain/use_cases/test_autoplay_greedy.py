"""Unit tests for Autoplay Use Case with AIGreedyPlayer strategy."""

from unittest.mock import patch

from hexagons.game.driven.persistence.in_memory_game_repository import (
    InMemoryGameRepository,
)
from hexagons.game.domain.core.entities.position import Position
from hexagons.game.domain.core.entities.robot import Robot
from hexagons.game.domain.core.entities.princess import Princess
from hexagons.game.domain.core.entities.game import Game
from hexagons.game.domain.core.entities.game_history import GameHistory
from hexagons.game.domain.core.value_objects.direction import Direction
from hexagons.aiplayer.domain.use_cases.autoplay import AutoplayUseCase, AutoplayCommand


def make_small_board():
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    board = Game(rows=2, cols=2, robot=robot, princess=Princess(position=Position(1, 1)))
    board.flowers = {Position(0, 1)}
    board.initial_flower_count = 1
    board.obstacles = set()
    return board


def test_autoplay_applies_greedy_solver_actions_and_records_direction():
    """Test that autoplay applies AIGreedyPlayer solver actions and records direction."""
    repo = InMemoryGameRepository()
    board = make_small_board()
    repo.save("a1", board)
    repo.save_history("a1", GameHistory(game_id="a1"))

    # stub solver to rotate north then move
    with patch(
        "hexagons.aiplayer.domain.core.entities.ai_greedy_player.AIGreedyPlayer.solve",
        return_value=[("rotate", Direction.NORTH), ("move", Direction.NORTH)],
    ):
        use_case = AutoplayUseCase(repo)
        res = use_case.execute(AutoplayCommand(game_id="a1"))

    assert isinstance(res.success, bool)
    b = repo.get("a1")
    assert b is not None
    assert getattr(b, "robot", None) is not None
    assert b.robot.orientation == Direction.NORTH
    history = repo.get_history("a1")
    assert history is not None
    # first action should be rotate with NORTH
    assert history.actions[0].action_type.value == "rotate"
    assert history.actions[0].direction == Direction.NORTH


def test_autoplay_greedy_handles_solver_exception_gracefully():
    """Test that autoplay handles AIGreedyPlayer solver exceptions gracefully."""
    repo = InMemoryGameRepository()
    board = make_small_board()
    repo.save("a2", board)
    repo.save_history("a2", GameHistory(game_id="a2"))

    with patch(
        "hexagons.aiplayer.domain.core.entities.ai_greedy_player.AIGreedyPlayer.solve",
        side_effect=Exception("solver fail"),
    ):
        use_case = AutoplayUseCase(repo)
        res = use_case.execute(AutoplayCommand(game_id="a2"))

    assert res.success is False
    assert "solver fail" in res.message


def test_autoplay_with_greedy_strategy_explicit():
    """Test autoplay uses AIGreedyPlayer when strategy='greedy' (explicit)."""
    repo = InMemoryGameRepository()
    board = make_small_board()
    repo.save("a4", board)
    repo.save_history("a4", GameHistory(game_id="a4"))

    with patch(
        "hexagons.aiplayer.domain.core.entities.ai_greedy_player.AIGreedyPlayer.solve",
        return_value=[("rotate", Direction.SOUTH), ("move", Direction.SOUTH)],
    ):
        use_case = AutoplayUseCase(repo)
        res = use_case.execute(AutoplayCommand(game_id="a4", strategy="greedy"))

    assert isinstance(res.success, bool)
    b = repo.get("a4")
    assert b is not None
    assert b.robot.orientation == Direction.SOUTH
    history = repo.get_history("a4")
    assert history is not None
    assert history.actions[0].action_type.value == "rotate"


def test_autoplay_defaults_to_greedy_strategy():
    """Test autoplay defaults to AIGreedyPlayer when no strategy specified."""
    repo = InMemoryGameRepository()
    board = make_small_board()
    repo.save("a5", board)
    repo.save_history("a5", GameHistory(game_id="a5"))

    with patch(
        "hexagons.aiplayer.domain.core.entities.ai_greedy_player.AIGreedyPlayer.solve",
        return_value=[("rotate", Direction.WEST), ("move", Direction.WEST)],
    ):
        use_case = AutoplayUseCase(repo)
        # No strategy parameter - should default to greedy
        res = use_case.execute(AutoplayCommand(game_id="a5"))

    assert isinstance(res.success, bool)
    b = repo.get("a5")
    assert b is not None
    assert b.robot.orientation == Direction.WEST


def test_autoplay_greedy_strategy_called():
    """Test that AIGreedyPlayer.solve is called when using greedy strategy."""
    repo = InMemoryGameRepository()
    board = make_small_board()
    repo.save("greedy_called", board)
    repo.save_history("greedy_called", GameHistory(game_id="greedy_called"))

    with patch(
        "hexagons.aiplayer.domain.core.entities.ai_greedy_player.AIGreedyPlayer.solve",
        return_value=[("rotate", Direction.NORTH), ("move", Direction.NORTH)],
    ) as mock_greedy:
        use_case = AutoplayUseCase(repo)
        use_case.execute(AutoplayCommand(game_id="greedy_called", strategy="greedy"))

    # Verify the greedy solver was called
    mock_greedy.assert_called_once()
