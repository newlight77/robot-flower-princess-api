#!/usr/bin/env python3
"""
Quick diagnostic test to verify feature extraction for action validity.
"""

import sys
sys.path.insert(0, 'src')

from hexagons.mlplayer.domain.ml.feature_engineer import FeatureEngineer

# Test case 1: Robot at (0,0) facing EAST with obstacle at (0,1)
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

# Test case 2: Robot at (0,0) facing SOUTH with clear path
game_state_clear = {
    'board': {
        'rows': 5,
        'cols': 5,
        'flowers_positions': [],
        'obstacles_positions': [{'row': 0, 'col': 1}],  # Obstacle to the east
        'robot_position': {'row': 0, 'col': 0},
        'princess_position': {'row': 4, 'col': 4},
        'initial_flowers_count': 0,
        'initial_obstacles_count': 1,
    },
    'robot': {
        'position': {'row': 0, 'col': 0},
        'orientation': 'SOUTH',  # Facing away from obstacle
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
print("Feature Extraction Diagnostic Test")
print("="*60)

# Test blocked path
print("\nTest 1: Robot at (0,0) facing EAST with obstacle at (0,1)")
print("-"*60)
features_blocked = FeatureEngineer.extract_features(game_state_blocked)
print(f"Total features: {len(features_blocked)}")

feature_names = FeatureEngineer.get_feature_names()
print(f"Total feature names: {len(feature_names)}")

# Find action validity features (last 6 features)
action_validity_start = len(features_blocked) - 6
action_validity_features = features_blocked[action_validity_start:]
action_validity_names = feature_names[action_validity_start:]

print("\nAction Validity Features:")
for name, value in zip(action_validity_names, action_validity_features):
    symbol = "✅" if value == 1.0 else "❌"
    print(f"  {symbol} {name}: {value}")

print("\nExpected:")
print("  ❌ can_move_forward: 0.0 (obstacle blocks path)")
print("  ❌ can_pick_forward: 0.0 (no flower ahead)")
print("  ❌ can_give_forward: 0.0 (no princess ahead)")
print("  ✅ can_clean_forward: 1.0 (obstacle ahead)")
print("  ❌ can_drop_forward: 0.0 (no flowers to drop)")
print("  ✅ should_rotate: 1.0 (blocked)")

# Test clear path
print("\n" + "="*60)
print("Test 2: Robot at (0,0) facing SOUTH (clear path)")
print("-"*60)
features_clear = FeatureEngineer.extract_features(game_state_clear)
action_validity_features_clear = features_clear[action_validity_start:]

print("\nAction Validity Features:")
for name, value in zip(action_validity_names, action_validity_features_clear):
    symbol = "✅" if value == 1.0 else "❌"
    print(f"  {symbol} {name}: {value}")

print("\nExpected:")
print("  ✅ can_move_forward: 1.0 (clear path)")
print("  ❌ can_pick_forward: 0.0 (no flower ahead)")
print("  ❌ can_give_forward: 0.0 (no princess ahead)")
print("  ❌ can_clean_forward: 0.0 (no obstacle ahead)")
print("  ❌ can_drop_forward: 0.0 (no flowers to drop)")
print("  ❌ should_rotate: 0.0 (not blocked)")

print("\n" + "="*60)
print("Summary")
print("="*60)

# Verify the blocked case
can_move_blocked = action_validity_features[0]
can_clean_blocked = action_validity_features[3]
should_rotate_blocked = action_validity_features[5]

# Verify the clear case
can_move_clear = action_validity_features_clear[0]
should_rotate_clear = action_validity_features_clear[5]

if can_move_blocked == 0.0 and can_clean_blocked == 1.0 and should_rotate_blocked == 1.0:
    print("✅ Test 1 PASSED: Correctly identifies blocked path")
else:
    print("❌ Test 1 FAILED: Incorrect feature extraction for blocked path")
    print(f"   can_move={can_move_blocked} (expected 0.0)")
    print(f"   can_clean={can_clean_blocked} (expected 1.0)")
    print(f"   should_rotate={should_rotate_blocked} (expected 1.0)")

if can_move_clear == 1.0 and should_rotate_clear == 0.0:
    print("✅ Test 2 PASSED: Correctly identifies clear path")
else:
    print("❌ Test 2 FAILED: Incorrect feature extraction for clear path")
    print(f"   can_move={can_move_clear} (expected 1.0)")
    print(f"   should_rotate={should_rotate_clear} (expected 0.0)")

print("="*60)
