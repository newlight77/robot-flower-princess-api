from unittest.mock import patch

from robot_flower_princess.driven.persistence.in_memory_game_repository import InMemoryGameRepository
from robot_flower_princess.domain.entities.position import Position
from robot_flower_princess.domain.entities.robot import Robot
from robot_flower_princess.domain.entities.board import Board
from robot_flower_princess.domain.entities.game_history import GameHistory
from robot_flower_princess.domain.value_objects.direction import Direction
from robot_flower_princess.domain.exceptions.game_exceptions import GameException

from robot_flower_princess.application.use_cases.move_robot import MoveRobotUseCase, MoveRobotCommand
from robot_flower_princess.application.use_cases.pick_flower import PickFlowerUseCase, PickFlowerCommand
from robot_flower_princess.application.use_cases.drop_flower import DropFlowerUseCase, DropFlowerCommand
from robot_flower_princess.application.use_cases.give_flowers import GiveFlowersUseCase, GiveFlowersCommand
from robot_flower_princess.application.use_cases.clean_obstacle import CleanObstacleUseCase, CleanObstacleCommand
from robot_flower_princess.domain.value_objects.action_type import ActionType


def make_center_board():
    robot = Robot(position=Position(1, 1), orientation=Direction.EAST)
    board = Board(rows=3, cols=3, robot=robot, princess_position=Position(2, 2))
    board.flowers = set()
    board.obstacles = set()
    board.initial_flower_count = 0
    return board


def test_move_error_records_failed_action_direction():
    repo = InMemoryGameRepository()
    board = make_center_board()
    repo.save("merr", board)
    repo.save_history("merr", GameHistory())

    with patch("robot_flower_princess.application.use_cases.move_robot.GameService.move_robot", side_effect=GameException("boom")):
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

    with patch("robot_flower_princess.application.use_cases.pick_flower.GameService.pick_flower", side_effect=GameException("nope")):
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

    with patch("robot_flower_princess.application.use_cases.drop_flower.GameService.drop_flower", side_effect=GameException("bad")):
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

    with patch("robot_flower_princess.application.use_cases.give_flowers.GameService.give_flowers", side_effect=GameException("fail")):
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

    with patch("robot_flower_princess.application.use_cases.clean_obstacle.GameService.clean_obstacle", side_effect=GameException("boom")):
        use_case = CleanObstacleUseCase(repo)
        use_case.execute(CleanObstacleCommand(game_id="cerr", direction=Direction.NORTH))

    history = repo.get_history("cerr")
    assert history is not None
    last = history.actions[-1]
    assert last.action_type == ActionType.CLEAN
    assert last.direction == Direction.NORTH
