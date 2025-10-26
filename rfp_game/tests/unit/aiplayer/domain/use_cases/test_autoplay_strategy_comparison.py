"""Unit tests comparing AIGreedyPlayer vs AIOptimalPlayer strategies in Autoplay Use Case."""

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


async def test_autoplay_greedy_and_optimal_both_callable():
    """Test that both AI strategies can be invoked via the use case."""
    repo = InMemoryGameRepository()
    board1 = make_small_board()
    board2 = make_small_board()
    repo.save("greedy_game", board1)
    repo.save("optimal_game", board2)

    # Mock both strategies
    with patch(
        "hexagons.aiplayer.domain.core.entities.ai_greedy_player.AIGreedyPlayer.solve",
        return_value=[],
    ) as greedy_mock:
        use_case = AutoplayUseCase(repo)
        await use_case.execute(AutoplayCommand(game_id="greedy_game", strategy="greedy"))
        greedy_mock.assert_called_once()

    with patch(
        "hexagons.aiplayer.domain.core.entities.ai_optimal_player.AIOptimalPlayer.solve",
        return_value=[],
    ) as optimal_mock:
        use_case = AutoplayUseCase(repo)
        await use_case.execute(AutoplayCommand(game_id="optimal_game", strategy="optimal"))
        optimal_mock.assert_called_once()


async def test_autoplay_strategy_selection_isolation():
    """Test that strategy parameter correctly selects the AI player without calling the other."""
    repo = InMemoryGameRepository()
    board = make_small_board()
    repo.save("validation", board)

    # Patch both strategies but only greedy should be called
    with (
        patch(
            "hexagons.aiplayer.domain.core.entities.ai_greedy_player.AIGreedyPlayer.solve",
            return_value=[],
        ) as greedy_mock,
        patch(
            "hexagons.aiplayer.domain.core.entities.ai_optimal_player.AIOptimalPlayer.solve",
            return_value=[],
        ) as optimal_mock,
    ):
        use_case = AutoplayUseCase(repo)
        await use_case.execute(AutoplayCommand(game_id="validation", strategy="greedy"))

    greedy_mock.assert_called_once()
    optimal_mock.assert_not_called()
