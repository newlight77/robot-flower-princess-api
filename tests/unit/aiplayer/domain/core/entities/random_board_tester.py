"""
Script to test AI player with randomly generated game boards.
Helps identify failure patterns and improve the solver.
"""

import random
from hexagons.game.domain.core.entities.game import Game
from hexagons.game.domain.core.entities.robot import Robot
from hexagons.game.domain.core.entities.position import Position
from hexagons.game.domain.core.value_objects.direction import Direction
from hexagons.aiplayer.domain.core.entities.ai_greedy_player import AIGreedyPlayer
from hexagons.aiplayer.domain.core.entities.ai_optimal_player import AIOptimalPlayer
from tests.unit.aiplayer.domain.core.entities.ai_player_tester import AIPlayerTester


class RandomBoardGenerator:
    """Generate random game boards for testing."""

    @staticmethod
    def generate_board(
        rows: int = 5, cols: int = 5, num_flowers: int = 2, num_obstacles: int = 5, seed: int = None
    ) -> Game:
        """Generate a random solvable game board."""
        if seed is not None:
            random.seed(seed)

        # Create empty board
        robot_pos = Position(0, 0)
        princess_pos = Position(rows - 1, cols - 1)

        robot = Robot(position=robot_pos, orientation=Direction.EAST)
        board = Game(rows=rows, cols=cols, robot=robot, princess_position=princess_pos)

        # Generate random positions for flowers and obstacles
        available_positions = []
        for r in range(rows):
            for c in range(cols):
                pos = Position(r, c)
                # Don't place on robot or princess
                if pos != robot_pos and pos != princess_pos:
                    available_positions.append(pos)

        # Randomly select positions
        random.shuffle(available_positions)

        # Place flowers
        flowers = set()
        for i in range(min(num_flowers, len(available_positions))):
            flowers.add(available_positions[i])

        # Place obstacles (after flowers)
        obstacles = set()
        for i in range(num_flowers, min(num_flowers + num_obstacles, len(available_positions))):
            obstacles.add(available_positions[i])

        board.flowers = flowers
        board.obstacles = obstacles
        board.initial_flower_count = len(flowers)

        return board


def run_iteration(
    iteration: int, num_tests: int = 10, player: AIGreedyPlayer | AIOptimalPlayer = AIGreedyPlayer()
):
    """Run one iteration of testing."""
    print(f"\n{'='*60}")
    print(f"ITERATION {iteration}")
    print(f"{'='*60}")

    tester = AIPlayerTester(player=player)

    # Test various board sizes and configurations
    configs = [
        {"rows": 3, "cols": 3, "num_flowers": 1, "num_obstacles": 2},
        {"rows": 5, "cols": 5, "num_flowers": 2, "num_obstacles": 5},
        {"rows": 5, "cols": 5, "num_flowers": 3, "num_obstacles": 8},
        {"rows": 7, "cols": 7, "num_flowers": 3, "num_obstacles": 15},
        {"rows": 10, "cols": 10, "num_flowers": 2, "num_obstacles": 20},
        {"rows": 10, "cols": 10, "num_flowers": 5, "num_obstacles": 30},
    ]

    for i in range(num_tests):
        config = configs[i % len(configs)]
        board = RandomBoardGenerator.generate_board(
            **config, seed=iteration * 1000 + i  # Deterministic but different each iteration
        )

        print(
            f"\nTest {i+1}/{num_tests}: {config['rows']}x{config['cols']}, "
            f"{config['num_flowers']} flowers, {config['num_obstacles']} obstacles"
        )

        result = tester.test_board(board, board_id=f"iter{iteration}_test{i+1}")

        status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
        print(f"  Result: {status}")
        if result["success"]:
            print(
                f"  Actions: {result['actions_taken']}, " f"Cleaned: {result['obstacles_cleaned']}"
            )
        else:
            print(f"  Reason: {result.get('failure_reason', 'unknown')}")

    tester.print_summary()
    return tester


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("AI PLAYER ITERATIVE IMPROVEMENT TEST")
    print("=" * 60)
    print("Testing AI solver with randomly generated boards...")
    print("This will help identify failure patterns for improvement.")

    all_iterations = []

    for iteration in range(1, 11):
        tester = run_iteration(iteration, num_tests=10)
        all_iterations.append(tester)

    # Final summary
    print("\n" + "=" * 60)
    print("OVERALL SUMMARY (10 ITERATIONS)")
    print("=" * 60)

    total_success = sum(t.success_count for t in all_iterations)
    total_tests = sum(t.success_count + t.failure_count for t in all_iterations)
    overall_success_rate = (total_success / total_tests * 100) if total_tests > 0 else 0

    print(f"Total Tests: {total_tests}")
    print(f"Total Successes: {total_success} ({overall_success_rate:.1f}%)")
    print(f"Total Failures: {total_tests - total_success} ({100-overall_success_rate:.1f}%)")

    print("\nSuccess Rate by Iteration:")
    for i, tester in enumerate(all_iterations, 1):
        total = tester.success_count + tester.failure_count
        rate = (tester.success_count / total * 100) if total > 0 else 0
        print(f"  Iteration {i}: {tester.success_count}/{total} ({rate:.1f}%)")

    # Aggregate failure patterns
    print("\nAggregated Failure Patterns:")
    all_patterns = {}
    for tester in all_iterations:
        for pattern, count in tester.failure_patterns.items():
            all_patterns[pattern] = all_patterns.get(pattern, 0) + count

    for pattern, count in sorted(all_patterns.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  - {pattern}: {count}")

    print("=" * 60)
