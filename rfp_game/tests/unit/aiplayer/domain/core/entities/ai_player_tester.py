from typing import Dict, List
from hexagons.game.domain.core.entities.game import Game
from hexagons.aiplayer.domain.core.entities.ai_greedy_player import AIGreedyPlayer
from hexagons.aiplayer.domain.core.entities.ai_optimal_player import AIOptimalPlayer


class AIPlayerTester:
    """Test AI player and collect statistics."""

    def __init__(self, player: AIGreedyPlayer | AIOptimalPlayer):
        self.player = player
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
            "other": 0,
        }

    def test_board(self, game: Game, game_id: str = "test") -> Dict:
        """Test a single board and return results."""
        initial_flowers = len(game.flowers)
        initial_obstacles = len(game.obstacles)

        try:
            # Try to solve
            actions = self.player.solve(game)

            # Check if solved
            success = len(game.flowers) == 0 and game.robot.flowers_held == 0 and game.flowers_delivered > 0

            result = {
                "game_id": game_id,
                "success": success,
                "actions_taken": len(actions),
                "initial_flowers": initial_flowers,
                "remaining_flowers": len(game.flowers),
                "flowers_delivered": game.flowers_delivered,
                "initial_obstacles": initial_obstacles,
                "remaining_obstacles": len(game.obstacles),
                "obstacles_cleaned": initial_obstacles - len(game.obstacles),
                "robot_final_position": f"({game.robot.position.row},{game.robot.position.col})",
                "robot_flowers_held": game.robot.flowers_held,
            }

            if success:
                self.success_count += 1
            else:
                self.failure_count += 1
                # Analyze failure pattern
                self._analyze_failure(game, actions, result)

            self.results.append(result)
            return result

        except Exception as e:
            self.failure_count += 1
            result = {"game_id": game_id, "success": False, "error": str(e), "actions_taken": 0}
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

        print("\n" + "=" * 60)
        print("AI PLAYER TEST SUMMARY")
        print("=" * 60)
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
                print("\nSuccessful Runs Stats:")
                print(f"  - Avg actions: {avg_actions:.1f}")
                print(f"  - Avg obstacles cleaned: {avg_cleaned:.1f}")

        print("=" * 60 + "\n")
