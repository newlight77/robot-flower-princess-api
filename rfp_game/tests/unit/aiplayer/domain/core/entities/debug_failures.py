"""Debug specific failures with detailed logging."""

from tests.unit.aiplayer.domain.core.entities.random_board_tester import RandomBoardGenerator
from tests.unit.aiplayer.domain.core.entities.ai_player_tester import AIPlayerTester
from hexagons.aiplayer.domain.core.entities.ai_greedy_player import AIGreedyPlayer
from hexagons.game.domain.core.entities.position import Position


def debug_failing_board(seed, config):
    """Debug a single board with detailed state tracking."""
    print(f"\n{'='*70}")
    print(f"DEBUG: {config['rows']}x{config['cols']}, seed={seed}")
    print(f"{'='*70}")

    board = RandomBoardGenerator.generate_board(**config, seed=seed, player=AIGreedyPlayer())

    # Save initial state
    initial_robot_pos = board.robot.position
    initial_princess_pos = board.princess.position
    initial_flowers = len(board.flowers)
    initial_obstacles = len(board.obstacles)

    print("Initial State:")
    print(f"  Robot: {initial_robot_pos}")
    print(f"  Princess: {initial_princess_pos}")
    print(f"  Flowers: {initial_flowers} at {list(board.flowers)[:3]}{'...' if initial_flowers > 3 else ''}")
    print(f"  Obstacles: {initial_obstacles}")

    # Check initial paths
    princess_adj = AIGreedyPlayer._get_adjacent_positions(initial_princess_pos, board)
    print(f"  Princess accessible: {len(princess_adj)} adjacent empty cells")

    if princess_adj:
        closest_princess = min(princess_adj, key=lambda p: initial_robot_pos.manhattan_distance(p))
        path_to_princess = AIGreedyPlayer._find_path(board, initial_robot_pos, closest_princess)
        print(f"  Initial path to princess: {'YES (%d steps)' % len(path_to_princess) if path_to_princess else 'NO'}")

    # Check flower accessibility
    accessible = 0
    for flower in board.flowers:
        adj = AIGreedyPlayer._get_adjacent_positions(flower, board)
        if adj:
            target = min(adj, key=lambda p: initial_robot_pos.manhattan_distance(p))
            if AIGreedyPlayer._find_path(board, initial_robot_pos, target):
                accessible += 1
    print(f"  Accessible flowers: {accessible}/{initial_flowers}")

    # Try to solve
    print("\nAttempting to solve...")
    tester = AIPlayerTester()
    result = tester.test_board(board, board_id=f"debug_{seed}")

    print(f"\nResult: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    if not result["success"]:
        print(f"  Reason: {result.get('failure_reason', 'unknown')}")
        print(f"  Detail: {result.get('failure_detail', 'N/A')}")
        print(f"  Actions taken: {result['actions_taken']}")
        print(f"  Flowers picked: {initial_flowers - result['remaining_flowers']}/{initial_flowers}")
        print(f"  Flowers delivered: {result['flowers_delivered']}")
        print(f"  Robot holding: {result['robot_flowers_held']}")
        print(f"  Obstacles cleaned: {result['obstacles_cleaned']}")
        print(f"  Final robot position: {result['robot_final_position']}")

        # Analyze why it failed
        if result.get("failure_reason") == "stuck_with_flowers":
            print(f"\n  Analysis: Robot is holding {result['robot_flowers_held']} flowers")
            # Check if path exists from final position
            if princess_adj:
                final_pos_str = result["robot_final_position"]
                # Parse position string "(row,col)"
                row, col = map(int, final_pos_str.strip("()").split(","))
                final_pos = Position(row, col)
                path_from_final = AIGreedyPlayer._find_path(board, final_pos, closest_princess)
                print(f"  Path from final position to princess: {'YES' if path_from_final else 'NO'}")

        elif result.get("failure_reason") == "robot_blocked":
            print(f"\n  Analysis: Robot gave up after {result['actions_taken']} actions")
            print("  Possible reasons:")
            print("    - No safe flowers found")
            print("    - Can't clean blocking obstacles")
            print("    - Princess completely surrounded")

    return result


# Test the most problematic seeds
failing_configs = [
    # Known stuck_with_flowers cases
    (1002, {"rows": 5, "cols": 5, "num_flowers": 3, "num_obstacles": 8}),
    (1008, {"rows": 5, "cols": 5, "num_flowers": 3, "num_obstacles": 8}),
    (1005, {"rows": 10, "cols": 10, "num_flowers": 5, "num_obstacles": 30}),
    (5005, {"rows": 10, "cols": 10, "num_flowers": 5, "num_obstacles": 30}),
    # Known robot_blocked cases
    (3002, {"rows": 5, "cols": 5, "num_flowers": 3, "num_obstacles": 8}),
    (3009, {"rows": 7, "cols": 7, "num_flowers": 3, "num_obstacles": 15}),
    (1005, {"rows": 10, "cols": 10, "num_flowers": 2, "num_obstacles": 20}),
]

if __name__ == "__main__":
    print("DEBUGGING FAILING BOARDS")
    print("=" * 70)

    results = []
    for seed, config in failing_configs:
        result = debug_failing_board(seed, config)
        results.append(result)

    print(f"\n\n{'='*70}")
    print(f"SUMMARY: {sum(1 for r in results if r['success'])}/{len(results)} succeeded")
    print(f"{'='*70}")
