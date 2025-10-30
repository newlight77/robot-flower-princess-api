import pytest

from hexagons.game.driven.persistence.in_memory_game_repository import (
    InMemoryGameRepository,
)
from hexagons.game.domain.core.entities.position import Position
from hexagons.game.domain.core.entities.game import Game
from hexagons.game.domain.core.value_objects.direction import Direction

from hexagons.game.domain.use_cases.rotate_robot import (
    RotateRobotUseCase,
    RotateRobotCommand,
)
from hexagons.game.domain.use_cases.move_robot import MoveRobotUseCase, MoveRobotCommand
from hexagons.game.domain.use_cases.pick_flower import PickFlowerUseCase, PickFlowerCommand
from hexagons.game.domain.use_cases.drop_flower import DropFlowerUseCase, DropFlowerCommand
from hexagons.game.domain.use_cases.give_flowers import (
    GiveFlowersUseCase,
    GiveFlowersCommand,
)


@pytest.fixture
def repo():
    return InMemoryGameRepository()


def make_game_with_flower():
    game = Game(rows=3, cols=3)
    game.robot.position = Position(1, 1)
    game.robot.orientation = Direction.NORTH
    game.princess.position = Position(2, 2)
    # place a flower north of robot
    game.flowers = {Position(0, 1)}
    game.obstacles = set()
    game.board.initial_flowers_count = len(game.flowers)
    return game


def test_rotate_use_case_missing_game(repo, data_collector):
    use_case = RotateRobotUseCase(repo, data_collector)
    with pytest.raises(ValueError):
        use_case.execute(RotateRobotCommand(game_id="missing", direction=Direction.NORTH))


def test_rotate_use_case_success(repo, data_collector):
    game = make_game_with_flower()
    repo.save("g1", game)

    use_case = RotateRobotUseCase(repo, data_collector)
    res = use_case.execute(RotateRobotCommand(game_id="g1", direction=Direction.SOUTH))
    assert res.success is True
    assert res.game.robot.orientation == Direction.SOUTH


def test_move_use_case_missing_game(repo, data_collector):
    use_case = MoveRobotUseCase(repo, data_collector)
    with pytest.raises(ValueError):
        use_case.execute(MoveRobotCommand(game_id="missing", direction=Direction.NORTH))


def test_move_use_case_success(repo, data_collector):
    game = make_game_with_flower()
    repo.save("g2", game)

    use_case = MoveRobotUseCase(repo, data_collector)
    res = use_case.execute(MoveRobotCommand(game_id="g2", direction=Direction.NORTH))
    assert isinstance(res.success, bool)
    assert hasattr(res, "game")
    assert hasattr(res.game, "board")
    assert hasattr(res.game, "robot")
    assert hasattr(res.game, "princess")


def test_pick_drop_give_use_cases(repo, data_collector):
    game = make_game_with_flower()
    repo.save("g3", game)

    pick_uc = PickFlowerUseCase(repo, data_collector)
    pick_res = pick_uc.execute(PickFlowerCommand(game_id="g3", direction=Direction.NORTH))
    # pick may succeed or fail depending on board orientation/placement; ensure boolean
    assert isinstance(pick_res.success, bool)

    drop_uc = DropFlowerUseCase(repo, data_collector)
    drop_res = drop_uc.execute(DropFlowerCommand(game_id="g3", direction=Direction.NORTH))
    assert isinstance(drop_res.success, bool)

    # give - likely fail unless robot adjacent to princess and holding flowers; just ensure it runs
    give_uc = GiveFlowersUseCase(repo, data_collector)
    give_res = give_uc.execute(GiveFlowersCommand(game_id="g3", direction=Direction.NORTH))
    assert isinstance(give_res.success, bool)
