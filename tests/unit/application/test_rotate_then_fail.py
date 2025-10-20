from unittest.mock import patch

from robot_flower_princess.driven.persistence.in_memory_game_repository import InMemoryGameRepository
from robot_flower_princess.domain.core.entities.position import Position
from robot_flower_princess.domain.core.entities.robot import Robot
from robot_flower_princess.domain.core.entities.board import Board
from robot_flower_princess.domain.core.entities.game_history import GameHistory
from robot_flower_princess.domain.core.value_objects.direction import Direction
from robot_flower_princess.domain.core.exceptions.game_exceptions import GameException
from robot_flower_princess.domain.core.value_objects.action_type import ActionType

from robot_flower_princess.domain.use_cases.move_robot import MoveRobotUseCase, MoveRobotCommand
from robot_flower_princess.domain.use_cases.rotate_robot import RotateRobotUseCase, RotateRobotCommand


def make_small_board():
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    board = Board(rows=2, cols=2, robot=robot, princess_position=Position(1, 1))
    board.flowers = set()
    board.obstacles = set()
    board.initial_flower_count = 0
    return board


def test_rotate_then_move_failure_records_both_entries():
    repo = InMemoryGameRepository()
    board = make_small_board()
    repo.save("r1", board)
    repo.save_history("r1", GameHistory())

    # Patch move to raise after rotate is applied
    with patch("robot_flower_princess.domain.use_cases.move_robot.GameService.move_robot", side_effect=GameException("blocked")):
        # Apply rotate then move via commands
        rot_uc = RotateRobotUseCase(repo)
        rot_uc.execute(RotateRobotCommand(game_id="r1", direction=Direction.NORTH))

        move_uc = MoveRobotUseCase(repo)
        res = move_uc.execute(MoveRobotCommand(game_id="r1", direction=Direction.NORTH))

    history = repo.get_history("r1")
    assert history is not None
    # expect two actions: rotate (success) and move (failed)
    assert len(history.actions) >= 2
    assert history.actions[-2].action_type.value == "rotate"
    assert history.actions[-2].direction == Direction.NORTH
    assert history.actions[-1].action_type.value == "move"
    assert history.actions[-1].direction == Direction.NORTH
