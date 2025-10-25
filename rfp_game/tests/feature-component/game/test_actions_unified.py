def test_clean_removes_obstacle(client, create_game):
    game_id, board = create_game()
    # find an obstacle adjacent to robot if possible
    robot_pos = board["robot"]["position"]
    r, c = robot_pos["row"], robot_pos["col"]
    grid = board["grid"]

    # try neighbors (up, down, left, right)
    neighbors = [
        (r - 1, c),
        (r + 1, c),
        (r, c - 1),
        (r, c + 1),
    ]

    found = False
    for nr, nc in neighbors:
        if 0 <= nr < board["rows"] and 0 <= nc < board["cols"]:
            if grid[nr][nc] == "🗑️":
                found = True
                break

    if not found:
        # if no obstacle adjacent, perform a clean (frontend always sends direction)
        current_dir = board["robot"]["orientation"]
        resp = client.post(
            f"/api/games/{game_id}/action", json={"action": "clean", "direction": current_dir}
        )
        assert resp.status_code == 200
        # success could be True or False depending on adjacency; ensure response shape
        assert "success" in resp.json()
    else:
        # there is an obstacle adjacent; rotate robot to face it then clean
        # determine direction
        if nr == r - 1 and nc == c:
            direction = "north"
        elif nr == r + 1 and nc == c:
            direction = "south"
        elif nr == r and nc == c - 1:
            direction = "west"
        else:
            direction = "east"

        resp = client.post(
            f"/api/games/{game_id}/action", json={"action": "rotate", "direction": direction}
        )
        assert resp.status_code == 200
        resp = client.post(
            f"/api/games/{game_id}/action", json={"action": "clean", "direction": direction}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        new_grid = data["board"]["grid"]
        assert new_grid[nr][nc] == "⬜"
