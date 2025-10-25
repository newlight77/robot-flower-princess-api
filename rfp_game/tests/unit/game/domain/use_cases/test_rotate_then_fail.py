from unittest.mock import patch

from hexagons.game.driven.persistence.in_memory_game_repository import (
    InMemoryGameRepository,
)
from hexagons.game.domain.core.entities.position import Position
from hexagons.game.domain.core.entities.robot import Robot
from hexagons.game.domain.core.entities.game import Game
from hexagons.game.domain.core.entities.game_history import GameHistory
from hexagons.game.domain.core.value_objects.direction import Direction
from hexagons.game.domain.core.exceptions.game_exceptions import GameException

from hexagons.game.domain.use_cases.move_robot import MoveRobotUseCase, MoveRobotCommand
from hexagons.game.domain.use_cases.rotate_robot import (
    RotateRobotUseCase,
    RotateRobotCommand,
)


def make_small_board():
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    board = Game(rows=2, cols=2, robot=robot, princess_position=Position(1, 1))
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
    with patch(
        "hexagons.game.domain.use_cases.move_robot.GameService.move_robot",
        side_effect=GameException("blocked"),
    ):
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
    assert history.actions[-1].success is False
    assert history.actions[-1].message == "blocked"

    assert res.success is False
    assert res.robot.orientation.value == Direction.NORTH
    assert res.robot.position.row == 0
    assert res.robot.position.col == 0
    assert res.princess.position.row == 1
    assert res.princess.position.col == 1
    assert res.flowers == set()
    assert res.obstacles == set()
    assert res.status == "in_progress"
