#!/usr/bin/env python3
"""
Test the HTTP prediction endpoint (simulates the actual API call).
"""

import sys
sys.path.insert(0, 'src')

from hexagons.mlplayer.domain.use_cases.predict_action import PredictActionCommand, PredictActionUseCase

# EXACT scenario: Robot at (0,0) facing EAST with obstacle at (0,1)
command = PredictActionCommand(
    strategy="default",
    game_id="test_blocked",
    board={
        "rows": 7,
        "cols": 7,
        "robot_position": {"row": 0, "col": 0},
        "princess_position": {"row": 6, "col": 6},
        "flowers_positions": [{"row": 2, "col": 3}, {"row": 5, "col": 5}],
        "obstacles_positions": [{"row": 0, "col": 1}],  # Blocking EAST!
        "initial_flowers_count": 2,
        "initial_obstacles_count": 1,
        "grid": [],
    },
    robot={
        "position": {"row": 0, "col": 0},
        "orientation": "EAST",  # Facing obstacle!
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
    },
    obstacles={},
    flowers={},
)

print("="*70)
print("Testing HTTP Prediction Endpoint (PredictActionUseCase)")
print("="*70)
print("\n📍 Scenario:")
print("  - Robot at (0,0) facing EAST")
print("  - Obstacle at (0,1) - BLOCKS the path!")
print("\n" + "-"*70)

# Execute use case (this is what the HTTP endpoint does)
print("\n🔧 Executing PredictActionUseCase...")
use_case = PredictActionUseCase()
result = use_case.execute(command)

print("\n" + "="*70)
print("📊 PREDICTION RESULT")
print("="*70)
print(f"\n🎯 Action: {result.action.upper()}")
if result.direction:
    print(f"🧭 Direction: {result.direction}")
print(f"💯 Confidence: {result.confidence:.2%}")
print(f"📊 Board Score: {result.board_score:.2f}")

# Verdict
print("\n" + "="*70)
print("🏁 VERDICT")
print("="*70)

if result.action == "move":
    print("\n❌ BUG CONFIRMED!")
    print("   The HTTP endpoint is returning 'move' when blocked!")
    print("\n🔍 This means:")
    print("   - The ML Player service IS using this buggy prediction")
    print("   - Check the logs above for 'Using heuristic' messages")
    print("   - The service may not have restarted properly")
elif result.action == "clean":
    print("\n✅ WORKING CORRECTLY!")
    print("   The HTTP endpoint correctly returns 'clean'.")
    print("\n🔧 If you're still seeing 'move' in gameplay:")
    print("   1. Make sure ML Player service is ACTUALLY restarted")
    print("   2. Check if ML Player service is running on correct port")
    print("   3. Verify RFP Game is calling the correct ML Player URL")
elif result.action == "rotate":
    print("\n✅ ACCEPTABLE!")
    print("   The HTTP endpoint returns 'rotate'.")
else:
    print(f"\n⚠️  Unexpected: {result.action}")

print("="*70)
