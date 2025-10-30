# 🎯 Strategic Features Upgrade

## Overview

Enhanced the feature engineering with **4 new strategic planning features** to help the ML model learn sophisticated gameplay strategies.

**Total features: 78 → 82**

---

## 🧠 **Strategic Problem Solved**

### **Before: Robot Gets Stuck**
```
Robot (holding 3 flowers) → 🗑️ Obstacle
Status: can_clean=0.0, can_move=0.0 → STUCK! ❌
```

### **After: Robot Plans Ahead**
```
Robot (holding 3 flowers) → 🗑️ Obstacle
Strategy:
1. Check: blocked_with_flowers=1.0 ✓
2. Check: nearby_empty_cells_ratio=0.75 ✓ (3 empty cells around)
3. Action: DROP flower to empty cell
4. Action: CLEAN obstacle
5. Action: PICK flower back
6. Action: MOVE forward ✅
```

---

## 🆕 **New Features (78-81)**

### **Feature 78: `blocked_with_flowers`**
**Purpose:** Detect when robot is stuck with flowers and needs to drop them first

```python
blocked_with_flowers = 1.0 if (forward_cell == "obstacle" and has_collected_flowers) else 0.0
```

**When it fires:**
- Robot has flowers collected AND
- Obstacle directly ahead

**ML learns:** "If this is 1.0, I should DROP flowers before cleaning"

---

### **Feature 79: `nearby_empty_cells_ratio`**
**Purpose:** Count available drop zones around robot (normalized 0-1)

```python
# Checks all 4 directions (NORTH, SOUTH, EAST, WEST)
nearby_empty_cells_ratio = (count of empty adjacent cells) / 4.0
```

**Values:**
- `0.0` = No empty cells (can't drop anywhere!)
- `0.25` = 1 empty cell
- `0.5` = 2 empty cells
- `0.75` = 3 empty cells
- `1.0` = 4 empty cells (max flexibility)

**ML learns:** "Before picking flowers, check if I have drop zones available"

---

### **Feature 80: `obstacles_ahead_2steps`**
**Purpose:** Look ahead 2 steps to detect obstacles early (normalized 0-1)

```python
# Simulates moving 2 steps forward in current orientation
obstacles_ahead_2steps = (count of obstacles in next 2 cells) / 2.0
```

**Values:**
- `0.0` = Clear path (both cells empty/flower)
- `0.5` = 1 obstacle in next 2 steps
- `1.0` = 2 obstacles ahead (heavily blocked!)

**ML learns:** "Don't pick flower if path ahead is blocked"

---

### **Feature 81: `can_pick_and_continue`**
**Purpose:** Only pick flower if we can continue moving forward after

```python
if can_pick == 1.0:
    # Check cell BEYOND the flower
    if beyond_flower_cell in ["empty", "flower", "princess"]:
        can_pick_and_continue = 1.0  # Safe to pick!
    else:
        can_pick_and_continue = 0.0  # Blocked after flower!
```

**Example:**
```
Robot → 🌸 → ⬜  => can_pick_and_continue=1.0 ✅
Robot → 🌸 → 🗑️ => can_pick_and_continue=0.0 ❌ (blocked!)
```

**ML learns:** "Pick flowers only when I can continue the path"

---

## 📋 **Complete Feature Breakdown (82 features)**

| Group | Features | Count | Purpose |
|-------|----------|-------|---------|
| Basic info | 0-11 | 12 | Board size, positions, capacities |
| Directional awareness | 12-43 | 32 | What's in each direction (N/S/E/W) |
| Task context | 44-53 | 10 | Game phase, progress, priorities |
| Path quality | 54-61 | 8 | Distance, obstacles to targets |
| Multi-flower strategy | 62-67 | 6 | TSP-like flower collection planning |
| Orientation | 68-71 | 4 | Current direction (one-hot) |
| Action validity | 72-77 | 6 | Can execute each action? |
| **Strategic planning** | **78-81** | **4** | **🆕 Drop/clean/pick strategy** |

---

## 🔄 **Retraining Required**

The old model was trained on 78 features. The new feature engineer produces 82 features. **You MUST retrain!**

### **Step 1: Clean Old Data (Optional)**
```bash
cd ml_player
mkdir -p data/training/backup
mv data/training/samples_*.jsonl data/training/backup/
```

### **Step 2: Collect New Training Data**
```bash
# Collect 1000 AI-solved games with strategic features
make ml-collect-quality-data
```

### **Step 3: Retrain Models**
```bash
# Train Random Forest + Gradient Boosting
make ml-train
```

**Expected output:**
```
✓ Total samples: 8,000-12,000
✓ Features: 82 (was 78)
✓ Test accuracy: 75-85%
```

### **Step 4: Restart ML Player**
```bash
# Stop current ML Player (Ctrl+C), then:
cd ml_player
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8001 --app-dir src
```

---

## 🎯 **Expected Improvements**

### **Behavior Before:**
- Robot picks flowers blindly
- Gets stuck when carrying flowers + obstacle ahead
- No drop strategy
- Random wandering

### **Behavior After:**
- Robot checks path before picking flowers (`can_pick_and_continue`)
- Detects "blocked with flowers" scenario (`blocked_with_flowers`)
- Looks for drop zones (`nearby_empty_cells_ratio`)
- Plans 2 steps ahead (`obstacles_ahead_2steps`)
- Executes: DROP → CLEAN → PICK → MOVE strategy

---

## 🧪 **Testing the Improvement**

### **Test Scenario: Blocked Path**
```
Grid:
⬜ ⬜ ⬜
⬜ 🤖 🌸
⬜ 🗑️ ⬜
```

**Old Model (78 features):**
1. Pick flower ✓
2. Rotate SOUTH ✓
3. Try to MOVE → **STUCK** ❌ (can_clean=0, has flowers)

**New Model (82 features):**
1. Check: `can_pick_and_continue=0.0` (obstacle beyond flower)
2. Rotate to avoid obstacle first
3. Pick flower when path is clear
4. OR: Pick flower → detect `blocked_with_flowers=1.0` → DROP → CLEAN → PICK → MOVE ✅

---

## 📊 **Feature Importance (Expected)**

After retraining, the new strategic features should rank highly:

```
Top features (expected):
1. can_move_forward        (15%)
2. can_pick_and_continue   (12%) 🆕
3. blocked_with_flowers    (10%) 🆕
4. capacity_utilization    (8%)
5. nearby_empty_cells      (7%) 🆕
6. obstacles_ahead_2steps  (6%) 🆕
...
```

---

## ✅ **Validation**

After retraining, verify the model learned the strategy:

```bash
# Check feature importance
cat ml_player/models/*_metrics.json | jq '.feature_importance' | head -20

# Verify 82 features
cat ml_player/models/*_metrics.json | jq '.train_samples'
# Should show: "features": 82
```

---

## 📝 **Files Modified**

1. ✅ `ml_player/src/hexagons/mlplayer/domain/ml/feature_engineer.py`
   - New strategic planning features (4)
   - Updated docstrings (78 → 82)
   - Updated `get_feature_names()` (82 names)

2. ✅ `ml_player/src/hexagons/mltraining/domain/ml/feature_engineer.py`
   - Same changes as above (training version)

3. ✅ `ml_player/src/hexagons/mlplayer/domain/core/entities/ai_ml_player.py`
   - **CRITICAL FIX:** Updated validation logic to use fixed index `72` instead of `len(features) - 6`
   - Before: `action_validity_start = len(features) - 6` → pointed to wrong features (76-81)
   - After: `action_validity_start = 72` → correctly points to action validity (72-77)

---

## 🚨 **Important Notes**

1. **Old models won't work** - They expect 78 features, new engineer produces 82
2. **Both training & prediction updated** - Consistent feature extraction
3. **Validation logic unchanged** - Still uses features 72-77 for action validity
4. **No API changes** - Same action encoding (9 classes: 0-8)

---

## 🎓 **Strategic Learning Path**

The model will learn these patterns from training data:

1. **Pattern 1:** `blocked_with_flowers=1 AND nearby_empty_cells>0` → **DROP**
2. **Pattern 2:** `can_pick_and_continue=0` → **ROTATE** (find better path)
3. **Pattern 3:** `obstacles_ahead_2steps=1` → **CLEAN** or **ROTATE** early
4. **Pattern 4:** `can_pick_and_continue=1 AND can_pick=1` → **PICK** confidently

These patterns emerge naturally from high-quality AI-solved game data! 🚀
