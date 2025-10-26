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
from hexagons.game.domain.core.exceptions.game_exceptions import GameException
from hexagons.game.domain.core.value_objects.action_type import ActionType

from hexagons.game.domain.use_cases.move_robot import MoveRobotUseCase, MoveRobotCommand
from hexagons.game.domain.use_cases.pick_flower import PickFlowerUseCase, PickFlowerCommand
from hexagons.game.domain.use_cases.drop_flower import DropFlowerUseCase, DropFlowerCommand
from hexagons.game.domain.use_cases.give_flowers import (
    GiveFlowersUseCase,
    GiveFlowersCommand,
)
from hexagons.game.domain.use_cases.clean_obstacle import (
    CleanObstacleUseCase,
    CleanObstacleCommand,
)


def make_center_board():
    robot = Robot(position=Position(1, 1), orientation=Direction.EAST)
    board = Game(rows=3, cols=3, robot=robot, princess=Princess(position=Position(2, 2)))
    board.flowers = set()
    board.obstacles = set()
    board.initial_flower_count = 0
    return board


def test_move_error_records_failed_action_direction():
    repo = InMemoryGameRepository()
    board = make_center_board()
    repo.save("merr", board)
    repo.save_history("merr", GameHistory())

    with patch(
        "hexagons.game.domain.use_cases.move_robot.GameService.move_robot",
        side_effect=GameException("boom"),
    ):
        use_case = MoveRobotUseCase(repo)
        use_case.execute(MoveRobotCommand(game_id="merr", direction=Direction.NORTH))

    history = repo.get_history("merr")
    assert history is not None
    last = history.actions[-1]
    assert last.action_type == ActionType.MOVE
    assert last.direction == Direction.NORTH


def test_pick_error_records_failed_action_direction():
    repo = InMemoryGameRepository()
    board = make_center_board()
    repo.save("perr", board)
    repo.save_history("perr", GameHistory())

    with patch(
        "hexagons.game.domain.use_cases.pick_flower.GameService.pick_flower",
        side_effect=GameException("nope"),
    ):
        use_case = PickFlowerUseCase(repo)
        use_case.execute(PickFlowerCommand(game_id="perr", direction=Direction.NORTH))

    history = repo.get_history("perr")
    assert history is not None
    last = history.actions[-1]
    assert last.action_type == ActionType.PICK
    assert last.direction == Direction.NORTH


def test_drop_error_records_failed_action_direction():
    repo = InMemoryGameRepository()
    board = make_center_board()
    board.robot.flowers_held = 1
    repo.save("derr", board)
    repo.save_history("derr", GameHistory())

    with patch(
        "hexagons.game.domain.use_cases.drop_flower.GameService.drop_flower",
        side_effect=GameException("bad"),
    ):
        use_case = DropFlowerUseCase(repo)
        use_case.execute(DropFlowerCommand(game_id="derr", direction=Direction.NORTH))

    history = repo.get_history("derr")
    assert history is not None
    last = history.actions[-1]
    assert last.action_type == ActionType.DROP
    assert last.direction == Direction.NORTH


def test_give_error_records_failed_action_direction():
    repo = InMemoryGameRepository()
    board = make_center_board()
    board.robot.flowers_held = 1
    repo.save("gerr", board)
    repo.save_history("gerr", GameHistory())

    with patch(
        "hexagons.game.domain.use_cases.give_flowers.GameService.give_flowers",
        side_effect=GameException("fail"),
    ):
        use_case = GiveFlowersUseCase(repo)
        use_case.execute(GiveFlowersCommand(game_id="gerr", direction=Direction.NORTH))

    history = repo.get_history("gerr")
    assert history is not None
    last = history.actions[-1]
    assert last.action_type == ActionType.GIVE
    assert last.direction == Direction.NORTH


def test_clean_error_records_failed_action_direction():
    repo = InMemoryGameRepository()
    board = make_center_board()
    repo.save("cerr", board)
    repo.save_history("cerr", GameHistory())

    with patch(
        "hexagons.game.domain.use_cases.clean_obstacle.GameService.clean_obstacle",
        side_effect=GameException("boom"),
    ):
        use_case = CleanObstacleUseCase(repo)
        use_case.execute(CleanObstacleCommand(game_id="cerr", direction=Direction.NORTH))

    history = repo.get_history("cerr")
    assert history is not None
    last = history.actions[-1]
    assert last.action_type == ActionType.CLEAN
    assert last.direction == Direction.NORTH
