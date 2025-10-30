"""Additional unit tests for AIGreedyPlayer helper methods to improve coverage."""

from hexagons.game.domain.core.entities.game import Game
from hexagons.game.domain.core.entities.position import Position
from hexagons.game.domain.core.value_objects.direction import Direction
from hexagons.aiplayer.domain.core.entities.ai_greedy_player import AIGreedyPlayer


def test_find_path_trivial_returns_empty():
    """_find_path should return empty path when start equals goal."""
    board = Game(rows=3, cols=3)
    start = Position(1, 1)
    goal = Position(1, 1)

    path = AIGreedyPlayer._find_path(board, start, goal)

    assert isinstance(path, list)
    assert path == []


def test_find_path_simple_straight_line():
    """_find_path should return a straight line path when corridor is clear."""
    game = Game(rows=3, cols=3)
    game.board.initial_flowers_count = 1
    # Clear board by default; ensure start/goal are empty
    start = Position(0, 0)
    goal = Position(2, 2)

    path = AIGreedyPlayer._find_path(game, start, goal)

    # Expect two steps to the east
    assert [p for p in path] == [Position(0, 1), Position(0, 2)]


def test_get_direction_between_adjacent_positions():
    """_get_direction should map adjacent positions to correct Direction."""
    a = Position(2, 2)

    assert AIGreedyPlayer._get_direction(a, Position(1, 2)) == Direction.NORTH
    assert AIGreedyPlayer._get_direction(a, Position(3, 2)) == Direction.SOUTH
    assert AIGreedyPlayer._get_direction(a, Position(2, 3)) == Direction.EAST
    assert AIGreedyPlayer._get_direction(a, Position(2, 1)) == Direction.WEST
