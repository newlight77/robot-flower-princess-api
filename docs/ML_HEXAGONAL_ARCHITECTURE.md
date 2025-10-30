# ML Architecture - Training and Inference Hexagons

## Overview

The ML Player application contains two separate hexagons following the Single Responsibility Principle:

1. **mltraining** hexagon - Data collection and model training
2. **mlplayer** hexagon - ML model inference and predictions

Both hexagons are within the **same rfp_ml_autoplay application** (port 8001).

### Important: AI Player Distribution

**rfp_ml_autoplay application** (port 8001):
- `AIMLPlayer` - Machine learning-based AI (uses trained models)

**rfp_game application** (port 8000):
- `AIGreedyPlayer` - BFS-based greedy strategy
- `AIOptimalPlayer` - A* pathfinding with multi-step planning
- `MLProxyPlayer` - HTTP client that delegates to rfp_ml_autoplay service

The separation allows the game to function with local AI strategies (Greedy, Optimal) without requiring the ML service, while optionally delegating to ML predictions when the service is available.

## Architecture

```
┌───────────────────────────────────────────────────────────┐
│          RFP Game Application (port 8000)                 │
│                                                           │
│   ╔════════════════╗               ╔═══════════════╗      │
│   ║     game       ║               ║   aiplayer    ║      │
│   ║    hexagon     ║──────────────>║    hexagon    ║      │
│   ║                ║               ║               ║      │
│   ║ - Board Logic  ║        ───────║ - AIGreedy    ║      │
│   ║ - Actions      ║       │───────║ - AIOptimal   ║      │
│   ║ - Game State   ║       │       ║ - MLProxy ────╫─-─┐  │
│   ╚════════════════╝       │       ╚═══════════════╝   │  │
│                            │                           │  │
└────────────────────────────│───────────────────────────┼──┘
             ________________│               ____________│
             |                              |
       Data Collection                      │ Autoplay
             │                              │ Requests
             │                              │
             |                              |
┌────────────|──────────────────────────────|───────────────┐
│            |      ML Player Application   |               │
│            ▼          (port 8001)         ▼               │
│   ╔════════════════╗              ╔═══════════════╗       │
│   ║  mltraining    ║              ║   mlplayer    ║       │
│   ║    hexagon     ║─────────────>║    hexagon    ║       │
│   ║                ║   models     ║               ║       │
│   ║ - Data Collect ║              ║ - AIMLPlayer  ║       │
│   ║ - Training     ║              ║ - Prediction  ║       │
│   ║ - Features     ║              ║ - Registry    ║       │
│   ╚════════════════╝              ╚═══════════════╝       │
│          │                                 │              │
│          ▼                                 ▼              │
│   [data/training/]                     [models/]          │
└───────────────────────────────────────────────────────────┘

Legend:
  ╔═══════╗  Hexagon boundary
  ║       ║
  ╚═══════╝

  ─────>    Data/control flow

  Port 8000: RFP Game (game + aiplayer hexagons)
  Port 8001: ML Player (mltraining + mlplayer hexagons)
```

## Responsibilities

### mltraining Hexagon
**Purpose**: Collect data and train models

**Location**: `rfp_ml_autoplay/src/hexagons/mltraining/`

**Components**:
- `domain/ml/DataCollector` - Stores gameplay samples
- `domain/ml/FeatureEngineer` - Converts game states to features
- `domain/ml/ModelTrainer` - Trains ML models (Random Forest, Gradient Boosting)
- `driver/bff/routers/ml_training_router` - Training API endpoints

**API Endpoints** (within rfp_ml_autoplay app):
- `POST /api/ml-training/collect` - Receive gameplay data
- `GET /api/ml-training/statistics` - Get collection stats

**Scripts** (in rfp_ml_autoplay/scripts/):
- `generate_training_data.py` - Create synthetic data
- `train_model.py` - Train models

**Data Flow**:
1. RFP Game → mltraining hexagon (gameplay data via `/api/ml-training/collect`)
2. mltraining → File System (stores in `rfp_ml_autoplay/data/training/`)
3. Training Scripts → mltraining (train models)
4. mltraining → File System (saves to `ml_player/models/`)

### mlplayer Hexagon
**Purpose**: Use trained models for ML-based predictions

**Location**: `rfp_ml_autoplay/src/hexagons/mlplayer/`

**Components**:
- `domain/core/entities/AIMLPlayer` - ML-based AI with heuristic fallback
- `domain/ml/ModelRegistry` - Loads trained models
- `domain/ml/FeatureEngineer` - Converts game states to features (for inference)
- `driver/bff/routers/ml_player_router` - Prediction API endpoints

**API Endpoints** (within rfp_ml_autoplay app):
- `POST /api/ml-player/predict/{game_id}` - Get ML-based action prediction
- `GET /api/ml-player/strategies` - List available ML strategies
- `GET /api/ml-player/strategies/{name}` - Get ML strategy details

**Data Flow**:
1. RFP Game → mlplayer hexagon (game state via `/api/ml-player/predict/{game_id}`)
2. mlplayer → File System (loads trained model from `rfp_ml_autoplay/models/`)
3. mlplayer → Uses FeatureEngineer to extract features from game state
4. mlplayer → Predicts action using trained ML model
5. mlplayer → RFP Game (returns predicted action)

**Note**: This hexagon is specifically for ML-based predictions. Other AI strategies (Greedy, Optimal, Proxy) are in `rfp_game/hexagons/aiplayer/`.

## Related: RFP Game AI Player Hexagon

**Note**: The following AI players are NOT in rfp_ml_autoplay, but in the RFP Game application:

### aiplayer Hexagon (rfp_game)
**Purpose**: Non-ML AI strategies and autoplay functionality

**Location**: `rfp_game/src/hexagons/aiplayer/`

**Components**:
- `domain/core/entities/AIGreedyPlayer` - BFS-based greedy strategy
- `domain/core/entities/AIOptimalPlayer` - A* pathfinding with multi-step planning
- `domain/core/entities/MLProxyPlayer` - Delegates decisions to ML Player service via HTTP
- `driver/bff/routers/aiplayer_router` - Autoplay API endpoints

**API Endpoints** (within rfp_game app on port 8000):
- `POST /api/games/{game_id}/autoplay` - Start autoplay with selected strategy

**Available Strategies**:
- `greedy` - Uses AIGreedyPlayer (BFS-based)
- `optimal` - Uses AIOptimalPlayer (A* with planning)
- `ml` - Uses MLProxyPlayer (delegates to ml_player service)

## Key Changes

### 1. New Hexagon Created Within rfp_ml_autoplay
- `rfp_ml_autoplay/src/hexagons/mltraining/` - Training hexagon
- Same application, same port (8001)
- Shares FastAPI app, but has own router

### 2. Files Organized by Hexagon

**mltraining hexagon** (`rfp_ml_autoplay/src/hexagons/mltraining/`):
- `domain/ml/data_collector.py`
- `domain/ml/feature_engineer.py`
- `domain/ml/model_trainer.py`
- `driver/bff/routers/ml_training_router.py` - `/collect` endpoint
- `driver/bff/schemas/data_collection_schema.py`

**mlplayer hexagon** (`rfp_ml_autoplay/src/hexagons/mlplayer/`):
- `domain/core/entities/ai_ml_player.py` - ML-based AI player only
- `domain/ml/model_registry.py` - Loads and manages trained models
- `domain/ml/feature_engineer.py` - Feature extraction for inference (duplicate of mltraining's version)
- `driver/bff/routers/ml_player_router.py` - `/predict` and `/strategies` endpoints

**Shared** (`rfp_ml_autoplay/`):
- `scripts/generate_training_data.py`
- `scripts/train_model.py`
- `models/` directory
- `data/training/` directory

### 3. RFP Game Updates

**gameplay_data_collector.py**:
- Sends data to ML Player service (same as before)
- Uses endpoint `/api/ml-training/collect` (training hexagon)
- Port remains 8001

**dependencies.py**:
- Uses `ML_PLAYER_SERVICE_URL` environment variable
- Default URL: `http://localhost:8001`

## Environment Variables

### RFP Game
- `ML_PLAYER_SERVICE_URL` - ML Player service URL (default: http://localhost:8001)
- `ENABLE_DATA_COLLECTION` - Enable/disable data collection (default: false)

### ML Player (both hexagons)
- `DATA_DIR` - Training data directory (default: data/training)
- `MODEL_DIR` - Model storage/loading directory (default: models)
- `GAME_SERVICE_URL` - RFP Game service URL (default: http://localhost:8000)

## Benefits

1. **Separation of Concerns**
   - Training and inference logic are separated into distinct hexagons
   - Each hexagon has clear, focused responsibility
   - Easier to maintain and test independently

2. **Single Application Deployment**
   - Both hexagons share the same FastAPI application
   - Single deployment process
   - Simpler infrastructure management
   - Shared dependencies and configuration

3. **Clear Domain Boundaries**
   - mltraining: Data collection, feature engineering, model training
   - mlplayer: Model loading, predictions, AI strategies
   - Hexagonal architecture enforced within single app

4. **Shared Resources**
   - Both hexagons access same models directory
   - Both use same data storage
   - Simplified model lifecycle (train → use)

## Running Services

```bash
# Terminal 1: RFP Game
cd rfp_game
make run  # Port 8000

# Terminal 2: ML Player (includes both hexagons)
cd rfp_ml_autoplay
make run  # Port 8001
```

Both `/api/ml-player/*` and `/api/ml-training/*` endpoints are available on port 8001.

## Data Flow Example

### Collecting Data
```
1. Player performs action in RFP Game (port 8000)
2. RFP Game sends to ML Player service → mltraining hexagon (/api/ml-training/collect on port 8001)
3. mltraining hexagon stores in rfp_ml_autoplay/data/training/samples_YYYY-MM-DD.jsonl
```

### Training Model
```
1. Run: cd rfp_ml_autoplay && make ml-train (or ml-train-gb)
2. Script loads samples from rfp_ml_autoplay/data/training/
3. mltraining hexagon extracts features using FeatureEngineer
4. mltraining hexagon trains model (Random Forest or Gradient Boosting)
5. Saves to rfp_ml_autoplay/models/model_name_timestamp.pkl
```

### Using AI
```
1. RFP Game calls ML Player service → mlplayer hexagon (/api/ml-player/predict on port 8001)
2. mlplayer hexagon loads best model from rfp_ml_autoplay/models/
3. mlplayer hexagon extracts features from game state
4. mlplayer hexagon predicts action using trained model
5. Returns action to RFP Game
```

## Testing

```bash
# Test ML Player (both hexagons)
cd rfp_ml_autoplay
make test

# E2E Test
# 1. Start both services
cd rfp_game && make run  # Terminal 1
cd rfp_ml_autoplay && make run  # Terminal 2

# 2. Enable data collection
export ENABLE_DATA_COLLECTION=true

# 3. Play game and verify data is collected
# Check rfp_ml_autoplay/data/training/samples_*.jsonl

# 4. Train model
cd rfp_ml_autoplay && make ml-train

# 5. Test AI: Use ML Player strategy in game
```

## Project Structure

```
rfp_ml_autoplay/
├── src/
│   ├── hexagons/
│   │   ├── mltraining/          # Training Hexagon
│   │   │   ├── domain/
│   │   │   │   └── ml/
│   │   │   │       ├── data_collector.py
│   │   │   │       ├── feature_engineer.py
│   │   │   │       └── model_trainer.py
│   │   │   ├── driver/
│   │   │   │   └── bff/
│   │   │   │       ├── routers/
│   │   │   │       │   └── ml_training_router.py
│   │   │   │       └── schemas/
│   │   │   │           └── data_collection_schema.py
│   │   │   └── driven/
│   │   │       └── adapters/
|   │   │   ├── mlplayer/            # Inference Hexagon
|   │   │   │   ├── domain/
|   │   │   │   │   ├── core/
|   │   │   │   │   │   └── entities/
|   │   │   │   │   │       └── ai_ml_player.py      # ML-based AI only
|   │   │   │   │   └── ml/
|   │   │   │   │       ├── model_registry.py
|   │   │   │   │       └── feature_engineer.py      # Duplicate (for inference)
│   │   │   ├── driver/
│   │   │   │   └── bff/
│   │   │   │       └── routers/
│   │   │   │           └── ml_player_router.py
│   │   │   └── driven/
│   │   │       └── adapters/
│   │   └── health/              # Health Check Hexagon
│   ├── configurator/
│   │   ├── dependencies.py      # Shared dependencies
│   │   └── settings.py
│   ├── shared/
│   │   └── logging.py
│   └── main.py                  # FastAPI app (includes all routers)
├── scripts/
│   ├── generate_training_data.py
│   └── train_model.py
├── models/                      # Trained models (shared)
├── data/
│   └── training/                # Training data (shared)
└── tests/
```

## Future Enhancements

1. **FeatureEngineer Duplication**
   - Currently duplicated in both `mltraining` and `mlplayer` hexagons
   - **Reason**: Each hexagon can evolve independently
   - **mltraining**: Uses it for training data preparation
   - **mlplayer**: Uses it for inference feature extraction
   - **Alternative**: Could extract to shared module if they must stay identical
   - **Current decision**: Keep separate for hexagon independence

2. **Model Versioning**
   - Track model versions
   - A/B testing different models
   - Rollback capability

3. **Monitoring**
   - Training metrics dashboard
   - Inference performance monitoring
   - Data quality checks

4. **Advanced Training**
   - Hyperparameter tuning
   - Cross-validation
   - Model ensemble

5. **Hexagon Expansion**
   - Could split into separate microservices later
   - Each hexagon ready for independent deployment
   - Current setup allows easy transition
