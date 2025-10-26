from hexagons.game.domain.core.entities.position import Position


def should_clean_removes_obstacle_successfully(
    client, make_empty_board, save_board, place_obstacle
):
    game_id = "component-clean-removes-obstacle"
    board = make_empty_board()
    # place an obstacle north of robot
    obstacle_north_pos = Position(0, 1)
    place_obstacle(board, obstacle_north_pos)
    save_board(game_id, board)

    # clean the north obstacle
    resp = client.post(
        f"/api/games/{game_id}/action", json={"action": "clean", "direction": "north"}
    )
    assert resp.status_code == 200
    data = resp.json()
    print(f"should_clean_removes_obstacle_successfully Data: {data}")
    assert data["success"] is True
    assert obstacle_north_pos not in board.obstacles

    # clean the south obstacle
    obstacle_south_pos = Position(0, 1)
    place_obstacle(board, obstacle_south_pos)
    resp = client.post(
        f"/api/games/{game_id}/action", json={"action": "clean", "direction": "south"}
    )
    assert resp.status_code == 200
    data = resp.json()
    print(f"should_clean_removes_obstacle_successfully Data: {data}")
    assert data["success"] is True
    assert obstacle_south_pos not in board.obstacles
