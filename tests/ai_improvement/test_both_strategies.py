"""Test both AI strategies side-by-side."""

from hexagons.game.domain.core.entities.game import Game
from hexagons.game.domain.core.entities.robot import Robot
from hexagons.game.domain.core.entities.position import Position
from hexagons.game.domain.core.value_objects.direction import Direction
from hexagons.aiplayer.domain.core.entities.ai_greedy_player import AIGreedyPlayer
from hexagons.aiplayer.domain.core.entities.ai_optimal_player import AIOptimalPlayer
import copy

def create_test_board():
    """Create a simple test board with 2 flowers and some obstacles."""
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    board = Game(rows=5, cols=5, robot=robot, princess_position=Position(4, 4))
    board.flowers = {Position(1, 1), Position(3, 3)}
    board.obstacles = {Position(2, 2), Position(1, 3)}
    board.initial_flower_count = len(board.flowers)
    return board

def test_strategy(board, strategy_name, solver_class):
    """Test a single strategy."""
    board_copy = copy.deepcopy(board)
    actions = solver_class.solve(board_copy)

    success = board_copy.get_status().value == "victory"

    print(f"\n{strategy_name}:")
    print(f"  Actions taken: {len(actions)}")
    print(f"  Success: {'✅ YES' if success else '❌ NO'}")
    print(f"  Flowers delivered: {board_copy.flowers_delivered}")
    print(f"  Obstacles cleaned: {len(board_copy.robot.obstacles_cleaned)}")

    return success, len(actions)

if __name__ == "__main__":
    print("="*60)
    print("AI STRATEGY COMPARISON TEST")
    print("="*60)

    board = create_test_board()

    print(f"\nInitial Board (5x5):")
    print(f"  Robot: {board.robot.position}")
    print(f"  Princess: {board.princess_position}")
    print(f"  Flowers: {len(board.flowers)} at {list(board.flowers)}")
    print(f"  Obstacles: {len(board.obstacles)} at {list(board.obstacles)}")

    # Test Greedy (safe) strategy
    greedy_success, greedy_actions = test_strategy(
        board, "Greedy Strategy (Safe & Reliable)", AIGreedyPlayer
    )

    # Test Optimal (fast) strategy
    optimal_success, optimal_actions = test_strategy(
        board, "Optimal Strategy (Fast & Efficient)", AIOptimalPlayer
    )

    print(f"\n{'='*60}")
    print("COMPARISON:")
    print(f"{'='*60}")

    if greedy_actions > 0 and optimal_actions > 0:
        efficiency = ((greedy_actions - optimal_actions) / greedy_actions) * 100
        print(f"  Optimal is {efficiency:.1f}% more efficient")

    print(f"  Both successful: {greedy_success and optimal_success}")

    print(f"\nRecommendation:")
    print(f"  - Use 'greedy' for reliability (default)")
    print(f"  - Use 'optimal' when speed matters more than success rate")
    print(f"="*60)
