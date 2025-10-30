# ML Player Service

AI Machine Learning player for Robot Flower Princess game using hybrid heuristic and ML-ready architecture.

## 🎯 Overview

This service provides an ML-based player that can predict optimal actions for the Robot Flower Princess game. It uses a **hybrid approach**:

- **MVP**: Heuristic-based decision making with tuned weighted parameters
- **Future**: Designed for easy upgrade to true ML models (scikit-learn, PyTorch, etc.)

## 🏗️ Architecture

The project follows **Hexagonal Architecture (Ports and Adapters)**:

```
ml_player/
├── src/
│   ├── hexagons/
│   │   └── mlplayer/
│   │       ├── domain/              # Business logic
│   │       │   ├── core/
│   │       │   │   ├── entities/    # AIMLPlayer, BoardState
│   │       │   │   └── value_objects/  # StrategyConfig
│   │       │   ├── ports/           # Interfaces
│   │       │   ├── services/        # Domain services
│   │       │   └── use_cases/       # Application logic
│   │       ├── driver/              # Inbound adapters
│   │       │   └── bff/
│   │       │       ├── routers/     # FastAPI routes
│   │       │       └── schemas/     # Pydantic models
│   │       └── driven/              # Outbound adapters
│   │           └── adapters/        # HTTP client, etc.
│   ├── configurator/                # Settings & DI
│   └── shared/                      # Common utilities
└── tests/                           # Test suite
    ├── unit/
    ├── integration/
    └── feature-component/
```

## 🚀 Features

### Current (MVP)
- ✅ Heuristic-based action prediction
- ✅ Configurable strategies (default, aggressive, conservative)
- ✅ RESTful API for predictions
- ✅ Weighted scoring system
- ✅ Feature extraction from game state

### Future (ML Upgrade Path)
- 🔄 Supervised learning from optimal solutions
- 🔄 Reinforcement learning (Q-learning, DQN)
- 🔄 Neural network policy
- 🔄 Model training & persistence
- 🔄 A/B testing between strategies

## 📋 Requirements

- Python 3.13+
- Poetry for dependency management
- Docker & Docker Compose (optional)
- Access to Robot Flower Princess game service

## 🛠️ Installation

### Using Poetry

```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Run the service
make run
```

### Using Docker

```bash
# Build and run
make docker-up

# Or manually
docker-compose up --build
```

## 🎮 Usage

### Start the Service

```bash
# Development mode with hot reload
make run

# Or with uvicorn directly
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8001 --app-dir src
```

The service will be available at:
- API: http://localhost:8001
- Docs: http://localhost:8001/docs
- Health: http://localhost:8001/health

### API Endpoints

#### Predict Action
```bash
POST /api/ml-player/predict/{game_id}
```

Request body:
```json
{
  "strategy": "default"  // or "aggressive", "conservative"
}
```

Response:
```json
{
  "game_id": "123e4567-e89b-12d3-a456-426614174000",
  "action": "move",
  "direction": "NORTH",
  "confidence": 0.85,
  "board_score": 12.5,
  "config_used": {
    "distance_to_flower_weight": -2.5,
    "risk_aversion": 0.7,
    ...
  }
}
```

#### List Strategies
```bash
GET /api/ml-player/strategies
```

#### Get Strategy Config
```bash
GET /api/ml-player/strategies/{strategy_name}
```

### Python Client Example

```python
import httpx

async def predict_action(game_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://localhost:8001/api/ml-player/predict/{game_id}",
            json={"strategy": "default"}
        )
        return response.json()
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test levels
make test-unit
make test-integration
make test-feature-component
```

## 🔧 Configuration

Configuration via environment variables or `.env` file:

```bash
# Application
APP_NAME="ML Player Service"
DEBUG=false

# Server
HOST=0.0.0.0
PORT=8001

# Game Service
GAME_SERVICE_URL=http://localhost:8000
GAME_SERVICE_TIMEOUT=30

# ML Configuration
DEFAULT_STRATEGY=default
ENABLE_ML_MODELS=false
MODEL_PATH=./models

# Logging
LOG_LEVEL=INFO
```

## 🎓 ML Upgrade Path

### Phase 1: Current (Heuristic MVP)
✅ Weighted scoring with tunable parameters
✅ Rule-based decision tree
✅ Feature extraction ready

### Phase 2: Supervised Learning
1. Collect training data from AIOptimalPlayer solutions
2. Train sklearn classifier (Random Forest, XGBoost)
3. Replace `evaluate_board()` with model predictions
4. Add model persistence (joblib)

### Phase 3: Deep Learning
1. Design neural network architecture
2. Train policy network with PyTorch/TensorFlow
3. Replace `select_action()` with network output
4. Add model serving infrastructure

### Phase 4: Reinforcement Learning
1. Implement Q-learning or DQN
2. Self-play training
3. Replace entire decision pipeline
4. Continuous learning from games

## 📊 Strategies

### Default
- Balanced approach
- Risk aversion: 0.7
- Lookahead: 3 moves

### Aggressive
- Lower risk aversion (0.3)
- Higher exploration (0.5)
- Shorter lookahead (2 moves)
- Prioritizes speed over safety

### Conservative
- Higher risk aversion (0.9)
- Lower exploration (0.1)
- Longer lookahead (4 moves)
- Prioritizes safety and planning

## 🚢 Deployment

### Local Development
```bash
make run
```

### Docker
```bash
make docker-up
```

### Production
```bash
# Build image
docker build -t ml-player-api:v1.0.0 .

# Run container
docker run -p 8001:8001 \
  -e GAME_SERVICE_URL=http://game-service:8000 \
  ml-player-api:v1.0.0
```

## 📝 Development

### Code Quality
```bash
# Format code
make format

# Lint
make lint
```

### Add New Strategy

1. Edit `src/hexagons/mlplayer/domain/core/value_objects/strategy_config.py`
2. Add new class method:
```python
@classmethod
def my_strategy(cls) -> "StrategyConfig":
    return cls(
        risk_aversion=0.5,
        exploration_factor=0.4,
        # ... other params
    )
```

3. Update router in `ml_player_router.py`

## 🤝 Contributing

1. Follow hexagonal architecture principles
2. Write tests for new features
3. Maintain backward compatibility
4. Document ML experiments

## 📄 License

Same as parent project.

## 🔗 Related Services

- **RFP Game Service**: Main game logic (port 8000)
- **ML Player Service**: This service (port 8001)
- **Frontend**: Game UI (port 3000)

## 📚 References

- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Poetry Documentation](https://python-poetry.org/docs/)
