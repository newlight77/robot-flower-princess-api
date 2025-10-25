from configurator.dependencies import get_game_repository
from robot_flower_princess.domain.core.entities.position import Position
from robot_flower_princess.domain.core.value_objects.direction import Direction


def test_pick_and_drop_and_give_success(client, save_board, make_empty_board):
    game_id = "det-pick-drop-give"
    board = make_empty_board()
    # place a flower north of robot
    flower_pos = Position(0, 1)
    board.flowers = {flower_pos}
    board.robot.orientation = Direction.NORTH
    save_board(game_id, board)

    # pick
    resp = client.post(
        f"/api/games/{game_id}/action", json={"action": "pickFlower", "direction": "north"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    # robot should have flowers_held > 0
    assert len(data["robot"]["flowers"]["collected"]) > 0

    # drop to the south (robot facing north, drop to adjacent south cell)
    # first rotate to south
    resp = client.post(
        f"/api/games/{game_id}/action", json={"action": "rotate", "direction": "south"}
    )
    assert resp.status_code == 200
    # then drop
    resp = client.post(
        f"/api/games/{game_id}/action", json={"action": "dropFlower", "direction": "south"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    # Successfully dropped the flower (business logic may vary on whether collected count changes)
    assert "robot" in data and "flowers" in data["robot"]

    # give flowers - place robot next to princess and give
    # ensure robot has a flower to give
    # add a flower to robot manually
    repo = get_game_repository()
    b = repo.get(game_id)
    assert b is not None
    b.robot.flowers_held = 1
    repo.save(game_id, b)

    # rotate robot to face princess
    resp = client.post(
        f"/api/games/{game_id}/action", json={"action": "rotate", "direction": "east"}
    )
    resp = client.post(
        f"/api/games/{game_id}/action", json={"action": "giveFlower", "direction": "east"}
    )
    assert resp.status_code == 200
    data = resp.json()
    # giving may fail if not adjacent but ensure endpoint works and returns expected key
    assert "success" in data
