import pytest
from typing import Any, Callable
from fastapi.testclient import TestClient

from main import app
from hexagons.game.domain.core.entities.game import Game
from hexagons.game.domain.core.entities.position import Position
from hexagons.game.domain.core.value_objects.direction import Direction
from configurator.dependencies import get_game_repository
from hexagons.game.driven.persistence.in_memory_game_repository import (
    InMemoryGameRepository,
)
from hexagons.game.domain.ports.ml_autoplay_data_collector import MLAutoplayDataCollectorPort


@pytest.fixture(scope="session")
def client() -> TestClient:
    """A TestClient instance for the FastAPI app (session-scoped).

    Returns:
        TestClient: a test client instance bound to the application
    """
    return TestClient(app)


@pytest.fixture
def repo():
    """Return the in-memory game repository used by the app.

    Returns:
        InMemoryGameRepository: the application's repository instance
    """
    return get_game_repository()


@pytest.fixture
def create_game(client):
    def _create(rows=5, cols=5):
        resp = client.post("/api/games/", json={"rows": rows, "cols": cols})
        assert resp.status_code == 201
        data = resp.json()
        game = data["game"]
        return game["id"]

    return _create


@pytest.fixture
def save_board(repo):
    def _save(game_id, board):
        repo.save(game_id, board)

    return _save


@pytest.fixture
def make_empty_board():
    from hexagons.game.domain.core.entities.game import Game
    from hexagons.game.domain.core.entities.position import Position
    from hexagons.game.domain.core.value_objects.direction import Direction

    def _make(rows=3, cols=3):
        board = Game(rows=rows, cols=cols)
        # Override default positions and clear random flowers/obstacles for testing
        board.robot.position = Position(1, 1)
        board.robot.orientation = Direction.NORTH
        board.princess.position = Position(2, 2)
        board.flowers = set()
        board.obstacles = set()
        return board

    return _make


@pytest.fixture
def seeded_game(client) -> Callable[..., str]:
    """Create a new game via the API and return its game_id.

    Returns:
        str: game id created via POST /api/games/
    """

    def _seed(rows: int = 5, cols: int = 5) -> str:
        resp = client.post("/api/games/", json={"rows": rows, "cols": cols})
        assert resp.status_code == 201
        return resp.json()["game"]["id"]

    return _seed


@pytest.fixture
def seeded_board(save_board, make_empty_board):
    """Create and save a deterministic empty board in the repo and return its id and board.

    Returns:
        (str, Game): tuple of game_id and board object
    """

    def _seed(game_id: str = "seeded-board", rows: int = 3, cols: int = 3):
        board = make_empty_board(rows, cols)
        save_board(game_id, board)
        return game_id, board

    return _seed


@pytest.fixture
def game_repository():
    """Fixture for game repository."""
    return InMemoryGameRepository()


@pytest.fixture
def sample_board():
    """Fixture for a simple test board."""
    flowers = {Position(1, 1)}
    obstacles = {Position(0, 1)}

    board = Game(rows=3, cols=3)
    # Override default positions
    board.robot.position = Position(0, 0)
    board.robot.orientation = Direction.EAST
    board.princess.position = Position(2, 2)
    # Set specific flowers and obstacles for testing
    board.flowers = flowers
    board.obstacles = obstacles
    return board


@pytest.fixture
def place_flower():
    def _place(board: Game, pos: Position):
        board.flowers.add(pos)
        board.initial_flower_count = len(board.flowers)
        return board

    return _place


@pytest.fixture
def place_obstacle():
    def _place(board: Game, pos: Position):
        board.obstacles.add(pos)
        return board

    return _place


@pytest.fixture
def place_robot():
    def _place(board: Game, pos: Position, orientation: Direction = Direction.NORTH):
        board.robot.position = pos
        board.robot.orientation = orientation
        return board

    return _place


@pytest.fixture
def data_collector():
    return NullMLAutoplayDataCollector()


class NullMLAutoplayDataCollector(MLAutoplayDataCollectorPort):
    """No-op implementation used for tests or when collection is disabled."""

    def collect_action(
        self,
        game_id: str,
        game_state: dict[str, Any],
        action: str,
        direction: str | None,
        outcome: dict[str, Any],
    ) -> None:
        return
