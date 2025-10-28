#!/usr/bin/env python3
"""
Debug tool to analyze what's happening during a live prediction.
Add this to your MLProxyPlayer to capture the exact game state being sent.
"""

import json

# PASTE THE GAME STATE JSON HERE that's being sent to ML Player
# You can get this from the logs: "MLProxyPlayer.get_prediction: Predicting action..."
# Look for the game_state parameter

DEBUG_GAME_STATE = {
    # PASTE YOUR ACTUAL GAME STATE HERE
    # Example:
    "board": {
        "rows": 7,
        "cols": 7,
        "robot_position": {"row": 0, "col": 0},
        "princess_position": {"row": 6, "col": 6},
        "flowers_positions": [],
        "obstacles_positions": [{"row": 0, "col": 1}],
        "initial_flowers_count": 0,
        "initial_obstacles_count": 1,
    },
    "robot": {
        "position": {"row": 0, "col": 0},
        "orientation": "EAST",  # ← CHECK THIS VALUE!
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
print("🔍 DEBUG: Analyzing Live Game State")
print("="*70)

print("\n📋 Game State:")
print(json.dumps(DEBUG_GAME_STATE, indent=2))

print("\n" + "-"*70)
print("🤖 Key Values:")
print("-"*70)

robot_pos = DEBUG_GAME_STATE["robot"]["position"]
robot_orient = DEBUG_GAME_STATE["robot"]["orientation"]
obstacles = DEBUG_GAME_STATE["board"]["obstacles_positions"]

print(f"Robot position: ({robot_pos['row']}, {robot_pos['col']})")
print(f"Robot orientation: {robot_orient}")
print(f"Obstacles: {obstacles}")

# Calculate what's in front of robot
target_row = robot_pos["row"]
target_col = robot_pos["col"]

if robot_orient == "NORTH":
    target_row -= 1
elif robot_orient == "SOUTH":
    target_row += 1
elif robot_orient == "EAST":
    target_col += 1
elif robot_orient == "WEST":
    target_col -= 1

print(f"\nTarget cell (in front): ({target_row}, {target_col})")

# Check if blocked
is_blocked = False
for obs in obstacles:
    if obs["row"] == target_row and obs["col"] == target_col:
        is_blocked = True
        print(f"⚠️  OBSTACLE at target cell!")
        break

if not is_blocked:
    print(f"✅ Target cell is CLEAR")

print("\n" + "="*70)
print("🎯 Expected Behavior:")
print("="*70)

if is_blocked:
    print("❌ Should NOT predict 'move'")
    print("✅ Should predict 'clean' or 'rotate'")
else:
    print("✅ Can predict 'move'")

print("\n" + "-"*70)
print("🔧 Next Steps:")
print("-"*70)
print("1. Paste the ACTUAL game_state from your logs above")
print("2. Run this script again")
print("3. Check if orientation or obstacle positions are unexpected")
print("="*70)
