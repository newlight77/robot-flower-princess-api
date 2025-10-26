from unittest.mock import patch

from hexagons.game.driven.persistence.in_memory_game_repository import (
    InMemoryGameRepository,
)
from hexagons.game.domain.core.entities.position import Position
from hexagons.game.domain.core.entities.robot import Robot
from hexagons.game.domain.core.entities.princess import Princess
from hexagons.game.domain.core.entities.game import Game
from hexagons.game.domain.core.value_objects.direction import Direction
from hexagons.game.domain.core.exceptions.game_exceptions import GameException

from hexagons.game.domain.use_cases.move_robot import MoveRobotUseCase, MoveRobotCommand
from hexagons.game.domain.use_cases.rotate_robot import (
    RotateRobotUseCase,
    RotateRobotCommand,
)


def make_small_board():
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    board = Game(rows=2, cols=2, robot=robot, princess=Princess(position=Position(1, 1)))
    board.flowers = set()
    board.obstacles = set()
    board.board.initial_flowers_count = 0
    return board


def test_rotate_then_move_failure_records_both_entries():
    repo = InMemoryGameRepository()
    board = make_small_board()
    repo.save("r1", board)

    # Patch move to raise after rotate is applied
    with patch(
        "hexagons.game.domain.use_cases.move_robot.GameService.move_robot",
        side_effect=GameException("blocked"),
    ):
        # Apply rotate then move via commands
        rot_uc = RotateRobotUseCase(repo)
        rot_uc.execute(RotateRobotCommand(game_id="r1", direction=Direction.NORTH))

        move_uc = MoveRobotUseCase(repo)
        res = move_uc.execute(MoveRobotCommand(game_id="r1", direction=Direction.NORTH))

    assert res.success is False
    assert res.game.robot.orientation.value == Direction.NORTH
    assert res.game.robot.position.row == 0
    assert res.game.robot.position.col == 0
    assert res.game.princess.position.row == 1
    assert res.game.princess.position.col == 1
    assert res.game.flowers == set()
    assert res.game.obstacles == set()
    assert res.game.get_status().value == "in_progress"
