#!/usr/bin/env python3
"""
Script to collect high-quality training data from successful AI games.
This generates REAL gameplay patterns, not synthetic data.

Usage:
    python scripts/collect_quality_training_data.py [--num-games 1000] [--output-dir data/training]
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List


def print_header():
    """Print script header."""
    print("=" * 60)
    print("🎯 Quality Training Data Collection")
    print("=" * 60)


def print_config(num_games: int, output_dir: str, timestamp: str):
    """Print configuration."""
    print("\n📋 Configuration:")
    print(f"  - Games to collect: {num_games}")
    print(f"  - Output directory: {output_dir}")
    print(f"  - Timestamp: {timestamp}")
    print()


def backup_old_data(output_dir: Path) -> bool:
    """
    Backup old training data files.

    Returns:
        True if backup was performed, False if no files to backup
    """
    print("🧹 Step 1: Cleaning old synthetic/low-quality data...")

    # Find all existing sample files
    sample_files = list(output_dir.glob("samples_*.jsonl"))

    if not sample_files:
        print("  - No old data found")
        return False

    print(f"  - Moving {len(sample_files)} old sample file(s) to backup...")

    # Create backup directory
    backup_dir = output_dir / "backup"
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Move files
    for sample_file in sample_files:
        target = backup_dir / sample_file.name
        # If target exists, append timestamp to avoid overwriting
        if target.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target = backup_dir / f"{sample_file.stem}_{timestamp}.jsonl"
        sample_file.rename(target)

    print("  ✓ Old data backed up")
    return True


def run_command(cmd: List[str], description: str) -> bool:
    """
    Run a command and return whether it succeeded.

    Args:
        cmd: Command and arguments to run
        description: Description of what the command does

    Returns:
        True if command succeeded, False otherwise
    """
    try:
        result = subprocess.run(
            cmd,
            check=True,
            text=True,
            capture_output=False  # Show output in real-time
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ {description} failed!")
        print(f"  Error: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Unexpected error running {description}: {e}")
        return False


def collect_data(num_games: int, output_dir: str, strategy: str) -> bool:
    """
    Collect training data from AI-solved games.

    Returns:
        True if collection succeeded, False otherwise
    """
    print("\n🎮 Step 2: Collecting from AI-solved games...")
    print(f"  This uses the {strategy.upper()} player which successfully solves games")
    print("  We learn from its successful strategies!")
    print()

    cmd = [
        "poetry", "run", "python", "scripts/collect_from_ai_solved_games.py",
        "--num-games", str(num_games),
        "--output-dir", output_dir,
        "--strategy", strategy,
        "--min-success-rate", "0.8"
    ]

    success = run_command(cmd, "Data collection")

    if success:
        print("  ✓ Data collection successful!")

    return success


def analyze_data(output_dir: str) -> bool:
    """
    Analyze collected training data.

    Returns:
        True if analysis succeeded, False otherwise
    """
    print("\n📊 Step 3: Analyzing collected data...")

    cmd = [
        "poetry", "run", "python", "scripts/analyze_training_data.py",
        "--data-dir", output_dir
    ]

    return run_command(cmd, "Data analysis")


def print_summary():
    """Print completion summary and next steps."""
    print("\n" + "=" * 60)
    print("✅ Data Collection Complete!")
    print("=" * 60)
    print()
    print("📈 Next steps:")
    print("  1. Review the data distribution above")
    print("  2. Run: make ml-train")
    print("  3. Check that accuracy is >85%")
    print("  4. Restart ML Player service")
    print()
    print("💡 Tip: If accuracy is still low, collect more games:")
    print("  poetry run python scripts/collect_quality_training_data.py --num-games 2000")
    print()


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Collect high-quality training data from AI-solved games"
    )
    parser.add_argument(
        "--num-games",
        type=int,
        default=1000,
        help="Number of games to collect (default: 1000)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/training",
        help="Output directory for training data (default: data/training)"
    )
    parser.add_argument(
        "--strategy",
        type=str,
        default="heuristic",
        choices=["greedy", "optimal", "heuristic"],
        help="AI strategy to use (default: heuristic)"
    )

    args = parser.parse_args()

    # Get timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Convert output_dir to Path
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Print header and config
    print_header()
    print_config(args.num_games, args.output_dir, timestamp)

    # Step 1: Backup old data
    backup_old_data(output_dir)

    # Step 2: Collect data
    if not collect_data(args.num_games, args.output_dir, args.strategy):
        print("\n❌ Data collection failed. Exiting.")
        sys.exit(1)

    # Step 3: Analyze data
    if not analyze_data(args.output_dir):
        print("\n⚠️  Data analysis failed, but data was collected successfully.")
        # Don't exit with error - data collection was successful

    # Step 4: Print summary
    print_summary()

    sys.exit(0)


if __name__ == "__main__":
    main()
