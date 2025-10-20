import pytest
from typing import Callable
from fastapi.testclient import TestClient

from robot_flower_princess.main import app
from robot_flower_princess.domain.entities.board import Board
from robot_flower_princess.domain.entities.position import Position
from robot_flower_princess.domain.entities.robot import Robot
from robot_flower_princess.domain.entities.game_history import GameHistory
from robot_flower_princess.domain.value_objects.direction import Direction
from robot_flower_princess.infrastructure.api.dependencies import get_game_repository
from robot_flower_princess.infrastructure.persistence.in_memory_game_repository import InMemoryGameRepository


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
        return resp.json()["id"], resp.json()["board"]

    return _create


@pytest.fixture
def save_board(repo):
    def _save(game_id, board):
        repo.save(game_id, board)
        history = GameHistory()
        history.add_action(action=None, board_state=board.to_dict())
        repo.save_history(game_id, history)

    return _save


@pytest.fixture
def make_empty_board():
    from robot_flower_princess.domain.entities.board import Board
    from robot_flower_princess.domain.entities.position import Position
    from robot_flower_princess.domain.entities.robot import Robot
    from robot_flower_princess.domain.value_objects.direction import Direction

    def _make(rows=3, cols=3):
        robot_pos = Position(1, 1)
        robot = Robot(position=robot_pos, orientation=Direction.NORTH)
        board = Board(rows=rows, cols=cols, robot=robot, princess_position=Position(2, 2))
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
        return resp.json()["id"]

    return _seed


@pytest.fixture
def seeded_board(save_board, make_empty_board):
    """Create and save a deterministic empty board in the repo and return its id and board.

    Returns:
        (str, Board): tuple of game_id and board object
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
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    princess_pos = Position(2, 2)
    flowers = {Position(1, 1)}
    obstacles = {Position(0, 1)}

    board = Board(
        rows=3,
        cols=3,
        robot=robot,
        princess_position=princess_pos,
        flowers=flowers,
        obstacles=obstacles,
    )
    board.initial_flower_count = len(flowers)
    return board


@pytest.fixture
def place_flower():
    def _place(board: Board, pos: Position):
        board.flowers.add(pos)
        board.initial_flower_count = len(board.flowers)
        return board

    return _place


@pytest.fixture
def place_obstacle():
    def _place(board: Board, pos: Position):
        board.obstacles.add(pos)
        return board

    return _place


@pytest.fixture
def place_robot():
    def _place(board: Board, pos: Position, orientation: Direction = Direction.NORTH):
        board.robot.position = pos
        board.robot.orientation = orientation
        return board

    return _place
