#!/usr/bin/env python3
"""
Test model prediction with blocked path scenario.
"""

import sys
sys.path.insert(0, 'src')

from hexagons.mlplayer.domain.ml.feature_engineer import FeatureEngineer
from hexagons.mlplayer.domain.ml.model_registry import ModelRegistry

# Test case: Robot at (0,0) facing EAST with obstacle at (0,1)
game_state_blocked = {
    'board': {
        'rows': 5,
        'cols': 5,
        'flowers_positions': [],
        'obstacles_positions': [{'row': 0, 'col': 1}],  # Obstacle directly ahead
        'robot_position': {'row': 0, 'col': 0},
        'princess_position': {'row': 4, 'col': 4},
        'initial_flowers_count': 0,
        'initial_obstacles_count': 1,
    },
    'robot': {
        'position': {'row': 0, 'col': 0},
        'orientation': 'EAST',  # Facing the obstacle
        'flowers_collected': [],
        'flowers_delivered': [],
        'flowers_collection_capacity': 10,
        'obstacles_cleaned': [],
    },
    'princess': {
        'position': {'row': 4, 'col': 4},
    }
}

print("="*60)
print("Model Prediction Test - Blocked Path Scenario")
print("="*60)
print("\nScenario: Robot at (0,0) facing EAST with obstacle at (0,1)")
print("Expected: Model should predict 'rotate' or 'clean', NOT 'move'")
print("-"*60)

# Extract features
features = FeatureEngineer.extract_features(game_state_blocked)
print(f"\n✓ Features extracted: {len(features)} features")

# Check action validity features
feature_names = FeatureEngineer.get_feature_names()
action_validity_start = len(features) - 6
print(f"✓ can_move_forward: {features[action_validity_start]}")
print(f"✓ can_clean_forward: {features[action_validity_start + 3]}")
print(f"✓ should_rotate: {features[action_validity_start + 5]}")

# Load best model
print("\n" + "-"*60)
print("Loading model...")
registry = ModelRegistry()
model, metadata = registry.load_best_model()

if model is None:
    print("❌ ERROR: No model found!")
    sys.exit(1)

print(f"✓ Model loaded: {metadata.name}")
print(f"✓ Model type: {metadata.model_type}")
print(f"✓ Test accuracy: {metadata.test_accuracy:.2%}")

# Predict
print("\n" + "-"*60)
print("Making prediction...")
features_array = features.reshape(1, -1)
prediction = model.predict(features_array)[0]
probabilities = model.predict_proba(features_array)[0]

print(f"\nPredicted class: {prediction}")

# Decode prediction
action, direction = FeatureEngineer.decode_action(prediction)
print(f"Decoded action: {action}")
print(f"Decoded direction: {direction}")

# Show top 3 predictions
top_3_indices = probabilities.argsort()[-3:][::-1]
print("\nTop 3 predictions:")
for i, idx in enumerate(top_3_indices, 1):
    act, dir = FeatureEngineer.decode_action(idx)
    prob = probabilities[idx]
    symbol = "→" if i == 1 else " "
    print(f"  {symbol} {i}. {act} {dir if dir else ''}: {prob:.2%}")

# Check if prediction is valid
print("\n" + "="*60)
print("Result:")
print("="*60)

if action == "move":
    print("❌ FAIL: Model predicted 'move' when path is blocked!")
    print("   This should NOT happen with the new training data.")
    print("   The model may need retraining or there's a feature mismatch.")
elif action == "clean":
    print("✅ PASS: Model predicted 'clean' - correct choice!")
elif action == "rotate":
    print("✅ PASS: Model predicted 'rotate' - acceptable choice!")
else:
    print(f"⚠️  Model predicted '{action}' - unexpected but not catastrophic")

print("="*60)
