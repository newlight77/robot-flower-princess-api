from unittest.mock import patch

from hexagons.game.driven.persistence.in_memory_game_repository import (
    InMemoryGameRepository,
)
from hexagons.game.domain.core.entities.position import Position
from hexagons.game.domain.core.entities.game import Game
from hexagons.game.domain.core.value_objects.direction import Direction
from hexagons.game.domain.core.exceptions.game_exceptions import GameException

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
    board = Game(rows=3, cols=3)
    board.robot.position = Position(1, 1)
    board.robot.orientation = Direction.EAST
    board.princess.position = Position(2, 2)
    board.flowers = set()
    board.obstacles = set()
    board.board.initial_flowers_count = 0
    return board


def test_move_error_records_failed_action_direction():
    repo = InMemoryGameRepository()
    board = make_center_board()
    repo.save("merr", board)

    with patch(
        "hexagons.game.domain.use_cases.move_robot.GameService.move_robot",
        side_effect=GameException("boom"),
    ):
        use_case = MoveRobotUseCase(repo)
        use_case.execute(MoveRobotCommand(game_id="merr", direction=Direction.NORTH))


def test_pick_error_records_failed_action_direction():
    repo = InMemoryGameRepository()
    board = make_center_board()
    repo.save("perr", board)

    with patch(
        "hexagons.game.domain.use_cases.pick_flower.GameService.pick_flower",
        side_effect=GameException("nope"),
    ):
        use_case = PickFlowerUseCase(repo)
        use_case.execute(PickFlowerCommand(game_id="perr", direction=Direction.NORTH))


def test_drop_error_records_failed_action_direction():
    repo = InMemoryGameRepository()
    board = make_center_board()
    board.robot.pick_flower(Position(0, 1))
    repo.save("derr", board)

    with patch(
        "hexagons.game.domain.use_cases.drop_flower.GameService.drop_flower",
        side_effect=GameException("bad"),
    ):
        use_case = DropFlowerUseCase(repo)
        use_case.execute(DropFlowerCommand(game_id="derr", direction=Direction.NORTH))


def test_give_error_records_failed_action_direction():
    repo = InMemoryGameRepository()
    board = make_center_board()
    board.robot.pick_flower(Position(0, 1))
    repo.save("gerr", board)

    with patch(
        "hexagons.game.domain.use_cases.give_flowers.GameService.give_flowers",
        side_effect=GameException("fail"),
    ):
        use_case = GiveFlowersUseCase(repo)
        use_case.execute(GiveFlowersCommand(game_id="gerr", direction=Direction.NORTH))


def test_clean_error_records_failed_action_direction():
    repo = InMemoryGameRepository()
    board = make_center_board()
    repo.save("cerr", board)

    with patch(
        "hexagons.game.domain.use_cases.clean_obstacle.GameService.clean_obstacle",
        side_effect=GameException("boom"),
    ):
        use_case = CleanObstacleUseCase(repo)
        use_case.execute(CleanObstacleCommand(game_id="cerr", direction=Direction.NORTH))
