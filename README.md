# Robot Flower Princess - Multi-Service Project

This repository contains two independent services that work together:

## 🎮 Services

### 1. RFP Game (`rfp_game/`)
The main game service implementing the Robot Flower Princess game logic.

**Key Features**:
- Core game mechanics (robot movement, flower collection, princess interactions)
- Multiple AI strategies (Greedy, Optimal, ML Proxy)
- RESTful API with FastAPI
- Hexagonal architecture (driver, domain, driven)

**Tech Stack**: Python 3.13, FastAPI, Poetry, Pytest

**Documentation**:
- [Game Rules](docs/GAME_RULES.md) - Learn how to play
- [Service README](rfp_game/README.md) - Technical details

### 2. ML Player (`ml_player/`)
Machine learning-based player service that provides intelligent game-playing strategies.

**Key Features**:
- AI ML Player with heuristic-based decision making
- HTTP client for game state integration
- Extensible architecture for future ML model integration
- Independent microservice architecture

**Tech Stack**: Python 3.13, FastAPI, Poetry, Pytest

**Documentation**: See [`ml_player/README.md`](ml_player/README.md)

---

## 🚀 CI/CD Workflows

This project uses **separate GitHub Actions workflows** for each service:

### RFP Game CI (`.github/workflows/ci.yml`)
**Triggers**: Only when files in `rfp_game/` change
- ✅ Unit tests (146 tests)
- ✅ Integration tests (6 tests)
- ✅ Feature-component tests (13 tests)
- ✅ Coverage check (80%+ enforced)
- ✅ Linting (Black + Ruff)
- ✅ Docker build & health check

### ML Player CI (`.github/workflows/ml_player-ci.yml`)
**Triggers**: Only when files in `ml_player/` change
- ✅ Unit tests (21 tests)
- ✅ Coverage check (80%+ enforced)
- ✅ Linting (Black + Ruff)
- ✅ Docker build & health check

**Benefits**:
- ⚡ **Faster CI**: Only runs tests for changed services
- 💰 **Cost Efficient**: Reduces unnecessary CI runs
- 🔒 **Isolation**: Changes to one service don't trigger tests for the other
- 🎯 **Clear Feedback**: CI results are specific to the changed service

---

## 📁 Project Structure

```
.
├── rfp_game/              # Main game service
│   ├── src/
│   │   ├── hexagons/      # Hexagonal architecture
│   │   │   ├── game/      # Game hexagon
│   │   │   ├── aiplayer/  # AI Player hexagon
│   │   │   └── health/    # Health hexagon
│   │   ├── configurator/
│   │   ├── shared/
│   │   └── main.py
│   ├── tests/             # Unit, integration, feature-component tests
│   ├── Dockerfile
│   ├── Makefile
│   └── pyproject.toml
│
├── ml_player/             # ML Player service
│   ├── src/
│   │   ├── hexagons/      # Hexagonal architecture
│   │   │   ├── mlplayer/  # ML Player hexagon
│   │   │   └── health/    # Health hexagon
│   │   ├── configurator/
│   │   ├── shared/
│   │   └── main.py
│   ├── tests/             # Unit tests
│   ├── Dockerfile
│   ├── Makefile
│   └── pyproject.toml
│
├── docs/                  # Comprehensive documentation
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── CI_CD.md          # CI/CD workflow documentation
│   ├── DATA_COLLECTION.md
│   ├── TESTING_GUIDE.md
│   ├── machine_learning/
│   │   ├── ML_GUIDE.md
│   │   └── ML_IMPLEMENTATION.md
│   └── ...
│
├── testing/               # E2E test scripts
│   ├── README.md
│   ├── test_data_collection.py
│   └── test_data_collection.sh
│
└── .github/
    └── workflows/
        ├── ci.yml         # RFP Game CI
        └── ml_player-ci.yml  # ML Player CI
```

---

## 🛠️ Development

### RFP Game

```bash
cd rfp_game

# Install dependencies
make install

# Run tests
make test              # All tests
make test-unit         # Unit tests only
make test-integration  # Integration tests only
make test-feature      # Feature-component tests only

# Check coverage
make coverage
make coverage-combine

# Lint and format
make format
make lint

# Docker
make docker-build
make docker-run

# Start development server
make run
```

### ML Player

```bash
cd ml_player

# Install dependencies
make install

# Run tests
make test              # All tests

# Check coverage
make coverage

# Lint and format
make format
make lint

# Docker
make docker-build
make docker-run

# Start development server
make run
```

---

## 📚 Documentation

Comprehensive documentation is available in the [`docs/`](docs/) directory:

- **[Game Rules](docs/GAME_RULES.md)** - Complete game mechanics, rules, and examples
- **[Architecture](docs/ARCHITECTURE.md)** - System design and hexagonal architecture
- **[API Documentation](docs/API.md)** - RESTful API endpoints
- **[CI/CD Workflow](docs/CI_CD.md)** - GitHub Actions pipeline
- **[Testing Guide](docs/TESTING_GUIDE.md)** - Test organization and strategies
- **[Testing Strategy](docs/TESTING_STRATEGY.md)** - Testing approach and best practices
- **[ML Player Integration](docs/ML_PLAYER_INTEGRATION.md)** - ML Player service details
- **[Coverage](docs/COVERAGE.md)** - Test coverage analysis
- **[Deployment](docs/DEPLOYMENT.md)** - Deployment instructions

---

## 🧪 Testing

Both services follow the **test pyramid** approach:

### RFP Game
- **Unit Tests** (146): Fast, isolated domain logic tests
- **Integration Tests** (6): API endpoint and layer interaction tests
- **Feature-Component Tests** (13): End-to-end workflow tests
- **Total**: 165 tests with ~90% coverage

### ML Player
- **Unit Tests** (21): Core AI logic and HTTP client tests
- **Total**: 21 tests with 80%+ coverage

**Coverage Threshold**: 80% (enforced in CI)

---

## 🐳 Docker

Both services are containerized and can be run independently:

### RFP Game
```bash
docker build -t rfp-game:latest rfp_game/
docker run -p 8000:8000 rfp-game:latest
```

### ML Player
```bash
docker build -t ml-player:latest ml_player/
docker run -p 8001:8001 ml-player:latest
```

### Docker Compose
```bash
# Start both services
docker-compose up

# RFP Game: http://localhost:8000
# ML Player: http://localhost:8001
```

---

## 🎯 Key Features

- ✅ **Hexagonal Architecture**: Clean separation of concerns
- ✅ **Independent Services**: Each service runs independently
- ✅ **Comprehensive Testing**: High test coverage with test pyramid
- ✅ **Separate CI Pipelines**: Efficient path-based triggering
- ✅ **Type Safety**: Python type hints throughout
- ✅ **Code Quality**: Automated linting and formatting
- ✅ **Docker Ready**: Both services containerized
- ✅ **API First**: RESTful APIs with FastAPI
- ✅ **Well Documented**: Extensive documentation

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`make test`, `make lint`)
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

**Note**: CI will automatically run tests only for the changed service(s).

---

## 📝 License

This project is licensed under the MIT License.

---

## 📬 Contact

For questions or support, please open an issue in the repository.
