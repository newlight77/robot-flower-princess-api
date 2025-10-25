"""
Script to test AI player with randomly generated game boards.
Helps identify failure patterns and improve the solver.
"""
import random
from typing import List, Tuple, Dict
from hexagons.game.domain.core.entities.game import Game
from hexagons.game.domain.core.entities.robot import Robot
from hexagons.game.domain.core.entities.position import Position
from hexagons.game.domain.core.value_objects.direction import Direction
from hexagons.aiplayer.domain.core.entities.game_solver_player import GameSolverPlayer


class RandomBoardGenerator:
    """Generate random game boards for testing."""

    @staticmethod
    def generate_board(
        rows: int = 5,
        cols: int = 5,
        num_flowers: int = 2,
        num_obstacles: int = 5,
        seed: int = None
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


class AIPlayerTester:
    """Test AI player and collect statistics."""

    def __init__(self):
        self.results: List[Dict] = []
        self.success_count = 0
        self.failure_count = 0
        self.failure_patterns = {
            "no_path_to_flower": 0,
            "no_path_to_princess": 0,
            "infinite_loop": 0,
            "stuck_with_flowers": 0,
            "robot_blocked": 0,
            "too_many_iterations": 0,
            "other": 0
        }

    def test_board(self, board: Game, board_id: str = "test") -> Dict:
        """Test a single board and return results."""
        initial_flowers = len(board.flowers)
        initial_obstacles = len(board.obstacles)

        try:
            # Try to solve
            actions = GameSolverPlayer.solve(board)

            # Check if solved
            success = (
                len(board.flowers) == 0 and
                board.robot.flowers_held == 0 and
                board.flowers_delivered > 0
            )

            result = {
                "board_id": board_id,
                "success": success,
                "actions_taken": len(actions),
                "initial_flowers": initial_flowers,
                "remaining_flowers": len(board.flowers),
                "flowers_delivered": board.flowers_delivered,
                "initial_obstacles": initial_obstacles,
                "remaining_obstacles": len(board.obstacles),
                "obstacles_cleaned": initial_obstacles - len(board.obstacles),
                "robot_final_position": f"({board.robot.position.row},{board.robot.position.col})",
                "robot_flowers_held": board.robot.flowers_held
            }

            if success:
                self.success_count += 1
            else:
                self.failure_count += 1
                # Analyze failure pattern
                self._analyze_failure(board, actions, result)

            self.results.append(result)
            return result

        except Exception as e:
            self.failure_count += 1
            result = {
                "board_id": board_id,
                "success": False,
                "error": str(e),
                "actions_taken": 0
            }
            self.results.append(result)
            self.failure_patterns["other"] += 1
            return result

    def _analyze_failure(self, board: Game, actions: List, result: Dict):
        """Analyze why the solver failed."""
        initial_flowers = result.get("initial_flowers", 0)

        if len(actions) == 0:
            # No actions taken - likely robot is blocked or no path
            if len(board.flowers) == initial_flowers:
                self.failure_patterns["robot_blocked"] += 1
                result["failure_reason"] = "robot_blocked"
                result["failure_detail"] = f"No actions taken, {len(board.flowers)} flowers remain"
            else:
                self.failure_patterns["other"] += 1
                result["failure_reason"] = "other"
                result["failure_detail"] = "Actions taken but immediately failed"
        elif len(actions) >= 1000:
            self.failure_patterns["too_many_iterations"] += 1
            result["failure_reason"] = "too_many_iterations"
            result["failure_detail"] = f"{len(actions)} actions taken (max 1000)"
        elif board.robot.flowers_held > 0:
            # Robot has flowers but didn't deliver
            self.failure_patterns["stuck_with_flowers"] += 1
            result["failure_reason"] = "stuck_with_flowers"
            result["failure_detail"] = f"Holding {board.robot.flowers_held} flowers, can't reach princess"
        elif len(board.flowers) > 0:
            # Couldn't pick all flowers
            flowers_picked = initial_flowers - len(board.flowers)
            self.failure_patterns["no_path_to_flower"] += 1
            result["failure_reason"] = "no_path_to_flower"
            result["failure_detail"] = f"Picked {flowers_picked}/{initial_flowers}, can't reach remaining"
        elif board.flowers_delivered == 0:
            # No flowers picked or delivered - complete failure
            self.failure_patterns["robot_blocked"] += 1
            result["failure_reason"] = "robot_blocked"
            result["failure_detail"] = "No progress made at all"
        else:
            # Partial success but didn't complete
            self.failure_patterns["other"] += 1
            result["failure_reason"] = "other"
            result["failure_detail"] = f"Delivered {board.flowers_delivered} but incomplete"

    def print_summary(self):
        """Print test summary."""
        total = self.success_count + self.failure_count
        success_rate = (self.success_count / total * 100) if total > 0 else 0

        print("\n" + "="*60)
        print("AI PLAYER TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {total}")
        print(f"Successes: {self.success_count} ({success_rate:.1f}%)")
        print(f"Failures: {self.failure_count} ({100-success_rate:.1f}%)")
        print("\nFailure Patterns:")
        for pattern, count in self.failure_patterns.items():
            if count > 0:
                print(f"  - {pattern}: {count}")

        if self.results:
            successful_results = [r for r in self.results if r.get("success")]
            if successful_results:
                avg_actions = sum(r["actions_taken"] for r in successful_results) / len(successful_results)
                avg_cleaned = sum(r["obstacles_cleaned"] for r in successful_results) / len(successful_results)
                print(f"\nSuccessful Runs Stats:")
                print(f"  - Avg actions: {avg_actions:.1f}")
                print(f"  - Avg obstacles cleaned: {avg_cleaned:.1f}")

        print("="*60 + "\n")


def run_iteration(iteration: int, num_tests: int = 10):
    """Run one iteration of testing."""
    print(f"\n{'='*60}")
    print(f"ITERATION {iteration}")
    print(f"{'='*60}")

    tester = AIPlayerTester()

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
            **config,
            seed=iteration * 1000 + i  # Deterministic but different each iteration
        )

        print(f"\nTest {i+1}/{num_tests}: {config['rows']}x{config['cols']}, "
              f"{config['num_flowers']} flowers, {config['num_obstacles']} obstacles")

        result = tester.test_board(board, board_id=f"iter{iteration}_test{i+1}")

        status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
        print(f"  Result: {status}")
        if result["success"]:
            print(f"  Actions: {result['actions_taken']}, "
                  f"Cleaned: {result['obstacles_cleaned']}")
        else:
            print(f"  Reason: {result.get('failure_reason', 'unknown')}")

    tester.print_summary()
    return tester


if __name__ == "__main__":
    print("\n" + "="*60)
    print("AI PLAYER ITERATIVE IMPROVEMENT TEST")
    print("="*60)
    print("Testing AI solver with randomly generated boards...")
    print("This will help identify failure patterns for improvement.")

    all_iterations = []

    for iteration in range(1, 11):
        tester = run_iteration(iteration, num_tests=10)
        all_iterations.append(tester)

    # Final summary
    print("\n" + "="*60)
    print("OVERALL SUMMARY (10 ITERATIONS)")
    print("="*60)

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

    print("="*60)
