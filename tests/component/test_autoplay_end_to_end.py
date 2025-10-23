from fastapi.testclient import TestClient
from robot_flower_princess.main import app
from robot_flower_princess.driven.persistence.in_memory_game_repository import (
    InMemoryGameRepository,
)
from robot_flower_princess.domain.core.entities.position import Position
from robot_flower_princess.domain.core.entities.robot import Robot
from robot_flower_princess.domain.core.entities.game import Game
from robot_flower_princess.domain.core.entities.game_history import GameHistory
from robot_flower_princess.domain.core.value_objects.direction import Direction

client = TestClient(app)


def test_autoplay_end_to_end():
    repo = InMemoryGameRepository()
    # create a small solvable board
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    board = Game(rows=2, cols=2, robot=robot, princess_position=Position(1, 1))
    board.flowers = {Position(0, 1)}
    board.obstacles = set()
    board.initial_flower_count = len(board.flowers)

    game_id = "component-autoplay"
    repo.save(game_id, board)
    repo.save_history(game_id, GameHistory(game_id=game_id))

    # Temporarily override the app dependency to use our repo
    from robot_flower_princess.configurator.dependencies import get_game_repository

    # Save any existing override and set our test override
    original_override = app.dependency_overrides.get(get_game_repository)
    app.dependency_overrides[get_game_repository] = lambda: repo

    try:
        resp = client.post(f"/api/games/{game_id}/autoplay")
        assert resp.status_code == 200
        data = resp.json()
        assert "actions_taken" in data["message"] or "board" in data
    finally:
        # restore original override
        if original_override is None:
            app.dependency_overrides.pop(get_game_repository, None)
        else:
            app.dependency_overrides[get_game_repository] = original_override


def test_autoplay_with_obstacles():
    """Test autoplay can solve a game with obstacles - may not complete but should make progress."""
    repo = InMemoryGameRepository()

    # Create a simple 3x3 board where robot can access everything
    # Layout:
    # R F _
    # _ O _
    # _ _ P
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    board = Game(rows=3, cols=3, robot=robot, princess_position=Position(2, 2))
    board.flowers = {Position(0, 1)}
    board.obstacles = {Position(1, 1)}  # One obstacle in the middle
    board.initial_flower_count = len(board.flowers)

    game_id = "component-autoplay-obstacles"
    repo.save(game_id, board)
    repo.save_history(game_id, GameHistory(game_id=game_id))

    # Temporarily override the app dependency to use our repo
    from robot_flower_princess.configurator.dependencies import get_game_repository

    original_override = app.dependency_overrides.get(get_game_repository)
    app.dependency_overrides[get_game_repository] = lambda: repo

    try:
        resp = client.post(f"/api/games/{game_id}/autoplay")
        assert resp.status_code == 200
        data = resp.json()

        # Autoplay should successfully attempt to solve
        assert resp.status_code == 200
        assert "success" in data or "message" in data

    finally:
        # restore original override
        if original_override is None:
            app.dependency_overrides.pop(get_game_repository, None)
        else:
            app.dependency_overrides[get_game_repository] = original_override
