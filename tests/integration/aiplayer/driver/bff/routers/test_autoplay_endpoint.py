def test_autoplay(client):
    """Test autoplay endpoint with default (greedy) strategy."""
    create_response = client.post("/api/games/", json={"rows": 5, "cols": 5})
    game_id = create_response.json()["id"]

    response = client.post(f"/api/games/{game_id}/autoplay")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "board" in data


def test_autoplay_greedy_strategy_explicit(client):
    """Test autoplay endpoint with explicit greedy strategy."""
    create_response = client.post("/api/games/", json={"rows": 5, "cols": 5})
    game_id = create_response.json()["id"]

    response = client.post(f"/api/games/{game_id}/autoplay?strategy=greedy")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "board" in data


def test_autoplay_optimal_strategy(client):
    """Test autoplay endpoint with optimal strategy."""
    create_response = client.post("/api/games/", json={"rows": 5, "cols": 5})
    game_id = create_response.json()["id"]

    response = client.post(f"/api/games/{game_id}/autoplay?strategy=optimal")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "board" in data


def test_autoplay_optimal_small_board(client):
    """Test autoplay with optimal strategy on a smaller board."""
    create_response = client.post("/api/games/", json={"rows": 3, "cols": 3})
    game_id = create_response.json()["id"]

    response = client.post(f"/api/games/{game_id}/autoplay?strategy=optimal")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "board" in data
    # Verify response contains action information (case-insensitive)
    assert "actions taken" in data.get("message", "").lower()


def test_autoplay_invalid_strategy(client):
    """Test autoplay endpoint with invalid strategy parameter (returns 422)."""
    create_response = client.post("/api/games/", json={"rows": 5, "cols": 5})
    game_id = create_response.json()["id"]

    response = client.post(f"/api/games/{game_id}/autoplay?strategy=invalid")
    # Invalid strategy should return 422 Unprocessable Entity
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_autoplay_strategy_parameter_case_sensitive(client):
    """Test that strategy parameter is case-sensitive (uppercase returns 422)."""
    create_response = client.post("/api/games/", json={"rows": 4, "cols": 4})
    game_id = create_response.json()["id"]

    # Test with uppercase - should return 422
    response = client.post(f"/api/games/{game_id}/autoplay?strategy=OPTIMAL")
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
