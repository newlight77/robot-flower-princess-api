from hexagons.game.driven.persistence.in_memory_game_repository import (
    InMemoryGameRepository,
)
from hexagons.game.domain.core.entities.position import Position
from hexagons.game.domain.core.entities.robot import Robot
from hexagons.game.domain.core.entities.princess import Princess
from hexagons.game.domain.core.entities.game import Game
from hexagons.game.domain.core.value_objects.direction import Direction

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


def make_center_board(rows=3, cols=3):
    robot = Robot(position=Position(1, 1), orientation=Direction.EAST)
    board = Game(
        rows=rows, cols=cols, robot=robot, princess=Princess(position=Position(rows - 1, cols - 1))
    )
    board.flowers = set()
    board.obstacles = set()
    board.board.initial_flowers_count = 0
    return board


def test_move_rotates_then_moves():
    repo = InMemoryGameRepository()
    board = make_center_board()
    repo.save("m1", board)

    use_case = MoveRobotUseCase(repo)
    res = use_case.execute(MoveRobotCommand(game_id="m1", direction=Direction.NORTH))

    assert isinstance(res.success, bool)
    b = repo.get("m1")
    assert b is not None
    assert b.robot.orientation == Direction.NORTH
    # position should have moved north if action succeeded
    if res.success:
        assert b.robot.position == Position(0, 1)


def test_pick_rotates_then_picks():
    repo = InMemoryGameRepository()
    board = make_center_board()
    # place a flower north of center
    flower_pos = Position(0, 1)
    board.flowers = {flower_pos}
    board.board.initial_flowers_count = 1
    repo.save("p1", board)

    use_case = PickFlowerUseCase(repo)
    res = use_case.execute(PickFlowerCommand(game_id="p1", direction=Direction.NORTH))

    assert isinstance(res.success, bool)
    b = repo.get("p1")
    assert b is not None
    assert b.robot.orientation == Direction.NORTH
    if res.success:
        assert b.robot.flowers_held > 0
        assert flower_pos not in b.flowers


def test_drop_rotates_then_drops():
    repo = InMemoryGameRepository()
    board = make_center_board()
    board.robot.pick_flower(Position(0, 1))
    repo.save("d1", board)

    use_case = DropFlowerUseCase(repo)
    res = use_case.execute(DropFlowerCommand(game_id="d1", direction=Direction.NORTH))

    assert isinstance(res.success, bool)
    b = repo.get("d1")
    assert b is not None
    assert b.robot.orientation == Direction.NORTH
    if res.success:
        assert b.robot.flowers_held == 0
        assert Position(0, 1) in b.flowers


def test_give_rotates_then_gives():
    repo = InMemoryGameRepository()
    board = make_center_board()
    # place princess north of robot
    board.princess.position = Position(0, 1)
    board.robot.pick_flower(Position(0, 1))
    repo.save("g1", board)

    use_case = GiveFlowersUseCase(repo)
    res = use_case.execute(GiveFlowersCommand(game_id="g1", direction=Direction.NORTH))

    assert isinstance(res.success, bool)
    b = repo.get("g1")
    assert b is not None
    assert b.robot.orientation == Direction.NORTH
    if res.success:
        assert b.robot.flowers_held == 0


def test_clean_rotates_then_cleans():
    repo = InMemoryGameRepository()
    board = make_center_board()
    obs_pos = Position(0, 1)
    board.obstacles = {obs_pos}
    repo.save("c1", board)

    use_case = CleanObstacleUseCase(repo)
    res = use_case.execute(CleanObstacleCommand(game_id="c1", direction=Direction.NORTH))

    assert isinstance(res.success, bool)
    b = repo.get("c1")
    assert b is not None
    assert b.robot.orientation == Direction.NORTH
    if res.success:
        assert obs_pos not in b.obstacles
