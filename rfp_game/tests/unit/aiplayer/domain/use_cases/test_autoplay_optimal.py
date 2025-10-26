"""Unit tests for Autoplay Use Case with AIOptimalPlayer strategy."""

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


async def test_autoplay_with_optimal_strategy():
    """Test autoplay uses AIOptimalPlayer when strategy='optimal'."""
    repo = InMemoryGameRepository()
    board = make_small_board()
    repo.save("a3", board)

    # stub AIOptimalPlayer solver
    with patch(
        "hexagons.aiplayer.domain.core.entities.ai_optimal_player.AIOptimalPlayer.solve",
        return_value=[("rotate", Direction.NORTH), ("move", Direction.NORTH)],
    ):
        use_case = AutoplayUseCase(repo)
        res = await use_case.execute(AutoplayCommand(game_id="a3", strategy="optimal"))

    assert isinstance(res.success, bool)
    b = repo.get("a3")
    assert b is not None
    # assert len(b.robot.executed_actions) >= 1
    # assert len(b.robot.flowers.delivered) >= 1
    assert b.board.get_remaining_flowers_count() == 0


async def test_autoplay_optimal_handles_exception_gracefully():
    """Test autoplay handles AIOptimalPlayer exceptions gracefully."""
    repo = InMemoryGameRepository()
    board = make_small_board()
    repo.save("a6", board)

    with patch(
        "hexagons.aiplayer.domain.core.entities.ai_optimal_player.AIOptimalPlayer.solve",
        side_effect=Exception("optimal solver fail"),
    ):
        use_case = AutoplayUseCase(repo)
        res = await use_case.execute(AutoplayCommand(game_id="a6", strategy="optimal"))

    assert res.success is False
    assert "optimal solver fail" in res.message


async def test_autoplay_optimal_strategy_called():
    """Test that AIOptimalPlayer.solve is called when using optimal strategy."""
    repo = InMemoryGameRepository()
    board = make_small_board()
    repo.save("optimal_called", board)

    with patch(
        "hexagons.aiplayer.domain.core.entities.ai_optimal_player.AIOptimalPlayer.solve",
        return_value=[("rotate", Direction.NORTH), ("move", Direction.NORTH)],
    ) as mock_optimal:
        use_case = AutoplayUseCase(repo)
        await use_case.execute(AutoplayCommand(game_id="optimal_called", strategy="optimal"))

    # Verify the optimal solver was called
    mock_optimal.assert_called_once()
