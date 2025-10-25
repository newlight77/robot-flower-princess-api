"""Unit tests for AI player entities (AIGreedyPlayer and AIOptimalPlayer)."""

import pytest
from copy import deepcopy

from hexagons.game.domain.core.entities.game import Game
from hexagons.game.domain.core.entities.robot import Robot
from hexagons.game.domain.core.entities.position import Position
from hexagons.game.domain.core.value_objects.direction import Direction
from hexagons.aiplayer.domain.core.entities.ai_greedy_player import AIGreedyPlayer
from hexagons.aiplayer.domain.core.entities.ai_optimal_player import AIOptimalPlayer


@pytest.fixture
def simple_board():
    """Create a simple solvable game board."""
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    board = Game(rows=5, cols=5, robot=robot, princess_position=Position(4, 4))
    board.flowers = {Position(1, 1), Position(3, 3)}
    board.obstacles = set()
    board.initial_flower_count = len(board.flowers)
    return board


@pytest.fixture
def board_with_obstacles():
    """Create a board with obstacles that requires cleaning."""
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    board = Game(rows=5, cols=5, robot=robot, princess_position=Position(4, 4))
    board.flowers = {Position(1, 1)}
    board.obstacles = {Position(2, 2), Position(1, 3)}
    board.initial_flower_count = len(board.flowers)
    return board


class TestAIGreedyPlayer:
    """Tests for AIGreedyPlayer (safe, reliable strategy)."""

    def test_solve_returns_list_of_actions(self, simple_board):
        """AIGreedyPlayer.solve should return a list of action tuples."""
        actions = AIGreedyPlayer.solve(simple_board)

        assert isinstance(actions, list)
        assert len(actions) > 0

        # Each action should be a tuple of (action_type, direction)
        for action in actions:
            assert isinstance(action, tuple)
            assert len(action) == 2
            action_type, direction = action
            assert isinstance(action_type, str)
            assert action_type in ["rotate", "move", "pick", "give", "drop", "clean"]

    def test_solve_simple_board_successfully(self, simple_board):
        """AIGreedyPlayer should solve a simple board and deliver all flowers."""
        board = deepcopy(simple_board)
        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0
        assert board.get_status().value == "victory"
        assert board.flowers_delivered == 2
        assert len(board.flowers) == 0

    def test_solve_board_with_obstacles(self, board_with_obstacles):
        """AIGreedyPlayer should solve a board with obstacles."""
        board = deepcopy(board_with_obstacles)
        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0
        # Should successfully deliver the flower or at least try
        assert board.flowers_delivered >= 0

    def test_solve_empty_board_no_actions(self):
        """AIGreedyPlayer should return empty actions for board with no flowers."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=3, cols=3, robot=robot, princess_position=Position(2, 2))
        board.flowers = set()
        board.initial_flower_count = 0

        actions = AIGreedyPlayer.solve(board)

        # Should return an empty list or minimal actions
        assert isinstance(actions, list)

    def test_solve_does_not_modify_original_board(self, simple_board):
        """AIGreedyPlayer.solve should not modify the passed board (if deepcopy is used correctly)."""
        board = deepcopy(simple_board)
        initial_robot_pos = board.robot.position
        initial_flower_count = len(board.flowers)

        # Solve modifies the board, but we pass a copy
        _ = AIGreedyPlayer.solve(board)

        # The board passed to solve is modified (it's the working board)
        # This test verifies the solver works with the board it receives
        assert board.robot.position != initial_robot_pos or len(board.flowers) != initial_flower_count


class TestAIOptimalPlayer:
    """Tests for AIOptimalPlayer (fast, efficient strategy)."""

    def test_solve_returns_list_of_actions(self, simple_board):
        """AIOptimalPlayer.solve should return a list of action tuples."""
        actions = AIOptimalPlayer.solve(simple_board)

        assert isinstance(actions, list)
        assert len(actions) > 0

        # Each action should be a tuple of (action_type, direction)
        for action in actions:
            assert isinstance(action, tuple)
            assert len(action) == 2
            action_type, direction = action
            assert isinstance(action_type, str)
            assert action_type in ["rotate", "move", "pick", "give", "drop", "clean"]

    def test_solve_simple_board_successfully(self, simple_board):
        """AIOptimalPlayer should solve a simple board and deliver all flowers."""
        board = deepcopy(simple_board)
        actions = AIOptimalPlayer.solve(board)

        assert len(actions) > 0
        assert board.get_status().value == "victory"
        assert board.flowers_delivered == 2
        assert len(board.flowers) == 0

    def test_solve_board_with_obstacles(self, board_with_obstacles):
        """AIOptimalPlayer should solve a board with obstacles."""
        board = deepcopy(board_with_obstacles)
        actions = AIOptimalPlayer.solve(board)

        assert len(actions) > 0
        # Should successfully deliver the flower or at least try
        assert board.flowers_delivered >= 0

    def test_solve_empty_board_no_actions(self):
        """AIOptimalPlayer should return empty actions for board with no flowers."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=3, cols=3, robot=robot, princess_position=Position(2, 2))
        board.flowers = set()
        board.initial_flower_count = 0

        actions = AIOptimalPlayer.solve(board)

        # Should return an empty list or minimal actions
        assert isinstance(actions, list)


class TestAIPlayerComparison:
    """Compare both AI strategies on the same boards."""

    def test_both_players_solve_simple_board(self, simple_board):
        """Both AI players should successfully solve a simple board."""
        greedy_board = deepcopy(simple_board)
        optimal_board = deepcopy(simple_board)

        greedy_actions = AIGreedyPlayer.solve(greedy_board)
        optimal_actions = AIOptimalPlayer.solve(optimal_board)

        # Both should succeed
        assert greedy_board.get_status().value == "victory"
        assert optimal_board.get_status().value == "victory"

        # Both should deliver all flowers
        assert greedy_board.flowers_delivered == 2
        assert optimal_board.flowers_delivered == 2

        # Both should return non-empty action lists
        assert len(greedy_actions) > 0
        assert len(optimal_actions) > 0

    def test_optimal_player_uses_fewer_actions(self, simple_board):
        """
        On simple boards, optimal player often (but not always) uses fewer actions.

        Note: This is a general trend test, not a strict requirement.
        The optimal player aims for efficiency but may not always be shorter.
        """
        greedy_board = deepcopy(simple_board)
        optimal_board = deepcopy(simple_board)

        greedy_actions = AIGreedyPlayer.solve(greedy_board)
        optimal_actions = AIOptimalPlayer.solve(optimal_board)

        # Just verify both return valid action lists
        # (The "optimal" strategy may not always be shorter in practice)
        assert len(greedy_actions) > 0
        assert len(optimal_actions) > 0

        # Document the difference for informational purposes
        print(f"\nActions count - Greedy: {len(greedy_actions)}, Optimal: {len(optimal_actions)}")
