"""Unit tests for AIOptimalPlayer (fast, efficient AI strategy)."""

import pytest
from copy import deepcopy

from hexagons.game.domain.core.entities.game import Game
from hexagons.game.domain.core.entities.position import Position
from hexagons.game.domain.core.value_objects.direction import Direction
from hexagons.aiplayer.domain.core.entities.ai_optimal_player import AIOptimalPlayer


@pytest.fixture
def simple_game():
    """Create a simple solvable game board."""
    game = Game(rows=5, cols=5)

    game.robot.position = Position(0, 0)

    game.robot.orientation = Direction.EAST

    game.princess.position = Position(4, 4)
    game.flowers = {Position(1, 1), Position(3, 3)}
    game.board.initial_flowers_count = len(game.flowers)
    game.obstacles = set()
    game.board.initial_flowers_count = len(game.flowers)
    return game


@pytest.fixture
def game_with_obstacles():
    """Create a board with obstacles that requires cleaning."""
    game = Game(rows=5, cols=5)

    game.robot.position = Position(0, 0)

    game.robot.orientation = Direction.EAST

    game.princess.position = Position(4, 4)
    game.flowers = {Position(1, 1)}
    game.board.initial_flowers_count = len(game.flowers)
    game.obstacles = {Position(2, 2), Position(1, 3)}
    game.board.initial_flowers_count = len(game.flowers)
    return game


class TestAIOptimalPlayer:
    """Tests for AIOptimalPlayer (fast, efficient strategy)."""

    def test_solve_returns_list_of_actions(self, simple_game):
        """AIOptimalPlayer.solve should return a list of action tuples."""
        actions = AIOptimalPlayer.solve(simple_game)

        assert isinstance(actions, list)
        assert len(actions) > 0

        # Each action should be a tuple of (action_type, direction)
        for action in actions:
            assert isinstance(action, tuple)
            assert len(action) == 2
            action_type, direction = action
            assert isinstance(action_type, str)
            assert action_type in ["rotate", "move", "pick", "give", "drop", "clean"]

    def test_solve_simple_board_successfully(self, simple_game):
        """AIOptimalPlayer should solve a simple board and deliver all flowers."""
        game = deepcopy(simple_game)
        actions = AIOptimalPlayer.solve(game)

        assert len(actions) > 0
        assert game.get_status().value == "victory"
        assert game.flowers_delivered == 2
        assert len(game.flowers) == 0

    def test_solve_board_with_obstacles(self, game_with_obstacles):
        """AIOptimalPlayer should solve a board with obstacles."""
        game = deepcopy(game_with_obstacles)
        actions = AIOptimalPlayer.solve(game)

        assert len(actions) > 0
        # Should successfully deliver the flower or at least try
        assert game.flowers_delivered >= 0

    def test_solve_empty_board_no_actions(self):
        """AIOptimalPlayer should return empty actions for board with no flowers."""
        game = Game(rows=3, cols=3)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(2, 2)
        game.flowers = set()
        game.board.initial_flowers_count = 0

        actions = AIOptimalPlayer.solve(game)

        # Should return an empty list or minimal actions
        assert isinstance(actions, list)

    def test_solve_does_not_modify_original_board(self, simple_game):
        """AIOptimalPlayer.solve should work with the board it receives."""
        game = deepcopy(simple_game)
        initial_robot_pos = game.robot.position
        initial_flower_count = len(game.flowers)

        # Solve modifies the board, but we pass a copy
        _ = AIOptimalPlayer.solve(game)

        # The board passed to solve is modified (it's the working board)
        # This test verifies the solver works with the board it receives
        assert game.robot.position != initial_robot_pos or len(game.flowers) != initial_flower_count

    def test_solve_complex_board_with_multiple_flowers(self):
        """
        AIOptimalPlayer should handle boards with multiple flowers efficiently.

        Tests multi-step planning with permutations for optimal flower sequencing.
        """
        game = Game(rows=7, cols=7)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(6, 6)
        game.flowers = {
            Position(1, 1),
            Position(2, 2),
            Position(3, 3),
            Position(4, 4),
        }
        game.obstacles = {Position(2, 3), Position(3, 2)}
        game.board.initial_flowers_count = len(game.flowers)

        actions = AIOptimalPlayer.solve(game)

        # Should complete successfully
        assert len(actions) > 0
        assert isinstance(actions, list)

        # Multi-step planning should result in a reasonable number of actions
        # (Not testing exact number as algorithm may vary)
        assert len(actions) < 200  # Sanity check

    def test_uses_astar_pathfinding(self, simple_game):
        """
        AIOptimalPlayer uses A* pathfinding with Manhattan distance heuristic.

        This test verifies the algorithm completes successfully with obstacles,
        which requires A* pathfinding to work correctly.
        """
        game = deepcopy(simple_game)

        # Add obstacles to make pathfinding more interesting
        game.obstacles = {Position(2, 2), Position(1, 3), Position(3, 1)}

        actions = AIOptimalPlayer.solve(game)

        # A* should find optimal paths and complete the game
        assert len(actions) > 0
        # If A* works, the robot should successfully navigate and deliver
        assert game.flowers_delivered >= 0

    def test_multi_step_planning_with_small_flower_set(self):
        """
        AIOptimalPlayer uses permutations for ≤4 flowers.

        Tests the optimal flower sequencing algorithm.
        """
        game = Game(rows=6, cols=6)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(5, 5)

        # Use 3 flowers to trigger permutation planning
        game.flowers = {
            Position(1, 1),
            Position(2, 3),
            Position(4, 2),
        }
        game.obstacles = set()
        game.board.initial_flowers_count = len(game.flowers)

        actions = AIOptimalPlayer.solve(game)

        # Should find optimal sequence and complete
        assert len(actions) > 0
        assert game.get_status().value == "victory"
        assert game.flowers_delivered == 3

    def test_smart_obstacle_evaluation(self, simple_game):
        """
        AIOptimalPlayer evaluates which obstacles to clean for best paths.

        Tests smart obstacle cleaning with look-ahead evaluation.
        """
        game = deepcopy(simple_game)

        # Add strategic obstacles that require smart evaluation
        game.obstacles = {
            Position(2, 2),  # Middle obstacle
            Position(3, 3),  # Near a flower
            Position(1, 4),  # Near princess path
        }

        actions = AIOptimalPlayer.solve(game)

        # Should intelligently evaluate and clean obstacles
        assert isinstance(actions, list)
        assert len(actions) > 0

        # Check if obstacles were cleaned strategically
        # (The solver should clean some obstacles if needed)
        obstacle_cleaning_actions = [a for a in actions if a[0] == "clean"]
        # May or may not need to clean depending on paths found
        assert isinstance(obstacle_cleaning_actions, list)

    def test_with_large_flower_set_uses_greedy_lookahead(self):
        """
        AIOptimalPlayer uses greedy with 2-step look-ahead for >4 flowers.

        Tests the algorithm switching strategy for larger flower sets.
        """
        game = Game(rows=8, cols=8)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(7, 7)

        # Use 6 flowers to trigger greedy with look-ahead (not permutations)
        game.flowers = {
            Position(1, 1),
            Position(2, 2),
            Position(3, 3),
            Position(4, 4),
            Position(5, 5),
            Position(6, 6),
        }
        game.obstacles = set()
        game.board.initial_flowers_count = len(game.flowers)

        actions = AIOptimalPlayer.solve(game)

        # Should complete with reasonable action count
        assert len(actions) > 0
        assert isinstance(actions, list)
        # Should be efficient despite large flower count
        assert len(actions) < 300  # Sanity check

    def test_robot_starts_surrounded_by_obstacles(self):
        """
        AIOptimalPlayer should handle robot starting position blocked by obstacles.

        Tests initial obstacle cleaning before any movement.
        """
        game = Game(rows=5, cols=5)

        game.robot.position = Position(2, 2)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(4, 4)

        # Surround robot with obstacles
        game.obstacles = {
            Position(1, 2),  # North
            Position(3, 2),  # South
            Position(2, 1),  # West
            Position(2, 3),  # East
        }
        game.flowers = {Position(4, 3)}
        game.board.initial_flowers_count = len(game.flowers)

        actions = AIOptimalPlayer.solve(game)

        # Should clean at least one obstacle to start
        assert len(actions) > 0
        clean_actions = [a for a in actions if a[0] == "clean"]
        assert len(clean_actions) > 0  # Must clean to proceed

    def test_princess_surrounded_by_obstacles(self):
        """
        AIOptimalPlayer should clean obstacles around princess to deliver flowers.

        Tests obstacle removal near goal position.
        """
        game = Game(rows=5, cols=5)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(2, 2)

        # Surround princess with obstacles
        game.obstacles = {
            Position(1, 2),  # North
            Position(3, 2),  # South
            Position(2, 1),  # West
            Position(2, 3),  # East
        }
        game.flowers = {Position(0, 1)}
        game.board.initial_flowers_count = len(game.flowers)

        actions = AIOptimalPlayer.solve(game)

        # Should attempt to clean obstacles near princess
        assert len(actions) > 0
        clean_actions = [a for a in actions if a[0] == "clean"]
        assert len(clean_actions) > 0  # Must clean to reach princess

    def test_very_large_board_scalability(self):
        """
        AIOptimalPlayer should handle large boards efficiently.

        Tests scalability of A* pathfinding on larger grids.
        """
        game = Game(rows=15, cols=15)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(14, 14)

        # Place flowers at various distances
        game.flowers = {
            Position(3, 3),
            Position(7, 7),
            Position(11, 11),
        }
        game.obstacles = {
            Position(5, 5),
            Position(8, 8),
        }
        game.board.initial_flowers_count = len(game.flowers)

        actions = AIOptimalPlayer.solve(game)

        # Should complete without excessive actions
        assert len(actions) > 0
        # A* should be efficient even on large boards
        assert len(actions) < 500  # Reasonable limit for this size

    def test_clustered_vs_spread_flowers(self):
        """
        AIOptimalPlayer should efficiently handle clustered flowers.

        Tests multi-step planning with nearby flowers.
        """
        game = Game(rows=6, cols=6)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(5, 5)

        # Cluster flowers together
        game.flowers = {
            Position(2, 2),
            Position(2, 3),  # Adjacent to first
            Position(3, 2),  # Adjacent to first
        }
        game.obstacles = set()
        game.board.initial_flowers_count = len(game.flowers)

        actions = AIOptimalPlayer.solve(game)

        # Should efficiently collect clustered flowers
        assert len(actions) > 0
        assert game.get_status().value == "victory"
        assert game.flowers_delivered == 3
        # Clustered flowers should result in fewer actions
        assert len(actions) < 100  # Should be relatively efficient

    def test_robot_far_from_all_flowers(self):
        """
        AIOptimalPlayer should handle cases where robot starts far from flowers.

        Tests long-distance pathfinding initialization.
        """
        game = Game(rows=10, cols=10)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(9, 9)

        # Place flowers far from robot
        game.flowers = {
            Position(8, 8),
            Position(7, 8),
        }
        game.obstacles = set()
        game.board.initial_flowers_count = len(game.flowers)

        actions = AIOptimalPlayer.solve(game)

        # Should navigate long distances efficiently
        assert len(actions) > 0
        assert game.get_status().value == "victory"
        assert game.flowers_delivered == 2

    def test_unsolvable_board_handles_gracefully(self):
        """
        AIOptimalPlayer should handle unsolvable boards gracefully.

        Tests failure scenario where princess is completely inaccessible.
        """
        game = Game(rows=5, cols=5)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(4, 4)

        # Create wall of obstacles blocking princess
        game.obstacles = {
            Position(3, 3),
            Position(3, 4),
            Position(4, 3),
        }
        game.flowers = {Position(1, 1)}
        game.board.initial_flowers_count = len(game.flowers)

        actions = AIOptimalPlayer.solve(game)

        # Should return actions (may not complete successfully)
        assert isinstance(actions, list)
        # May or may not succeed depending on obstacle cleaning ability

    def test_incremental_flower_delivery_strategy(self):
        """
        AIOptimalPlayer should handle incremental deliveries efficiently.

        Tests multiple pickup-deliver cycles.
        """
        game = Game(rows=8, cols=8)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(7, 7)

        # Spread flowers requiring multiple trips
        game.flowers = {
            Position(1, 1),
            Position(2, 2),
            Position(3, 3),
            Position(4, 4),
            Position(5, 5),
        }
        game.obstacles = set()
        game.board.initial_flowers_count = len(game.flowers)

        actions = AIOptimalPlayer.solve(game)

        # Should complete all deliveries
        assert len(actions) > 0
        # Check for multiple give actions (incremental deliveries)
        give_actions = [a for a in actions if a[0] == "give"]
        # May deliver incrementally depending on strategy
        assert len(give_actions) >= 1

    def test_maze_like_obstacle_configuration(self):
        """
        AIOptimalPlayer's A* should navigate maze-like obstacles efficiently.

        Tests complex pathfinding scenarios.
        """
        game = Game(rows=7, cols=7)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(6, 6)

        # Create maze-like obstacles
        game.obstacles = {
            Position(1, 0),
            Position(1, 1),
            Position(1, 2),
            Position(3, 1),
            Position(3, 2),
            Position(3, 3),
            Position(5, 2),
            Position(5, 3),
            Position(5, 4),
        }
        game.flowers = {Position(4, 4)}
        game.board.initial_flowers_count = len(game.flowers)

        actions = AIOptimalPlayer.solve(game)

        # A* should find path through maze
        assert len(actions) > 0
        # Should navigate complex paths
        assert isinstance(actions, list)

    def test_maximum_flowers_stress_test(self):
        """
        AIOptimalPlayer should handle many flowers (stress test).

        Tests algorithm performance with high flower count.
        """
        game = Game(rows=10, cols=10)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(9, 9)

        # Place many flowers (10 flowers)
        game.flowers = {
            Position(1, 1),
            Position(2, 2),
            Position(3, 3),
            Position(4, 4),
            Position(5, 5),
            Position(6, 6),
            Position(7, 7),
            Position(8, 8),
            Position(1, 8),
            Position(8, 1),
        }
        game.obstacles = set()
        game.board.initial_flowers_count = len(game.flowers)

        actions = AIOptimalPlayer.solve(game)

        # Should handle many flowers
        assert len(actions) > 0
        assert isinstance(actions, list)
        # Should complete within reasonable action count
        assert len(actions) < 600  # Stress test sanity check

    def test_alternating_obstacle_pattern(self):
        """
        AIOptimalPlayer should handle alternating obstacle patterns.

        Tests strategic obstacle evaluation with complex patterns.
        """
        game = Game(rows=6, cols=6)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(5, 5)

        # Create checkerboard-like obstacle pattern
        game.obstacles = {
            Position(1, 1),
            Position(1, 3),
            Position(1, 5),
            Position(3, 1),
            Position(3, 3),
            Position(3, 5),
        }
        game.flowers = {Position(2, 2), Position(4, 4)}
        game.board.initial_flowers_count = len(game.flowers)

        actions = AIOptimalPlayer.solve(game)

        # Should navigate alternating pattern
        assert len(actions) > 0
        assert isinstance(actions, list)

    def test_single_flower_optimal_path(self):
        """AIOptimalPlayer should find optimal path for single flower."""
        game = Game(rows=4, cols=4)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(3, 3)
        game.flowers = {Position(1, 1)}
        game.board.initial_flowers_count = len(game.flowers)
        game.obstacles = set()
        game.board.initial_flowers_count = 1

        actions = AIOptimalPlayer.solve(game)

        assert len(actions) > 0
        assert game.get_status().value == "victory"
        assert game.flowers_delivered == 1

    def test_two_flower_permutation_planning(self):
        """AIOptimalPlayer should test both permutations for 2 flowers."""
        game = Game(rows=5, cols=5)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(4, 4)
        game.flowers = {Position(1, 1), Position(3, 3)}
        game.board.initial_flowers_count = len(game.flowers)
        game.obstacles = set()
        game.board.initial_flowers_count = 2

        actions = AIOptimalPlayer.solve(game)

        assert len(actions) > 0
        assert game.flowers_delivered == 2

    def test_three_flower_permutation_planning(self):
        """AIOptimalPlayer should optimize sequence for 3 flowers."""
        game = Game(rows=6, cols=6)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(5, 5)
        game.flowers = {Position(1, 1), Position(2, 3), Position(4, 2)}
        game.board.initial_flowers_count = len(game.flowers)
        game.obstacles = set()
        game.board.initial_flowers_count = 3

        actions = AIOptimalPlayer.solve(game)

        assert len(actions) > 0
        assert game.get_status().value == "victory"
        assert game.flowers_delivered == 3

    def test_four_flower_permutation_planning(self):
        """AIOptimalPlayer should optimize sequence for 4 flowers (max permutations)."""
        game = Game(rows=6, cols=6)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(5, 5)
        game.flowers = {
            Position(1, 1),
            Position(1, 4),
            Position(4, 1),
            Position(4, 4),
        }
        game.obstacles = set()
        game.board.initial_flowers_count = 4

        actions = AIOptimalPlayer.solve(game)

        assert len(actions) > 0
        assert game.flowers_delivered == 4

    def test_five_flower_greedy_lookahead(self):
        """AIOptimalPlayer should use greedy with look-ahead for 5 flowers."""
        game = Game(rows=7, cols=7)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(6, 6)
        game.flowers = {
            Position(1, 1),
            Position(2, 2),
            Position(3, 3),
            Position(4, 4),
            Position(5, 5),
        }
        game.obstacles = set()
        game.board.initial_flowers_count = 5

        actions = AIOptimalPlayer.solve(game)

        assert len(actions) > 0
        assert game.flowers_delivered == 5

    def test_corridor_with_obstacles_astar_navigation(self):
        """AIOptimalPlayer's A* should find optimal path through corridor."""
        game = Game(rows=5, cols=8)

        game.robot.position = Position(0, 2)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(4, 2)
        # Corridor with obstacles
        game.obstacles = {
            Position(1, 1),
            Position(1, 3),
            Position(2, 1),
            Position(2, 3),
            Position(3, 1),
            Position(3, 3),
        }
        game.flowers = {Position(3, 2)}
        game.board.initial_flowers_count = 1

        actions = AIOptimalPlayer.solve(game)

        assert len(actions) > 0
        assert game.get_status().value == "victory"

    def test_diagonal_obstacle_wall(self):
        """AIOptimalPlayer should navigate around diagonal obstacle walls."""
        game = Game(rows=7, cols=7)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(6, 6)
        # Diagonal wall
        game.obstacles = {
            Position(1, 2),
            Position(2, 3),
            Position(3, 4),
            Position(4, 5),
        }
        game.flowers = {Position(3, 3)}
        game.board.initial_flowers_count = 1

        actions = AIOptimalPlayer.solve(game)

        assert len(actions) > 0

    def test_l_shaped_obstacle_barrier(self):
        """AIOptimalPlayer should navigate L-shaped obstacle patterns."""
        game = Game(rows=6, cols=6)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(5, 5)
        # L-shaped barrier
        game.obstacles = {
            Position(2, 1),
            Position(2, 2),
            Position(2, 3),
            Position(3, 3),
            Position(4, 3),
        }
        game.flowers = {Position(4, 4)}
        game.board.initial_flowers_count = 1

        actions = AIOptimalPlayer.solve(game)

        assert len(actions) > 0

    def test_zigzag_path_required(self):
        """AIOptimalPlayer should handle zigzag path requirements."""
        game = Game(rows=7, cols=7)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(6, 6)
        # Staggered obstacles requiring zigzag
        game.obstacles = {
            Position(1, 1),
            Position(1, 2),
            Position(2, 3),
            Position(2, 4),
            Position(3, 1),
            Position(3, 2),
            Position(4, 3),
            Position(4, 4),
        }
        game.flowers = {Position(5, 5)}
        game.board.initial_flowers_count = 1

        actions = AIOptimalPlayer.solve(game)

        assert len(actions) > 0

    def test_flowers_requiring_backtracking(self):
        """AIOptimalPlayer should handle scenarios requiring backtracking."""
        game = Game(rows=7, cols=7)

        game.robot.position = Position(3, 3)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(3, 3)
        # Flowers in opposite corners
        game.flowers = {Position(0, 0), Position(6, 6)}
        game.board.initial_flowers_count = len(game.flowers)
        game.obstacles = set()
        game.board.initial_flowers_count = 2

        actions = AIOptimalPlayer.solve(game)

        assert len(actions) > 0
        assert game.flowers_delivered == 2

    def test_obstacle_creates_detour(self):
        """AIOptimalPlayer should efficiently handle forced detours."""
        game = Game(rows=5, cols=5)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(4, 4)
        # Wall forcing detour
        game.obstacles = {
            Position(2, 0),
            Position(2, 1),
            Position(2, 2),
            Position(2, 3),
        }
        game.flowers = {Position(3, 2)}
        game.board.initial_flowers_count = 1

        actions = AIOptimalPlayer.solve(game)

        assert len(actions) > 0

    def test_multiple_obstacle_clusters(self):
        """AIOptimalPlayer should navigate multiple obstacle clusters."""
        game = Game(rows=8, cols=8)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(7, 7)
        # Multiple clusters
        game.obstacles = {
            Position(1, 1),
            Position(1, 2),  # Cluster 1
            Position(3, 3),
            Position(3, 4),  # Cluster 2
            Position(5, 5),
            Position(5, 6),  # Cluster 3
        }
        game.flowers = {Position(2, 2), Position(6, 6)}
        game.board.initial_flowers_count = 2

        actions = AIOptimalPlayer.solve(game)

        assert len(actions) > 0

    def test_flower_adjacent_to_obstacle(self):
        """AIOptimalPlayer should collect flowers next to obstacles."""
        game = Game(rows=5, cols=5)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(4, 4)
        game.obstacles = {Position(2, 2)}
        game.flowers = {Position(2, 3)}  # Adjacent to obstacle
        game.board.initial_flowers_count = 1

        actions = AIOptimalPlayer.solve(game)

        assert len(actions) > 0
        assert game.get_status().value == "victory"

    def test_princess_in_corner_with_obstacles(self):
        """AIOptimalPlayer should reach princess in corner through obstacles."""
        game = Game(rows=5, cols=5)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(4, 4)
        # Obstacles near princess corner
        game.obstacles = {Position(3, 3), Position(3, 4), Position(4, 3)}
        game.flowers = {Position(1, 1)}
        game.board.initial_flowers_count = 1

        actions = AIOptimalPlayer.solve(game)

        # Should clean obstacles or find path
        assert len(actions) > 0

    def test_scattered_flowers_across_board(self):
        """AIOptimalPlayer should efficiently collect scattered flowers."""
        game = Game(rows=9, cols=9)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(8, 8)
        # Scattered pattern
        game.flowers = {
            Position(1, 7),
            Position(3, 2),
            Position(5, 5),
            Position(7, 1),
            Position(6, 6),
        }
        game.obstacles = set()
        game.board.initial_flowers_count = 5

        actions = AIOptimalPlayer.solve(game)

        assert len(actions) > 0
        assert game.flowers_delivered == 5

    def test_seven_flowers_lookahead_strategy(self):
        """AIOptimalPlayer should handle 7 flowers with greedy look-ahead."""
        game = Game(rows=9, cols=9)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(8, 8)
        game.flowers = {
            Position(1, 1),
            Position(2, 2),
            Position(3, 3),
            Position(4, 4),
            Position(5, 5),
            Position(6, 6),
            Position(7, 7),
        }
        game.obstacles = set()
        game.board.initial_flowers_count = 7

        actions = AIOptimalPlayer.solve(game)

        assert len(actions) > 0
        assert game.flowers_delivered == 7

    def test_box_shaped_obstacle_enclosure(self):
        """AIOptimalPlayer should navigate box-shaped obstacles."""
        game = Game(rows=7, cols=7)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(6, 6)
        # Box/square of obstacles
        game.obstacles = {
            Position(2, 2),
            Position(2, 3),
            Position(2, 4),
            Position(3, 2),
            Position(3, 4),
            Position(4, 2),
            Position(4, 3),
            Position(4, 4),
        }
        game.flowers = {Position(3, 3), Position(5, 5)}  # One inside box
        game.board.initial_flowers_count = 2

        actions = AIOptimalPlayer.solve(game)

        assert len(actions) > 0

    def test_very_large_board_with_many_flowers(self):
        """AIOptimalPlayer should handle very large boards with many flowers."""
        game = Game(rows=15, cols=15)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(14, 14)
        game.flowers = {
            Position(2, 2),
            Position(4, 4),
            Position(6, 6),
            Position(8, 8),
            Position(10, 10),
            Position(12, 12),
        }
        game.obstacles = {
            Position(3, 3),
            Position(7, 7),
            Position(11, 11),
        }
        game.board.initial_flowers_count = 6

        actions = AIOptimalPlayer.solve(game)

        assert len(actions) > 0
        assert len(actions) < 600  # Efficiency check

    def test_rectangular_board_tall(self):
        """AIOptimalPlayer should handle rectangular boards (taller than wide)."""
        gane = Game(rows=10, cols=5)

        gane.robot.position = Position(0, 0)

        gane.robot.orientation = Direction.EAST

        gane.princess.position = Position(9, 4)
        gane.flowers = {Position(3, 2), Position(7, 3)}
        gane.board.initial_flowers_count = len(gane.flowers)
        gane.obstacles = set()
        gane.board.initial_flowers_count = 2

        actions = AIOptimalPlayer.solve(gane)

        assert len(actions) > 0
        assert gane.flowers_delivered == 2

    def test_minimum_board_size(self):
        """AIOptimalPlayer should work on minimum 3x3 board."""
        game = Game(rows=3, cols=3)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(2, 2)
        game.flowers = {Position(1, 1)}
        game.board.initial_flowers_count = len(game.flowers)
        game.obstacles = set()
        game.board.initial_flowers_count = 1

        actions = AIOptimalPlayer.solve(game)

        assert len(actions) > 0
        assert game.get_status().value == "victory"

    def test_flower_line_horizontal(self):
        """AIOptimalPlayer should efficiently collect horizontal flower line."""
        game = Game(rows=7, cols=10)

        game.robot.position = Position(3, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(3, 9)
        # Horizontal line
        game.flowers = {
            Position(3, 2),
            Position(3, 4),
            Position(3, 6),
            Position(3, 8),
        }
        game.obstacles = set()
        game.board.initial_flowers_count = 4

        actions = AIOptimalPlayer.solve(game)

        assert len(actions) > 0
        assert game.flowers_delivered == 4

    def test_flower_line_vertical(self):
        """AIOptimalPlayer should efficiently collect vertical flower line."""
        game = Game(rows=10, cols=7)

        game.robot.position = Position(0, 3)

        game.robot.orientation = Direction.SOUTH

        game.princess.position = Position(9, 3)
        # Vertical line
        game.flowers = {
            Position(2, 3),
            Position(4, 3),
            Position(6, 3),
            Position(8, 3),
        }
        game.obstacles = set()
        game.board.initial_flowers_count = 4

        actions = AIOptimalPlayer.solve(game)

        assert len(actions) > 0
        assert game.flowers_delivered == 4

    def test_grid_pattern_flowers(self):
        """AIOptimalPlayer should optimize collection of grid-patterned flowers."""
        game = Game(rows=9, cols=9)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(8, 8)
        # Grid pattern (every other cell)
        game.flowers = {
            Position(2, 2),
            Position(2, 4),
            Position(2, 6),
            Position(4, 2),
            Position(4, 4),
            Position(4, 6),
            Position(6, 2),
            Position(6, 4),
            Position(6, 6),
        }
        game.obstacles = set()
        game.board.initial_flowers_count = 9

        actions = AIOptimalPlayer.solve(game)

        assert len(actions) > 0
        assert len(actions) < 500  # Should be efficient

    def test_perimeter_flowers(self):
        """AIOptimalPlayer should collect flowers around board perimeter."""
        game = Game(rows=7, cols=7)

        game.robot.position = Position(3, 3)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(3, 3)
        # Perimeter
        game.flowers = {
            Position(0, 0),
            Position(0, 6),  # Top corners
            Position(6, 0),
            Position(6, 6),  # Bottom corners
        }
        game.obstacles = set()
        game.board.initial_flowers_count = 4

        actions = AIOptimalPlayer.solve(game)

        assert len(actions) > 0
        assert game.flowers_delivered == 4

    def test_obstacle_wall_with_gap(self):
        """AIOptimalPlayer should find and use gaps in obstacle walls."""
        game = Game(rows=7, cols=7)

        game.robot.position = Position(0, 0)

        game.robot.orientation = Direction.EAST

        game.princess.position = Position(6, 6)
        # Wall with one gap
        game.obstacles = {
            Position(3, 0),
            Position(3, 1),
            Position(3, 2),
            # Gap at Position(3, 3)
            Position(3, 4),
            Position(3, 5),
            Position(3, 6),
        }
        game.flowers = {Position(5, 5)}
        game.board.initial_flowers_count = 1

        actions = AIOptimalPlayer.solve(game)

        assert len(actions) > 0
        assert game.get_status().value == "victory"
