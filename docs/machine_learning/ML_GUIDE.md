# Machine Learning Implementation Guide

## Overview

The ML Player service now supports **true machine learning** for action prediction. The system uses supervised learning to train models on game play data and predict optimal actions.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  ML Pipeline Architecture                    │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌───────────────┐     ┌──────────────┐
│ Data         │────▶│  Feature      │────▶│    Model     │
│ Collection   │     │  Engineering  │     │   Training   │
└──────────────┘     └───────────────┘     └──────────────┘
       │                                            │
       │                                            ▼
       │                                    ┌──────────────┐
       │                                    │    Model     │
       │                                    │   Registry   │
       │                                    └──────────────┘
       │                                            │
       ▼                                            ▼
┌──────────────┐                          ┌──────────────┐
│ Trained      │◀─────────────────────────│  Inference   │
│ Models       │                          │   Service    │
└──────────────┘                          └──────────────┘
```

## Components

### 1. **Data Collector** (`domain/ml/data_collector.py`)

Collects game states and actions for training.

**Features**:
- Stores data in JSONL format (one sample per line)
- Organizes data by date for easy management
- Tracks statistics (total samples, action distribution)

**Usage**:
```python
from hexagons.mlplayer.domain.ml import GameDataCollector

collector = GameDataCollector(data_dir="data/training")

# Collect a sample
collector.collect_sample(
    game_id="game_123",
    game_state=game_state_dict,
    action="move",
    direction="NORTH",
    outcome={"success": True}
)

# Load samples
samples = collector.load_samples()
```

### 2. **Feature Engineer** (`domain/ml/feature_engineer.py`)

Transforms game states into ML-ready feature vectors.

**Features Extracted**:
- Board dimensions (rows, cols)
- Robot state (position, orientation, flowers, capacity)
- Princess position
- Flower/obstacle counts and positions
- Derived features:
  - Distance to princess (Manhattan)
  - Closest flower distance
  - Obstacle density
  - Path clearance
  - Orientation (one-hot encoding)

**Total Features**: 20 features

**Usage**:
```python
from hexagons.mlplayer.domain.ml import FeatureEngineer

engineer = FeatureEngineer()

# Extract features
features = engineer.extract_features(game_state)  # Returns numpy array

# Encode action
label = engineer.encode_action("move", "NORTH")  # Returns 0

# Decode action
action, direction = engineer.decode_action(0)  # Returns ("move", "NORTH")
```

### 3. **Model Trainer** (`domain/ml/model_trainer.py`)

Trains machine learning models on collected data.

**Supported Models**:
- **Random Forest**: Ensemble of decision trees
- **Gradient Boosting**: Sequential ensemble method

**Features**:
- Train/test split
- Comprehensive evaluation metrics
- Feature importance analysis
- Model persistence (pickle)
- Metrics storage (JSON)

**Usage**:
```python
from hexagons.mlplayer.domain.ml import ModelTrainer, GameDataCollector

collector = GameDataCollector(data_dir="data/training")
trainer = ModelTrainer(model_dir="models")

# Train model
result = trainer.train_from_collector(
    collector,
    model_type="random_forest",
    test_size=0.2,
    n_estimators=100
)

# Access results
model = result["model"]
metrics = result["metrics"]
print(f"Test accuracy: {metrics['test_accuracy']:.4f}")
```

### 4. **Model Registry** (`domain/ml/model_registry.py`)

Manages trained models and their versions.

**Features**:
- List all registered models
- Get best performing model
- Load models with caching
- Model metadata management

**Usage**:
```python
from hexagons.mlplayer.domain.ml import ModelRegistry

registry = ModelRegistry(model_dir="models")

# List all models
models = registry.list_models()

# Get best model
best_metadata = registry.get_best_model()

# Load best model
model, metadata = registry.load_best_model()
```

## Quick Start

### 1. Generate Synthetic Training Data

```bash
# Generate 1000 synthetic training samples
python scripts/generate_training_data.py --num-samples 1000

# With custom output directory
python scripts/generate_training_data.py \
  --num-samples 5000 \
  --output-dir data/training \
  --seed 42
```

This creates diverse game scenarios with optimal actions.

### 2. Train Your First Model

```bash
# Train a Random Forest model
python scripts/train_model.py --model-type random_forest

# With custom hyperparameters
python scripts/train_model.py \
  --model-type gradient_boosting \
  --n-estimators 200 \
  --max-depth 15 \
  --test-size 0.2
```

### 3. Use the Trained Model

The model will automatically be used by the ML Player service. Update your `AIMLPlayer`:

```python
from hexagons.mlplayer.domain.ml import ModelRegistry, FeatureEngineer

class AIMLPlayer:
    def __init__(self, config=None):
        self.config = config or StrategyConfig.default()

        # Load trained model
        registry = ModelRegistry()
        self.model, self.model_metadata = registry.load_best_model()
        self.feature_engineer = FeatureEngineer()

    def select_action(self, state):
        if self.model is None:
            # Fallback to heuristics
            return self._heuristic_action(state)

        # Extract features
        features = self.feature_engineer.extract_features(state.to_dict())

        # Predict action
        label = self.model.predict([features])[0]

        # Decode action
        action, direction = self.feature_engineer.decode_action(label)

        return action, direction
```

## Training Pipeline

### Step-by-Step Process

1. **Data Collection**:
   - Collect game states and actions during gameplay
   - Store in `data/training/samples_YYYY-MM-DD.jsonl`

2. **Feature Engineering**:
   - Transform raw game states into 20-dimensional feature vectors
   - Encode actions as integer labels (0-11)

3. **Model Training**:
   - Split data into train/test sets (80/20)
   - Train ensemble model (Random Forest or Gradient Boosting)
   - Evaluate on test set

4. **Model Evaluation**:
   - Calculate accuracy, precision, recall, F1-score
   - Analyze feature importance
   - Generate confusion matrix

5. **Model Registration**:
   - Save trained model to `models/` directory
   - Save metrics alongside model
   - Models are named with timestamps for versioning

6. **Model Serving**:
   - Load best model from registry
   - Use for real-time prediction
   - Fallback to heuristics if no model available

## Model Evaluation Metrics

After training, you'll see metrics like:

```
Training completed successfully!
═══════════════════════════════════════════════════════════
Train accuracy: 0.9823
Test accuracy: 0.9245
Train samples: 800
Test samples: 200

Top 10 Features:
  1. distance_to_princess: 0.1856
  2. closest_flower_distance: 0.1623
  3. flowers_collected: 0.1204
  4. robot_row: 0.0956
  5. robot_col: 0.0943
  6. path_clearance: 0.0812
  7. flowers_remaining: 0.0734
  8. obstacle_density: 0.0621
  9. princess_row: 0.0598
  10. princess_col: 0.0554
```

## Action Encoding

Actions are encoded as integer labels for classification:

| Label | Action   | Direction |
|-------|----------|-----------|
| 0     | move     | NORTH     |
| 1     | move     | SOUTH     |
| 2     | move     | EAST      |
| 3     | move     | WEST      |
| 4     | rotate   | NORTH     |
| 5     | rotate   | SOUTH     |
| 6     | rotate   | EAST      |
| 7     | rotate   | WEST      |
| 8     | pick     | -         |
| 9     | drop     | -         |
| 10    | give     | -         |
| 11    | clean    | -         |

**Total Classes**: 12

## Data Collection Strategies

### Real Gameplay Data

Collect data from actual games:

```python
# In your autoplay endpoint
collector = GameDataCollector()

# Before making a move
collector.collect_sample(
    game_id=game_id,
    game_state=current_state.to_dict(),
    action=predicted_action,
    direction=predicted_direction,
    outcome={"success": result.success}
)
```

### Synthetic Data

Generate diverse training scenarios:
- **Pick Flower**: Robot at flower location
- **Give Flowers**: Robot adjacent to princess with flowers
- **Move to Flower**: Robot navigating towards flower
- **Move to Princess**: Robot with flowers navigating to princess
- **Clean Obstacle**: Robot at obstacle location

## Model Comparison

Train multiple models and compare:

```bash
# Train Random Forest
python scripts/train_model.py --model-type random_forest

# Train Gradient Boosting
python scripts/train_model.py --model-type gradient_boosting

# Compare models
python -c "
from hexagons.mlplayer.domain.ml import ModelRegistry
registry = ModelRegistry()
for model in registry.list_models():
    print(f'{model.name}: {model.test_accuracy:.4f}')
"
```

## Advanced Features

### Hyperparameter Tuning

```bash
# Grid search over hyperparameters
for n_est in 50 100 200; do
  for max_d in 5 10 15; do
    python scripts/train_model.py \
      --n-estimators $n_est \
      --max-depth $max_d
  done
done
```

### Continuous Learning

Update models as new data arrives:

```bash
# Generate new data
python scripts/generate_training_data.py --num-samples 1000

# Retrain model
python scripts/train_model.py

# The new model will automatically be used if it performs better
```

### Model Versioning

All models are automatically versioned with timestamps:

```
models/
├── random_forest_20250127_143052.pkl
├── random_forest_20250127_143052_metrics.json
├── gradient_boosting_20250127_144235.pkl
└── gradient_boosting_20250127_144235_metrics.json
```

## Makefile Commands

Add these to your `Makefile`:

```makefile
# ML commands
ml-generate-data:
	poetry run python scripts/generate_training_data.py --num-samples 1000

ml-train:
	poetry run python scripts/train_model.py --model-type random_forest

ml-train-gb:
	poetry run python scripts/train_model.py --model-type gradient_boosting

ml-stats:
	poetry run python -c "from hexagons.mlplayer.domain.ml import GameDataCollector; \
	c = GameDataCollector(); print(c.get_statistics())"

ml-list-models:
	poetry run python -c "from hexagons.mlplayer.domain.ml import ModelRegistry; \
	r = ModelRegistry(); \
	for m in r.list_models(): print(f'{m.name}: accuracy={m.test_accuracy:.4f}')"
```

## Troubleshooting

### Issue: "Insufficient training data"

**Solution**: Generate more samples
```bash
python scripts/generate_training_data.py --num-samples 5000
```

### Issue: "Low model accuracy"

**Solutions**:
1. Collect more diverse training data
2. Tune hyperparameters
3. Try different model types
4. Check feature engineering

### Issue: "Model not found"

**Solution**: Train a model first
```bash
python scripts/train_model.py
```

## Future Enhancements

- [ ] Deep learning models (PyTorch)
- [ ] Reinforcement learning
- [ ] Online learning from gameplay
- [ ] A/B testing framework
- [ ] Model monitoring and alerts
- [ ] Feature store integration
- [ ] MLflow experiment tracking

## Performance Expectations

With well-curated training data:
- **Random Forest**: ~90-95% accuracy
- **Gradient Boosting**: ~92-96% accuracy
- **Inference Time**: < 10ms per prediction

## Summary

You now have a complete ML pipeline:
1. ✅ Data collection infrastructure
2. ✅ Feature engineering
3. ✅ Model training (Random Forest, Gradient Boosting)
4. ✅ Model registry and versioning
5. ✅ Easy-to-use scripts
6. ✅ Production-ready inference

Start by generating synthetic data, train your first model, and watch the ML Player learn optimal strategies!
