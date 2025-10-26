def test_create_game(client):
    response = client.post("/api/games/", json={"rows": 5, "cols": 5})
    assert response.status_code == 201
    data = response.json()
    assert "game" in data
    assert "message" in data
    game = data["game"]
    assert "id" in game
    assert game["board"]["rows"] == 5
