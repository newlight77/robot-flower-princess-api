def test_create_game(client):
    response = client.post("/api/games/", json={"rows": 5, "cols": 5})
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["board"]["rows"] == 5
