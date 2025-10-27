# Optimal ML Strategy for Robot Flower Princess Game

## Executive Summary

This document outlines an improved machine learning strategy for the Robot Flower Princess game, focusing on:
1. **Enhanced feature engineering** - capturing spatial awareness and task context
2. **Optimal data collection** - learning from successful game playthroughs
3. **Improved model architecture** - better suited for sequential decision-making

## Problem Analysis

### Game Objectives (in order)
1. **Pick all flowers** - robot must navigate to and collect all flowers on the board
2. **Deliver to princess** - once all flowers are collected, deliver them to the princess
3. **Clean obstacles** - remove obstacles that block optimal paths
4. **Optimize path** - minimize total actions by choosing efficient routes

### Current Limitations

#### 1. **Insufficient Spatial Awareness**
Current features (20 total):
- Basic positions (robot, princess, flowers)
- Counts (flowers, obstacles)
- Single distance metrics (closest flower, distance to princess)

**Missing:**
- What's in each direction (NORTH, SOUTH, EAST, WEST)?
- Is there a flower/obstacle/princess adjacent to robot?
- Path complexity/estimated steps to targets
- Relative positions of multiple flowers

#### 2. **Poor Data Collection Strategy**
Current approach generates **synthetic** scenarios:
- Random board layouts
- Isolated action examples (pick, move, give)
- No context of full game strategy
- Doesn't learn optimal sequencing

**Problem:** Model learns individual actions but not the **strategy** of:
- "Pick nearest flower first"
- "Clean obstacles only if they block the path"
- "Move towards next target efficiently"

#### 3. **Limited Action Context**
- Doesn't distinguish between game phases (collecting vs delivering)
- No "task priority" features
- Missing "next best action" heuristics

---

## Proposed Solution

### 1. Enhanced Feature Engineering

#### A. **Directional Awareness Features** (16 features)

Add features for each direction (N, S, E, W):
- **Adjacent cell type** (one-hot: empty, flower, obstacle, princess, out-of-bounds)
- **Distance to nearest flower** in that direction
- **Distance to nearest obstacle** in that direction
- **Is this direction towards nearest flower?** (boolean)

```python
def extract_directional_features(robot_pos, board_state, flowers, obstacles, princess):
    """Extract features for each cardinal direction."""
    features = []

    for direction in ['NORTH', 'SOUTH', 'EAST', 'WEST']:
        adjacent_pos = get_adjacent_position(robot_pos, direction)

        # What's in the adjacent cell?
        cell_type = get_cell_type(adjacent_pos, flowers, obstacles, princess, board_size)
        features.extend(one_hot_encode(cell_type))  # 5 features

        # Distance to nearest flower in this direction
        features.append(nearest_flower_in_direction(robot_pos, direction, flowers))

        # Distance to nearest obstacle in this direction
        features.append(nearest_obstacle_in_direction(robot_pos, direction, obstacles))

        # Is this direction towards closest flower?
        features.append(is_direction_towards_target(robot_pos, direction, nearest_flower))

    return features  # 4 directions × 8 features = 32 features
```

#### B. **Task Context Features** (10 features)

```python
def extract_task_context_features(game_state):
    """Features describing current task phase and priorities."""
    features = []

    # Game phase
    features.append(1.0 if has_uncollected_flowers else 0.0)  # Collection phase
    features.append(1.0 if has_collected_flowers and all_picked else 0.0)  # Delivery phase
    features.append(1.0 if at_capacity else 0.0)  # Need to deliver/drop

    # Task priorities
    features.append(percentage_flowers_collected)  # Progress: 0.0 to 1.0
    features.append(estimated_moves_to_nearest_flower)
    features.append(estimated_moves_to_princess)
    features.append(obstacles_blocking_optimal_path)  # Count

    # Robot capacity status
    features.append(flowers_held / capacity)  # Utilization
    features.append(can_pick_more_flowers)  # Boolean
    features.append(should_deliver_now)  # Heuristic: true if all flowers picked

    return features  # 10 features
```

#### C. **Path Quality Features** (8 features)

```python
def extract_path_features(robot_pos, target_pos, obstacles, board):
    """Features about path quality to target."""
    features = []

    # Manhattan distance
    features.append(manhattan_distance(robot_pos, target_pos))

    # Estimated actual path length (BFS/A*)
    features.append(shortest_path_length(robot_pos, target_pos, obstacles))

    # Path efficiency (actual / manhattan)
    efficiency = features[1] / (features[0] + 1e-6)
    features.append(efficiency)

    # Obstacles in straight-line path
    features.append(obstacles_in_line(robot_pos, target_pos, obstacles))

    # Path exists? (boolean)
    features.append(1.0 if features[1] < float('inf') else 0.0)

    # Alternative paths available
    features.append(count_alternative_paths(robot_pos, target_pos, obstacles))

    # Nearest flower and princess path features
    nearest_flower = get_nearest_flower(robot_pos, flowers)
    features.append(shortest_path_length(robot_pos, nearest_flower, obstacles))
    features.append(shortest_path_length(robot_pos, princess_pos, obstacles))

    return features  # 8 features
```

#### D. **Multi-Flower Strategy Features** (6 features)

```python
def extract_flower_strategy_features(robot_pos, flowers, princess_pos, obstacles):
    """Features for optimal flower collection strategy."""
    features = []

    # Sorted distances to all remaining flowers
    flower_distances = sorted([manhattan_distance(robot_pos, f) for f in flowers])

    # Distance to nearest, 2nd nearest, 3rd nearest (0 if not exists)
    features.extend([flower_distances[i] if i < len(flower_distances) else 0.0
                     for i in range(3)])

    # Average distance to all remaining flowers
    features.append(sum(flower_distances) / len(flower_distances) if flowers else 0.0)

    # Total estimated path to collect all flowers + deliver (TSP approximation)
    features.append(estimate_total_collection_path(robot_pos, flowers, princess_pos))

    # Clustering: are flowers clustered or spread?
    features.append(flower_clustering_metric(flowers))

    return features  # 6 features
```

### **Total New Features: ~72 features** (up from 20)

---

### 2. Optimal Data Collection Strategy

#### A. **Collect from Real Gameplay** (PRIMARY)

Instead of synthetic data, collect from actual games solved by existing AI players:

```python
# scripts/collect_gameplay_data.py

def collect_from_ai_games(num_games=1000):
    """Collect training data from AI-solved games."""

    collector = GameDataCollector()

    for i in range(num_games):
        # Create random game
        game = Game(rows=random.choice([5, 7, 10]),
                   cols=random.choice([5, 7, 10]))

        # Use GREEDY AI (75% success rate) to solve
        ai_player = AIGreedyPlayer()
        actions = ai_player.solve(game)

        if game.get_status() == GameStatus.VICTORY:
            # Replay game and collect state-action pairs
            game_replay = Game(same_config_as=game)

            for action, direction in actions:
                # Collect current state before action
                game_state = game_replay.to_dict()
                collector.collect_sample(
                    game_id=f"ai_game_{i}",
                    game_state=game_state,
                    action=action,
                    direction=direction,
                    outcome={"success": True, "final_victory": True}
                )

                # Execute action
                execute_action(game_replay, action, direction)

    return collector
```

**Benefits:**
- Learns complete game strategies
- Sees optimal action sequences
- Learns from successful patterns
- Captures real decision-making contexts

#### B. **Augment with Expert Heuristics**

Add samples demonstrating key strategies:

```python
def generate_expert_samples():
    """Generate samples from expert heuristics."""

    samples = []

    # Strategy 1: Always pick nearest flower first
    for _ in range(200):
        state = create_game_with_multiple_flowers()
        nearest_flower = find_nearest_flower(state)
        optimal_action = determine_action_towards(state, nearest_flower)
        samples.append((state, optimal_action))

    # Strategy 2: Clean obstacle only if blocking path
    for _ in range(200):
        state = create_game_with_obstacle_on_path()
        if obstacle_blocks_optimal_path(state):
            samples.append((state, "clean", direction_to_obstacle))
        else:
            samples.append((state, "move", direction_around_obstacle))

    # Strategy 3: Deliver when all flowers picked
    for _ in range(200):
        state = create_game_with_all_flowers_collected()
        direction_to_princess = calculate_direction(state)
        samples.append((state, "give", direction_to_princess))

    return samples
```

#### C. **Balanced Dataset Composition**

Target distribution:
- **60%** Real AI gameplay (successful games)
- **20%** Expert heuristic samples (strategy patterns)
- **15%** Edge case scenarios (obstacles, capacity limits)
- **5%** Failure cases (what NOT to do)

**Minimum dataset size:** 10,000 samples
- Diverse board sizes (5×5, 7×7, 10×10)
- Various flower counts (1-10)
- Different obstacle densities (0-30%)

---

### 3. Improved Model Architecture

#### A. **Model Choice: Gradient Boosting (Current) + Neural Network (Proposed)**

**Keep Gradient Boosting for:**
- Fast inference
- Good with tabular features
- Interpretable feature importance

**Add Neural Network for:**
- Better pattern recognition
- Handling feature interactions
- Sequence learning

#### B. **Ensemble Approach**

```python
class HybridMLPlayer:
    """Hybrid model combining multiple approaches."""

    def __init__(self):
        self.gb_model = GradientBoostingClassifier()  # Quick decisions
        self.nn_model = NeuralNetworkClassifier()     # Complex patterns
        self.heuristic = HeuristicPlayer()            # Fallback

    def predict(self, game_state):
        features = extract_enhanced_features(game_state)

        # Get predictions from all models
        gb_pred, gb_conf = self.gb_model.predict_proba(features)
        nn_pred, nn_conf = self.nn_model.predict_proba(features)

        # Weighted ensemble
        if gb_conf > 0.9:
            return gb_pred  # High confidence GB
        elif nn_conf > 0.85:
            return nn_pred  # High confidence NN
        else:
            # Combine predictions or use heuristic
            combined = weighted_average(gb_pred, nn_pred)

            if max(combined) < 0.7:  # Low confidence
                return self.heuristic.get_action(game_state)

            return combined
```

#### C. **Training Strategy**

```python
def train_models():
    """Train all model components."""

    # 1. Load and prepare data
    X, y = load_training_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # 2. Train Gradient Boosting (fast, baseline)
    gb_model = GradientBoostingClassifier(
        n_estimators=200,
        max_depth=8,
        learning_rate=0.1,
        min_samples_split=20
    )
    gb_model.fit(X_train, y_train)

    # 3. Train Neural Network (complex patterns)
    nn_model = Sequential([
        Dense(128, activation='relu', input_dim=72),
        Dropout(0.3),
        Dense(64, activation='relu'),
        Dropout(0.2),
        Dense(32, activation='relu'),
        Dense(24, activation='softmax')  # 24 action classes
    ])
    nn_model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    nn_model.fit(
        X_train, to_categorical(y_train, 24),
        epochs=50,
        batch_size=32,
        validation_split=0.2,
        callbacks=[EarlyStopping(patience=5)]
    )

    # 4. Evaluate ensemble
    evaluate_ensemble(gb_model, nn_model, X_test, y_test)
```

---

### 4. Evaluation Metrics

Track these metrics to measure improvement:

#### A. **Game Performance**
- **Win rate**: % of games successfully completed
- **Average actions**: Total actions per completed game
- **Efficiency**: Actions / optimal_actions ratio

#### B. **Strategy Metrics**
- **Flower collection order**: Does it pick nearest first?
- **Obstacle cleaning**: Only cleans when necessary?
- **Path optimality**: Takes shortest paths?

#### C. **Model Metrics**
- **Prediction accuracy**: % correct actions
- **Confidence scores**: Distribution of prediction confidence
- **Feature importance**: Which features matter most?

---

## Implementation Plan

### Phase 1: Enhanced Features (Week 1)
1. ✅ Implement directional awareness features
2. ✅ Add task context features
3. ✅ Add path quality features
4. ✅ Update feature_engineer.py with 72 features
5. ✅ Test feature extraction

### Phase 2: Data Collection (Week 2)
1. ✅ Implement AI gameplay collector
2. ✅ Generate 5,000 AI gameplay samples
3. ✅ Add 2,000 expert heuristic samples
4. ✅ Add 1,000 edge case samples
5. ✅ Validate dataset balance

### Phase 3: Model Training (Week 3)
1. ✅ Retrain GB model with new features
2. ✅ Train NN model
3. ✅ Implement ensemble predictor
4. ✅ Tune hyperparameters
5. ✅ Evaluate and compare

### Phase 4: Integration & Testing (Week 4)
1. ✅ Deploy new model to ML Player service
2. ✅ A/B test against current model
3. ✅ Monitor win rate and efficiency
4. ✅ Iterate based on results

---

## Expected Improvements

### Before (Current)
- **Features**: 20 basic features
- **Data**: 1,000 synthetic samples
- **Win Rate**: ~40-50% (estimated)
- **Strategy**: Random/inconsistent

### After (Proposed)
- **Features**: 72 enhanced features with spatial awareness
- **Data**: 10,000 diverse gameplay samples
- **Win Rate**: 70-80% (target)
- **Strategy**: Nearest-first flower collection, optimal pathfinding

---

## Conclusion

The proposed ML strategy addresses the core limitations:

1. **Better features** capture spatial awareness and task context
2. **Real gameplay data** teaches optimal strategies, not just isolated actions
3. **Ensemble approach** combines fast heuristics with learned patterns
4. **Clear metrics** track progress toward game objectives

**Key Insight:** The game is fundamentally a **sequential decision problem** with clear objectives. The ML model should learn the **strategy** (pick nearest flower, optimize path, deliver to princess), not just individual action prediction.

**Next Step:** Start with Phase 1 - implement enhanced features and validate they improve model performance.
