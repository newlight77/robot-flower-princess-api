#!/usr/bin/env python3
"""
Generate synthetic training data for ML models.

Creates game scenarios and optimal actions for initial training.
"""

import argparse
import random
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hexagons.mlplayer.domain.ml import GameDataCollector
from shared.logging import logger


def generate_sample_game_state(scenario: str = "random") -> tuple[dict, str, str | None]:
    """
    Generate a sample game state with corresponding optimal action.

    Args:
        scenario: Type of scenario to generate

    Returns:
        Tuple of (game_state, action, direction)
    """
    # Randomize board size for more diversity
    rows = random.choice([5, 7, 10])
    cols = random.choice([5, 7, 10])

    # Random orientations
    orientations = ["NORTH", "SOUTH", "EAST", "WEST"]

    # Random positions
    robot_pos = {"row": random.randint(0, rows - 1), "col": random.randint(0, cols - 1)}
    princess_pos = {"row": random.randint(0, rows - 1), "col": random.randint(0, cols - 1)}

    # Ensure robot and princess are not at the same position
    while robot_pos == princess_pos:
        princess_pos = {"row": random.randint(0, rows - 1), "col": random.randint(0, cols - 1)}

    if scenario == "pick_flower":
        # Robot at flower position
        game_state = {
            "board": {
                "rows": rows,
                "cols": cols,
                "flowers_positions": [robot_pos],
                "obstacles_positions": [],
                "initial_flowers_count": 1,
                "initial_obstacles_count": 0,
            },
            "robot": {
                "position": robot_pos,
                "orientation": random.choice(orientations),
                "flowers_collected": [],
                "flowers_delivered": [],
                "flowers_collection_capacity": random.randint(5, 12),
                "obstacles_cleaned": [],
            },
            "princess": {"position": princess_pos, "flowers_received": [], "mood": "neutral"},
        }
        return game_state, "pick", game_state["robot"]["orientation"]

    elif scenario == "give_flowers":
        # Robot adjacent to princess with flowers
        adjacent_positions = [
            {"row": princess_pos["row"] + 1, "col": princess_pos["col"]},
            {"row": princess_pos["row"] - 1, "col": princess_pos["col"]},
            {"row": princess_pos["row"], "col": princess_pos["col"] + 1},
            {"row": princess_pos["row"], "col": princess_pos["col"] - 1},
        ]
        # Filter valid positions
        valid_positions = [
            p for p in adjacent_positions
            if 0 <= p["row"] < rows and 0 <= p["col"] < cols
        ]
        robot_pos = random.choice(valid_positions) if valid_positions else robot_pos

        # Determine direction to princess
        direction = None
        if robot_pos["row"] < princess_pos["row"]:
            direction = "SOUTH"
        elif robot_pos["row"] > princess_pos["row"]:
            direction = "NORTH"
        elif robot_pos["col"] < princess_pos["col"]:
            direction = "EAST"
        else:
            direction = "WEST"

        game_state = {
            "board": {
                "rows": rows,
                "cols": cols,
                "flowers_positions": [],
                "obstacles_positions": [],
                "initial_flowers_count": random.randint(2, 5),
                "initial_obstacles_count": 0,
            },
            "robot": {
                "position": robot_pos,
                "orientation": direction,
                "flowers_collected": [{"row": random.randint(0, rows-1), "col": random.randint(0, cols-1)}
                                     for _ in range(random.randint(1, 3))],
                "flowers_delivered": [],
                "flowers_collection_capacity": random.randint(5, 12),
                "obstacles_cleaned": [],
            },
            "princess": {"position": princess_pos, "flowers_received": [], "mood": "neutral"},
        }
        return game_state, "give", direction

    elif scenario == "move_to_flower":
        # Robot moving toward flower
        flower_pos = {"row": random.randint(0, rows - 1), "col": random.randint(0, cols - 1)}
        while flower_pos == robot_pos or flower_pos == princess_pos:
            flower_pos = {"row": random.randint(0, rows - 1), "col": random.randint(0, cols - 1)}

        # Determine best direction to move toward flower
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
                "flowers_collection_capacity": random.randint(5, 12),
                "obstacles_cleaned": [],
            },
            "princess": {"position": princess_pos, "flowers_received": [], "mood": "neutral"},
        }
        return game_state, "move", direction

    elif scenario == "move_to_princess":
        # Robot with flowers moving toward princess
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
                "flowers_positions": [],
                "obstacles_positions": [],
                "initial_flowers_count": random.randint(1, 3),
                "initial_obstacles_count": 0,
            },
            "robot": {
                "position": robot_pos,
                "orientation": direction,
                "flowers_collected": [{"row": random.randint(0, rows-1), "col": random.randint(0, cols-1)}],
                "flowers_delivered": [],
                "flowers_collection_capacity": random.randint(5, 12),
                "obstacles_cleaned": [],
            },
            "princess": {"position": princess_pos, "flowers_received": [], "mood": "neutral"},
        }
        return game_state, "move", direction

    elif scenario == "clean_obstacle":
        # Robot at obstacle position
        obstacle_pos = robot_pos.copy()

        game_state = {
            "board": {
                "rows": rows,
                "cols": cols,
                "flowers_positions": [{"row": random.randint(0, rows-1), "col": random.randint(0, cols-1)}],
                "obstacles_positions": [obstacle_pos],
                "initial_flowers_count": 1,
                "initial_obstacles_count": 1,
            },
            "robot": {
                "position": robot_pos,
                "orientation": random.choice(orientations),
                "flowers_collected": [],
                "flowers_delivered": [],
                "flowers_collection_capacity": random.randint(5, 12),
                "obstacles_cleaned": [],
            },
            "princess": {"position": princess_pos, "flowers_received": [], "mood": "neutral"},
        }
        return game_state, "clean", game_state["robot"]["orientation"]

    elif scenario == "rotate":
        # Robot needs to rotate to face target
        target_pos = {"row": random.randint(0, rows - 1), "col": random.randint(0, cols - 1)}
        while target_pos == robot_pos:
            target_pos = {"row": random.randint(0, rows - 1), "col": random.randint(0, cols - 1)}

        # Determine target direction
        dr = target_pos["row"] - robot_pos["row"]
        dc = target_pos["col"] - robot_pos["col"]

        if abs(dr) > abs(dc):
            target_direction = "SOUTH" if dr > 0 else "NORTH"
        else:
            target_direction = "EAST" if dc > 0 else "WEST"

        # Robot is facing wrong direction
        current_orientation = random.choice([o for o in orientations if o != target_direction])

        game_state = {
            "board": {
                "rows": rows,
                "cols": cols,
                "flowers_positions": [target_pos],
                "obstacles_positions": [],
                "initial_flowers_count": 1,
                "initial_obstacles_count": 0,
            },
            "robot": {
                "position": robot_pos,
                "orientation": current_orientation,
                "flowers_collected": [],
                "flowers_delivered": [],
                "flowers_collection_capacity": random.randint(5, 12),
                "obstacles_cleaned": [],
            },
            "princess": {"position": princess_pos, "flowers_received": [], "mood": "neutral"},
        }
        return game_state, "rotate", target_direction

    elif scenario == "drop":
        # Robot with flowers needs to drop one
        game_state = {
            "board": {
                "rows": rows,
                "cols": cols,
                "flowers_positions": [],
                "obstacles_positions": [],
                "initial_flowers_count": random.randint(2, 4),
                "initial_obstacles_count": 0,
            },
            "robot": {
                "position": robot_pos,
                "orientation": random.choice(orientations),
                "flowers_collected": [{"row": random.randint(0, rows-1), "col": random.randint(0, cols-1)}
                                     for _ in range(random.randint(5, 8))],  # Robot is at or near capacity
                "flowers_delivered": [],
                "flowers_collection_capacity": 8,
                "obstacles_cleaned": [],
            },
            "princess": {"position": princess_pos, "flowers_received": [], "mood": "neutral"},
        }
        return game_state, "drop", game_state["robot"]["orientation"]

    else:  # random
        # Generate random valid scenario
        scenarios = ["pick_flower", "give_flowers", "move_to_flower", "move_to_princess", "clean_obstacle", "rotate", "drop"]
        return generate_sample_game_state(random.choice(scenarios))


def main() -> None:
    """Generate training data."""
    parser = argparse.ArgumentParser(description="Generate synthetic training data")
    parser.add_argument("--output-dir", type=str, default="data/training", help="Output directory for data")
    parser.add_argument("--num-samples", type=int, default=1000, help="Number of samples to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")

    args = parser.parse_args()

    random.seed(args.seed)

    logger.info("=" * 60)
    logger.info("Generating Synthetic Training Data")
    logger.info("=" * 60)
    logger.info(f"Output directory: {args.output_dir}")
    logger.info(f"Number of samples: {args.num_samples}")
    logger.info(f"Random seed: {args.seed}")
    logger.info("=" * 60)

    # Initialize collector
    collector = GameDataCollector(data_dir=args.output_dir)

    # Generate samples
    scenario_types = ["pick_flower", "give_flowers", "move_to_flower", "move_to_princess", "clean_obstacle"]

    for i in range(args.num_samples):
        scenario = random.choice(scenario_types)
        game_state, action, direction = generate_sample_game_state(scenario)

        collector.collect_sample(
            game_id=f"synthetic_{i:05d}",
            game_state=game_state,
            action=action,
            direction=direction,
            outcome={"success": True},  # Assume optimal actions succeed
        )

        if (i + 1) % 100 == 0:
            logger.info(f"Generated {i + 1}/{args.num_samples} samples...")

    # Print statistics
    stats = collector.get_statistics()
    logger.info("=" * 60)
    logger.info("Data generation completed!")
    logger.info("=" * 60)
    logger.info(f"Total samples: {stats['total_samples']}")
    logger.info(f"Unique games: {stats['unique_games']}")
    logger.info(f"Action distribution:")
    for action, count in stats["action_distribution"].items():
        logger.info(f"  {action}: {count} ({count / stats['total_samples'] * 100:.1f}%)")
    logger.info(f"Data files: {stats['data_files']}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
