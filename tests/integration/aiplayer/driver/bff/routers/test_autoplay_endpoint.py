def test_autoplay(client):
    create_response = client.post("/api/games/", json={"rows": 5, "cols": 5})
    game_id = create_response.json()["id"]

    response = client.post(f"/api/games/{game_id}/autoplay")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "board" in data
