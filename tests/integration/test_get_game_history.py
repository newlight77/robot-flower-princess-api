def test_get_game_history(client):
    create_response = client.post("/api/games/", json={"rows": 5, "cols": 5})
    game_id = create_response.json()["id"]

    response = client.get(f"/api/games/{game_id}/history")
    assert response.status_code == 200
    assert "history" in response.json()
