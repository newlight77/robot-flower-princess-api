# 🤖🌸👑 Robot Flower Princess API

A strategic puzzle game API where you guide a robot to collect flowers and deliver them to a princess.

[![CI](https://github.com/yourusername/Robot-Flower-Princess-Back/workflows/CI/badge.svg)](https://github.com/yourusername/Robot-Flower-Princess-Back/actions)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com)

## 🎮 Game Overview

### Objective
Guide the robot to collect all flowers on the board and deliver them to the princess.

### Game Elements
- 🤖 **Robot**: Starts at top-left (0,0), controlled by player
- 👑 **Princess**: At bottom-right, receives flowers
- 🌸 **Flowers**: Scattered randomly (max 10% of board), need to be collected
- 🗑️ **Obstacles**: Block movement (~30% of board), can be cleaned
- ⬜ **Empty**: Walkable spaces

### Actions
1. **↩️ Rotate**: Turn to face a direction (north, south, east, west)
2. **🚶‍♂️ Move**: Move one cell in the direction faced
3. **⛏️🌸 Pick Flower**: Pick up a flower (max 12 at once)
4. **🫳🌸 Drop Flower**: Drop a flower on an empty cell
5. **🫴🏼🌸 Give Flowers**: Deliver flowers to princess
6. **🗑️ Clean**: Remove an obstacle

### Victory & Game Over
- **Victory**: All flowers delivered to princess
- **Game Over**: Invalid action attempted

## 🚀 Quick Start

### Pre-requisites
```bash
brew install poetry
pyenv install 3.13.0
```

### Using Docker (Recommended)
```bash
docker-compose up --build
# API available at http://localhost:8000
```

### Using Poetry
```bash
# Setup
pyenv local 3.13.0
poetry install
poetry env activate

# Run
make run
# or
poetry run uvicorn robot_flower_princess..main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Endpoints

#### Game Management
- `POST /api/games` - Create a new game
- `GET /api/games/{game_id}` - Get game state
- `GET /api/games/{game_id}/history` - Get move history

#### Actions
- `POST /api/games/{game_id}/actions/rotate` - Rotate robot
- `POST /api/games/{game_id}/actions/move` - Move robot
- `POST /api/games/{game_id}/actions/pick` - Pick flower
- `POST /api/games/{game_id}/actions/drop` - Drop flower
- `POST /api/games/{game_id}/actions/give` - Give flowers to princess
- `POST /api/games/{game_id}/actions/clean` - Clean obstacle

#### AI Player
- `POST /api/games/{game_id}/autoplay` - Let AI solve the game

## 🧪 Testing

```bash
make test                 # Run all tests
make test-cov             # Run with coverage (legacy html in htmlcov/)
make coverage-unit        # Run unit tests and write .coverage/coverage-unit.xml
make coverage-integration # Run integration tests and write .coverage/coverage-integration.xml
make coverage-e2e         # Run end-to-end test and write .coverage/coverage-e2e.xml
make coverage-combine     # Merge coverage files and write .coverage/coverage-combined.xml + .coverage/coverage_html/
make lint                 # Run linters
make format               # Format code
```

After running `make coverage-combine` open the HTML report locally:

```bash
open .coverage/coverage_html/index.html
```

## 🏗️ Architecture

This project follows **Hexagonal Architecture** (Ports and Adapters):

```
src/robot_flower_princess/
├── domain/              # Core business logic
│   ├── entities/        # Game entities
│   ├── value_objects/   # Immutable values
│   ├── services/        # Domain services
│   └── exceptions/      # Domain exceptions
├── application/         # Use cases
│   ├── ports/           # Interfaces
│   └── use_cases/       # Application logic
└── infrastructure/      # External adapters
    ├── api/             # FastAPI
    ├── persistence/     # In-memory repository
    └── ai/              # AI solver
```

## 📖 Example Usage

### Create a Game
```bash
curl -X POST "http://localhost:8000/api/games" \
  -H "Content-Type: application/json" \
  -d '{"rows": 10, "cols": 10}'
```

### Rotate Robot
```bash
curl -X POST "http://localhost:8000/api/games/{game_id}/actions/rotate" \
  -H "Content-Type: application/json" \
  -d '{"direction": "south"}'
```

### Move Robot
```bash
curl -X POST "http://localhost:8000/api/games/{game_id}/actions/move"
```

### Auto-Play
```bash
curl -X POST "http://localhost:8000/api/games/{game_id}/autoplay"
```

### Get History
```bash
curl -X GET "http://localhost:8000/api/games/{game_id}/history"
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [Python 3.13](https://www.python.org/)
- [Poetry](https://python-poetry.org/)
- [Docker](https://www.docker.com/)
