"""Analyze specific failing boards to understand patterns."""

from tests.unit.aiplayer.domain.core.entities.random_board_tester import RandomBoardGenerator
from tests.unit.aiplayer.domain.core.entities.ai_player_tester import AIPlayerTester
from hexagons.aiplayer.domain.core.entities.ai_greedy_player import AIGreedyPlayer


def save_failing_boards():
    """Generate and save boards that fail for analysis."""
    player = AIGreedyPlayer()
    tester = AIPlayerTester(player=player)
    failing_boards = []

    # Test the specific seeds/configs that failed in the full run
    test_configs = [
        # 5x5 with 3 flowers, 8 obstacles - commonly fails
        {"rows": 5, "cols": 5, "num_flowers": 3, "num_obstacles": 8, "seed": 1002},
        {"rows": 5, "cols": 5, "num_flowers": 3, "num_obstacles": 8, "seed": 1008},
        {"rows": 5, "cols": 5, "num_flowers": 3, "num_obstacles": 8, "seed": 2002},
        {"rows": 5, "cols": 5, "num_flowers": 3, "num_obstacles": 8, "seed": 3002},
        # 7x7 with 3 flowers, 15 obstacles - commonly fails
        {"rows": 7, "cols": 7, "num_flowers": 3, "num_obstacles": 15, "seed": 1003},
        {"rows": 7, "cols": 7, "num_flowers": 3, "num_obstacles": 15, "seed": 3009},
        {"rows": 7, "cols": 7, "num_flowers": 3, "num_obstacles": 15, "seed": 4009},
        {"rows": 7, "cols": 7, "num_flowers": 3, "num_obstacles": 15, "seed": 5003},
        # 10x10 with 5 flowers, 30 obstacles - sometimes fails
        {"rows": 10, "cols": 10, "num_flowers": 5, "num_obstacles": 30, "seed": 1005},
        {"rows": 10, "cols": 10, "num_flowers": 5, "num_obstacles": 30, "seed": 3005},
        {"rows": 10, "cols": 10, "num_flowers": 5, "num_obstacles": 30, "seed": 5005},
    ]

    print("Analyzing failing boards...\n")

    for i, config in enumerate(test_configs, 1):
        board = RandomBoardGenerator.generate_board(**config, player=player)

        print(
            f"Test {i}: {config['rows']}x{config['cols']}, "
            f"{config['num_flowers']} flowers, {config['num_obstacles']} obstacles (seed={config['seed']})"
        )

        # Check if path exists from robot to princess
        robot_pos = board.robot.position
        princess_pos = board.princess_position

        # Check adjacent positions to princess
        adjacent_to_princess = AIGreedyPlayer._get_adjacent_positions(princess_pos, board)
        print(f"  Princess at {princess_pos}, {len(adjacent_to_princess)} adjacent empty cells")

        # Check if robot can reach any adjacent position
        can_reach_princess = False
        if adjacent_to_princess:
            target = min(adjacent_to_princess, key=lambda p: robot_pos.manhattan_distance(p))
            path = AIGreedyPlayer._find_path(board, robot_pos, target)
            can_reach_princess = len(path) > 0
            print(f"  Path from robot to princess: {'YES' if can_reach_princess else 'NO'}")
        else:
            print("  Path from robot to princess: NO (princess surrounded)")

        # Check flower accessibility
        accessible_flowers = 0
        for flower in board.flowers:
            adjacent_to_flower = AIGreedyPlayer._get_adjacent_positions(flower, board)
            if adjacent_to_flower:
                target = min(adjacent_to_flower, key=lambda p: robot_pos.manhattan_distance(p))
                path = AIGreedyPlayer._find_path(board, robot_pos, target)
                if path:
                    accessible_flowers += 1

        print(f"  Accessible flowers: {accessible_flowers}/{len(board.flowers)}")

        # Test it
        result = tester.test_board(board, board_id=f"failing_{i}")

        status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
        print(f"  Result: {status}")
        if not result["success"]:
            print(f"  Reason: {result.get('failure_reason', 'unknown')}")
            print(f"  Detail: {result.get('failure_detail', 'N/A')}")
            failing_boards.append((config, result))
        print()

    # Summary
    print(f"\n{'='*60}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*60}")
    print(f"Total Tested: {len(test_configs)}")
    print(f"Failed: {len(failing_boards)}")
    print(
        f"Success Rate: {(len(test_configs) - len(failing_boards)) / len(test_configs) * 100:.1f}%"
    )

    if failing_boards:
        print("\nCommon Patterns in Failing Boards:")
        stuck_count = sum(
            1 for _, r in failing_boards if r.get("failure_reason") == "stuck_with_flowers"
        )
        no_path_count = sum(
            1 for _, r in failing_boards if r.get("failure_reason") == "no_path_to_flower"
        )
        print(f"  - stuck_with_flowers: {stuck_count}")
        print(f"  - no_path_to_flower: {no_path_count}")

    return failing_boards


if __name__ == "__main__":
    failing_boards = save_failing_boards()
