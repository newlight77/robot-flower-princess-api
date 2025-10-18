import pytest
from fastapi.testclient import TestClient
from robot_flower_princess.infrastructure.api.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_game():
    response = client.post("/api/v1/games/", json={"rows": 5, "cols": 5})
    assert response.status_code == 201
    data = response.json()
    assert "game_id" in data
    assert data["board"]["rows"] == 5


def test_get_game_state():
    create_response = client.post("/api/v1/games/", json={"rows": 5, "cols": 5})
    game_id = create_response.json()["game_id"]

    response = client.get(f"/api/v1/games/{game_id}")
    assert response.status_code == 200
    assert response.json()["game_id"] == game_id


def test_rotate_robot():
    create_response = client.post("/api/v1/games/", json={"rows": 5, "cols": 5})
    game_id = create_response.json()["game_id"]

    response = client.post(
        f"/api/v1/games/{game_id}/actions/rotate",
        json={"direction": "south"}
    )
    assert response.status_code == 200
    assert response.json()["success"] == True


def test_get_game_history():
    create_response = client.post("/api/v1/games/", json={"rows": 5, "cols": 5})
    game_id = create_response.json()["game_id"]

    response = client.get(f"/api/v1/games/{game_id}/history")
    assert response.status_code == 200
    assert "history" in response.json()


def test_autoplay():
    create_response = client.post("/api/v1/games/", json={"rows": 5, "cols": 5})
    game_id = create_response.json()["game_id"]

    response = client.post(f"/api/v1/games/{game_id}/autoplay")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "board" in data
