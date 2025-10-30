"""Unit tests for Autoplay Use Case with AIOptimalPlayer strategy."""

from unittest.mock import patch

from hexagons.game.driven.persistence.in_memory_game_repository import (
    InMemoryGameRepository,
)
from hexagons.game.domain.core.entities.position import Position
from hexagons.game.domain.core.entities.game import Game
from hexagons.game.domain.core.value_objects.direction import Direction
from hexagons.aiplayer.domain.use_cases.autoplay import AutoplayUseCase, AutoplayCommand


def make_game_with_small_board():
    game = Game(rows=3, cols=3)

    game.board.flowers_positions = {Position(0, 1)}
    game.board.initial_flowers_count = 1
    game.board.initial_obstacles_count = 0
    game.board.obstacles_positions = set()
    return game


async def test_autoplay_with_optimal_strategy():
    """Test autoplay uses AIOptimalPlayer when strategy='optimal'."""
    repo = InMemoryGameRepository()
    game = make_game_with_small_board()
    repo.save("a3", game)

    # stub AIOptimalPlayer solver - rotate south then move (valid from (0,0) facing EAST)
    with patch(
        "hexagons.aiplayer.domain.core.entities.ai_optimal_player.AIOptimalPlayer.solve",
        return_value=[("rotate", Direction.SOUTH), ("move", None)],
    ):
        use_case = AutoplayUseCase(repo)
        res = await use_case.execute(AutoplayCommand(game_id="a3", strategy="optimal"))

    assert isinstance(res.success, bool)
    b = repo.get("a3")
    assert b is not None
    # Verify actions were executed (2 actions: rotate + move)
    assert len(b.robot.executed_actions) >= 2
    # Note: Mock solver doesn't actually collect flowers, so we can't assert about completion


async def test_autoplay_optimal_handles_exception_gracefully():
    """Test autoplay handles AIOptimalPlayer exceptions gracefully."""
    repo = InMemoryGameRepository()
    game = make_game_with_small_board()
    repo.save("a6", game)

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
    game = make_game_with_small_board()
    repo.save("optimal_called", game)

    with patch(
        "hexagons.aiplayer.domain.core.entities.ai_optimal_player.AIOptimalPlayer.solve",
        return_value=[("rotate", Direction.SOUTH), ("move", None)],
    ) as mock_optimal:
        use_case = AutoplayUseCase(repo)
        await use_case.execute(AutoplayCommand(game_id="optimal_called", strategy="optimal"))

    # Verify the optimal solver was called
    mock_optimal.assert_called_once()
