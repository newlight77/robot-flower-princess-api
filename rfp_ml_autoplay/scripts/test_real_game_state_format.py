#!/usr/bin/env python3
"""
Test prediction using the EXACT format sent by the real game (MLProxyPlayer format).
"""

import sys
sys.path.insert(0, 'src')

from hexagons.mlplayer.domain.use_cases.predict_action import PredictActionCommand, PredictActionUseCase

# This is the EXACT format that MLProxyPlayer._convert_game_to_state() sends
# Based on the to_dict() methods of Game, Board, Robot, Princess
real_game_state_from_proxy = {
    "game_id": "test_real_format",
    "status": "In Progress",
    "board": {
        "rows": 7,
        "cols": 7,
        "robot_position": {"row": 0, "col": 0},
        "princess_position": {"row": 6, "col": 6},
        "flowers_positions": [{"row": 2, "col": 3}],
        "obstacles_positions": [{"row": 0, "col": 1}],  # BLOCKING EAST!
        "initial_flowers_count": 1,
        "initial_obstacles_count": 1,
        # The real game might send grid data
        "grid": [[None for _ in range(7)] for _ in range(7)],
    },
    "robot": {
        "position": {"row": 0, "col": 0},
        "orientation": "EAST",  # Facing the obstacle!
        "flowers_collected": [],
        "flowers_delivered": [],
        "flowers_collection_capacity": 10,
        "obstacles_cleaned": [],
        "executed_actions": [],
    },
    "princess": {
        "position": {"row": 6, "col": 6},
        "flowers_received": [],
        "mood": "neutral",
    }
}

print("="*70)
print("Testing with REAL Game State Format")
print("="*70)
print("\n📍 Robot at (0,0) facing EAST")
print("🚧 Obstacle at (0,1) - BLOCKING!")
print("\n" + "-"*70)

# Create command exactly as the HTTP endpoint receives it
command = PredictActionCommand(
    strategy="default",
    game_id=real_game_state_from_proxy["game_id"],
    board=real_game_state_from_proxy["board"],
    robot=real_game_state_from_proxy["robot"],
    princess=real_game_state_from_proxy["princess"],
    obstacles={},  # MLProxyPlayer doesn't send this
    flowers={},    # MLProxyPlayer doesn't send this
)

# Execute
print("\n🔧 Executing prediction with REAL format...")
use_case = PredictActionUseCase()
result = use_case.execute(command)

print("\n" + "="*70)
print("📊 RESULT")
print("="*70)
print(f"\n🎯 Action: {result.action.upper()}")
if result.direction:
    print(f"🧭 Direction: {result.direction}")
print(f"💯 Confidence: {result.confidence:.2%}")

# Check the converted GameState to see what features were extracted
print("\n" + "-"*70)
print("🔍 Verifying Feature Extraction...")
print("-"*70)

game_state_obj = command.convert_to_game_state()
from hexagons.mlplayer.domain.ml.feature_engineer import FeatureEngineer
features = FeatureEngineer.extract_features(game_state_obj.to_dict())

print(f"Total features: {len(features)}")
action_validity_start = len(features) - 6
print(f"\n🎯 Action Validity Features (last 6):")
print(f"  can_move_forward: {features[action_validity_start]:.1f}")
print(f"  can_pick_forward: {features[action_validity_start + 1]:.1f}")
print(f"  can_give_forward: {features[action_validity_start + 2]:.1f}")
print(f"  can_clean_forward: {features[action_validity_start + 3]:.1f}")
print(f"  can_drop_forward: {features[action_validity_start + 4]:.1f}")
print(f"  should_rotate: {features[action_validity_start + 5]:.1f}")

# Verdict
print("\n" + "="*70)
print("🏁 VERDICT")
print("="*70)

if result.action == "move":
    print("\n❌ BUG!")
    print("   Predicted 'move' with real game format!")
    print("\n🔍 Debug info:")
    print(f"   can_move_forward = {features[action_validity_start]}")
    if features[action_validity_start] == 0.0:
        print("   ❌ Feature says path is blocked, but model predicted move anyway!")
        print("   ⚠️  This suggests a FEATURE MISMATCH between training and prediction!")
    else:
        print("   ⚠️  Feature incorrectly says path is clear!")
elif result.action == "clean":
    print("\n✅ CORRECT!")
    print("   Predicted 'clean' - obstacle will be removed.")
elif result.action == "rotate":
    print("\n✅ ACCEPTABLE!")
    print("   Predicted 'rotate' - will change orientation.")
else:
    print(f"\n⚠️  Unexpected: {result.action}")

print("="*70)
