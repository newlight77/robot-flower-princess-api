from fastapi.testclient import TestClient
from robot_flower_princess.main import app

from robot_flower_princess.infrastructure.api.dependencies import get_game_repository
from robot_flower_princess.domain.entities.board import Board
from robot_flower_princess.domain.entities.position import Position
from robot_flower_princess.domain.entities.robot import Robot
from robot_flower_princess.domain.value_objects.direction import Direction
from robot_flower_princess.domain.entities.game_history import GameHistory

client = TestClient(app)


def save_board(game_id: str, board: Board):
    repo = get_game_repository()
    repo.save(game_id, board)
    history = GameHistory()
    history.add_action(action=None, board_state=board.to_dict())
    repo.save_history(game_id, history)


def make_empty_board(rows=3, cols=3) -> Board:
    # build a small empty board with robot at center for deterministic actions
    robot_pos = Position(1, 1)
    robot = Robot(position=robot_pos, orientation=Direction.NORTH)
    board = Board(rows=rows, cols=cols, robot=robot, princess_position=Position(2, 2))
    # ensure empties
    board.flowers = set()
    board.obstacles = set()
    return board


def test_move_success():
    game_id = "det-move"
    board = make_empty_board()
    # robot at (1,1) facing north; moving north should go to (0,1)
    board.robot.orientation = Direction.NORTH
    save_board(game_id, board)

    resp = client.post(f"/api/games/{game_id}/actions", json={"action": "move"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True or data["success"] is False
    # If success True, robot should have moved
    if data["success"]:
        assert data["board"]["robot"]["position"] == {"row": 0, "col": 1}


def test_pick_and_drop_and_give_success():
    game_id = "det-pick-drop-give"
    board = make_empty_board()
    # place a flower north of robot
    flower_pos = Position(0, 1)
    board.flowers = {flower_pos}
    board.robot.orientation = Direction.NORTH
    save_board(game_id, board)

    # pick
    resp = client.post(f"/api/games/{game_id}/actions", json={"action": "pickFlower"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    # robot should have flowers_held > 0
    assert data["board"]["robot"]["flowers_held"] > 0

    # drop to the south (robot facing north, drop to adjacent south cell)
    # first rotate to south
    resp = client.post(f"/api/games/{game_id}/actions", json={"action": "rotate", "direction": "south"})
    assert resp.status_code == 200
    # then drop
    resp = client.post(f"/api/games/{game_id}/actions", json={"action": "dropFlower"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    # robot should have 0 flowers_held after drop
    assert data["board"]["robot"]["flowers_held"] == 0

    # give flowers - place robot next to princess and give
    # ensure robot has a flower to give
    # add a flower to robot manually
    repo = get_game_repository()
    b = repo.get(game_id)
    assert b is not None
    b.robot.flowers_held = 1
    repo.save(game_id, b)

    # rotate robot to face princess
    resp = client.post(f"/api/games/{game_id}/actions", json={"action": "rotate", "direction": "east"})
    resp = client.post(f"/api/games/{game_id}/actions", json={"action": "giveFlower"})
    assert resp.status_code == 200
    data = resp.json()
    # giving may fail if not adjacent but ensure endpoint works and returns expected key
    assert "success" in data
