#!/usr/bin/env python3
"""
Analyze training data to check quality and distribution.
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, 'src')

from hexagons.mltraining.domain.ml.feature_engineer import FeatureEngineer


def analyze_data(data_dir: str):
    """Analyze training data quality."""
    data_path = Path(data_dir)

    # Find all .jsonl files
    jsonl_files = list(data_path.glob("samples_*.jsonl"))

    if not jsonl_files:
        print("❌ No training data files found!")
        return

    print(f"\n📁 Found {len(jsonl_files)} data file(s)")

    total_samples = 0
    action_counts = Counter()
    direction_counts = Counter()
    engineer = FeatureEngineer()

    for jsonl_file in jsonl_files:
        print(f"\n  Analyzing: {jsonl_file.name}")

        with open(jsonl_file, 'r') as f:
            for line in f:
                if not line.strip():
                    continue

                sample = json.loads(line)
                total_samples += 1

                # Count actions
                action = sample.get("action", "unknown")
                direction = sample.get("direction")

                # Decode for readability
                try:
                    label = engineer.encode_action(action, direction)
                    decoded_action, decoded_dir = engineer.decode_action(label)

                    if decoded_dir:
                        action_key = f"{decoded_action}_{decoded_dir}"
                    else:
                        action_key = decoded_action

                    action_counts[action_key] += 1

                    if decoded_dir:
                        direction_counts[decoded_dir] += 1

                except Exception as e:
                    action_counts["ERROR"] += 1

    # Print summary
    print("\n" + "="*60)
    print("📊 TRAINING DATA ANALYSIS")
    print("="*60)

    print(f"\n✓ Total samples: {total_samples:,}")

    if total_samples == 0:
        print("\n❌ No samples found in data files!")
        return

    # Action distribution
    print(f"\n📋 Action Distribution:")
    print(f"{'Action':<20} {'Count':<10} {'Percentage':<12} {'Bar'}")
    print("-" * 60)

    for action, count in sorted(action_counts.items(), key=lambda x: -x[1]):
        percentage = (count / total_samples) * 100
        bar_length = int(percentage / 2)  # Scale to 50 chars max
        bar = "█" * bar_length
        print(f"{action:<20} {count:<10} {percentage:>6.2f}%     {bar}")

    # Direction distribution
    if direction_counts:
        print(f"\n🧭 Direction Distribution:")
        for direction, count in sorted(direction_counts.items(), key=lambda x: -x[1]):
            percentage = (count / sum(direction_counts.values())) * 100
            print(f"  {direction:<10} {count:<10} {percentage:>6.2f}%")

    # Quality checks
    print(f"\n✅ Quality Checks:")

    # Check balance
    if action_counts:
        max_count = max(action_counts.values())
        min_count = min(action_counts.values())
        balance_ratio = max_count / min_count if min_count > 0 else float('inf')

        if balance_ratio < 3:
            print(f"  ✓ Good balance (ratio: {balance_ratio:.1f}:1)")
        elif balance_ratio < 10:
            print(f"  ⚠️  Moderate imbalance (ratio: {balance_ratio:.1f}:1)")
        else:
            print(f"  ❌ High imbalance (ratio: {balance_ratio:.1f}:1)")
            print(f"     Consider collecting more data from diverse games")

    # Check sample count
    if total_samples < 1000:
        print(f"  ❌ Low sample count ({total_samples})")
        print(f"     Recommended: 10,000+ samples for good performance")
    elif total_samples < 5000:
        print(f"  ⚠️  Moderate sample count ({total_samples})")
        print(f"     Recommended: 10,000+ samples for best performance")
    else:
        print(f"  ✓ Good sample count ({total_samples:,})")

    # Recommendations
    print(f"\n💡 Recommendations:")
    if total_samples < 10000:
        print(f"  • Collect more data: run collect_from_ai_solved_games.py with --num-games 2000")

    if balance_ratio > 5:
        print(f"  • Improve balance: ensure diverse game scenarios")

    print(f"  • Target accuracy: >85% test accuracy")
    print(f"  • After training: Check confusion matrix for weak spots")

    print("\n" + "="*60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze training data quality")
    parser.add_argument("--data-dir", default="data/training", help="Training data directory")

    args = parser.parse_args()
    analyze_data(args.data_dir)
