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


def make_center_game():
    game = Game(rows=3, cols=3)
    game.robot.position = Position(1, 1)
    game.robot.orientation = Direction.EAST
    game.princess.position = Position(2, 2)
    game.flowers = set()
    game.obstacles = set()
    game.board.initial_flowers_count = 0
    game.board.initial_obstacles_count = 0
    return game


def test_move_error_records_failed_action_direction(data_collector):
    repo = InMemoryGameRepository()
    game = make_center_game()
    repo.save("merr", game)

    with patch(
        "hexagons.game.domain.use_cases.move_robot.GameService.move_robot",
        side_effect=GameException("boom"),
    ):
        use_case = MoveRobotUseCase(repo, data_collector)
        use_case.execute(MoveRobotCommand(game_id="merr", direction=Direction.NORTH))


def test_pick_error_records_failed_action_direction(data_collector):
    repo = InMemoryGameRepository()
    game = make_center_game()
    repo.save("perr", game)

    with patch(
        "hexagons.game.domain.use_cases.pick_flower.GameService.pick_flower",
        side_effect=GameException("nope"),
    ):
        use_case = PickFlowerUseCase(repo, data_collector)
        use_case.execute(PickFlowerCommand(game_id="perr", direction=Direction.NORTH))


def test_drop_error_records_failed_action_direction(data_collector):
    repo = InMemoryGameRepository()
    game = make_center_game()
    game.robot.pick_flower(Position(0, 1))
    repo.save("derr", game)

    with patch(
        "hexagons.game.domain.use_cases.drop_flower.GameService.drop_flower",
        side_effect=GameException("bad"),
    ):
        use_case = DropFlowerUseCase(repo, data_collector)
        use_case.execute(DropFlowerCommand(game_id="derr", direction=Direction.NORTH))


def test_give_error_records_failed_action_direction(data_collector):
    repo = InMemoryGameRepository()
    game = make_center_game()
    game.robot.pick_flower(Position(0, 1))
    repo.save("gerr", game)

    with patch(
        "hexagons.game.domain.use_cases.give_flowers.GameService.give_flowers",
        side_effect=GameException("fail"),
    ):
        use_case = GiveFlowersUseCase(repo, data_collector)
        use_case.execute(GiveFlowersCommand(game_id="gerr", direction=Direction.NORTH))


def test_clean_error_records_failed_action_direction(data_collector):
    repo = InMemoryGameRepository()
    game = make_center_game()
    repo.save("cerr", game)

    with patch(
        "hexagons.game.domain.use_cases.clean_obstacle.GameService.clean_obstacle",
        side_effect=GameException("boom"),
    ):
        use_case = CleanObstacleUseCase(repo, data_collector)
        use_case.execute(CleanObstacleCommand(game_id="cerr", direction=Direction.NORTH))
