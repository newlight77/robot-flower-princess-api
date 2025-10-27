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
    rows, cols = 5, 5

    if scenario == "pick_flower":
        # Robot at (2, 2), flower at (2, 2), princess at (4, 4)
        game_state = {
            "board": {
                "rows": rows,
                "cols": cols,
                "flowers_positions": [{"row": 2, "col": 2}],
                "obstacles_positions": [],
                "initial_flowers_count": 1,
                "initial_obstacles_count": 0,
            },
            "robot": {
                "position": {"row": 2, "col": 2},
                "orientation": "EAST",
                "flowers_collected": [],
                "flowers_delivered": [],
                "flowers_collection_capacity": 5,
                "obstacles_cleaned": [],
            },
            "princess": {"position": {"row": 4, "col": 4}, "flowers_received": [], "mood": "neutral"},
        }
        return game_state, "pick", None

    elif scenario == "give_flowers":
        # Robot at (3, 4) with flowers, princess at (4, 4)
        game_state = {
            "board": {
                "rows": rows,
                "cols": cols,
                "flowers_positions": [],
                "obstacles_positions": [],
                "initial_flowers_count": 2,
                "initial_obstacles_count": 0,
            },
            "robot": {
                "position": {"row": 3, "col": 4},
                "orientation": "SOUTH",
                "flowers_collected": [{"row": 1, "col": 1}, {"row": 2, "col": 2}],
                "flowers_delivered": [],
                "flowers_collection_capacity": 5,
                "obstacles_cleaned": [],
            },
            "princess": {"position": {"row": 4, "col": 4}, "flowers_received": [], "mood": "neutral"},
        }
        return game_state, "give", None

    elif scenario == "move_to_flower":
        # Robot at (1, 1), flower at (1, 3)
        game_state = {
            "board": {
                "rows": rows,
                "cols": cols,
                "flowers_positions": [{"row": 1, "col": 3}],
                "obstacles_positions": [],
                "initial_flowers_count": 1,
                "initial_obstacles_count": 0,
            },
            "robot": {
                "position": {"row": 1, "col": 1},
                "orientation": "EAST",
                "flowers_collected": [],
                "flowers_delivered": [],
                "flowers_collection_capacity": 5,
                "obstacles_cleaned": [],
            },
            "princess": {"position": {"row": 4, "col": 4}, "flowers_received": [], "mood": "neutral"},
        }
        return game_state, "move", "EAST"

    elif scenario == "move_to_princess":
        # Robot at (2, 4) with flowers, princess at (4, 4)
        game_state = {
            "board": {
                "rows": rows,
                "cols": cols,
                "flowers_positions": [],
                "obstacles_positions": [],
                "initial_flowers_count": 1,
                "initial_obstacles_count": 0,
            },
            "robot": {
                "position": {"row": 2, "col": 4},
                "orientation": "SOUTH",
                "flowers_collected": [{"row": 1, "col": 1}],
                "flowers_delivered": [],
                "flowers_collection_capacity": 5,
                "obstacles_cleaned": [],
            },
            "princess": {"position": {"row": 4, "col": 4}, "flowers_received": [], "mood": "neutral"},
        }
        return game_state, "move", "SOUTH"

    elif scenario == "clean_obstacle":
        # Robot at (2, 2), obstacle at (2, 2)
        game_state = {
            "board": {
                "rows": rows,
                "cols": cols,
                "flowers_positions": [{"row": 3, "col": 3}],
                "obstacles_positions": [{"row": 2, "col": 2}],
                "initial_flowers_count": 1,
                "initial_obstacles_count": 1,
            },
            "robot": {
                "position": {"row": 2, "col": 2},
                "orientation": "EAST",
                "flowers_collected": [],
                "flowers_delivered": [],
                "flowers_collection_capacity": 5,
                "obstacles_cleaned": [],
            },
            "princess": {"position": {"row": 4, "col": 4}, "flowers_received": [], "mood": "neutral"},
        }
        return game_state, "clean", None

    else:  # random
        # Generate random valid scenario
        scenarios = ["pick_flower", "give_flowers", "move_to_flower", "move_to_princess", "clean_obstacle"]
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
