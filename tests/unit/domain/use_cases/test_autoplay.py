from unittest.mock import patch

from hexagons.game.driven.persistence.in_memory_game_repository import (
    InMemoryGameRepository,
)
from hexagons.game.domain.core.entities.position import Position
from hexagons.game.domain.core.entities.robot import Robot
from hexagons.game.domain.core.entities.game import Game
from hexagons.game.domain.core.entities.game_history import GameHistory
from hexagons.game.domain.core.value_objects.direction import Direction
from hexagons.game.domain.use_cases.autoplay import AutoplayUseCase, AutoplayCommand


def make_small_board():
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    board = Game(rows=2, cols=2, robot=robot, princess_position=Position(1, 1))
    board.flowers = {Position(0, 1)}
    board.initial_flower_count = 1
    board.obstacles = set()
    return board


def test_autoplay_applies_solver_actions_and_records_direction():
    repo = InMemoryGameRepository()
    board = make_small_board()
    repo.save("a1", board)
    repo.save_history("a1", GameHistory())

    # stub solver to rotate north then move
    with patch(
        "hexagons.game.domain.core.entities.game_solver_player.GameSolverPlayer.solve",
        return_value=[("rotate", Direction.NORTH), ("move", Direction.NORTH)],
    ):
        use_case = AutoplayUseCase(repo)
        res = use_case.execute(AutoplayCommand(game_id="a1"))

    assert isinstance(res.success, bool)
    b = repo.get("a1")
    # after rotate to NORTH and move, robot at ( -1? ) or moved; ensure orientation set
    assert b is not None
    assert getattr(b, "robot", None) is not None
    assert b.robot.orientation == Direction.NORTH
    history = repo.get_history("a1")
    assert history is not None
    # first action should be rotate with NORTH
    assert history.actions[0].action_type.value == "rotate"
    assert history.actions[0].direction == Direction.NORTH


def test_autoplay_handles_solver_exception_gracefully():
    repo = InMemoryGameRepository()
    board = make_small_board()
    repo.save("a2", board)
    repo.save_history("a2", GameHistory())

    with patch(
        "hexagons.game.domain.core.entities.game_solver_player.GameSolverPlayer.solve",
        side_effect=Exception("solver fail"),
    ):
        use_case = AutoplayUseCase(repo)
        res = use_case.execute(AutoplayCommand(game_id="a2"))

    assert res.success is False
    assert "solver fail" in res.message
