def test_invalid_direction_payload(client, seeded_board):
    game_id, board = seeded_board("invalid-dir")

    # Send an invalid direction value
    resp = client.post(
        f"/api/games/{game_id}/action", json={"action": "move", "direction": "upwards"}
    )
    assert resp.status_code == 422
