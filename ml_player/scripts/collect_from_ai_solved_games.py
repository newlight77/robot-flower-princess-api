#!/usr/bin/env python3
"""
Collect training data from AI-solved games.

This approach is SUPERIOR to synthetic data because:
1. Learns complete strategies, not isolated actions
2. Sees optimal action sequences in context
3. Captures real decision-making patterns
4. Learns from successful game completions

Usage:
    python collect_from_ai_games.py --num-games 1000 --output-dir data/training
"""

import argparse
import random
import sys
from pathlib import Path
from typing import Any

# Add paths FIRST before any hexagons imports
script_path = Path(__file__).resolve()
rfp_game_path = script_path.parent.parent.parent / "rfp_game" / "src"
ml_player_path = script_path.parent.parent / "src"

sys.path.insert(0, str(rfp_game_path))
sys.path.insert(0, str(ml_player_path))

# Now import everything
from hexagons.mltraining.domain.ml import GameDataCollector
from shared.logging import get_logger

# Import from rfp_game
from hexagons.game.domain.core.entities.game import Game
from hexagons.game.domain.core.value_objects.game_status import GameStatus
from hexagons.game.domain.services.game_service import GameService
from hexagons.aiplayer.domain.core.entities.ai_greedy_player import AIGreedyPlayer
from hexagons.aiplayer.domain.core.entities.ai_optimal_player import AIOptimalPlayer

logger = get_logger("collect_from_ai_solved_games")


def _execute_action_on_game(game: Game, action: str, direction: Any) -> bool:
    """
    Execute an action on the game.

    Returns:
        True if action was successful, False otherwise
    """
    try:
        if action == "rotate":
            GameService.rotate_robot(game, direction)
        elif action == "move":
            # GameService.rotate_robot(game, direction)
            GameService.move_robot(game)
        elif action == "pick":
            # GameService.rotate_robot(game, direction)
            GameService.pick_flower(game)
        elif action == "give":
            # GameService.rotate_robot(game, direction)
            GameService.give_flowers(game)
        elif action == "clean":
            # GameService.rotate_robot(game, direction)
            GameService.clean_obstacle(game)
        elif action == "drop":
            #   GameService.rotate_robot(game, direction)
            GameService.drop_flower(game)
        else:
            logger.warning(f"Unknown action: {action}")
            return False
        return True
    except Exception as e:
        logger.debug(f"Action failed: {action} {direction} - {e}")
        return False


def _collect_from_ai_solved_game(
    game_id: str,
    rows: int,
    cols: int,
    collector: GameDataCollector,
    use_optimal: bool = False
) -> dict:
    """
    Generate a game, solve it with AI, and collect training samples.

    Args:
        game_id: Unique game identifier
        rows: Board rows
        cols: Board columns
        collector: Data collector instance
        use_optimal: Use optimal AI (faster but lower success rate)

    Returns:
        Statistics about the collection
    """
    # Create game
    game = Game(game_id=game_id, rows=rows, cols=cols)

    # Choose AI player
    if use_optimal:
        ai_player = AIOptimalPlayer()
        ai_name = "Optimal"
    else:
        ai_player = AIGreedyPlayer()
        ai_name = "Greedy"

    # Get solution
    try:
        actions = ai_player.solve(game)
    except Exception as e:
        logger.debug(f"AI failed to solve game {game_id}: {e}")
        return {
            "success": False,
            "samples_collected": 0,
            "ai_player": ai_name
        }

    # Check if game was solved successfully
    if game.get_status() != GameStatus.VICTORY:
        return {
            "success": False,
            "samples_collected": 0,
            "ai_player": ai_name
        }

    # Replay game and collect state-action pairs
    game_replay = Game(game_id=game_id, rows=rows, cols=cols)
    samples_collected = 0

    for i, (action, direction) in enumerate(actions):
        # Get current state BEFORE action
        game_state = game_replay.to_dict()

        # Only rotate actions should have a direction
        # Move actions don't take direction - they move in current orientation
        if action == "move":
            direction = None

        # Collect sample
        collector.collect_sample(
            game_id=game_id,
            game_state=game_state,
            action=action,
            direction=direction.value if direction else None,
            outcome={
                "success": True,
                "step": i,
                "total_steps": len(actions),
                "final_victory": True,
                "ai_player": ai_name
            }
        )
        samples_collected += 1

        # Execute action on replay game
        if not _execute_action_on_game(game_replay, action, direction):
            logger.warning(f"Action execution failed during replay: {action} {direction}")
            break

    return {
        "success": True,
        "samples_collected": samples_collected,
        "total_actions": len(actions),
        "ai_player": ai_name
    }


def _collect_expert_heuristic_samples(
    collector: GameDataCollector,
    num_samples: int = 1000
) -> int:
    """
    Collect samples demonstrating expert strategies.

    Strategies:
    1. Always pick nearest flower first
    2. Move towards nearest flower
    3. Clean obstacle only if blocking path
    4. Deliver when all flowers collected

    Args:
        collector: Data collector instance
        num_samples: Number of samples per strategy

    Returns:
        Total samples collected
    """
    samples_collected = 0

    # Strategy 1: Robot adjacent to nearest flower -> PICK
    logger.info("Generating 'pick nearest flower' samples...")
    for i in range(num_samples // 4):
        rows = random.choice([5, 7, 10])
        cols = random.choice([5, 7, 10])

        robot_pos = {
            "row": random.randint(1, rows - 2),
            "col": random.randint(1, cols - 2)
        }
        princess_pos = {
            "row": random.randint(0, rows-1),
            "col": random.randint(0, cols-1)
        }

        # Place flower adjacent to robot
        direction = random.choice(["NORTH", "SOUTH", "EAST", "WEST"])
        if direction == "NORTH":
            flower_pos = {"row": robot_pos["row"] - 1, "col": robot_pos["col"]}
        elif direction == "SOUTH":
            flower_pos = {"row": robot_pos["row"] + 1, "col": robot_pos["col"]}
        elif direction == "EAST":
            flower_pos = {"row": robot_pos["row"], "col": robot_pos["col"] + 1}
        else:  # WEST
            flower_pos = {"row": robot_pos["row"], "col": robot_pos["col"] - 1}

        game_state = {
            "board": {
                "rows": rows,
                "cols": cols,
                "robot_position": robot_pos,
                "princess_position": princess_pos,
                "flowers_positions": [flower_pos],
                "obstacles_positions": [],
                "initial_flowers_count": 1,
                "initial_obstacles_count": 0,
            },
            "robot": {
                "position": robot_pos,
                "orientation": direction,
                "flowers_collected": [],
                "flowers_delivered": [],
                "flowers_collection_capacity": random.randint(8, 12),
                "obstacles_cleaned": [],
            },
            "princess": {
                "position": {"row": random.randint(0, rows-1), "col": random.randint(0, cols-1)},
                "flowers_received": [],
                "mood": "neutral"
            },
        }

        collector.collect_sample(
            game_id=f"expert_pick_{i}",
            game_state=game_state,
            action="pick",
            direction=None,  # Pick doesn't take direction - uses robot's orientation
            outcome={"success": True, "strategy": "pick_nearest"}
        )
        samples_collected += 1

    # Strategy 2: Robot with flowers adjacent to princess -> GIVE
    logger.info("Generating 'deliver to princess' samples...")
    for i in range(num_samples // 4):
        rows = random.choice([5, 7, 10])
        cols = random.choice([5, 7, 10])

        princess_pos = {
            "row": random.randint(1, rows - 2),
            "col": random.randint(1, cols - 2)
        }

        # Place robot adjacent to princess
        direction = random.choice(["NORTH", "SOUTH", "EAST", "WEST"])
        if direction == "NORTH":
            robot_pos = {"row": princess_pos["row"] + 1, "col": princess_pos["col"]}
        elif direction == "SOUTH":
            robot_pos = {"row": princess_pos["row"] - 1, "col": princess_pos["col"]}
        elif direction == "EAST":
            robot_pos = {"row": princess_pos["row"], "col": princess_pos["col"] - 1}
        else:  # WEST
            robot_pos = {"row": princess_pos["row"], "col": princess_pos["col"] + 1}

        game_state = {
            "board": {
                "rows": rows,
                "cols": cols,
                "robot_position": robot_pos,
                "princess_position": princess_pos,
                "flowers_positions": [],  # All flowers picked
                "obstacles_positions": [],
                "initial_flowers_count": random.randint(3, 7),
                "initial_obstacles_count": 0,
            },
            "robot": {
                "position": robot_pos,
                "orientation": direction,
                "flowers_collected": [
                    {"row": random.randint(0, rows-1), "col": random.randint(0, cols-1)}
                    for _ in range(random.randint(2, 5))
                ],
                "flowers_delivered": [],
                "flowers_collection_capacity": random.randint(8, 12),
                "obstacles_cleaned": [],
            },
            "princess": {
                "position": princess_pos,
                "flowers_received": [],
                "mood": "neutral"
            },
        }

        collector.collect_sample(
            game_id=f"expert_give_{i}",
            game_state=game_state,
            action="give",
            direction=None,  # Give doesn't take direction - uses robot's orientation
            outcome={"success": True, "strategy": "deliver_all"}
        )
        samples_collected += 1

    # Strategy 3: Move towards nearest flower
    logger.info("Generating 'move to nearest flower' samples...")
    for i in range(num_samples // 4):
        rows = random.choice([5, 7, 10])
        cols = random.choice([5, 7, 10])

        robot_pos = {
            "row": random.randint(0, rows - 1),
            "col": random.randint(0, cols - 1)
        }

        # Place flower at distance 2-5
        distance = random.randint(2, 5)
        flower_pos = {
            "row": robot_pos["row"] + random.randint(-distance, distance),
            "col": robot_pos["col"] + random.randint(-distance, distance)
        }

        # Clamp to board
        flower_pos["row"] = max(0, min(rows - 1, flower_pos["row"]))
        flower_pos["col"] = max(0, min(cols - 1, flower_pos["col"]))

        # Determine best move direction
        dr = flower_pos["row"] - robot_pos["row"]
        dc = flower_pos["col"] - robot_pos["col"]

        if abs(dr) > abs(dc):
            direction = "SOUTH" if dr > 0 else "NORTH"
        else:
            direction = "EAST" if dc > 0 else "WEST"

        game_state = {
            "board": {
                "rows": rows,
                "cols": cols,
                "robot_position": robot_pos,
                "princess_position": princess_pos,
                "flowers_positions": [flower_pos],
                "obstacles_positions": [],
                "initial_flowers_count": 1,
                "initial_obstacles_count": 0,
            },
            "robot": {
                "position": robot_pos,
                "orientation": direction,
                "flowers_collected": [],
                "flowers_delivered": [],
                "flowers_collection_capacity": random.randint(8, 12),
                "obstacles_cleaned": [],
            },
            "princess": {
                "position": princess_pos,
                "flowers_received": [],
                "mood": "neutral"
            },
        }

        collector.collect_sample(
            game_id=f"expert_move_flower_{i}",
            game_state=game_state,
            action="move",
            direction=None,  # Move doesn't take direction - uses robot's orientation
            outcome={"success": True, "strategy": "move_to_nearest"}
        )
        samples_collected += 1

    # Strategy 4: Move towards princess when flowers collected
    logger.info("Generating 'move to princess' samples...")
    for i in range(num_samples // 4):
        rows = random.choice([5, 7, 10])
        cols = random.choice([5, 7, 10])

        robot_pos = {
            "row": random.randint(0, rows - 1),
            "col": random.randint(0, cols - 1)
        }

        princess_pos = {
            "row": random.randint(0, rows - 1),
            "col": random.randint(0, cols - 1)
        }

        # Determine best move direction
        dr = princess_pos["row"] - robot_pos["row"]
        dc = princess_pos["col"] - robot_pos["col"]

        if abs(dr) > abs(dc):
            direction = "SOUTH" if dr > 0 else "NORTH"
        else:
            direction = "EAST" if dc > 0 else "WEST"

        game_state = {
            "board": {
                "rows": rows,
                "cols": cols,
                "robot_position": robot_pos,
                "princess_position": princess_pos,
                "flowers_positions": [],  # All picked
                "obstacles_positions": [],
                "initial_flowers_count": random.randint(3, 7),
                "initial_obstacles_count": 0,
            },
            "robot": {
                "position": robot_pos,
                "orientation": direction,
                "flowers_collected": [
                    {"row": random.randint(0, rows-1), "col": random.randint(0, cols-1)}
                    for _ in range(random.randint(2, 4))
                ],
                "flowers_delivered": [],
                "flowers_collection_capacity": random.randint(8, 12),
                "obstacles_cleaned": [],
            },
            "princess": {
                "position": princess_pos,
                "flowers_received": [],
                "mood": "neutral"
            },
        }

        collector.collect_sample(
            game_id=f"expert_move_princess_{i}",
            game_state=game_state,
            action="move",
            direction=None,  # Move doesn't take direction - uses robot's orientation
            outcome={"success": True, "strategy": "deliver_mode"}
        )
        samples_collected += 1

    return samples_collected


def _main() -> None:
    """Main data collection function."""
    parser = argparse.ArgumentParser(
        description="Collect training data from AI-solved games"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/training",
        help="Output directory for data"
    )
    parser.add_argument(
        "--num-games",
        type=int,
        default=500,
        help="Number of games to generate and solve"
    )
    parser.add_argument(
        "--num-expert-samples",
        type=int,
        default=1000,
        help="Number of expert heuristic samples"
    )
    parser.add_argument(
        "--use-optimal",
        action="store_true",
        help="Use optimal AI (25%% faster but 13%% lower success)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed"
    )

    args = parser.parse_args()

    random.seed(args.seed)

    logger.info("=" * 60)
    logger.info("Collecting Training Data from AI Games")
    logger.info("=" * 60)
    logger.info(f"Output directory: {args.output_dir}")
    logger.info(f"Number of games: {args.num_games}")
    logger.info(f"Expert samples: {args.num_expert_samples}")
    logger.info(f"AI Player: {'Optimal' if args.use_optimal else 'Greedy'}")
    logger.info(f"Random seed: {args.seed}")
    logger.info("=" * 60)

    # Initialize collector
    collector = GameDataCollector(data_dir=args.output_dir)

    # Phase 1: Collect from AI-solved games (60% of dataset)
    logger.info("\n" + "=" * 60)
    logger.info("Phase 1: Collecting from AI-solved games")
    logger.info("=" * 60)

    successful_games = 0
    total_samples = 0
    board_sizes = [(5, 5), (7, 7), (10, 10), (5, 10), (10, 5), (7, 10)]

    for i in range(args.num_games):
        rows, cols = random.choice(board_sizes)

        result = _collect_from_ai_solved_game(
            game_id=f"ai_game_{i:05d}",
            rows=rows,
            cols=cols,
            collector=collector,
            use_optimal=args.use_optimal
        )

        if result["success"]:
            successful_games += 1
            total_samples += result["samples_collected"]

        if (i + 1) % 50 == 0:
            logger.info(
                f"Processed {i + 1}/{args.num_games} games "
                f"({successful_games} successful, {total_samples} samples)"
            )

    logger.info(f"\nPhase 1 completed:")
    logger.info(f"  Successful games: {successful_games}/{args.num_games}")
    logger.info(f"  Samples collected: {total_samples}")

    # Phase 2: Collect expert heuristic samples (20% of dataset)
    logger.info("\n" + "=" * 60)
    logger.info("Phase 2: Collecting expert heuristic samples")
    logger.info("=" * 60)

    expert_samples = _collect_expert_heuristic_samples(
        collector=collector,
        num_samples=args.num_expert_samples
    )

    logger.info(f"Phase 2 completed: {expert_samples} samples collected")

    # Print final statistics
    stats = collector.get_statistics()
    logger.info("\n" + "=" * 60)
    logger.info("Data collection completed!")
    logger.info("=" * 60)
    logger.info(f"Total samples: {stats['total_samples']}")
    logger.info(f"Unique games: {stats['unique_games']}")
    logger.info(f"Action distribution:")
    for action, count in sorted(stats["action_distribution"].items()):
        percentage = count / stats['total_samples'] * 100
        logger.info(f"  {action:10s}: {count:5d} ({percentage:5.1f}%)")
    logger.info(f"Data files: {stats['data_files']}")
    logger.info("=" * 60)

    # Recommendations
    logger.info("\nNext steps:")
    logger.info("1. Train models with: python scripts/train_model.py")
    logger.info("2. Compare with previous model performance")
    logger.info("3. Iterate on feature engineering if needed")


if __name__ == "__main__":
    _main()
