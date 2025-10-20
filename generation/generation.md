# 🤖🌸👑 Robot-Flower-Princess-Back - Complete Generator Guide

A comprehensive guide to generate a production-ready FastAPI game backend following Hexagonal Architecture principles.

## 📋 Table of Contents

- [Overview](#overview)
- [Project Features](#project-features)
- [Architecture](#architecture)
- [Generator Usage](#generator-usage)
- [Manual Assembly Guide](#manual-assembly-guide)
- [Quick Start After Generation](#quick-start-after-generation)
- [API Documentation](#api-documentation)
- [Development Workflow](#development-workflow)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This generator creates a complete FastAPI backend for a strategic puzzle game where a robot must collect flowers and deliver them to a princess. The project follows best practices and modern Python development standards.

### What Gets Generated

- **70+ files** organized in clean hexagonal architecture
- **~3000+ lines** of production-ready Python code
- **Complete test suite** with unit and integration tests
- **Docker support** with docker-compose
- **CI/CD pipeline** with GitHub Actions
- **API documentation** automatically generated with OpenAPI/Swagger
- **AI solver** that can automatically complete games

---

## 🎮 Project Features

### Game Mechanics

#### Board Elements
- 🤖 **Robot**: Starts at position (0,0), controlled by player
- 👑 **Princess**: Located at bottom-right corner, receives flowers
- 🌸 **Flowers**: Randomly placed (max 10% of board), collectible
- 🗑️ **Obstacles**: Block movement (~30% of board), cleanable
- ⬜ **Empty cells**: Walkable spaces

#### Actions (6 types)
1. **↩️ Rotate**: Turn to face a direction (north, south, east, west)
2. **🚶‍♂️ Move**: Advance one cell in the direction faced
3. **⛏️🌸 Pick**: Collect a flower from adjacent cell (max 12 at once)
4. **🫳🌸 Drop**: Place a flower on adjacent empty cell
5. **🫴🏼🌸 Give**: Deliver flowers to princess (bouquet of 1-12 flowers)
6. **🗑️ Clean**: Remove an obstacle (only without flowers)

#### Victory & Game Over
- ✅ **Victory**: All flowers delivered to princess
- ❌ **Game Over**: Any invalid action attempted

### API Features

- **11 RESTful endpoints** for complete game control
- **Game history tracking** with step-by-step board states
- **AI autoplay** feature using BFS pathfinding algorithm
- **Error handling** with detailed error messages
- **CORS support** for frontend integration

---

## 🏗️ Architecture

### Hexagonal Architecture (Ports & Adapters)

```
┌─────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                    │
│              (Adapters - External World)                 │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  FastAPI     │  │  Repository  │  │  AI Solver   │  │
│  │  (HTTP API)  │  │  (In-Memory) │  │  (BFS)       │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                   Application Layer                      │
│               (Use Cases - Business Rules)               │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Use Cases (Orchestration)                       │  │
│  │  • CreateGame  • RotateRobot  • MoveRobot       │  │
│  │  • PickFlower  • DropFlower   • GiveFlowers     │  │
│  │  • CleanObstacle  • GetGameState  • Autoplay    │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Ports (Interfaces)                              │  │
│  │  • GameRepository                                │  │
│  └──────────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                      Domain Layer                        │
│            (Core Business Logic - Pure Python)           │
│                                                          │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │Entities  │  │Value Objects │  │   Services       │  │
│  │• Board   │  │• Direction   │  │ • GameService    │  │
│  │• Robot   │  │• GameStatus  │  │                  │  │
│  │• Position│  │• ActionType  │  │                  │  │
│  └──────────┘  └──────────────┘  └──────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │          Domain Exceptions                       │  │
│  │  • InvalidMoveException  • InvalidPickException │  │
│  │  • GameOverException     • InvalidGiveException │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Benefits of This Architecture

1. **Testability**: Domain logic is pure and easily testable
2. **Maintainability**: Clear separation of concerns
3. **Flexibility**: Easy to swap implementations (e.g., in-memory → database)
4. **Independence**: Core business logic doesn't depend on frameworks
5. **Scalability**: Clean boundaries make it easy to extend

---

## 🛠️ Generator Usage

### Prerequisites

- Python 3.13+
- Terminal/Command Line access

### Available Artifacts

You have **4 artifacts** to assemble:

1. **`complete_robot_generator`** - Header, config files, and main function
2. **`robot_princess_part1`** - Domain layer (entities, value objects, services)
3. **`robot_princess_part2`** - Application layer (use cases, ports)
4. **`robot_princess_part3`** - Infrastructure layer (API, AI, tests)

---

## 📝 Manual Assembly Guide

### Method 1: Copy-Paste Assembly (Recommended)

#### Step 1: Create the Generator Script

```bash
touch generate_robot_flower_princess.py
```

#### Step 2: Add the Header

Open `generate_robot_flower_princess.py` and copy from **`complete_robot_generator`** artifact:

- Copy from the beginning (shebang `#!/usr/bin/env python3`)
- Copy until you see the line with root config files
- **Stop before** the comment `# Domain Layer files will be added next...`

Your file should start like this:

```python
#!/usr/bin/env python3
"""
Robot-Flower-Princess-Back Complete Project Generator
...
"""

import os
import zipfile
from pathlib import Path
from datetime import datetime

PROJECT_NAME = "Robot-Flower-Princess-Back"

print(f"""
╔══════════════════════════════════════════════════════════╗
║  🤖🌸👑 Robot-Flower-Princess-Back Generator         ║
...
╚══════════════════════════════════════════════════════════╝
""")

FILES = {
    # Configuration Files
    ".python-version": "3.13.0\n",
    ".gitignore": """# Python...""",
    ".env.example": """ENVIRONMENT=development...""",
    "pyproject.toml": """[tool.poetry]...""",
    "Dockerfile": """FROM python:3.13-slim...""",
    "docker-compose.yml": """version: '3.8'...""",
    "Makefile": """.PHONY: help...""",
    ".github/workflows/ci.yml": """name: CI...""",
    "README.md": """# 🤖🌸👑 Robot-Flower-Princess-Back...""",
```

#### Step 3: Add Domain Layer

From **`robot_princess_part1`** artifact, copy ALL content starting from:

```python
    # Domain Layer - Value Objects
    "src/robot_flower_princess/domain/value_objects/direction.py": """from enum import Enum
```

Paste it directly after the root config files in the FILES dictionary.

#### Step 4: Add Application Layer

From **`robot_princess_part2`** artifact, copy ALL content starting from:

```python
    # Application Layer - Ports
    "src/robot_flower_princess/application/ports/game_repository.py": """from abc import ABC
```

Paste it directly after Part 1 content.

#### Step 5: Add Infrastructure Layer & Tests

From **`robot_princess_part3`** artifact, copy ALL content starting from:

```python
    # Infrastructure Layer - Persistence
    "src/robot_flower_princess/infrastructure/persistence/in_memory_game_repository.py":
```

Paste it directly after Part 2 content.

#### Step 6: Close the FILES Dictionary

After all Part 3 content, add the closing brace:

```python
}
```

#### Step 7: Add the Main Function

Go back to **`complete_robot_generator`** artifact and copy the `def create_project():` function and everything after it:

```python
def create_project():
    """Create the complete project structure."""

    print(f"🤖 Creating {PROJECT_NAME}...")
    # ... rest of the function ...

if __name__ == "__main__":
    try:
        create_project()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
```

### Method 2: Script Verification

After assembly, verify your script:

```bash
# Check syntax
python3 -m py_compile generate_robot_flower_princess.py

# Count lines (should be ~2000+)
wc -l generate_robot_flower_princess.py

# Check structure
grep -c '"src/robot_flower_princess' generate_robot_flower_princess.py
# Should return ~40 (number of source files)
```

### Method 3: Quick Validation Checklist

```bash
# Run these checks on your assembled script:

# 1. Has shebang
head -1 generate_robot_flower_princess.py | grep "#!/usr/bin/env python3"

# 2. Has FILES dictionary
grep "FILES = {" generate_robot_flower_princess.py

# 3. Has all three layers
grep -c "# Domain Layer" generate_robot_flower_princess.py  # Should be 1+
grep -c "# Application Layer" generate_robot_flower_princess.py  # Should be 1+
grep -c "# Infrastructure Layer" generate_robot_flower_princess.py  # Should be 1+

# 4. Has create_project function
grep "def create_project():" generate_robot_flower_princess.py

# 5. Has main block
grep 'if __name__ == "__main__":' generate_robot_flower_princess.py
```

---

## 🚀 Quick Start After Generation

### Step 1: Run the Generator

```bash
# Make executable (Unix/Linux/macOS)
chmod +x generate_robot_flower_princess.py

# Run the generator
python3 generate_robot_flower_princess.py
```

**Expected Output:**

```
╔══════════════════════════════════════════════════════════╗
║  🤖🌸👑 Robot-Flower-Princess-Back Generator         ║
║                                                          ║
║  Creating a complete FastAPI project with:              ║
║  ✓ Hexagonal Architecture                               ║
║  ✓ Complete Test Suite                                  ║
║  ✓ Docker Support                                        ║
║  ✓ CI/CD with GitHub Actions                            ║
║  ✓ AI Solver                                             ║
║  ✓ Full Game History                                     ║
╚══════════════════════════════════════════════════════════╝

🤖 Creating Robot-Flower-Princess-Back...
============================================================
✅ Created 15 directories
✅ Created: .python-version
✅ Created: .gitignore
✅ Created: .env.example
...
✅ Created 70+ files

📦 Creating ZIP archive: Robot-Flower-Princess-Back-20250119_143022.zip
✅ ZIP archive created: Robot-Flower-Princess-Back-20250119_143022.zip (0.25 MB)

============================================================
✨ Project created successfully!

📦 Download: /path/to/Robot-Flower-Princess-Back-20250119_143022.zip

📋 Next steps:
  1. unzip Robot-Flower-Princess-Back-20250119_143022.zip
  2. cd Robot-Flower-Princess-Back
  3. pyenv install 3.13.0 && pyenv local 3.13.0
  4. poetry install
  5. make run

🐳 Or use Docker:
  docker-compose up --build

📚 API docs: http://localhost:8000/docs

✅ Total files created: 70
✅ Total directories created: 15

🎉 Happy coding!
```

### Step 2: Extract and Setup

```bash
# Extract the ZIP
unzip Robot-Flower-Princess-Back-*.zip
cd Robot-Flower-Princess-Back

# Setup Python environment
pyenv install 3.13.0
pyenv local 3.13.0

# Install dependencies
poetry install
```

### Step 3: Run the Application

#### Option A: Using Make (Recommended)

```bash
make run
# Starts the server at http://localhost:8000
```

#### Option B: Using Poetry Directly

```bash
poetry shell
uvicorn robot_flower_princess..main:app --reload --host 0.0.0.0 --port 8000
```

#### Option C: Using Docker

```bash
docker-compose up --build
```

### Step 4: Access the API

Open your browser to:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 📚 API Documentation

### Endpoints Overview

#### Game Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/games/` | Create a new game |
| `GET` | `/api/v1/games/{game_id}` | Get current game state |
| `GET` | `/api/v1/games/{game_id}/history` | Get complete move history |

#### Robot Actions

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/games/{game_id}/action/rotate` | Rotate robot to face direction |
| `POST` | `/api/v1/games/{game_id}/action/move` | Move robot forward |
| `POST` | `/api/v1/games/{game_id}/action/pick` | Pick up a flower |
| `POST` | `/api/v1/games/{game_id}/action/drop` | Drop a flower |
| `POST` | `/api/v1/games/{game_id}/action/give` | Give flowers to princess |
| `POST` | `/api/v1/games/{game_id}/action/clean` | Clean an obstacle |

#### AI Features

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/games/{game_id}/autoplay` | Let AI solve the game |

### Example Usage

#### Create a Game

```bash
curl -X POST "http://localhost:8000/api/v1/games/" \
  -H "Content-Type: application/json" \
  -d '{
    "rows": 10,
    "cols": 10
  }'
```

**Response:**
```json
{
  "game_id": "550e8400-e29b-41d4-a716-446655440000",
  "board": {
    "rows": 10,
    "cols": 10,
    "grid": [["🤖", "⬜", ...], ...],
    "robot": {
      "position": {"row": 0, "col": 0},
      "orientation": "east",
      "flowers_held": 0,
      "max_flowers": 12
    },
    "princess_position": {"row": 9, "col": 9},
    "flowers_remaining": 5,
    "flowers_delivered": 0,
    "total_flowers": 5,
    "status": "in_progress"
  },
  "message": "Game created successfully"
}
```

#### Rotate Robot

```bash
curl -X POST "http://localhost:8000/api/v1/games/{game_id}/action/rotate" \
  -H "Content-Type: application/json" \
  -d '{"direction": "south"}'
```

#### Move Robot

```bash
curl -X POST "http://localhost:8000/api/v1/games/{game_id}/action/move"
```

#### Pick Flower

```bash
curl -X POST "http://localhost:8000/api/v1/games/{game_id}/action/pick"
```

#### Give Flowers to Princess

```bash
curl -X POST "http://localhost:8000/api/v1/games/{game_id}/action/give"
```

#### AI Autoplay

```bash
curl -X POST "http://localhost:8000/api/v1/games/{game_id}/autoplay"
```

#### Get Game History

```bash
curl -X GET "http://localhost:8000/api/v1/games/{game_id}/history"
```

**Response:**
```json
{
  "game_id": "550e8400-e29b-41d4-a716-446655440000",
  "history": {
    "total_actions": 15,
    "actions": [
      {
        "action_type": "rotate",
        "direction": "south",
        "success": true,
        "message": "Rotated to face south"
      },
      {
        "action_type": "move",
        "direction": "south",
        "success": true,
        "message": "Move successful"
      }
    ],
    "board_states": [...]
  }
}
```

---

## 💻 Development Workflow

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
poetry run pytest tests/unit/domain/test_board.py -v

# Run integration tests only
poetry run pytest tests/integration/ -v
```

### Code Quality

```bash
# Format code
make format

# Run linters
make lint

# Type checking
poetry run mypy src/
```

### Docker Development

```bash
# Start services
make docker-up

# Stop services
make docker-down

# View logs
docker-compose logs -f api

# Rebuild after changes
docker-compose up --build
```

### Available Make Commands

```bash
make help          # Show all available commands
make install       # Install dependencies
make test          # Run tests
make test-cov      # Run tests with coverage
make lint          # Run linters (ruff, mypy)
make format        # Format code (black, ruff)
make run           # Run the application
make docker-up     # Start with Docker
make docker-down   # Stop Docker containers
make clean         # Clean cache files
```

---

## 🔧 Troubleshooting

### Common Issues

#### Issue 1: Generator Script Syntax Error

**Symptom:**
```
SyntaxError: unexpected EOF while parsing
```

**Solution:**
- Check that the FILES dictionary has a closing brace `}`
- Verify all string quotes are properly closed
- Run: `python3 -m py_compile generate_robot_flower_princess.py`

#### Issue 2: Missing Files in Generated Project

**Symptom:**
- Some source files are missing
- Directory structure incomplete

**Solution:**
- Verify all 3 parts are copied into FILES dictionary
- Check file count: `grep -c '"src/robot_flower_princess' generate_robot_flower_princess.py` should return ~40
- Re-run the generator

#### Issue 3: Poetry Installation Fails

**Symptom:**
```
Poetry could not find a pyproject.toml file
```

**Solution:**
```bash
# Ensure you're in the project directory
cd Robot-Flower-Princess-Back

# Verify pyproject.toml exists
ls -la pyproject.toml

# Try installing again
poetry install --no-cache
```

#### Issue 4: Python Version Mismatch

**Symptom:**
```
This project requires Python ^3.13
```

**Solution:**
```bash
# Install Python 3.13
pyenv install 3.13.0

# Set local version
pyenv local 3.13.0

# Verify
python --version  # Should show 3.13.x
```

#### Issue 5: Port 8000 Already in Use

**Symptom:**
```
Error: Address already in use
```

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn robot_flower_princess..main:app --port 8080
```

#### Issue 6: Docker Build Fails

**Symptom:**
```
ERROR: failed to solve
```

**Solution:**
```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache

# Check Docker disk space
docker system df
```

#### Issue 7: Tests Failing

**Symptom:**
```
ImportError: No module named 'robot_flower_princess'
```

**Solution:**
```bash
# Ensure you're in poetry shell
poetry shell

# Install in development mode
poetry install

# Run tests again
pytest
```

### Debug Mode

Enable debug logging:

```bash
# Edit .env file
echo "LOG_LEVEL=debug" >> .env

# Run with debug output
poetry run uvicorn robot_flower_princess..main:app --reload --log-level debug
```

### Getting Help

If you encounter issues not listed here:

1. Check the generated README.md in the project
2. Review the API documentation at `/docs`
3. Check test files for usage examples
4. Enable debug logging for more details

---

## 📦 Project Structure

```
Robot-Flower-Princess-Back/
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions CI/CD
├── src/
│   └── robot_flower_princess/
│       ├── domain/                # 🎯 Core business logic
│       │   ├── entities/          # Board, Robot, Position, GameHistory
│       │   ├── value_objects/     # Direction, GameStatus, ActionType
│       │   ├── exceptions/        # Game-specific exceptions
│       │   └── services/          # GameService
│       ├── application/           # 🎮 Use cases
│       │   ├── ports/             # GameRepository interface
│       │   └── use_cases/         # All game actions + autoplay
│       ├── infrastructure/        # 🔌 External adapters
│       │   ├── api/               # FastAPI routes, schemas
│       │   ├── persistence/       # In-memory repository
│       │   └── ai/                # BFS solver
│       └── config/                # Settings
├── tests/
│   ├── unit/                      # Unit tests
│   │   ├── domain/                # Domain logic tests
│   │   └── application/           # Use case tests
│   ├── integration/               # API integration tests
│   └── conftest.py                # Pytest fixtures
├── .python-version                # Python version (3.13.0)
├── .gitignore                     # Git ignore rules
├── .env.example                   # Environment variables template
├── pyproject.toml                 # Poetry dependencies
├── Dockerfile                     # Docker image definition
├── docker-compose.yml             # Docker compose configuration
├── Makefile                       # Development commands
└── README.md                      # Project documentation
```

---

## 🎓 Learning Resources

### Understanding Hexagonal Architecture

- **Domain Layer**: Pure business logic, no dependencies
- **Application Layer**: Orchestrates domain, defines ports (interfaces)
- **Infrastructure Layer**: Implements ports, connects to external world

### Key Concepts

1. **Dependency Inversion**: High-level modules don't depend on low-level modules
2. **Ports**: Interfaces that define contracts
3. **Adapters**: Implementations of ports
4. **Use Cases**: Application-specific business rules
5. **Domain Services**: Business logic that doesn't belong to entities

### Testing Strategy

- **Unit Tests**: Test domain logic in isolation
- **Integration Tests**: Test API endpoints end-to-end
- **Fixtures**: Reusable test data (conftest.py)

---

## 📈 Next Steps

### Extend the Project

1. **Add Persistence**: Replace in-memory repository with PostgreSQL
2. **Add Authentication**: Implement JWT-based auth
3. **Add WebSockets**: Real-time game updates
4. **Create Frontend**: Build a web UI with React/Vue
5. **Add Multiplayer**: Multiple robots on same board
6. **Improve AI**: Implement A* pathfinding
7. **Add Metrics**: Prometheus/Grafana monitoring

### Production Deployment

1. **Environment Variables**: Configure for production
2. **Database**: Set up PostgreSQL/Redis
3. **HTTPS**: Configure SSL certificates
4. **Docker Registry**: Push images to Docker Hub
5. **Kubernetes**: Deploy with K8s
6. **Monitoring**: Set up logging and metrics
7. **CI/CD**: Configure automated deployments

---

## 📄 License

This generated project template is provided under the MIT License.

---

## 🙏 Acknowledgments

Generated project uses:

- **FastAPI** - Modern Python web framework
- **Poetry** - Dependency management
- **Pydantic** - Data validation
- **Pytest** - Testing framework
- **Docker** - Containerization
- **GitHub Actions** - CI/CD

---

## ✨ Summary

You now have a complete guide to:

1. ✅ Assemble the generator script from 4 artifacts
2. ✅ Run the generator to create the project
3. ✅ Set up and run the application
4. ✅ Use the API to play the game
5. ✅ Develop and extend the project
6. ✅ Troubleshoot common issues

**Total Generation Time**: ~5 minutes
**Total Setup Time**: ~10 minutes
**Ready to Code**: Immediately after generation! 🚀

Happy coding! 🎉