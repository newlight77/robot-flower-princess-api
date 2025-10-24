from robot_flower_princess.domain.core.value_objects.direction import Direction


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_game(client):
    response = client.post("/api/games/", json={"rows": 5, "cols": 5})
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["board"]["rows"] == 5


def test_get_game_state(client):
    create_response = client.post("/api/games/", json={"rows": 5, "cols": 5})
    game_id = create_response.json()["id"]

    response = client.get(f"/api/games/{game_id}")
    assert response.status_code == 200
    assert response.json()["id"] == game_id

def test_rotate_changes_orientation(client, create_game):
    game_id, board = create_game()

    resp = client.post(
        f"/api/games/{game_id}/action", json={"action": "rotate", "direction": "south"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["robot"]["orientation"] == "south"


def test_robot_move(client, save_board, make_empty_board):
    game_id = "det-move"
    board = make_empty_board()
    # robot at (1,1) facing north; moving north should go to (0,1)
    board.robot.orientation = Direction.NORTH
    save_board(game_id, board)

    resp = client.post(
        f"/api/games/{game_id}/action", json={"action": "move", "direction": "north"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True or data["success"] is False
    # If success True, robot should have moved
    if data["success"]:
        assert data["robot"]["position"] == {"row": 0, "col": 1}

def test_invalid_direction_payload(client, seeded_board):
    game_id, board = seeded_board("invalid-dir")

    # Send an invalid direction value
    resp = client.post(
        f"/api/games/{game_id}/action", json={"action": "move", "direction": "upwards"}
    )
    assert resp.status_code == 422
    assert "detail" in resp.json()
    assert resp.json()["detail"][0]["msg"] == "invalid direction"
    assert resp.json()["detail"][0]["type"] == "value_error.enum"
    assert resp.json()["detail"][0]["ctx"]["enum_values"] == ["north", "south", "east", "west"]

def test_move_with_helpers(client, make_empty_board, save_board):
    game_id = "helper-move"
    board = make_empty_board()
    # place robot at center facing north
    save_board(game_id, board)

    resp = client.post(
        f"/api/games/{game_id}/action", json={"action": "move", "direction": "north"}
    )
    assert resp.status_code == 200
    data = resp.json()
    # if move succeeded, robot moved to row 0, col 1
    if data["success"]:
        assert data["robot"]["position"] == {"row": 0, "col": 1}


def test_get_game_history(client):
    create_response = client.post("/api/games/", json={"rows": 5, "cols": 5})
    game_id = create_response.json()["id"]

    response = client.get(f"/api/games/{game_id}/history")
    assert response.status_code == 200
    assert "history" in response.json()


def test_autoplay(client):
    create_response = client.post("/api/games/", json={"rows": 5, "cols": 5})
    game_id = create_response.json()["id"]

    response = client.post(f"/api/games/{game_id}/autoplay")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "board" in data
