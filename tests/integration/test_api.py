import pytest


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


def test_rotate_robot(client):
    create_response = client.post("/api/games/", json={"rows": 5, "cols": 5})
    game_id = create_response.json()["id"]

    response = client.post(f"/api/games/{game_id}/action", json={"action": "rotate", "direction": "south"})
    assert response.status_code == 200
    assert response.json()["success"]


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
