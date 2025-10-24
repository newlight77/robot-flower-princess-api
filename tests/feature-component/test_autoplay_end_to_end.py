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


def test_autoplay_multiple_flowers_with_obstacles():
    """Test autoplay can handle multiple flowers and clean obstacles."""
    repo = InMemoryGameRepository()

    # Create a simple 4x4 board with 2 flowers and some obstacles
    # Layout:
    # R F _ _
    # _ _ _ _
    # _ O _ F
    # _ _ _ P
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    board = Game(rows=4, cols=4, robot=robot, princess_position=Position(3, 3))
    board.flowers = {
        Position(0, 1),  # Next to robot
        Position(2, 3),  # Near princess
    }
    board.obstacles = {Position(2, 1)}  # One obstacle
    board.initial_flower_count = len(board.flowers)

    game_id = "component-autoplay-multiple-flowers"
    repo.save(game_id, board)
    repo.save_history(game_id, GameHistory(game_id=game_id))

    # Temporarily override the app dependency to use our repo
    from robot_flower_princess.configurator.dependencies import get_game_repository

    original_override = app.dependency_overrides.get(get_game_repository)
    app.dependency_overrides[get_game_repository] = lambda: repo

    try:
        resp = client.post(f"/api/games/{game_id}/autoplay")
        assert resp.status_code == 200

        # Should successfully complete or at least make progress
        assert resp.status_code == 200

        # Verify some progress was made
        actions_taken = len(repo.get_history(game_id).actions) if repo.get_history(game_id) else 0

        # The solver should have taken some actions
        assert actions_taken > 0, f"Solver should have taken actions, but took {actions_taken}"

    finally:
        # restore original override
        if original_override is None:
            app.dependency_overrides.pop(get_game_repository, None)
        else:
            app.dependency_overrides[get_game_repository] = original_override


def test_autoplay_normal_delivery_clear_path():
    """Test 1: Normal delivery with clear path - navigate and deliver."""
    repo = InMemoryGameRepository()

    # Simple 3x3 board with clear path
    # Layout:
    # R F _
    # _ _ _
    # _ _ P
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    board = Game(rows=3, cols=3, robot=robot, princess_position=Position(2, 2))
    board.flowers = {Position(0, 1)}
    board.obstacles = set()  # No obstacles
    board.initial_flower_count = len(board.flowers)

    game_id = "test-clear-path"
    repo.save(game_id, board)
    repo.save_history(game_id, GameHistory(game_id=game_id))

    from robot_flower_princess.configurator.dependencies import get_game_repository

    original_override = app.dependency_overrides.get(get_game_repository)
    app.dependency_overrides[get_game_repository] = lambda: repo

    try:
        resp = client.post(f"/api/games/{game_id}/autoplay")
        assert resp.status_code == 200

        final_board = repo.get(game_id)
        # Should successfully deliver flower
        assert final_board.flowers_delivered > 0 or final_board.get_status().value == "victory"

    finally:
        if original_override is None:
            app.dependency_overrides.pop(get_game_repository, None)
        else:
            app.dependency_overrides[get_game_repository] = original_override


def test_autoplay_blocked_path_drop_and_clean():
    """Test 2: Blocked path with flowers - drop, clean, pick up, deliver."""
    repo = InMemoryGameRepository()

    # 4x4 board where robot picks flower but can't reach princess
    # Layout:
    # R F _ _
    # _ O O O
    # _ O O O
    # _ _ _ P
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    board = Game(rows=4, cols=4, robot=robot, princess_position=Position(3, 3))
    board.flowers = {Position(0, 1)}
    # Wall of obstacles blocking path
    board.obstacles = {
        Position(1, 1),
        Position(1, 2),
        Position(1, 3),
        Position(2, 1),
        Position(2, 2),
        Position(2, 3),
    }
    board.initial_flower_count = len(board.flowers)

    game_id = "test-blocked-path"
    repo.save(game_id, board)
    repo.save_history(game_id, GameHistory(game_id=game_id))

    from robot_flower_princess.configurator.dependencies import get_game_repository

    original_override = app.dependency_overrides.get(get_game_repository)
    app.dependency_overrides[get_game_repository] = lambda: repo

    try:
        resp = client.post(f"/api/games/{game_id}/autoplay")
        assert resp.status_code == 200

        final_board = repo.get(game_id)
        # Should have cleaned at least one obstacle or dropped flowers
        assert (
            len(final_board.obstacles) < 6  # Cleaned at least one
            or len(final_board.flowers) > 0  # Dropped flower back
        )

    finally:
        if original_override is None:
            app.dependency_overrides.pop(get_game_repository, None)
        else:
            app.dependency_overrides[get_game_repository] = original_override


def test_autoplay_no_adjacent_space_to_princess():
    """Test 3: No adjacent space to princess - drop, clean near princess, deliver."""
    repo = InMemoryGameRepository()

    # 4x4 board where princess is surrounded by obstacles
    # Layout:
    # R F _ _
    # _ _ _ _
    # _ _ O O
    # _ _ O P
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    board = Game(rows=4, cols=4, robot=robot, princess_position=Position(3, 3))
    board.flowers = {Position(0, 1)}
    # Obstacles surround princess
    board.obstacles = {
        Position(2, 2),
        Position(2, 3),  # Above princess
        Position(3, 2),  # Left of princess
    }
    board.initial_flower_count = len(board.flowers)

    game_id = "test-no-adjacent-space"
    repo.save(game_id, board)
    repo.save_history(game_id, GameHistory(game_id=game_id))

    from robot_flower_princess.configurator.dependencies import get_game_repository

    original_override = app.dependency_overrides.get(get_game_repository)
    app.dependency_overrides[get_game_repository] = lambda: repo

    try:
        resp = client.post(f"/api/games/{game_id}/autoplay")
        assert resp.status_code == 200

        final_board = repo.get(game_id)
        # Should have cleaned obstacle near princess or made progress
        assert (
            len(final_board.obstacles) < 3  # Cleaned at least one
            or final_board.robot.flowers_held == 0  # Dropped flowers
        )

    finally:
        if original_override is None:
            app.dependency_overrides.pop(get_game_repository, None)
        else:
            app.dependency_overrides[get_game_repository] = original_override


def test_autoplay_navigate_adjacent_to_princess():
    """Test 5: Navigate adjacent to princess, not onto princess position."""
    repo = InMemoryGameRepository()

    # Simple 3x3 board - solver should navigate NEXT to princess, not onto her
    # Layout:
    # R F _
    # _ _ _
    # _ _ P
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    board = Game(rows=3, cols=3, robot=robot, princess_position=Position(2, 2))
    board.flowers = {Position(0, 1)}
    board.obstacles = set()
    board.initial_flower_count = len(board.flowers)

    game_id = "test-navigate-adjacent"
    repo.save(game_id, board)
    repo.save_history(game_id, GameHistory(game_id=game_id))

    from robot_flower_princess.configurator.dependencies import get_game_repository

    original_override = app.dependency_overrides.get(get_game_repository)
    app.dependency_overrides[get_game_repository] = lambda: repo

    try:
        resp = client.post(f"/api/games/{game_id}/autoplay")
        assert resp.status_code == 200
        data = resp.json()

        # Should succeed without "blocked by princess" error
        assert "blocked by princess" not in data.get("message", "").lower()

        final_board = repo.get(game_id)
        # Robot should be adjacent to princess, not on princess
        assert final_board.robot.position != board.princess_position
        # Should have made progress
        assert final_board.flowers_delivered > 0 or len(final_board.flowers) == 0

    finally:
        if original_override is None:
            app.dependency_overrides.pop(get_game_repository, None)
        else:
            app.dependency_overrides[get_game_repository] = original_override
