from fastapi.testclient import TestClient
from main import app
from hexagons.game.driven.persistence.in_memory_game_repository import (
    InMemoryGameRepository,
)
from hexagons.game.domain.core.entities.position import Position
from hexagons.game.domain.core.entities.robot import Robot
from hexagons.game.domain.core.entities.princess import Princess
from hexagons.game.domain.core.entities.game import Game
from hexagons.game.domain.core.value_objects.direction import Direction

client = TestClient(app)


def should_autoplay_successfully_with_clear_path():
    repo = InMemoryGameRepository()
    # create a small solvable board
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    board = Game(rows=2, cols=2, robot=robot, princess=Princess(position=Position(1, 1)))
    board.flowers = {Position(0, 1)}
    board.obstacles = set()
    board.board.initial_flowers_count = len(board.flowers)

    game_id = "component-autoplay"
    repo.save(game_id, board)

    # Temporarily override the app dependency to use our repo
    from configurator.dependencies import get_game_repository

    # Save any existing override and set our test override
    original_override = app.dependency_overrides.get(get_game_repository)
    app.dependency_overrides[get_game_repository] = lambda: repo

    try:
        resp = client.post(f"/api/games/{game_id}/autoplay")
        assert resp.status_code == 200
        data = resp.json()
        print(f"should_autoplay_successfully_with_clear_path Data: {data}")
        assert "success" in data["message"] or "board" in data
        assert len(data["game"]["robot"]["executed_actions"]) >= 10
        assert data["game"]["status"] == "victory"

    finally:
        # restore original override
        if original_override is None:
            app.dependency_overrides.pop(get_game_repository, None)
        else:
            app.dependency_overrides[get_game_repository] = original_override


def should_autoplay_successfully_with_obstacles():
    """Test autoplay can solve a game with obstacles - may not complete but should make progress."""
    repo = InMemoryGameRepository()

    # Create a simple 3x3 board where robot can access everything
    # Layout:
    # R F _
    # _ O _
    # _ _ P
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    board = Game(rows=3, cols=3, robot=robot, princess=Princess(position=Position(2, 2)))
    board.flowers = {Position(0, 1)}
    board.obstacles = {Position(1, 1)}  # One obstacle in the middle
    board.board.initial_flowers_count = len(board.flowers)

    game_id = "component-autoplay-with-obstacles"
    repo.save(game_id, board)

    # Temporarily override the app dependency to use our repo
    from configurator.dependencies import get_game_repository

    original_override = app.dependency_overrides.get(get_game_repository)
    app.dependency_overrides[get_game_repository] = lambda: repo

    try:
        resp = client.post(f"/api/games/{game_id}/autoplay")
        assert resp.status_code == 200
        data = resp.json()

        # Autoplay should successfully attempt to solve
        assert resp.status_code == 200
        data = resp.json()
        print(f"should_autoplay_successfully_with_obstacles Data: {data}")
        assert "success" in data["message"] or "board" in data
        assert len(data["game"]["robot"]["executed_actions"]) >= 10
        assert data["game"]["status"] == "victory"

    finally:
        # restore original override
        if original_override is None:
            app.dependency_overrides.pop(get_game_repository, None)
        else:
            app.dependency_overrides[get_game_repository] = original_override


def should_autoplay_successfully_with_multiple_flowers_and_obstacles():
    """Test autoplay can handle multiple flowers and clean obstacles."""
    repo = InMemoryGameRepository()

    # Create a simple 4x4 board with 2 flowers and some obstacles
    # Layout:
    # R F _ _
    # _ _ _ _
    # _ O _ F
    # _ _ _ P
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    board = Game(rows=4, cols=4, robot=robot, princess=Princess(position=Position(3, 3)))
    board.flowers = {
        Position(0, 1),  # Next to robot
        Position(2, 3),  # Near princess
    }
    board.obstacles = {Position(2, 1)}  # One obstacle
    board.board.initial_flowers_count = len(board.flowers)

    game_id = "component-autoplay-with-multiple-flowers-and-obstacles"
    repo.save(game_id, board)

    # Temporarily override the app dependency to use our repo
    from configurator.dependencies import get_game_repository

    original_override = app.dependency_overrides.get(get_game_repository)
    app.dependency_overrides[get_game_repository] = lambda: repo

    try:
        resp = client.post(f"/api/games/{game_id}/autoplay")
        assert resp.status_code == 200

        # Should successfully complete or at least make progress
        data = resp.json()
        print(f"should_autoplay_successfully_with_multiple_flowers_and_obstacles Data: {data}")
        assert "success" in data["message"] or "board" in data
        assert len(data["game"]["robot"]["executed_actions"]) >= 10
        assert data["game"]["status"] == "victory"

        # Verify some progress was made

    finally:
        # restore original override
        if original_override is None:
            app.dependency_overrides.pop(get_game_repository, None)
        else:
            app.dependency_overrides[get_game_repository] = original_override


def should_autoplay_successfully_with_normal_delivery_clear_path():
    """Test 1: Normal delivery with clear path - navigate and deliver."""
    repo = InMemoryGameRepository()

    # Simple 3x3 board with clear path
    # Layout:
    # R F _
    # _ _ _
    # _ _ P
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    board = Game(rows=3, cols=3, robot=robot, princess=Princess(position=Position(2, 2)))
    board.flowers = {Position(0, 1)}
    board.obstacles = set()  # No obstacles
    board.board.initial_flowers_count = len(board.flowers)

    game_id = "component-autoplay-with-normal-delivery-clear-path"
    repo.save(game_id, board)

    from configurator.dependencies import get_game_repository

    original_override = app.dependency_overrides.get(get_game_repository)
    app.dependency_overrides[get_game_repository] = lambda: repo

    try:
        resp = client.post(f"/api/games/{game_id}/autoplay")
        assert resp.status_code == 200

        # Should successfully deliver flower
        data = resp.json()
        print(f"should_autoplay_successfully_with_normal_delivery_clear_path Data: {data}")
        assert "success" in data["message"] or "board" in data
        assert len(data["game"]["robot"]["flowers"]["delivered"]) >= 1
        assert len(data["game"]["robot"]["executed_actions"]) >= 10
        assert data["game"]["status"] == "victory"

    finally:
        if original_override is None:
            app.dependency_overrides.pop(get_game_repository, None)
        else:
            app.dependency_overrides[get_game_repository] = original_override


def should_autoplay_successfully_with_blocked_path_drop_and_clean():
    """Test 2: Blocked path with flowers - drop, clean, pick up, deliver."""
    repo = InMemoryGameRepository()

    # 4x4 board where robot picks flower but can't reach princess
    # Layout:
    # R F _ _
    # _ O O O
    # _ O O O
    # _ _ _ P
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    board = Game(rows=4, cols=4, robot=robot, princess=Princess(position=Position(3, 3)))
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
    board.board.initial_flowers_count = len(board.flowers)

    game_id = "component-autoplay-with-blocked-path-drop-and-clean"
    repo.save(game_id, board)

    from configurator.dependencies import get_game_repository

    original_override = app.dependency_overrides.get(get_game_repository)
    app.dependency_overrides[get_game_repository] = lambda: repo

    try:
        resp = client.post(f"/api/games/{game_id}/autoplay")
        assert resp.status_code == 200
        data = resp.json()
        print(f"should_autoplay_successfully_with_blocked_path_drop_and_clean Data: {data}")
        assert "success" in data["message"] or "board" in data
        assert len(data["game"]["robot"]["executed_actions"]) >= 10
        assert data["game"]["status"] == "victory"

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


def should_autoplay_successfully_with_no_adjacent_space_to_princess():
    """Test 3: No adjacent space to princess - drop, clean near princess, deliver."""
    repo = InMemoryGameRepository()

    # 4x4 board where princess is surrounded by obstacles
    # Layout:
    # R F _ _
    # _ _ _ _
    # _ _ O O
    # _ _ O P
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    board = Game(rows=4, cols=4, robot=robot, princess=Princess(position=Position(3, 3)))
    board.flowers = {Position(0, 1)}
    # Obstacles surround princess
    board.obstacles = {
        Position(2, 2),
        Position(2, 3),  # Above princess
        Position(3, 2),  # Left of princess
    }
    board.board.initial_flowers_count = len(board.flowers)

    game_id = "component-autoplay-with-no-adjacent-space-to-princess"
    repo.save(game_id, board)

    from configurator.dependencies import get_game_repository

    original_override = app.dependency_overrides.get(get_game_repository)
    app.dependency_overrides[get_game_repository] = lambda: repo

    try:
        resp = client.post(f"/api/games/{game_id}/autoplay")
        assert resp.status_code == 200

        data = resp.json()
        print(f"should_autoplay_successfully_with_no_adjacent_space_to_princess Data: {data}")
        assert "success" in data["message"] or "board" in data
        assert len(data["game"]["robot"]["executed_actions"]) >= 10
        assert data["game"]["status"] == "victory"

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


def should_autoplay_successfully_with_navigate_adjacent_to_princess():
    """Test 5: Navigate adjacent to princess, not onto princess position."""
    repo = InMemoryGameRepository()

    # Simple 3x3 board - solver should navigate NEXT to princess, not onto her
    # Layout:
    # R F _
    # _ _ _
    # _ _ P
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    board = Game(rows=3, cols=3, robot=robot, princess=Princess(position=Position(2, 2)))
    board.flowers = {Position(0, 1)}
    board.obstacles = set()
    board.board.initial_flowers_count = len(board.flowers)

    game_id = "component-autoplay-with-navigate-adjacent-to-princess"
    repo.save(game_id, board)

    from configurator.dependencies import get_game_repository

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
        assert final_board.robot.position != board.princess.position
        # Should have made progress
        data = resp.json()
        print(f"should_autoplay_successfully_with_navigate_adjacent_to_princess Data: {data}")
        assert "success" in data["message"] or "board" in data
        assert len(data["game"]["robot"]["executed_actions"]) >= 10
        assert data["game"]["status"] == "victory"

    finally:
        if original_override is None:
            app.dependency_overrides.pop(get_game_repository, None)
        else:
            app.dependency_overrides[get_game_repository] = original_override


def should_autoplay_successfully_with_blocked_path():
    """
    Test autoplay when robot has obstacles in direct path to flower.

    Scenario:
    - Robot at (1,0) facing EAST
    - Flower at (1,2)
    - Obstacle blocking direct path at (1,1)
    - Princess at (2,2)

    Layout (3x3):
    _ _ _
    R O F
    _ _ P

    Expected:
    - AI attempts to solve the board (may clean obstacle or go around)
    - Response is successful (200 status)
    """
    repo = InMemoryGameRepository()

    robot = Robot(position=Position(1, 0), orientation=Direction.EAST)
    board = Game(rows=3, cols=3, robot=robot, princess=Princess(position=Position(2, 2)))
    board.flowers = {Position(1, 2)}
    board.obstacles = {Position(1, 1)}  # Blocking direct path to flower
    board.board.initial_flowers_count = len(board.flowers)

    game_id = "component-autoplay-blocked-path"
    repo.save(game_id, board)

    from configurator.dependencies import get_game_repository

    original_override = app.dependency_overrides.get(get_game_repository)
    app.dependency_overrides[get_game_repository] = lambda: repo

    try:
        resp = client.post(f"/api/games/{game_id}/autoplay")
        assert resp.status_code == 200

        data = resp.json()
        print(f"should_autoplay_successfully_with_blocked_path Data: {data}")
        assert "success" in data["message"] or "board" in data
        assert len(data["game"]["robot"]["executed_actions"]) >= 10
        assert data["game"]["status"] == "victory"

    finally:
        if original_override is None:
            app.dependency_overrides.pop(get_game_repository, None)
        else:
            app.dependency_overrides[get_game_repository] = original_override


# =====================================================
# AIOptimalPlayer Tests (strategy="optimal")
# =====================================================


def should_autoplay_successfully_with_optimal_strategy():
    """Test AIOptimalPlayer with simple solvable board."""
    repo = InMemoryGameRepository()
    # create a small solvable board
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    board = Game(rows=2, cols=2, robot=robot, princess=Princess(position=Position(1, 1)))
    board.flowers = {Position(0, 1)}
    board.obstacles = set()
    board.board.initial_flowers_count = len(board.flowers)

    game_id = "component-autoplay-with-optimal-strategy"
    repo.save(game_id, board)

    from configurator.dependencies import get_game_repository

    original_override = app.dependency_overrides.get(get_game_repository)
    app.dependency_overrides[get_game_repository] = lambda: repo

    try:
        resp = client.post(f"/api/games/{game_id}/autoplay?strategy=optimal")
        assert resp.status_code == 200
        data = resp.json()
        print(f"should_autoplay_successfully_with_optimal_strategy Data: {data}")
        assert "success" in data["message"] or "board" in data
    finally:
        if original_override is None:
            app.dependency_overrides.pop(get_game_repository, None)
        else:
            app.dependency_overrides[get_game_repository] = original_override


def should_autoplay_successfully_with_optimal_strategy_and_obstacles():
    """Test AIOptimalPlayer can solve a game with obstacles."""
    repo = InMemoryGameRepository()

    # Create a simple 3x3 board where robot can access everything
    # Layout:
    # R F _
    # _ O _
    # _ _ P
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    board = Game(rows=3, cols=3, robot=robot, princess=Princess(position=Position(2, 2)))
    board.flowers = {Position(0, 1)}
    board.obstacles = {Position(1, 1)}  # One obstacle in the middle
    board.board.initial_flowers_count = len(board.flowers)

    game_id = "component-autoplay-with-optimal-strategy-and-obstacles"
    repo.save(game_id, board)

    from configurator.dependencies import get_game_repository

    original_override = app.dependency_overrides.get(get_game_repository)
    app.dependency_overrides[get_game_repository] = lambda: repo

    try:
        resp = client.post(f"/api/games/{game_id}/autoplay?strategy=optimal")
        assert resp.status_code == 200
        data = resp.json()

        # Verify the endpoint works with optimal strategy
        data = resp.json()
        print(f"should_autoplay_successfully_with_optimal_strategy_and_obstacles Data: {data}")
        assert "success" in data["message"] or "board" in data
        assert len(data["game"]["robot"]["executed_actions"]) >= 10
        assert data["game"]["status"] == "victory"

    finally:
        if original_override is None:
            app.dependency_overrides.pop(get_game_repository, None)
        else:
            app.dependency_overrides[get_game_repository] = original_override


def should_autoplay_successfully_with_optimal_strategy_and_multiple_flowers():
    """Test AIOptimalPlayer can handle multiple flowers and plan efficiently."""
    repo = InMemoryGameRepository()

    # Create a simple 4x4 board with 2 flowers
    # Layout:
    # R F _ _
    # _ _ _ _
    # _ O _ F
    # _ _ _ P
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    board = Game(rows=4, cols=4, robot=robot, princess=Princess(position=Position(3, 3)))
    board.flowers = {
        Position(0, 1),  # Next to robot
        Position(2, 3),  # Near princess
    }
    board.obstacles = {Position(2, 1)}  # One obstacle
    board.board.initial_flowers_count = len(board.flowers)

    game_id = "component-autoplay-with-optimal-strategy-and-multiple-flowers"
    repo.save(game_id, board)

    from configurator.dependencies import get_game_repository

    original_override = app.dependency_overrides.get(get_game_repository)
    app.dependency_overrides[get_game_repository] = lambda: repo

    try:
        resp = client.post(f"/api/games/{game_id}/autoplay?strategy=optimal")
        assert resp.status_code == 200

        # Verify the endpoint works with optimal strategy
        data = resp.json()
        print(f"should_autoplay_successfully_with_optimal_strategy_and_multiple_flowers Data: {data}")
        assert "success" in data["message"] or "board" in data
        assert len(data["game"]["robot"]["executed_actions"]) >= 10
        assert data["game"]["status"] == "victory"

    finally:
        if original_override is None:
            app.dependency_overrides.pop(get_game_repository, None)
        else:
            app.dependency_overrides[get_game_repository] = original_override


def should_autoplay_successfully_with_optimal_strategy_and_clear_path():
    """Test AIOptimalPlayer with clear path - should be efficient."""
    repo = InMemoryGameRepository()

    # Simple 3x3 board with clear path
    # Layout:
    # R F _
    # _ _ _
    # _ _ P
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    board = Game(rows=3, cols=3, robot=robot, princess=Princess(position=Position(2, 2)))
    board.flowers = {Position(0, 1)}
    board.obstacles = set()  # No obstacles
    board.board.initial_flowers_count = len(board.flowers)

    game_id = "component-autoplay-with-optimal-strategy-and-clear-path"
    repo.save(game_id, board)

    from configurator.dependencies import get_game_repository

    original_override = app.dependency_overrides.get(get_game_repository)
    app.dependency_overrides[get_game_repository] = lambda: repo

    try:
        resp = client.post(f"/api/games/{game_id}/autoplay?strategy=optimal")
        assert resp.status_code == 200

        # Optimal should use fewer actions (more efficient)
        # This is a simple board, so action count should be reasonable
        data = resp.json()
        print(f"should_autoplay_successfully_with_optimal_strategy_and_clear_path Data: {data}")
        assert "success" in data["message"] or "board" in data
        assert len(data["game"]["robot"]["executed_actions"]) >= 10
        assert data["game"]["status"] == "victory"

    finally:
        if original_override is None:
            app.dependency_overrides.pop(get_game_repository, None)
        else:
            app.dependency_overrides[get_game_repository] = original_override


def should_autoplay_successfully_with_optimal_strategy_and_complex_obstacle_pattern():
    """Test AIOptimalPlayer with complex obstacle pattern requiring smart navigation."""
    repo = InMemoryGameRepository()

    # 4x4 board where robot needs to navigate around obstacles
    # Layout:
    # R F _ _
    # _ O O O
    # _ O _ _
    # _ _ _ P
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    board = Game(rows=4, cols=4, robot=robot, princess=Princess(position=Position(3, 3)))
    board.flowers = {Position(0, 1)}
    board.obstacles = {
        Position(1, 1),
        Position(1, 2),
        Position(1, 3),
        Position(2, 1),
    }
    board.board.initial_flowers_count = len(board.flowers)

    game_id = "component-autoplay-with-optimal-strategy-and-complex-obstacle-pattern"
    repo.save(game_id, board)

    from configurator.dependencies import get_game_repository

    original_override = app.dependency_overrides.get(get_game_repository)
    app.dependency_overrides[get_game_repository] = lambda: repo

    try:
        resp = client.post(f"/api/games/{game_id}/autoplay?strategy=optimal")
        assert resp.status_code == 200

        # Verify the endpoint works with optimal strategy
        data = resp.json()
        print(f"should_autoplay_successfully_with_optimal_strategy_and_complex_obstacle_pattern Data: {data}")
        assert "success" in data["message"] or "board" in data

    finally:
        if original_override is None:
            app.dependency_overrides.pop(get_game_repository, None)
        else:
            app.dependency_overrides[get_game_repository] = original_override
