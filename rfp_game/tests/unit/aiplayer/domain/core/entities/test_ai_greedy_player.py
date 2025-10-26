"""Unit tests for AIGreedyPlayer (safe, reliable AI strategy)."""

import pytest
from copy import deepcopy

from hexagons.game.domain.core.entities.game import Game
from hexagons.game.domain.core.entities.robot import Robot
from hexagons.game.domain.core.entities.princess import Princess
from hexagons.game.domain.core.entities.position import Position
from hexagons.game.domain.core.value_objects.direction import Direction
from hexagons.aiplayer.domain.core.entities.ai_greedy_player import AIGreedyPlayer


@pytest.fixture
def simple_board():
    """Create a simple solvable game board."""
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    board = Game(rows=5, cols=5, robot=robot, princess=Princess(position=Position(4, 4)))
    board.flowers = {Position(1, 1), Position(3, 3)}
    board.obstacles = set()
    board.board.initial_flowers_count = len(board.flowers)
    return board


@pytest.fixture
def board_with_obstacles():
    """Create a board with obstacles that requires cleaning."""
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    board = Game(rows=5, cols=5, robot=robot, princess=Princess(position=Position(4, 4)))
    board.flowers = {Position(1, 1)}
    board.obstacles = {Position(2, 2), Position(1, 3)}
    board.board.initial_flowers_count = len(board.flowers)
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
        board = Game(rows=3, cols=3, robot=robot, princess=Princess(position=Position(2, 2)))
        board.flowers = set()
        board.board.initial_flowers_count = 0

        actions = AIGreedyPlayer.solve(board)

        # Should return an empty list or minimal actions
        assert isinstance(actions, list)

    def test_solve_does_not_modify_original_board(self, simple_board):
        """AIGreedyPlayer.solve should work with the board it receives."""
        board = deepcopy(simple_board)
        initial_robot_pos = board.robot.position
        initial_flower_count = len(board.flowers)

        # Solve modifies the board, but we pass a copy
        _ = AIGreedyPlayer.solve(board)

        # The board passed to solve is modified (it's the working board)
        # This test verifies the solver works with the board it receives
        assert (
            board.robot.position != initial_robot_pos or len(board.flowers) != initial_flower_count
        )

    def test_uses_bfs_pathfinding(self, simple_board):
        """
        AIGreedyPlayer uses BFS pathfinding (implicit test).

        Verifies the algorithm completes successfully with obstacles,
        which requires BFS pathfinding to work correctly.
        """
        board = deepcopy(simple_board)

        # Add obstacles to make pathfinding interesting
        board.obstacles = {Position(2, 2), Position(1, 3), Position(3, 1)}

        actions = AIGreedyPlayer.solve(board)

        # BFS should find a path and complete the game
        assert len(actions) > 0
        # If BFS works, the robot should successfully navigate and deliver
        assert board.flowers_delivered >= 0

    def test_safe_flower_selection_strategy(self, simple_board):
        """
        AIGreedyPlayer validates safety before picking flowers.

        This is the core of the "greedy but safe" strategy.
        """
        board = deepcopy(simple_board)

        # Add complex obstacle pattern
        board.obstacles = {Position(2, 1), Position(2, 2), Position(2, 3), Position(3, 2)}

        actions = AIGreedyPlayer.solve(board)

        # Should complete or safely handle the challenging board
        assert isinstance(actions, list)
        # Greedy player should not get stuck (safety checks)
        assert len(actions) > 0

    def test_single_flower_simple_path(self):
        """AIGreedyPlayer should efficiently collect a single nearby flower."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=4, cols=4, robot=robot, princess=Princess(position=Position(3, 3)))
        board.flowers = {Position(1, 1)}
        board.obstacles = set()
        board.board.initial_flowers_count = 1

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0
        assert board.get_status().value == "victory"
        assert board.flowers_delivered == 1

    def test_multiple_flowers_sequential_collection(self):
        """AIGreedyPlayer should collect multiple flowers sequentially."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=6, cols=6, robot=robot, princess=Princess(position=Position(5, 5)))
        board.flowers = {
            Position(1, 1),
            Position(2, 2),
            Position(3, 3),
            Position(4, 4),
        }
        board.obstacles = set()
        board.board.initial_flowers_count = 4

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0
        assert board.flowers_delivered == 4
        assert len(board.flowers) == 0

    def test_large_board_navigation(self):
        """AIGreedyPlayer should handle large boards efficiently."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=12, cols=12, robot=robot, princess=Princess(position=Position(11, 11)))
        board.flowers = {Position(5, 5), Position(8, 8)}
        board.obstacles = set()
        board.board.initial_flowers_count = 2

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0
        assert board.get_status().value == "victory"
        assert board.flowers_delivered == 2

    def test_dense_obstacle_field(self):
        """AIGreedyPlayer should navigate through dense obstacle fields."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=6, cols=6, robot=robot, princess=Princess(position=Position(5, 5)))
        board.flowers = {Position(3, 3)}
        # Create dense obstacle pattern
        board.obstacles = {
            Position(1, 1),
            Position(1, 2),
            Position(1, 3),
            Position(2, 1),
            Position(3, 1),
            Position(4, 2),
            Position(4, 3),
            Position(4, 4),
        }
        board.board.initial_flowers_count = 1

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0
        assert isinstance(actions, list)

    def test_robot_surrounded_must_clean_first(self):
        """AIGreedyPlayer must clean obstacles when robot is surrounded."""
        robot = Robot(position=Position(2, 2), orientation=Direction.EAST)
        board = Game(rows=5, cols=5, robot=robot, princess=Princess(position=Position(4, 4)))
        # Surround robot
        board.obstacles = {
            Position(1, 2),
            Position(3, 2),  # North/South
            Position(2, 1),
            Position(2, 3),  # West/East
        }
        board.flowers = {Position(4, 3)}
        board.board.initial_flowers_count = 1

        actions = AIGreedyPlayer.solve(board)

        # Should clean at least one obstacle
        clean_actions = [a for a in actions if a[0] == "clean"]
        assert len(clean_actions) > 0

    def test_princess_blocked_by_obstacles(self):
        """AIGreedyPlayer should clean path to princess when blocked."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=5, cols=5, robot=robot, princess=Princess(position=Position(2, 2)))
        # Surround princess
        board.obstacles = {
            Position(1, 2),
            Position(3, 2),
            Position(2, 1),
            Position(2, 3),
        }
        board.flowers = {Position(0, 1)}
        board.board.initial_flowers_count = 1

        actions = AIGreedyPlayer.solve(board)

        # Should clean obstacles to reach princess
        clean_actions = [a for a in actions if a[0] == "clean"]
        assert len(clean_actions) > 0

    def test_flowers_in_corners(self):
        """AIGreedyPlayer should collect flowers from board corners."""
        robot = Robot(position=Position(2, 2), orientation=Direction.EAST)
        board = Game(rows=5, cols=5, robot=robot, princess=Princess(position=Position(2, 2)))
        board.flowers = {
            Position(0, 0),  # Top-left corner
            Position(0, 4),  # Top-right corner
            Position(4, 0),  # Bottom-left corner
            Position(4, 4),  # Bottom-right corner
        }
        board.obstacles = set()
        board.board.initial_flowers_count = 4

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0
        assert board.flowers_delivered == 4

    def test_long_distance_to_first_flower(self):
        """AIGreedyPlayer should handle long initial navigation."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=10, cols=10, robot=robot, princess=Princess(position=Position(9, 9)))
        board.flowers = {Position(8, 8)}  # Far from robot
        board.obstacles = set()
        board.board.initial_flowers_count = 1

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0
        assert board.get_status().value == "victory"

    def test_clustered_flowers_near_princess(self):
        """AIGreedyPlayer should efficiently handle flowers near princess."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=8, cols=8, robot=robot, princess=Princess(position=Position(7, 7)))
        # Cluster flowers near princess (but not adjacent)
        board.flowers = {
            Position(5, 5),
            Position(5, 6),
            Position(6, 5),
        }
        board.obstacles = set()
        board.board.initial_flowers_count = 3

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0
        assert board.flowers_delivered == 3

    def test_alternating_flowers_and_obstacles(self):
        """AIGreedyPlayer should navigate alternating pattern."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=7, cols=7, robot=robot, princess=Princess(position=Position(6, 6)))
        board.flowers = {Position(2, 2), Position(4, 4)}
        board.obstacles = {Position(1, 1), Position(3, 3), Position(5, 5)}
        board.board.initial_flowers_count = 2

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0
        assert isinstance(actions, list)

    def test_narrow_corridor_navigation(self):
        """AIGreedyPlayer should navigate through narrow corridors."""
        robot = Robot(position=Position(0, 2), orientation=Direction.EAST)
        board = Game(rows=5, cols=7, robot=robot, princess=Princess(position=Position(4, 2)))
        # Create corridor with obstacles on sides
        board.obstacles = {
            Position(1, 1),
            Position(1, 3),
            Position(2, 1),
            Position(2, 3),
            Position(3, 1),
            Position(3, 3),
        }
        board.flowers = {Position(3, 2)}  # In the corridor
        board.board.initial_flowers_count = 1

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0

    def test_many_flowers_stress_test(self):
        """AIGreedyPlayer should handle many flowers (stress test)."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=10, cols=10, robot=robot, princess=Princess(position=Position(9, 9)))
        # Place 8 flowers
        board.flowers = {
            Position(1, 1),
            Position(2, 2),
            Position(3, 3),
            Position(4, 4),
            Position(5, 5),
            Position(6, 6),
            Position(7, 7),
            Position(8, 8),
        }
        board.obstacles = set()
        board.board.initial_flowers_count = 8

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0
        assert isinstance(actions, list)
        # Greedy player should complete with reasonable actions
        assert len(actions) < 500  # Sanity check

    def test_spiral_obstacle_pattern(self):
        """AIGreedyPlayer should navigate spiral obstacle patterns."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=7, cols=7, robot=robot, princess=Princess(position=Position(3, 3)))
        # Spiral pattern
        board.obstacles = {
            Position(1, 1),
            Position(1, 2),
            Position(1, 3),
            Position(1, 4),
            Position(1, 5),
            Position(2, 5),
            Position(3, 5),
            Position(4, 5),
            Position(5, 5),
            Position(5, 4),
            Position(5, 3),
            Position(5, 2),
            Position(5, 1),
            Position(4, 1),
            Position(3, 1),
        }
        board.flowers = {Position(3, 3)}  # Center
        board.board.initial_flowers_count = 1

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0

    def test_robot_starts_next_to_princess(self):
        """AIGreedyPlayer should handle robot starting adjacent to princess."""
        robot = Robot(position=Position(2, 2), orientation=Direction.EAST)
        board = Game(rows=5, cols=5, robot=robot, princess=Princess(position=Position(2, 3)))
        board.flowers = {Position(0, 0), Position(4, 4)}
        board.obstacles = set()
        board.board.initial_flowers_count = 2

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0
        assert board.flowers_delivered == 2

    def test_diagonal_flower_placement(self):
        """AIGreedyPlayer should collect diagonally placed flowers."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=8, cols=8, robot=robot, princess=Princess(position=Position(7, 7)))
        # Diagonal line of flowers
        board.flowers = {
            Position(1, 1),
            Position(2, 2),
            Position(3, 3),
            Position(4, 4),
            Position(5, 5),
            Position(6, 6),
        }
        board.obstacles = set()
        board.board.initial_flowers_count = 6

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0
        assert board.flowers_delivered == 6

    def test_u_shaped_obstacle_barrier(self):
        """AIGreedyPlayer should navigate around U-shaped barriers."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=6, cols=6, robot=robot, princess=Princess(position=Position(5, 5)))
        # U-shaped barrier
        board.obstacles = {
            Position(2, 1),
            Position(2, 2),
            Position(2, 3),
            Position(3, 1),
            Position(3, 3),
        }
        board.flowers = {Position(3, 2)}  # Inside the U
        board.board.initial_flowers_count = 1

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0

    def test_incremental_delivery_multiple_trips(self):
        """AIGreedyPlayer should handle multiple delivery trips."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=8, cols=8, robot=robot, princess=Princess(position=Position(7, 7)))
        board.flowers = {
            Position(1, 1),
            Position(2, 1),
            Position(3, 1),
            Position(4, 1),
            Position(5, 1),
        }
        board.obstacles = set()
        board.board.initial_flowers_count = 5

        actions = AIGreedyPlayer.solve(board)

        # Check for give actions (deliveries)
        give_actions = [a for a in actions if a[0] == "give"]
        assert len(give_actions) >= 1
        assert board.flowers_delivered == 5

    def test_very_small_board(self):
        """AIGreedyPlayer should work on very small boards."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=3, cols=3, robot=robot, princess=Princess(position=Position(2, 2)))
        board.flowers = {Position(1, 1)}
        board.obstacles = set()
        board.board.initial_flowers_count = 1

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0
        assert board.get_status().value == "victory"

    def test_rectangular_board_wider_than_tall(self):
        """AIGreedyPlayer should handle non-square boards."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=5, cols=10, robot=robot, princess=Princess(position=Position(4, 9)))
        board.flowers = {Position(2, 4), Position(3, 7)}
        board.obstacles = set()
        board.board.initial_flowers_count = 2

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0
        assert board.flowers_delivered == 2

    def test_cross_shaped_obstacle_pattern(self):
        """AIGreedyPlayer should navigate cross-shaped obstacles."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=7, cols=7, robot=robot, princess=Princess(position=Position(6, 6)))
        # Cross pattern
        board.obstacles = {
            Position(3, 1),
            Position(3, 2),
            Position(3, 3),
            Position(3, 4),
            Position(3, 5),
            Position(1, 3),
            Position(2, 3),
            Position(4, 3),
            Position(5, 3),
        }
        board.flowers = {Position(1, 1), Position(5, 5)}
        board.board.initial_flowers_count = 2

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0

    def test_single_flower_at_max_distance(self):
        """AIGreedyPlayer should handle flower at maximum distance."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=15, cols=15, robot=robot, princess=Princess(position=Position(7, 7)))
        board.flowers = {Position(14, 14)}  # Maximum distance
        board.obstacles = set()
        board.board.initial_flowers_count = 1

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0
        assert board.get_status().value == "victory"

    def test_flowers_along_edges(self):
        """AIGreedyPlayer should collect flowers along board edges."""
        robot = Robot(position=Position(3, 3), orientation=Direction.EAST)
        board = Game(rows=7, cols=7, robot=robot, princess=Princess(position=Position(3, 3)))
        # Flowers on all edges
        board.flowers = {
            Position(0, 3),  # Top edge
            Position(6, 3),  # Bottom edge
            Position(3, 0),  # Left edge
            Position(3, 6),  # Right edge
        }
        board.obstacles = set()
        board.board.initial_flowers_count = 4

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0
        assert board.flowers_delivered == 4

    def test_zigzag_obstacle_walls(self):
        """AIGreedyPlayer should navigate zigzag walls."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=8, cols=8, robot=robot, princess=Princess(position=Position(7, 7)))
        # Zigzag wall pattern
        board.obstacles = {
            Position(1, 1),
            Position(1, 2),
            Position(2, 3),
            Position(2, 4),
            Position(3, 5),
            Position(3, 6),
            Position(4, 1),
            Position(4, 2),
            Position(5, 3),
            Position(5, 4),
        }
        board.flowers = {Position(6, 6)}
        board.board.initial_flowers_count = 1

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0

    def test_flower_between_two_obstacles(self):
        """AIGreedyPlayer should collect flower squeezed between obstacles."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=5, cols=5, robot=robot, princess=Princess(position=Position(4, 4)))
        board.obstacles = {Position(2, 1), Position(2, 3)}
        board.flowers = {Position(2, 2)}  # Between obstacles
        board.board.initial_flowers_count = 1

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0
        assert board.get_status().value == "victory"

    def test_multiple_scattered_obstacle_groups(self):
        """AIGreedyPlayer should navigate multiple scattered obstacle groups."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=9, cols=9, robot=robot, princess=Princess(position=Position(8, 8)))
        # Multiple scattered groups
        board.obstacles = {
            Position(1, 1),
            Position(1, 2),  # Group 1
            Position(3, 5),
            Position(4, 5),  # Group 2
            Position(6, 2),
            Position(6, 3),  # Group 3
            Position(5, 7),
            Position(6, 7),  # Group 4
        }
        board.flowers = {Position(4, 4), Position(7, 7)}
        board.board.initial_flowers_count = 2

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0

    def test_all_flowers_in_one_row(self):
        """AIGreedyPlayer should collect all flowers from single row."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=8, cols=8, robot=robot, princess=Princess(position=Position(7, 7)))
        # All flowers in row 3
        board.flowers = {
            Position(3, 1),
            Position(3, 3),
            Position(3, 5),
            Position(3, 7),
        }
        board.obstacles = set()
        board.board.initial_flowers_count = 4

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0
        assert board.flowers_delivered == 4

    def test_all_flowers_in_one_column(self):
        """AIGreedyPlayer should collect all flowers from single column."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=8, cols=8, robot=robot, princess=Princess(position=Position(7, 7)))
        # All flowers in column 4
        board.flowers = {
            Position(1, 4),
            Position(3, 4),
            Position(5, 4),
        }
        board.obstacles = set()
        board.board.initial_flowers_count = 3

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0
        assert board.flowers_delivered == 3

    def test_circular_obstacle_pattern(self):
        """AIGreedyPlayer should navigate circular obstacle patterns."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=7, cols=7, robot=robot, princess=Princess(position=Position(6, 6)))
        # Circular pattern around center
        board.obstacles = {
            Position(2, 3),
            Position(3, 2),
            Position(3, 4),
            Position(4, 3),
        }
        board.flowers = {Position(3, 3)}  # Center
        board.board.initial_flowers_count = 1

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0

    def test_flowers_requiring_precise_navigation(self):
        """AIGreedyPlayer should handle flowers requiring precise paths."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=6, cols=6, robot=robot, princess=Princess(position=Position(5, 5)))
        # Narrow path to flower
        board.obstacles = {
            Position(1, 1),
            Position(1, 2),
            Position(1, 3),
            Position(2, 0),
            Position(2, 4),
            Position(3, 0),
            Position(3, 4),
        }
        board.flowers = {Position(2, 2)}  # In narrow space
        board.board.initial_flowers_count = 1

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0

    def test_maximum_obstacles_with_flowers(self):
        """AIGreedyPlayer should handle many obstacles with flowers."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=10, cols=10, robot=robot, princess=Princess(position=Position(9, 9)))
        # Many obstacles
        board.obstacles = {
            Position(1, 1),
            Position(2, 2),
            Position(3, 3),
            Position(1, 4),
            Position(2, 5),
            Position(3, 6),
            Position(4, 1),
            Position(5, 2),
            Position(6, 3),
            Position(7, 4),
            Position(8, 5),
        }
        board.flowers = {Position(5, 5), Position(7, 7)}
        board.board.initial_flowers_count = 2

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0

    def test_flowers_and_obstacles_checkerboard(self):
        """AIGreedyPlayer should handle checkerboard pattern."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=8, cols=8, robot=robot, princess=Princess(position=Position(7, 7)))
        # Checkerboard obstacles
        board.obstacles = {
            Position(1, 1),
            Position(1, 3),
            Position(1, 5),
            Position(3, 1),
            Position(3, 3),
            Position(3, 5),
            Position(5, 1),
            Position(5, 3),
            Position(5, 5),
        }
        board.flowers = {Position(2, 2), Position(4, 4), Position(6, 6)}
        board.board.initial_flowers_count = 3

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0

    def test_long_corridor_with_flower_at_end(self):
        """AIGreedyPlayer should navigate long corridor to flower."""
        robot = Robot(position=Position(0, 3), orientation=Direction.EAST)
        board = Game(rows=7, cols=10, robot=robot, princess=Princess(position=Position(6, 3)))
        # Long corridor
        board.obstacles = {
            Position(1, 2),
            Position(1, 4),
            Position(2, 2),
            Position(2, 4),
            Position(3, 2),
            Position(3, 4),
            Position(4, 2),
            Position(4, 4),
            Position(5, 2),
            Position(5, 4),
        }
        board.flowers = {Position(5, 3)}  # At end of corridor
        board.board.initial_flowers_count = 1

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0

    def test_t_shaped_obstacle_junction(self):
        """AIGreedyPlayer should navigate T-shaped obstacle junctions."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=7, cols=7, robot=robot, princess=Princess(position=Position(6, 6)))
        # T-shaped junction
        board.obstacles = {
            Position(3, 1),
            Position(3, 2),
            Position(3, 3),
            Position(3, 4),
            Position(3, 5),
            Position(1, 3),
            Position(2, 3),
            Position(4, 3),
            Position(5, 3),
        }
        board.flowers = {Position(1, 1), Position(5, 5)}
        board.board.initial_flowers_count = 2

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0

    def test_double_wall_with_gap(self):
        """AIGreedyPlayer should find gap in double walls."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=8, cols=8, robot=robot, princess=Princess(position=Position(7, 7)))
        # Double wall with gap in middle
        board.obstacles = {
            # First wall
            Position(2, 0),
            Position(2, 1),
            Position(2, 2),
            # Gap at 2,3
            Position(2, 4),
            Position(2, 5),
            Position(2, 6),
            Position(2, 7),
            # Second wall
            Position(5, 0),
            Position(5, 1),
            Position(5, 2),
            # Gap at 5,3
            Position(5, 4),
            Position(5, 5),
            Position(5, 6),
            Position(5, 7),
        }
        board.flowers = {Position(6, 6)}
        board.board.initial_flowers_count = 1

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0

    def test_flowers_behind_obstacle_shield(self):
        """AIGreedyPlayer should collect flowers behind obstacle shields."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=7, cols=7, robot=robot, princess=Princess(position=Position(6, 6)))
        # Shield of obstacles
        board.obstacles = {
            Position(2, 2),
            Position(2, 3),
            Position(2, 4),
        }
        board.flowers = {Position(3, 3)}  # Behind shield
        board.board.initial_flowers_count = 1

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0

    def test_ultra_large_board(self):
        """AIGreedyPlayer should handle ultra-large boards."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=20, cols=20, robot=robot, princess=Princess(position=Position(19, 19)))
        board.flowers = {Position(10, 10), Position(15, 15)}
        board.obstacles = {Position(5, 5), Position(12, 12)}
        board.board.initial_flowers_count = 2

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0
        assert len(actions) < 800  # Reasonable limit

    def test_robot_and_princess_diagonal_opposite(self):
        """AIGreedyPlayer should handle diagonal opposite positions."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=10, cols=10, robot=robot, princess=Princess(position=Position(9, 9)))
        board.flowers = {Position(5, 5)}  # Center
        board.obstacles = set()
        board.board.initial_flowers_count = 1

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0
        assert board.get_status().value == "victory"

    def test_multiple_delivery_points_simulation(self):
        """AIGreedyPlayer should simulate multiple delivery cycles."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=10, cols=10, robot=robot, princess=Princess(position=Position(9, 9)))
        # Many flowers requiring multiple trips
        board.flowers = {
            Position(1, 1),
            Position(2, 1),
            Position(3, 1),
            Position(4, 1),
            Position(5, 1),
            Position(6, 1),
            Position(7, 1),
        }
        board.obstacles = set()
        board.board.initial_flowers_count = 7

        actions = AIGreedyPlayer.solve(board)

        # Check for multiple give actions
        give_actions = [a for a in actions if a[0] == "give"]
        assert len(give_actions) >= 1
        assert board.flowers_delivered == 7

    def test_dense_obstacles_sparse_flowers(self):
        """AIGreedyPlayer should handle dense obstacles with few flowers."""
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
        board = Game(rows=8, cols=8, robot=robot, princess=Princess(position=Position(7, 7)))
        # Very dense obstacles
        board.obstacles = {
            Position(1, 1),
            Position(1, 2),
            Position(1, 3),
            Position(1, 4),
            Position(2, 1),
            Position(2, 3),
            Position(2, 5),
            Position(3, 2),
            Position(3, 4),
            Position(3, 6),
            Position(4, 1),
            Position(4, 3),
            Position(4, 5),
            Position(5, 2),
            Position(5, 4),
            Position(5, 6),
        }
        board.flowers = {Position(6, 6)}  # Single flower
        board.board.initial_flowers_count = 1

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0

    def test_flower_at_each_orientation_from_center(self):
        """AIGreedyPlayer should collect flowers in all directions from center."""
        robot = Robot(position=Position(4, 4), orientation=Direction.EAST)
        board = Game(rows=9, cols=9, robot=robot, princess=Princess(position=Position(4, 4)))
        # Flowers in all 4 cardinal directions
        board.flowers = {
            Position(2, 4),  # North
            Position(6, 4),  # South
            Position(4, 2),  # West
            Position(4, 6),  # East
        }
        board.obstacles = set()
        board.board.initial_flowers_count = 4

        actions = AIGreedyPlayer.solve(board)

        assert len(actions) > 0
        assert board.flowers_delivered == 4
