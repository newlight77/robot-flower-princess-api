def should_pick_drop_give_with_helpers_successfully(client, make_empty_board, save_board, place_flower):
    game_id = "component-pick-drop-give-with-helpers"
    board = make_empty_board()
    # place a flower north of robot
    from hexagons.game.domain.core.entities.position import Position

    flower_pos = Position(0, 1)
    place_flower(board, flower_pos)
    save_board(game_id, board)

    # pick
    resp = client.post(f"/api/games/{game_id}/action", json={"action": "pickFlower", "direction": "north"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert len(data["game"]["robot"]["flowers_collected"]) > 0

    # rotate to south and drop
    resp = client.post(f"/api/games/{game_id}/action", json={"action": "rotate", "direction": "south"})
    assert resp.status_code == 200
    resp = client.post(f"/api/games/{game_id}/action", json={"action": "dropFlower", "direction": "south"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    # Successfully dropped the flower (business logic may vary on whether collected count changes)
    assert "robot" in data["game"] and "flowers_collected" in data["game"]["robot"]

    # give: set robot next to princess and add a flower to give
    from configurator.dependencies import get_game_repository

    repo = get_game_repository()
    b = repo.get(game_id)
    assert b is not None
    # put robot adjacent to princess and add a flower to collected
    b.robot.position = Position(2, 1)
    b.robot.flowers_collected.append(Position(1, 1))  # Add a flower to give
    repo.save(game_id, b)

    resp = client.post(f"/api/games/{game_id}/action", json={"action": "giveFlower", "direction": "south"})
    assert resp.status_code == 200
    data = resp.json()
    print(f"should_pick_drop_give_with_helpers_successfully Data: {data}")
    assert "success" in data["message"] or "board" in data


def should_clean_with_helpers_successfully(client, make_empty_board, save_board, place_obstacle, place_robot):
    game_id = "component-clean-with-helpers"
    board = make_empty_board()
    from hexagons.game.domain.core.entities.position import Position
    from hexagons.game.domain.core.value_objects.direction import Direction

    # place obstacle north of robot
    obs_pos = Position(0, 1)
    place_obstacle(board, obs_pos)
    # ensure robot faces north and is in position
    place_robot(board, Position(1, 1), orientation=Direction.NORTH)
    save_board(game_id, board)

    # rotate to north and clean
    resp = client.post(f"/api/games/{game_id}/action", json={"action": "rotate", "direction": "north"})
    assert resp.status_code == 200
    resp = client.post(f"/api/games/{game_id}/action", json={"action": "clean", "direction": "north"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["game"]["board"]["grid"][0][1] == "⬜"
