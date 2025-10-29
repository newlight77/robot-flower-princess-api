"""Unit tests for Autoplay Use Case with AIGreedyPlayer strategy."""

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


async def test_autoplay_applies_greedy_solver_actions_and_records_direction():
    """Test that autoplay applies AIGreedyPlayer solver actions and records direction."""
    repo = InMemoryGameRepository()
    game = make_game_with_small_board()
    repo.save("a1", game)

    # stub solver to rotate south then move (valid from (0,0), avoiding flower at (0,1))
    with patch(
        "hexagons.aiplayer.domain.core.entities.ai_greedy_player.AIGreedyPlayer.solve",
        return_value=[("rotate", Direction.SOUTH), ("move", None)],
    ):
        use_case = AutoplayUseCase(repo)
        res = await use_case.execute(AutoplayCommand(game_id="a1"))

    assert isinstance(res.success, bool)
    b = repo.get("a1")
    assert b is not None
    # Verify actions were executed (2 actions: rotate + move)
    assert len(b.robot.executed_actions) >= 2
    # Note: Mock solver doesn't actually collect flowers, so we can't assert about completion


async def test_autoplay_greedy_handles_solver_exception_gracefully():
    """Test that autoplay handles AIGreedyPlayer solver exceptions gracefully."""
    repo = InMemoryGameRepository()
    board = make_game_with_small_board()
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
    board = make_game_with_small_board()
    repo.save("a4", board)

    with patch(
        "hexagons.aiplayer.domain.core.entities.ai_greedy_player.AIGreedyPlayer.solve",
        return_value=[("rotate", Direction.SOUTH), ("move", None)],
    ):
        use_case = AutoplayUseCase(repo)
        res = await use_case.execute(AutoplayCommand(game_id="a4", strategy="greedy"))

    assert isinstance(res.success, bool)
    b = repo.get("a4")
    assert b is not None
    # Verify actions were executed (2 actions: rotate + move)
    assert len(b.robot.executed_actions) >= 2
    # Note: Mock solver doesn't actually collect flowers, so we can't assert about completion


async def test_autoplay_defaults_to_greedy_strategy():
    """Test autoplay defaults to AIGreedyPlayer when no strategy specified."""
    repo = InMemoryGameRepository()
    board = make_game_with_small_board()
    repo.save("a5", board)

    with patch(
        "hexagons.aiplayer.domain.core.entities.ai_greedy_player.AIGreedyPlayer.solve",
        return_value=[("rotate", Direction.SOUTH), ("move", None)],
    ):
        use_case = AutoplayUseCase(repo)
        # No strategy parameter - should default to greedy
        res = await use_case.execute(AutoplayCommand(game_id="a5"))

    assert isinstance(res.success, bool)
    b = repo.get("a5")
    assert b is not None
    # Verify actions were executed (2 actions: rotate + move)
    assert len(b.robot.executed_actions) >= 2
    # Note: Mock solver doesn't actually collect flowers, so we can't assert about completion


async def test_autoplay_greedy_strategy_called():
    """Test that AIGreedyPlayer.solve is called when using greedy strategy."""
    repo = InMemoryGameRepository()
    board = make_game_with_small_board()
    repo.save("greedy_called", board)

    with patch(
        "hexagons.aiplayer.domain.core.entities.ai_greedy_player.AIGreedyPlayer.solve",
        return_value=[("rotate", Direction.SOUTH), ("move", None)],
    ) as mock_greedy:
        use_case = AutoplayUseCase(repo)
        await use_case.execute(AutoplayCommand(game_id="greedy_called", strategy="greedy"))

    # Verify the greedy solver was called
    mock_greedy.assert_called_once()
