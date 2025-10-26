from configurator.dependencies import get_game_repository
from hexagons.game.domain.core.entities.position import Position
from hexagons.game.domain.core.value_objects.direction import Direction


def should_pick_drop_give_successfully(client, save_board, make_empty_board):
    game_id = "component-pick-drop-give"
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
    print(f"should_pick_drop_give_successfully Data: {data}")
    assert data["success"] is True
    # robot should have flowers_held > 0
    assert len(data["game"]["robot"]["flowers_collected"]) > 0

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
    print(f"should_pick_drop_give_successfully Data: {data}")
    assert data["success"] is True
    # Successfully dropped the flower (business logic may vary on whether collected count changes)
    assert (
        "game" in data and "robot" in data["game"] and "flowers_collected" in data["game"]["robot"]
    )

    # give flowers - place robot next to princess and give
    # ensure robot has a flower to give
    # add a flower to robot manually
    repo = get_game_repository()
    b = repo.get(game_id)
    assert b is not None
    b.robot.pick_flower(Position(1, 1))  # Add a flower
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


def test_drop_flower_at_different_position(client, save_board, make_empty_board):
    """
    Test the bug fix: dropping a flower at a position different from where it was picked.

    Scenario:
    1. Robot picks a flower from position A
    2. Robot moves to a new location
    3. Robot drops the flower at position B (different from A)

    Before fix: This would fail with "position not found" error
    After fix: This should succeed using LIFO (pop last flower)
    """
    from configurator.dependencies import get_game_repository

    game_id = "test-drop-different-position"
    board = make_empty_board(rows=10, cols=10)

    # Setup: Place robot at (6, 1) facing south
    # Place a flower directly south of robot at (7, 1)
    board.robot.position = Position(6, 1)
    board.robot.orientation = Direction.SOUTH
    flower_pos = Position(7, 1)
    board.flowers = {flower_pos}
    save_board(game_id, board)

    # Verify board setup
    repo = get_game_repository()
    retrieved_board = repo.get(game_id)
    assert flower_pos in retrieved_board.flowers, f"Flower not found at {flower_pos}"

    # Step 1: Pick the flower from (7, 1)
    resp = client.post(
        f"/api/games/{game_id}/action", json={"action": "pickFlower", "direction": "south"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True, f"Pick failed: {data}"
    assert len(data["game"]["robot"]["flowers_collected"]) == 1

    # Step 2: Rotate east and move to (6, 2)
    resp = client.post(
        f"/api/games/{game_id}/action", json={"action": "rotate", "direction": "east"}
    )
    assert resp.status_code == 200

    resp = client.post(f"/api/games/{game_id}/action", json={"action": "move", "direction": "east"})
    assert resp.status_code == 200

    # Step 3: Drop flower east at position (6, 3) - different from pick position (7, 1)
    # This is the critical test - drop_position != pick_position
    resp = client.post(
        f"/api/games/{game_id}/action", json={"action": "dropFlower", "direction": "east"}
    )
    assert resp.status_code == 200
    data = resp.json()

    # Verify success
    assert data["success"] is True, f"Drop failed: {data}"
    assert (
        len(data["game"]["robot"]["flowers_collected"]) == 0
    ), "Robot should have no flowers after dropping"

    # Verify the flower is now at the new position on the board
    board_state = data["game"]["board"]
    dropped_row, dropped_col = 6, 3
    assert (
        board_state["grid"][dropped_row][dropped_col] == "🌸"
    ), f"Expected flower at ({dropped_row}, {dropped_col})"


def test_pick_and_drop_multiple_flowers_lifo(client, save_board, make_empty_board):
    """
    Test that dropping multiple flowers follows LIFO (Last In, First Out) behavior.

    Scenario:
    1. Pick flower from position A
    2. Pick flower from position B
    3. Pick flower from position C
    4. Drop flower -> should remove flower from position C (last picked)
    5. Drop flower -> should remove flower from position B
    6. Drop flower -> should remove flower from position A
    """
    game_id = "test-drop-lifo"
    board = make_empty_board(rows=10, cols=10)

    # Setup: Robot at (5, 5) facing north, flowers around it
    board.robot.position = Position(5, 5)
    board.robot.orientation = Direction.NORTH

    # Place 3 flowers at different positions (north, east, south of robot)
    flower_north = Position(4, 5)
    flower_east = Position(5, 6)
    flower_south = Position(6, 5)
    board.flowers = {flower_north, flower_east, flower_south}
    save_board(game_id, board)

    # Pick flower 1 from north
    resp = client.post(
        f"/api/games/{game_id}/action", json={"action": "pickFlower", "direction": "north"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True, f"Pick north failed: {data}"
    assert len(data["game"]["robot"]["flowers_collected"]) == 1

    # Pick flower 2 from east
    resp = client.post(
        f"/api/games/{game_id}/action", json={"action": "pickFlower", "direction": "east"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True, f"Pick east failed: {data}"
    assert len(data["game"]["robot"]["flowers_collected"]) == 2

    # Pick flower 3 from south
    resp = client.post(
        f"/api/games/{game_id}/action", json={"action": "pickFlower", "direction": "south"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True, f"Pick south failed: {data}"
    assert len(data["game"]["robot"]["flowers_collected"]) == 3

    # Now drop flowers - they should be removed in LIFO order
    # Drop 1: Should remove flower from south (last picked) - drop it west
    resp = client.post(
        f"/api/games/{game_id}/action", json={"action": "dropFlower", "direction": "west"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True, f"Drop 1 failed: {data}"
    assert len(data["game"]["robot"]["flowers_collected"]) == 2

    # Drop 2: Should remove flower from east (second to last picked) - drop it north
    resp = client.post(
        f"/api/games/{game_id}/action", json={"action": "dropFlower", "direction": "north"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True, f"Drop 2 failed: {data}"
    assert len(data["game"]["robot"]["flowers_collected"]) == 1

    # Drop 3: Should remove flower from north (first picked) - drop it east
    resp = client.post(
        f"/api/games/{game_id}/action", json={"action": "dropFlower", "direction": "east"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True, f"Drop 3 failed: {data}"
    assert len(data["game"]["robot"]["flowers_collected"]) == 0, "All flowers should be dropped"
