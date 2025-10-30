#!/usr/bin/env python3
"""
Test the FULL prediction flow including AIMLPlayer to see if ML or heuristic is used.
"""

import sys
sys.path.insert(0, 'src')

from hexagons.mlplayer.domain.core.entities import AIMLPlayer
from hexagons.mlplayer.domain.core.value_objects import GameState

# EXACT scenario from error: Robot at (0,0) facing EAST with obstacle at (0,1)
game_state = GameState(
    game_id="test_blocked_path",
    board={
        "rows": 7,
        "cols": 7,
        "grid": [],
        "robot_position": {"row": 0, "col": 0},
        "princess_position": {"row": 6, "col": 6},
        "flowers_positions": [{"row": 2, "col": 3}, {"row": 5, "col": 5}],
        "obstacles_positions": [{"row": 0, "col": 1}],  # Blocking EAST
        "initial_flowers_count": 2,
        "initial_obstacles_count": 1,
    },
    robot={
        "position": {"row": 0, "col": 0},
        "orientation": "EAST",  # Facing the obstacle!
        "flowers_collected": [],
        "flowers_delivered": [],
        "flowers_collection_capacity": 10,
        "obstacles_cleaned": [],
        "executed_actions": [],
    },
    princess={
        "position": {"row": 6, "col": 6},
        "flowers_received": [],
        "mood": "neutral",
    }
)

print("="*70)
print("Testing Full Prediction Flow (AIMLPlayer)")
print("="*70)
print("\n📍 Scenario:")
print("  - Robot at (0,0) facing EAST")
print("  - Obstacle at (0,1) - BLOCKS the path!")
print("  - Flowers at (2,3) and (5,5)")
print("  - Princess at (6,6)")
print("\n" + "-"*70)

# Create AIMLPlayer
print("\n🤖 Creating AIMLPlayer...")
player = AIMLPlayer()

# Check if ML model loaded
print(f"\n📊 Model Status:")
print(f"  - use_ml: {player.use_ml}")
print(f"  - model loaded: {player.model is not None}")
if player.model_metadata:
    print(f"  - model name: {player.model_metadata.name}")
    print(f"  - model accuracy: {player.model_metadata.test_accuracy:.2%}")

# Select action
print("\n🎯 Calling select_action()...")
print("-"*70)
action, direction = player.select_action(game_state)

print("\n" + "="*70)
print("📊 RESULT")
print("="*70)
print(f"\n🎯 Action: {action.upper()}")
if direction:
    print(f"🧭 Direction: {direction}")

# Verdict
print("\n" + "="*70)
print("🏁 VERDICT")
print("="*70)

if action == "move":
    print("\n❌ CRITICAL BUG!")
    print("   AIMLPlayer predicted 'move' when obstacle blocks path!")
    print("\n🔍 Possible causes:")
    print("   1. ML model not being used (use_ml=False)")
    print("   2. ML prediction failed and fell back to OLD heuristic")
    print("   3. Heuristic fallback still has bugs")
    print(f"\n📋 Debug info:")
    print(f"   - use_ml: {player.use_ml}")
    print(f"   - model: {player.model is not None}")
elif action == "clean":
    print("\n✅ PERFECT!")
    print("   AIMLPlayer correctly predicted 'clean' to remove obstacle.")
    print(f"   Using: {'ML model' if player.use_ml else 'heuristics'}")
elif action == "rotate":
    print("\n✅ ACCEPTABLE!")
    print("   AIMLPlayer predicted 'rotate' to face different direction.")
    print(f"   Using: {'ML model' if player.use_ml else 'heuristics'}")
else:
    print(f"\n⚠️  Unexpected action: {action}")
    print(f"   Using: {'ML model' if player.use_ml else 'heuristics'}")

print("="*70)
