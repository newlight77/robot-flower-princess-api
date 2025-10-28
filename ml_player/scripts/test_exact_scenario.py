#!/usr/bin/env python3
"""
Test the EXACT scenario from the error message:
Robot at (0,0) oriented EAST, obstacle at (0,1)
"""

import sys
sys.path.insert(0, 'src')

from hexagons.mlplayer.domain.ml.feature_engineer import FeatureEngineer
from hexagons.mlplayer.domain.ml.model_registry import ModelRegistry

# EXACT scenario from error: "position=Position(row=0, col=1)" with "direction=Direction.EAST"
# This means robot is at (0,0) and trying to move EAST to (0,1) where there's an obstacle

game_state = {
    'board': {
        'rows': 7,
        'cols': 7,
        'flowers_positions': [
            {'row': 2, 'col': 3},
            {'row': 5, 'col': 5},
        ],
        'obstacles_positions': [
            {'row': 0, 'col': 1},  # THE BLOCKING OBSTACLE
        ],
        'robot_position': {'row': 0, 'col': 0},
        'princess_position': {'row': 6, 'col': 6},
        'initial_flowers_count': 2,
        'initial_obstacles_count': 1,
    },
    'robot': {
        'position': {'row': 0, 'col': 0},
        'orientation': 'EAST',  # Facing the obstacle at (0,1)
        'flowers_collected': [],
        'flowers_delivered': [],
        'flowers_collection_capacity': 10,
        'obstacles_cleaned': [],
    },
    'princess': {
        'position': {'row': 6, 'col': 6},
    }
}

print("="*70)
print("Testing EXACT Scenario from Error Message")
print("="*70)
print("\n📍 Robot position: (0, 0)")
print("🧭 Robot orientation: EAST")
print("🚧 Obstacle position: (0, 1) - directly ahead!")
print("🌸 Flowers at: (2,3) and (5,5)")
print("👸 Princess at: (6, 6)")
print("\n" + "-"*70)

# Extract features
features = FeatureEngineer.extract_features(game_state)
feature_names = FeatureEngineer.get_feature_names()

# Show critical features
print("\n🔍 Critical Features:")
print("-"*70)

# Robot orientation (features 72-75)
print(f"Orientation NORTH: {features[72]}")
print(f"Orientation SOUTH: {features[73]}")
print(f"Orientation EAST: {features[74]}")
print(f"Orientation WEST: {features[75]}")

# Action validity (features 72-77, last 6)
action_validity_start = len(features) - 6
print(f"\n🎯 Action Validity:")
print(f"  can_move_forward: {features[action_validity_start]}")
print(f"  can_pick_forward: {features[action_validity_start + 1]}")
print(f"  can_give_forward: {features[action_validity_start + 2]}")
print(f"  can_clean_forward: {features[action_validity_start + 3]}")
print(f"  can_drop_forward: {features[action_validity_start + 4]}")
print(f"  should_rotate: {features[action_validity_start + 5]}")

# Directional cell info (features for EAST direction)
# EAST direction features start at index 12 + 8*2 = 28
east_start = 12 + 8 * 2  # Basic(12) + NORTH(8) + SOUTH(8) + EAST(8)
print(f"\n🧭 EAST Direction Cell Type:")
print(f"  east_cell_empty: {features[east_start]}")
print(f"  east_cell_flower: {features[east_start + 1]}")
print(f"  east_cell_obstacle: {features[east_start + 2]}")
print(f"  east_cell_princess: {features[east_start + 3]}")
print(f"  east_cell_oob: {features[east_start + 4]}")

# Load model and predict
print("\n" + "-"*70)
print("🤖 Loading Model...")
registry = ModelRegistry()
model, metadata = registry.load_best_model()
print(f"✓ Loaded: {metadata.name} (accuracy={metadata.test_accuracy:.2%})")

# Predict
print("\n🎲 Making Prediction...")
features_array = features.reshape(1, -1)
prediction = model.predict(features_array)[0]
probabilities = model.predict_proba(features_array)[0]

# Decode
action, direction = FeatureEngineer.decode_action(prediction)

print("\n" + "="*70)
print("📊 PREDICTION RESULTS")
print("="*70)
print(f"\n🎯 Predicted Action: {action.upper()}")
if direction:
    print(f"🧭 Direction: {direction}")
print(f"💯 Confidence: {probabilities[prediction]:.2%}")

# Show all predictions sorted by probability
print("\n📈 All Action Probabilities:")
print("-"*70)
all_predictions = []
for i in range(len(probabilities)):
    act, dir = FeatureEngineer.decode_action(i)
    all_predictions.append((probabilities[i], act, dir))

all_predictions.sort(reverse=True)
for prob, act, dir in all_predictions[:10]:
    if prob > 0.001:  # Only show probabilities > 0.1%
        dir_str = f" {dir}" if dir else ""
        bar = "█" * int(prob * 50)
        print(f"  {prob:6.2%} {bar:20s} {act}{dir_str}")

# Final verdict
print("\n" + "="*70)
print("🏁 FINAL VERDICT")
print("="*70)

if action == "move":
    print("\n❌ CRITICAL FAILURE!")
    print("   Model predicted 'move' when obstacle blocks path!")
    print("   This WILL cause the error you're seeing.")
    print("\n🔧 Recommended Actions:")
    print("   1. Check if model is actually being used (not heuristic fallback)")
    print("   2. Verify game state conversion is correct")
    print("   3. Check for any preprocessing differences")
elif action == "clean":
    print("\n✅ PERFECT!")
    print("   Model correctly predicted 'clean' to remove obstacle.")
elif action == "rotate":
    print("\n✅ ACCEPTABLE!")
    print("   Model predicted 'rotate' to face different direction.")
else:
    print(f"\n⚠️  Model predicted '{action}' - unexpected")

print("="*70)
