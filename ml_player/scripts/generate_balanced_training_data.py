"""Generate balanced training data with ALL 9 action classes."""

import argparse
import random
import sys
from pathlib import Path

# Add parent/src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hexagons.mltraining.domain.ml import GameDataCollector
from shared.logging import get_logger

logger = get_logger("generate_balanced_training_data")


def generate_game_state(rows=7, cols=7):
    """Generate a random game state."""
    robot_pos = {"row": random.randint(0, rows - 1), "col": random.randint(0, cols - 1)}
    princess_pos = {"row": random.randint(0, rows - 1), "col": random.randint(0, cols - 1)}

    # Ensure robot and princess are not at the same position
    while robot_pos == princess_pos:
        princess_pos = {"row": random.randint(0, rows - 1), "col": random.randint(0, cols - 1)}

    # Generate random flowers and obstacles
    num_flowers = random.randint(1, 5)
    num_obstacles = random.randint(0, 3)

    flowers = []
    for _ in range(num_flowers):
        flower_pos = {"row": random.randint(0, rows - 1), "col": random.randint(0, cols - 1)}
        if flower_pos != robot_pos and flower_pos != princess_pos:
            flowers.append(flower_pos)

    obstacles = []
    for _ in range(num_obstacles):
        obs_pos = {"row": random.randint(0, rows - 1), "col": random.randint(0, cols - 1)}
        if obs_pos != robot_pos and obs_pos != princess_pos and obs_pos not in flowers:
            obstacles.append(obs_pos)

    orientation = random.choice(["NORTH", "SOUTH", "EAST", "WEST"])

    return {
        "board": {
            "rows": rows,
            "cols": cols,
            "robot_position": robot_pos,
            "princess_position": princess_pos,
            "flowers_positions": flowers,
            "obstacles_positions": obstacles,
            "initial_flowers_count": len(flowers),
            "initial_obstacles_count": len(obstacles),
        },
        "robot": {
            "position": robot_pos,
            "orientation": orientation,
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


def main():
    """Generate balanced training data with ALL 9 action classes."""
    parser = argparse.ArgumentParser(description="Generate balanced training data")
    parser.add_argument(
        "--output-dir", type=str, default="data/training", help="Output directory"
    )
    parser.add_argument(
        "--samples-per-class", type=int, default=500, help="Samples per action class"
    )

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Generating Balanced Training Data (ALL 9 Classes)")
    logger.info("=" * 60)
    logger.info(f"Output directory: {args.output_dir}")
    logger.info(f"Samples per class: {args.samples_per_class}")
    logger.info(f"Total samples: {args.samples_per_class * 9}")
    logger.info("=" * 60)

    collector = GameDataCollector(data_dir=args.output_dir)
    total_samples = 0

    # Action classes:
    # 0-3: rotate (NORTH, SOUTH, EAST, WEST)
    # 4: move
    # 5: pick
    # 6: drop
    # 7: give
    # 8: clean

    # Generate rotate actions (4 classes: rotate NORTH, SOUTH, EAST, WEST)
    logger.info("\nGenerating rotate actions...")
    for direction in ["NORTH", "SOUTH", "EAST", "WEST"]:
        for i in range(args.samples_per_class):
            game_state = generate_game_state()
            game_state["robot"]["orientation"] = direction

            collector.collect_sample(
                game_id=f"rotate_{direction}_{i:05d}",
                game_state=game_state,
                action="rotate",
                direction=direction,  # Only rotate takes direction!
                outcome={"success": True, "source": "balanced_synthetic"}
            )
            total_samples += 1

        logger.info(f"  rotate {direction}: {args.samples_per_class} samples")

    # Generate move actions (1 class)
    # Robot must have a CLEAR PATH in the direction it's facing (no obstacles, within bounds)
    logger.info("\nGenerating move actions...")
    for i in range(args.samples_per_class):
        game_state = generate_game_state()
        robot_pos = game_state["robot"]["position"]
        orientation = game_state["robot"]["orientation"]

        # Calculate target position based on orientation
        target_pos = {"row": robot_pos["row"], "col": robot_pos["col"]}
        if orientation == "NORTH":
            target_pos["row"] = robot_pos["row"] - 1
        elif orientation == "SOUTH":
            target_pos["row"] = robot_pos["row"] + 1
        elif orientation == "EAST":
            target_pos["col"] = robot_pos["col"] + 1
        else:  # WEST
            target_pos["col"] = robot_pos["col"] - 1

        # Ensure target is within bounds
        if target_pos["row"] < 0:
            target_pos["row"] = 0
            game_state["robot"]["orientation"] = "SOUTH"  # Change orientation to make move valid
        elif target_pos["row"] >= game_state["board"]["rows"]:
            target_pos["row"] = game_state["board"]["rows"] - 1
            game_state["robot"]["orientation"] = "NORTH"

        if target_pos["col"] < 0:
            target_pos["col"] = 0
            game_state["robot"]["orientation"] = "EAST"
        elif target_pos["col"] >= game_state["board"]["cols"]:
            target_pos["col"] = game_state["board"]["cols"] - 1
            game_state["robot"]["orientation"] = "WEST"

        # Clear target cell of any obstacles or flowers
        game_state["board"]["obstacles_positions"] = [
            o for o in game_state["board"]["obstacles_positions"]
            if o["row"] != target_pos["row"] or o["col"] != target_pos["col"]
        ]
        game_state["board"]["flowers_positions"] = [
            f for f in game_state["board"]["flowers_positions"]
            if f["row"] != target_pos["row"] or f["col"] != target_pos["col"]
        ]

        # Ensure princess is not at target position
        if (target_pos["row"] == game_state["princess"]["position"]["row"] and
            target_pos["col"] == game_state["princess"]["position"]["col"]):
            # Move princess elsewhere
            game_state["princess"]["position"] = {"row": 0, "col": 0}
            game_state["board"]["princess_position"] = {"row": 0, "col": 0}

        collector.collect_sample(
            game_id=f"move_{i:05d}",
            game_state=game_state,
            action="move",
            direction=None,  # Move doesn't take direction!
            outcome={"success": True, "source": "balanced_synthetic"}
        )
        total_samples += 1
    logger.info(f"  move: {args.samples_per_class} samples")

    # Generate pick actions (1 class)
    # Robot must be ADJACENT to a flower in the direction it's facing
    logger.info("\nGenerating pick actions...")
    for i in range(args.samples_per_class):
        game_state = generate_game_state()
        robot_pos = game_state["robot"]["position"]
        orientation = game_state["robot"]["orientation"]

        # Calculate adjacent position based on orientation
        flower_pos = {"row": robot_pos["row"], "col": robot_pos["col"]}
        if orientation == "NORTH":
            flower_pos["row"] = max(0, robot_pos["row"] - 1)
        elif orientation == "SOUTH":
            flower_pos["row"] = min(game_state["board"]["rows"] - 1, robot_pos["row"] + 1)
        elif orientation == "EAST":
            flower_pos["col"] = min(game_state["board"]["cols"] - 1, robot_pos["col"] + 1)
        else:  # WEST
            flower_pos["col"] = max(0, robot_pos["col"] - 1)

        # Place flower adjacent to robot
        game_state["board"]["flowers_positions"] = [flower_pos]
        game_state["board"]["initial_flowers_count"] = 1

        collector.collect_sample(
            game_id=f"pick_{i:05d}",
            game_state=game_state,
            action="pick",
            direction=None,  # Pick doesn't take direction!
            outcome={"success": True, "source": "balanced_synthetic"}
        )
        total_samples += 1
    logger.info(f"  pick: {args.samples_per_class} samples")

    # Generate drop actions (1 class)
    # Robot must have flowers and adjacent cell must be empty
    logger.info("\nGenerating drop actions...")
    for i in range(args.samples_per_class):
        game_state = generate_game_state()
        # Robot should have flowers to drop
        game_state["robot"]["flowers_collected"] = [{"row": 1, "col": 1}]

        # Ensure no obstacles or flowers in adjacent cell (in robot's orientation)
        robot_pos = game_state["robot"]["position"]
        orientation = game_state["robot"]["orientation"]

        adjacent_pos = {"row": robot_pos["row"], "col": robot_pos["col"]}
        if orientation == "NORTH":
            adjacent_pos["row"] = max(0, robot_pos["row"] - 1)
        elif orientation == "SOUTH":
            adjacent_pos["row"] = min(game_state["board"]["rows"] - 1, robot_pos["row"] + 1)
        elif orientation == "EAST":
            adjacent_pos["col"] = min(game_state["board"]["cols"] - 1, robot_pos["col"] + 1)
        else:  # WEST
            adjacent_pos["col"] = max(0, robot_pos["col"] - 1)

        # Clear adjacent cell
        game_state["board"]["flowers_positions"] = [
            f for f in game_state["board"]["flowers_positions"]
            if f["row"] != adjacent_pos["row"] or f["col"] != adjacent_pos["col"]
        ]
        game_state["board"]["obstacles_positions"] = [
            o for o in game_state["board"]["obstacles_positions"]
            if o["row"] != adjacent_pos["row"] or o["col"] != adjacent_pos["col"]
        ]

        collector.collect_sample(
            game_id=f"drop_{i:05d}",
            game_state=game_state,
            action="drop",
            direction=None,  # Drop doesn't take direction!
            outcome={"success": True, "source": "balanced_synthetic"}
        )
        total_samples += 1
    logger.info(f"  drop: {args.samples_per_class} samples")

    # Generate give actions (1 class)
    # Robot must be ADJACENT to princess in the direction it's facing
    logger.info("\nGenerating give actions...")
    for i in range(args.samples_per_class):
        game_state = generate_game_state()
        # Robot should have flowers to give
        game_state["robot"]["flowers_collected"] = [
            {"row": random.randint(0, 6), "col": random.randint(0, 6)}
            for _ in range(random.randint(1, 3))
        ]

        # Position robot adjacent to princess
        princess_pos = game_state["princess"]["position"]
        orientation = random.choice(["NORTH", "SOUTH", "EAST", "WEST"])

        robot_pos = {"row": princess_pos["row"], "col": princess_pos["col"]}
        if orientation == "NORTH":
            robot_pos["row"] = min(game_state["board"]["rows"] - 1, princess_pos["row"] + 1)
        elif orientation == "SOUTH":
            robot_pos["row"] = max(0, princess_pos["row"] - 1)
        elif orientation == "EAST":
            robot_pos["col"] = max(0, princess_pos["col"] - 1)
        else:  # WEST
            robot_pos["col"] = min(game_state["board"]["cols"] - 1, princess_pos["col"] + 1)

        game_state["robot"]["position"] = robot_pos
        game_state["robot"]["orientation"] = orientation
        game_state["board"]["robot_position"] = robot_pos

        collector.collect_sample(
            game_id=f"give_{i:05d}",
            game_state=game_state,
            action="give",
            direction=None,  # Give doesn't take direction!
            outcome={"success": True, "source": "balanced_synthetic"}
        )
        total_samples += 1
    logger.info(f"  give: {args.samples_per_class} samples")

    # Generate clean actions (1 class)
    # Robot must be ADJACENT to an obstacle in the direction it's facing
    logger.info("\nGenerating clean actions...")
    for i in range(args.samples_per_class):
        game_state = generate_game_state()
        robot_pos = game_state["robot"]["position"]
        orientation = game_state["robot"]["orientation"]

        # Calculate adjacent position based on orientation
        obstacle_pos = {"row": robot_pos["row"], "col": robot_pos["col"]}
        if orientation == "NORTH":
            obstacle_pos["row"] = max(0, robot_pos["row"] - 1)
        elif orientation == "SOUTH":
            obstacle_pos["row"] = min(game_state["board"]["rows"] - 1, robot_pos["row"] + 1)
        elif orientation == "EAST":
            obstacle_pos["col"] = min(game_state["board"]["cols"] - 1, robot_pos["col"] + 1)
        else:  # WEST
            obstacle_pos["col"] = max(0, robot_pos["col"] - 1)

        # Ensure princess is not at obstacle position
        if (obstacle_pos["row"] == game_state["princess"]["position"]["row"] and
            obstacle_pos["col"] == game_state["princess"]["position"]["col"]):
            # Move princess elsewhere
            game_state["princess"]["position"] = {"row": 0, "col": 0}
            game_state["board"]["princess_position"] = {"row": 0, "col": 0}

        # Place obstacle adjacent to robot
        game_state["board"]["obstacles_positions"] = [obstacle_pos]
        game_state["board"]["initial_obstacles_count"] = 1

        collector.collect_sample(
            game_id=f"clean_{i:05d}",
            game_state=game_state,
            action="clean",
            direction=None,  # Clean doesn't take direction!
            outcome={"success": True, "source": "balanced_synthetic"}
        )
        total_samples += 1
    logger.info(f"  clean: {args.samples_per_class} samples")

    # Print statistics
    stats = collector.get_statistics()
    logger.info("\n" + "=" * 60)
    logger.info("Data generation completed!")
    logger.info("=" * 60)
    logger.info(f"Total samples: {stats['total_samples']}")
    logger.info(f"Unique games: {stats['unique_games']}")
    logger.info(f"\nAction distribution:")
    for action, count in sorted(stats["action_distribution"].items()):
        pct = (count / stats['total_samples']) * 100
        logger.info(f"  {action:10s}: {count:5d} ({pct:5.1f}%)")
    logger.info(f"\nData files: {stats['data_files']}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
