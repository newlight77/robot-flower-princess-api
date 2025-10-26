def test_get_game_state(client):
    create_response = client.post("/api/games/", json={"rows": 5, "cols": 5})
    game_id = create_response.json()["game"]["id"]

    response = client.get(f"/api/games/{game_id}")
    assert response.status_code == 200
    data = response.json()
    assert "game" in data
    assert data["game"]["id"] == game_id
