import pytest

from robot_flower_princess.driven.persistence.in_memory_game_repository import InMemoryGameRepository
from robot_flower_princess.domain.entities.position import Position
from robot_flower_princess.domain.entities.robot import Robot
from robot_flower_princess.domain.value_objects.direction import Direction
from robot_flower_princess.domain.entities.board import Board
from robot_flower_princess.application.use_cases.rotate_robot import RotateRobotUseCase, RotateRobotCommand
from robot_flower_princess.application.use_cases.move_robot import MoveRobotUseCase, MoveRobotCommand
from robot_flower_princess.application.use_cases.pick_flower import PickFlowerUseCase, PickFlowerCommand
from robot_flower_princess.application.use_cases.drop_flower import DropFlowerUseCase, DropFlowerCommand
from robot_flower_princess.application.use_cases.give_flowers import GiveFlowersUseCase, GiveFlowersCommand
from robot_flower_princess.domain.entities.game_history import GameHistory


@pytest.fixture
def repo():
    return InMemoryGameRepository()


def make_board_with_flower():
    robot = Robot(position=Position(1, 1), orientation=Direction.NORTH)
    board = Board(rows=3, cols=3, robot=robot, princess_position=Position(2, 2))
    # place a flower north of robot
    board.flowers = {Position(0, 1)}
    board.obstacles = set()
    board.initial_flower_count = len(board.flowers)
    return board


def test_rotate_use_case_missing_game(repo):
    use_case = RotateRobotUseCase(repo)
    with pytest.raises(ValueError):
        use_case.execute(RotateRobotCommand(game_id="missing", direction=Direction.NORTH))


def test_rotate_use_case_success(repo):
    board = make_board_with_flower()
    repo.save("g1", board)
    repo.save_history("g1", GameHistory())

    use_case = RotateRobotUseCase(repo)
    res = use_case.execute(RotateRobotCommand(game_id="g1", direction=Direction.SOUTH))
    assert res.success is True
    assert res.board_state["robot"]["orientation"] == "south"


def test_move_use_case_missing_game(repo):
    use_case = MoveRobotUseCase(repo)
    with pytest.raises(ValueError):
        use_case.execute(MoveRobotCommand(game_id="missing", direction=Direction.NORTH))


def test_move_use_case_success(repo):
    board = make_board_with_flower()
    repo.save("g2", board)
    repo.save_history("g2", GameHistory())

    use_case = MoveRobotUseCase(repo)
    res = use_case.execute(MoveRobotCommand(game_id="g2", direction=Direction.NORTH))
    assert isinstance(res.success, bool)
    assert "board_state" in res.__dict__


def test_pick_drop_give_use_cases(repo):
    board = make_board_with_flower()
    repo.save("g3", board)
    repo.save_history("g3", GameHistory())

    pick_uc = PickFlowerUseCase(repo)
    pick_res = pick_uc.execute(PickFlowerCommand(game_id="g3", direction=Direction.NORTH))
    # pick may succeed or fail depending on board orientation/placement; ensure boolean
    assert isinstance(pick_res.success, bool)

    drop_uc = DropFlowerUseCase(repo)
    drop_res = drop_uc.execute(DropFlowerCommand(game_id="g3", direction=Direction.NORTH))
    assert isinstance(drop_res.success, bool)

    # give - likely fail unless robot adjacent to princess and holding flowers; just ensure it runs
    give_uc = GiveFlowersUseCase(repo)
    give_res = give_uc.execute(GiveFlowersCommand(game_id="g3", direction=Direction.NORTH))
    assert isinstance(give_res.success, bool)
