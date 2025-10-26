"""Unit tests for Autoplay Use Case with AIGreedyPlayer strategy."""

from unittest.mock import patch

from hexagons.game.driven.persistence.in_memory_game_repository import (
    InMemoryGameRepository,
)
from hexagons.game.domain.core.entities.position import Position
from hexagons.game.domain.core.entities.robot import Robot
from hexagons.game.domain.core.entities.princess import Princess
from hexagons.game.domain.core.entities.game import Game
from hexagons.game.domain.core.value_objects.direction import Direction
from hexagons.aiplayer.domain.use_cases.autoplay import AutoplayUseCase, AutoplayCommand


def make_small_board():
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    board = Game(rows=2, cols=2, robot=robot, princess=Princess(position=Position(1, 1)))
    board.flowers = {Position(0, 1)}
    board.board.initial_flowers_count = 1
    board.obstacles = set()
    return board


async def test_autoplay_applies_greedy_solver_actions_and_records_direction():
    """Test that autoplay applies AIGreedyPlayer solver actions and records direction."""
    repo = InMemoryGameRepository()
    board = make_small_board()
    repo.save("a1", board)

    # stub solver to rotate north then move
    with patch(
        "hexagons.aiplayer.domain.core.entities.ai_greedy_player.AIGreedyPlayer.solve",
        return_value=[("rotate", Direction.NORTH), ("move", Direction.NORTH)],
    ):
        use_case = AutoplayUseCase(repo)
        res = await use_case.execute(AutoplayCommand(game_id="a1"))

    assert isinstance(res.success, bool)
    b = repo.get("a1")
    assert b is not None
    assert b.robot.orientation == Direction.NORTH
    assert b.robot.executed_actions[0].direction == Direction.NORTH


async def test_autoplay_greedy_handles_solver_exception_gracefully():
    """Test that autoplay handles AIGreedyPlayer solver exceptions gracefully."""
    repo = InMemoryGameRepository()
    board = make_small_board()
    repo.save("a2", board)

    with patch(
        "hexagons.aiplayer.domain.core.entities.ai_greedy_player.AIGreedyPlayer.solve",
        side_effect=Exception("solver fail"),
    ):
        use_case = AutoplayUseCase(repo)
        res = await use_case.execute(AutoplayCommand(game_id="a2"))

    assert res.success is False
    assert "solver fail" in res.message


async def test_autoplay_with_greedy_strategy_explicit():
    """Test autoplay uses AIGreedyPlayer when strategy='greedy' (explicit)."""
    repo = InMemoryGameRepository()
    board = make_small_board()
    repo.save("a4", board)

    with patch(
        "hexagons.aiplayer.domain.core.entities.ai_greedy_player.AIGreedyPlayer.solve",
        return_value=[("rotate", Direction.SOUTH), ("move", Direction.SOUTH)],
    ):
        use_case = AutoplayUseCase(repo)
        res = await use_case.execute(AutoplayCommand(game_id="a4", strategy="greedy"))

    assert isinstance(res.success, bool)
    b = repo.get("a4")
    assert b is not None
    assert b.robot.orientation == Direction.SOUTH

async def test_autoplay_defaults_to_greedy_strategy():
    """Test autoplay defaults to AIGreedyPlayer when no strategy specified."""
    repo = InMemoryGameRepository()
    board = make_small_board()
    repo.save("a5", board)

    with patch(
        "hexagons.aiplayer.domain.core.entities.ai_greedy_player.AIGreedyPlayer.solve",
        return_value=[("rotate", Direction.WEST), ("move", Direction.WEST)],
    ):
        use_case = AutoplayUseCase(repo)
        # No strategy parameter - should default to greedy
        res = await use_case.execute(AutoplayCommand(game_id="a5"))

    assert isinstance(res.success, bool)
    b = repo.get("a5")
    assert b is not None
    assert b.robot.orientation == Direction.WEST


async def test_autoplay_greedy_strategy_called():
    """Test that AIGreedyPlayer.solve is called when using greedy strategy."""
    repo = InMemoryGameRepository()
    board = make_small_board()
    repo.save("greedy_called", board)

    with patch(
        "hexagons.aiplayer.domain.core.entities.ai_greedy_player.AIGreedyPlayer.solve",
        return_value=[("rotate", Direction.NORTH), ("move", Direction.NORTH)],
    ) as mock_greedy:
        use_case = AutoplayUseCase(repo)
        await use_case.execute(AutoplayCommand(game_id="greedy_called", strategy="greedy"))

    # Verify the greedy solver was called
    mock_greedy.assert_called_once()
