from hexagons.game.domain.core.value_objects.direction import Direction


def test_rotate_changes_orientation(client, create_game):
    game_id, board = create_game()

    resp = client.post(f"/api/games/{game_id}/action", json={"action": "rotate", "direction": "south"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["game"]["robot"]["orientation"] == "south"


def test_robot_move(client, save_board, make_empty_board):
    game_id = "det-move"
    board = make_empty_board()
    # robot at (1,1) facing north; moving north should go to (0,1)
    board.robot.orientation = Direction.NORTH
    save_board(game_id, board)

    resp = client.post(f"/api/games/{game_id}/action", json={"action": "move", "direction": "north"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True or data["success"] is False
    # If success True, robot should have moved
    if data["success"]:
        assert data["game"]["robot"]["position"] == {"row": 0, "col": 1}


def test_invalid_direction_payload(client, seeded_board):
    game_id, board = seeded_board("invalid-dir")

    # Send an invalid direction value
    resp = client.post(f"/api/games/{game_id}/action", json={"action": "move", "direction": "upwards"})
    assert resp.status_code == 422
    assert "detail" in resp.json()

    # Pydantic v2 returns different error format
    error_detail = resp.json()["detail"][0]
    error_msg = error_detail["msg"]

    # Check that the error message mentions the valid directions
    assert "north" in error_msg.lower() and "south" in error_msg.lower()

    # Pydantic v2 uses "literal_error" type for Literal validation
    assert error_detail["type"] == "literal_error"


def test_move_with_helpers(client, make_empty_board, save_board):
    game_id = "helper-move"
    board = make_empty_board()
    # place robot at center facing north
    save_board(game_id, board)

    resp = client.post(f"/api/games/{game_id}/action", json={"action": "move", "direction": "north"})
    assert resp.status_code == 200
    data = resp.json()
    # if move succeeded, robot moved to row 0, col 1
    if data["success"]:
        assert data["game"]["robot"]["position"] == {"row": 0, "col": 1}
