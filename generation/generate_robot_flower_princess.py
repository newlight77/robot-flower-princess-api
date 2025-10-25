#!/usr/bin/env python3
"""
Robot-Flower-Princess-Back Complete Project Generator
Generates the entire project structure with all files and creates a downloadable ZIP.

Usage:
    python3 generate_robot_flower_princess.py

This will create:
- Robot-Flower-Princess-Back/ directory with full project
- Robot-Flower-Princess-Back-YYYYMMDD_HHMMSS.zip file for download
"""

import os
import zipfile
from pathlib import Path
from datetime import datetime

PROJECT_NAME = "Robot-Flower-Princess-Back"

print(f"""
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
""")

# Define all file contents
FILES = {
    # Root Configuration Files
    ".python-version": "3.13.0\n",

    ".gitignore": """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment
.env
.env.local

# Poetry
poetry.lock

# Docker
docker-compose.override.yml

# macOS
.DS_Store
""",

    ".env.example": """ENVIRONMENT=development
LOG_LEVEL=info
API_PREFIX=/api/v1
HOST=0.0.0.0
PORT=8000
""",

    "pyproject.toml": """[tool.poetry]
name = "robot-flower-princess-back"
version = "1.0.0"
description = "A strategic puzzle game where a robot delivers flowers to a princess"
authors = ["Your Name <your.email@example.com>"]
readme = "README.md"
packages = [
    {include = "hexagons", from = "src"},
    {include = "configurator", from = "src"},
    {include = "shared", from = "src"}
]

[tool.poetry.dependencies]
python = "^3.13"
fastapi = "^0.115.0"
uvicorn = {extras = ["standard"], version = "^0.32.0"}
pydantic = "^2.9.2"
pydantic-settings = "^2.6.0"
python-dotenv = "^1.0.1"

[tool.poetry.group.dev.dependencies]
pytest = "^8.3.3"
pytest-asyncio = "^0.24.0"
pytest-cov = "^6.0.0"
httpx = "^0.27.2"
black = "^24.10.0"
ruff = "^0.7.3"
mypy = "^1.13.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
pythonpath = ["src"]

[tool.black]
line-length = 100
target-version = ['py313']

[tool.ruff]
line-length = 100
target-version = "py313"

[tool.mypy]
python_version = "3.13"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
""",

    "Dockerfile": """FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN poetry config virtualenvs.create false \\
    && poetry install --no-interaction --no-ansi --no-root --only main

# Copy application code
COPY src/ ./src/

# Install the application
RUN poetry install --no-interaction --no-ansi --only main

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:8000/health || exit 1

# Run with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
""",

    "docker-compose.yml": """version: '3.8'

services:
  api:
    build: .
    container_name: robot-flower-princess-api
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - LOG_LEVEL=info
    volumes:
      - ./src:/app/src
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
""",

    "Makefile": """.PHONY: help install test test-cov lint format run docker-up docker-down clean

help:
\t@echo "Robot-Flower-Princess-Back - Available commands:"
\t@echo "  make install      - Install dependencies"
\t@echo "  make test        - Run tests"
\t@echo "  make test-cov    - Run tests with coverage"
\t@echo "  make lint        - Run linters"
\t@echo "  make format      - Format code"
\t@echo "  make run         - Run the application"
\t@echo "  make docker-up   - Start with Docker"
\t@echo "  make docker-down - Stop Docker containers"
\t@echo "  make clean       - Clean cache files"

install:
\tpoetry install

test:
\tpoetry run pytest -v

test-cov:
\tpoetry run pytest --cov=src/hexagons --cov=src/configurator --cov=src/shared --cov-report=html --cov-report=term

lint:
\tpoetry run ruff check src/ tests/
\tpoetry run mypy src/

format:
\tpoetry run black src/ tests/
\tpoetry run ruff check --fix src/ tests/

run:
\tpoetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000

docker-up:
\tdocker-compose up --build

docker-down:
\tdocker-compose down

clean:
\tfind . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
\tfind . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
\tfind . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
\tfind . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
\tfind . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
\tfind . -type f -name ".coverage" -delete 2>/dev/null || true
""",

    ".github/workflows/ci.yml": """name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.13'

    - name: Install Poetry
      run: |
        curl -sSL https://install.python-poetry.org | python3 -
        echo "$HOME/.local/bin" >> $GITHUB_PATH

    - name: Install dependencies
      run: poetry install

    - name: Run linters
      run: |
        poetry run black --check src/ tests/
        poetry run ruff check src/ tests/
        poetry run mypy src/

    - name: Run tests with coverage
      run: poetry run pytest --cov=src/hexagons --cov=src/configurator --cov=src/shared --cov-report=xml --cov-report=term

    - name: Upload coverage reports
      uses: codecov/codecov-action@v4
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: false

  docker:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Build Docker image
      run: docker build -t robot-flower-princess:test .

    - name: Test Docker image
      run: |
        docker run -d -p 8000:8000 --name test-api robot-flower-princess:test
        sleep 10
        curl -f http://localhost:8000/health || exit 1
        docker stop test-api
""",

    "README.md": """# 🤖🌸👑 Robot-Flower-Princess-Back

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

### Using Docker (Recommended)
```bash
docker-compose up --build
# API available at http://localhost:8000
```

### Using Poetry
```bash
# Setup
pyenv install 3.13.0
pyenv local 3.13.0
poetry install

# Run
make run
# or
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Endpoints

#### Game Management
- `POST /api/v1/games` - Create a new game
- `GET /api/v1/games/{game_id}` - Get game state
- `GET /api/v1/games/{game_id}/history` - Get move history

#### Actions
- `POST /api/v1/games/{game_id}/action/rotate` - Rotate robot
- `POST /api/v1/games/{game_id}/action/move` - Move robot
- `POST /api/v1/games/{game_id}/action/pick` - Pick flower
- `POST /api/v1/games/{game_id}/action/drop` - Drop flower
- `POST /api/v1/games/{game_id}/action/give` - Give flowers to princess
- `POST /api/v1/games/{game_id}/action/clean` - Clean obstacle

#### AI Player
- `POST /api/v1/games/{game_id}/autoplay` - Let AI solve the game

## 🧪 Testing

```bash
make test          # Run all tests
make test-cov      # Run with coverage
make lint          # Run linters
make format        # Format code
```

## 🏗️ Architecture

This project follows **Hexagonal Architecture** (Ports and Adapters):

```
src/hexagons/game/
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
curl -X POST "http://localhost:8000/api/v1/games" \\
  -H "Content-Type: application/json" \\
  -d '{"rows": 10, "cols": 10}'
```

### Rotate Robot
```bash
curl -X POST "http://localhost:8000/api/v1/games/{game_id}/action/rotate" \\
  -H "Content-Type: application/json" \\
  -d '{"direction": "south"}'
```

### Move Robot
```bash
curl -X POST "http://localhost:8000/api/v1/games/{game_id}/action/move"
```

### Auto-Play
```bash
curl -X POST "http://localhost:8000/api/v1/games/{game_id}/autoplay"
```

### Get History
```bash
curl -X GET "http://localhost:8000/api/v1/games/{game_id}/history"
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
""",
    # ⬇️ PART 1: Domain Layer (from robot_princess_part1)
    # Domain Layer - Value Objects
    "src/hexagons/game/domain/value_objects/direction.py": """from enum import Enum

class Direction(str, Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"

    def get_delta(self) -> tuple[int, int]:
        \"\"\"Returns (row_delta, col_delta) for this direction.\"\"\"
        deltas = {
            Direction.NORTH: (-1, 0),
            Direction.SOUTH: (1, 0),
            Direction.EAST: (0, 1),
            Direction.WEST: (0, -1),
        }
        return deltas[self]

    def opposite(self) -> "Direction":
        \"\"\"Returns the opposite direction.\"\"\"
        opposites = {
            Direction.NORTH: Direction.SOUTH,
            Direction.SOUTH: Direction.NORTH,
            Direction.EAST: Direction.WEST,
            Direction.WEST: Direction.EAST,
        }
        return opposites[self]
""",

    "src/hexagons/game/domain/value_objects/game_status.py": """from enum import Enum

class GameStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    VICTORY = "victory"
    GAME_OVER = "game_over"
""",

    "src/hexagons/game/domain/value_objects/action_type.py": """from enum import Enum

class ActionType(str, Enum):
    ROTATE = "rotate"
    MOVE = "move"
    PICK = "pick"
    DROP = "drop"
    GIVE = "give"
    CLEAN = "clean"
""",

    # Domain Layer - Entities
    "src/hexagons/game/domain/entities/cell.py": """from enum import Enum

class CellType(str, Enum):
    EMPTY = "empty"
    ROBOT = "robot"
    PRINCESS = "princess"
    FLOWER = "flower"
    OBSTACLE = "obstacle"
""",

    "src/hexagons/game/domain/entities/position.py": """from dataclasses import dataclass

@dataclass(frozen=True)
class Position:
    row: int
    col: int

    def move(self, row_delta: int, col_delta: int) -> "Position":
        return Position(self.row + row_delta, self.col + col_delta)

    def __hash__(self) -> int:
        return hash((self.row, self.col))

    def manhattan_distance(self, other: "Position") -> int:
        \"\"\"Calculate Manhattan distance to another position.\"\"\"
        return abs(self.row - other.row) + abs(self.col - other.col)
""",

    "src/hexagons/game/domain/entities/robot.py": """from dataclasses import dataclass
from .position import Position
from ..value_objects.direction import Direction

@dataclass
class Robot:
    position: Position
    orientation: Direction = Direction.EAST
    flowers_held: int = 0
    max_flowers: int = 12

    def move_to(self, new_position: Position) -> None:
        self.position = new_position

    def rotate(self, direction: Direction) -> None:
        self.orientation = direction

    def pick_flower(self) -> None:
        if self.flowers_held >= self.max_flowers:
            raise ValueError(f"Cannot hold more than {self.max_flowers} flowers")
        self.flowers_held += 1

    def drop_flower(self) -> None:
        if self.flowers_held == 0:
            raise ValueError("No flowers to drop")
        self.flowers_held -= 1

    def give_flowers(self) -> int:
        count = self.flowers_held
        self.flowers_held = 0
        return count

    def can_clean(self) -> bool:
        return self.flowers_held == 0

    def can_pick(self) -> bool:
        return self.flowers_held < self.max_flowers
""",

    "src/hexagons/game/domain/entities/board.py": """from dataclasses import dataclass, field
import random
from typing import Optional
from .position import Position
from .robot import Robot
from .cell import CellType
from ..value_objects.direction import Direction
from ..value_objects.game_status import GameStatus

@dataclass
class Game:
    rows: int
    cols: int
    robot: Robot
    princess_position: Position
    flowers: set[Position] = field(default_factory=set)
    obstacles: set[Position] = field(default_factory=set)
    initial_flower_count: int = 0
    flowers_delivered: int = 0

    def __post_init__(self) -> None:
        self.initial_flower_count = len(self.flowers)

    @classmethod
    def create(cls, rows: int, cols: int) -> "Game":
        \"\"\"Factory method to create a new game with fixed positions.\"\"\"
        if rows < 3 or rows > 50 or cols < 3 or cols > 50:
            raise ValueError("Game size must be between 3x3 and 50x50")

        # Robot always at top-left
        robot_pos = Position(0, 0)

        # Princess always at bottom-right
        princess_pos = Position(rows - 1, cols - 1)

        total_cells = rows * cols
        max_flowers = max(1, int(total_cells * 0.1))
        num_obstacles = int(total_cells * 0.3)

        # Generate all positions except robot and princess
        all_positions = [Position(r, c) for r in range(rows) for c in range(cols)]
        all_positions = [p for p in all_positions if p != robot_pos and p != princess_pos]
        random.shuffle(all_positions)

        # Place flowers (up to 10% of board)
        num_flowers = random.randint(1, min(max_flowers, len(all_positions)))
        flowers = {all_positions.pop() for _ in range(num_flowers)}

        # Place obstacles (around 30% of board)
        obstacles = {all_positions.pop() for _ in range(min(num_obstacles, len(all_positions)))}

        robot = Robot(position=robot_pos, orientation=Direction.EAST)

        return cls(
            rows=rows,
            cols=cols,
            robot=robot,
            princess_position=princess_pos,
            flowers=flowers,
            obstacles=obstacles,
        )

    def get_cell_type(self, position: Position) -> CellType:
        \"\"\"Get the type of cell at the given position.\"\"\"
        if position == self.robot.position:
            return CellType.ROBOT
        if position == self.princess_position:
            return CellType.PRINCESS
        if position in self.flowers:
            return CellType.FLOWER
        if position in self.obstacles:
            return CellType.OBSTACLE
        return CellType.EMPTY

    def is_valid_position(self, position: Position) -> bool:
        \"\"\"Check if a position is within board boundaries.\"\"\"
        return 0 <= position.row < self.rows and 0 <= position.col < self.cols

    def is_empty(self, position: Position) -> bool:
        \"\"\"Check if a position is empty.\"\"\"
        return self.get_cell_type(position) == CellType.EMPTY

    def get_status(self) -> GameStatus:
        \"\"\"Determine the current game status.\"\"\"
        if self.flowers_delivered == self.initial_flower_count and self.initial_flower_count > 0:
            return GameStatus.VICTORY
        return GameStatus.IN_PROGRESS

    def to_dict(self) -> dict:
        \"\"\"Convert board to dictionary representation.\"\"\"
        grid = []
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                pos = Position(r, c)
                cell = self.get_cell_type(pos)

                emoji_map = {
                    CellType.ROBOT: "🤖",
                    CellType.PRINCESS: "👑",
                    CellType.FLOWER: "🌸",
                    CellType.OBSTACLE: "🗑️",
                    CellType.EMPTY: "⬜",
                }
                row.append(emoji_map[cell])
            grid.append(row)

        return {
            "rows": self.rows,
            "cols": self.cols,
            "grid": grid,
            "robot": {
                "position": {"row": self.robot.position.row, "col": self.robot.position.col},
                "orientation": self.robot.orientation.value,
                "flowers_held": self.robot.flowers_held,
                "max_flowers": self.robot.max_flowers,
            },
            "princess_position": {"row": self.princess_position.row, "col": self.princess_position.col},
            "flowers_remaining": len(self.flowers),
            "flowers_delivered": self.flowers_delivered,
            "total_flowers": self.initial_flower_count,
            "status": self.get_status().value,
        }
""",

    "src/hexagons/game/domain/entities/game_history.py": """from dataclasses import dataclass, field
from typing import List
from ..value_objects.action_type import ActionType
from ..value_objects.direction import Direction

@dataclass
class Action:
    action_type: ActionType
    direction: Direction | None = None
    success: bool = True
    message: str = ""

@dataclass
class GameHistory:
    actions: List[Action] = field(default_factory=list)
    board_states: List[dict] = field(default_factory=list)

    def add_action(self, action: Action | None, board_state: dict) -> None:
        \"\"\"Record an action and the resulting board state.\"\"\"
        if action:
            self.actions.append(action)
        self.board_states.append(board_state)

    def to_dict(self) -> dict:
        \"\"\"Convert history to dictionary.\"\"\"
        return {
            "total_actions": len(self.actions),
            "actions": [
                {
                    "action_type": action.action_type.value,
                    "direction": action.direction.value if action.direction else None,
                    "success": action.success,
                    "message": action.message,
                }
                for action in self.actions
            ],
            "board_states": self.board_states,
        }
""",

    # Domain Layer - Exceptions
    "src/hexagons/game/domain/exceptions/game_exceptions.py": """class GameException(Exception):
    \"\"\"Base exception for game-related errors.\"\"\"
    pass

class InvalidMoveException(GameException):
    \"\"\"Raised when an invalid move is attempted.\"\"\"
    pass

class InvalidActionException(GameException):
    \"\"\"Raised when an invalid action is attempted.\"\"\"
    pass

class GameOverException(GameException):
    \"\"\"Raised when the game is over.\"\"\"
    pass

class InvalidRotationException(GameException):
    \"\"\"Raised when an invalid rotation is attempted.\"\"\"
    pass

class InvalidPickException(GameException):
    \"\"\"Raised when an invalid pick is attempted.\"\"\"
    pass

class InvalidDropException(GameException):
    \"\"\"Raised when an invalid drop is attempted.\"\"\"
    pass

class InvalidGiveException(GameException):
    \"\"\"Raised when an invalid give is attempted.\"\"\"
    pass

class InvalidCleanException(GameException):
    \"\"\"Raised when an invalid clean is attempted.\"\"\"
    pass
""",

    # Domain Layer - Services
    "src/hexagons/game/domain/services/game_service.py": """from ..entities.game import Game
from ..entities.position import Position
from ..value_objects.direction import Direction
from ..value_objects.game_status import GameStatus
from ..exceptions.game_exceptions import (
    InvalidMoveException,
    InvalidActionException,
    GameOverException,
    InvalidPickException,
    InvalidDropException,
    InvalidGiveException,
    InvalidCleanException,
)

class GameService:
    \"\"\"Domain service for game logic.\"\"\"

    @staticmethod
    def rotate_robot(board: Game, direction: Direction) -> None:
        \"\"\"Rotate the robot to face a direction.\"\"\"
        if board.get_status() != GameStatus.IN_PROGRESS:
            raise GameOverException("Game is already over")

        board.robot.rotate(direction)

    @staticmethod
    def move_robot(board: Game) -> None:
        \"\"\"Move the robot in the direction it's facing.\"\"\"
        if board.get_status() != GameStatus.IN_PROGRESS:
            raise GameOverException("Game is already over")

        # Calculate new position based on orientation
        row_delta, col_delta = board.robot.orientation.get_delta()
        new_position = board.robot.position.move(row_delta, col_delta)

        # Validate move
        if not board.is_valid_position(new_position):
            raise InvalidMoveException("Move would go outside the board")

        if not board.is_empty(new_position):
            cell_type = board.get_cell_type(new_position)
            raise InvalidMoveException(f"Target cell is blocked by {cell_type.value}")

        # Execute move
        board.robot.move_to(new_position)

    @staticmethod
    def pick_flower(board: Game) -> None:
        \"\"\"Pick a flower from an adjacent cell.\"\"\"
        if board.get_status() != GameStatus.IN_PROGRESS:
            raise GameOverException("Game is already over")

        if not board.robot.can_pick():
            raise InvalidPickException(f"Robot cannot hold more than {board.robot.max_flowers} flowers")

        # Get position in front of robot
        row_delta, col_delta = board.robot.orientation.get_delta()
        target_position = board.robot.position.move(row_delta, col_delta)

        if not board.is_valid_position(target_position):
            raise InvalidPickException("No flower to pick in that direction")

        if target_position not in board.flowers:
            raise InvalidPickException("No flower at target position")

        # Pick the flower
        board.robot.pick_flower()
        board.flowers.remove(target_position)

    @staticmethod
    def drop_flower(board: Game) -> None:
        \"\"\"Drop a flower on an adjacent empty cell.\"\"\"
        if board.get_status() != GameStatus.IN_PROGRESS:
            raise GameOverException("Game is already over")

        if board.robot.flowers_held == 0:
            raise InvalidDropException("Robot has no flowers to drop")

        # Get position in front of robot
        row_delta, col_delta = board.robot.orientation.get_delta()
        target_position = board.robot.position.move(row_delta, col_delta)

        if not board.is_valid_position(target_position):
            raise InvalidDropException("Cannot drop flower outside the board")

        if not board.is_empty(target_position):
            raise InvalidDropException("Target cell is not empty")

        # Drop the flower
        board.robot.drop_flower()
        board.flowers.add(target_position)

    @staticmethod
    def give_flowers(board: Game) -> None:
        \"\"\"Give flowers to the princess.\"\"\"
        if board.get_status() != GameStatus.IN_PROGRESS:
            raise GameOverException("Game is already over")

        if board.robot.flowers_held == 0:
            raise InvalidGiveException("Robot has no flowers to give")

        # Get position in front of robot
        row_delta, col_delta = board.robot.orientation.get_delta()
        target_position = board.robot.position.move(row_delta, col_delta)

        if not board.is_valid_position(target_position):
            raise InvalidGiveException("No princess in that direction")

        if target_position != board.princess_position:
            raise InvalidGiveException("Princess is not at target position")

        # Give flowers
        delivered = board.robot.give_flowers()
        board.flowers_delivered += delivered

    @staticmethod
    def clean_obstacle(board: Game) -> None:
        \"\"\"Clean an obstacle in the direction faced.\"\"\"
        if board.get_status() != GameStatus.IN_PROGRESS:
            raise GameOverException("Game is already over")

        if not board.robot.can_clean():
            raise InvalidCleanException("Cannot clean while holding flowers")

        # Get position in front of robot
        row_delta, col_delta = board.robot.orientation.get_delta()
        target_position = board.robot.position.move(row_delta, col_delta)

        if not board.is_valid_position(target_position):
            raise InvalidCleanException("No obstacle to clean in that direction")

        if target_position not in board.obstacles:
            raise InvalidCleanException("No obstacle at target position")

        # Remove obstacle
        board.obstacles.remove(target_position)
""",
    # ⬇️ PART 2: Application Layer (from robot_princess_part2)
    # Application Layer - Ports
    "src/hexagons/game/application/ports/game_repository.py": """from abc import ABC, abstractmethod
from typing import Optional
from ...domain.entities.game import Game
from ...domain.entities.game_history import GameHistory

class GameRepository(ABC):
    \"\"\"Port for game persistence.\"\"\"

    @abstractmethod
    def save(self, game_id: str, board: Game) -> None:
        \"\"\"Save a game board.\"\"\"
        pass

    @abstractmethod
    def get(self, game_id: str) -> Optional[Game]:
        \"\"\"Retrieve a game board by ID.\"\"\"
        pass

    @abstractmethod
    def delete(self, game_id: str) -> None:
        \"\"\"Delete a game board.\"\"\"
        pass

    @abstractmethod
    def exists(self, game_id: str) -> bool:
        \"\"\"Check if a game exists.\"\"\"
        pass

    @abstractmethod
    def save_history(self, game_id: str, history: GameHistory) -> None:
        \"\"\"Save game history.\"\"\"
        pass

    @abstractmethod
    def get_history(self, game_id: str) -> Optional[GameHistory]:
        \"\"\"Get game history.\"\"\"
        pass
""",

    # Application Layer - Use Cases
    "src/hexagons/game/application/use_cases/create_game.py": """from dataclasses import dataclass
import uuid
from ..ports.game_repository import GameRepository
from ...domain.entities.game import Game
from ...domain.entities.game_history import GameHistory

@dataclass
class CreateGameCommand:
    rows: int
    cols: int

@dataclass
class CreateGameResult:
    game_id: str
    board_state: dict

class CreateGameUseCase:
    def __init__(self, repository: GameRepository):
        self.repository = repository

    def execute(self, command: CreateGameCommand) -> CreateGameResult:
        \"\"\"Create a new game with the specified board size.\"\"\"
        board = Game.create(rows=command.rows, cols=command.cols)
        game_id = str(uuid.uuid4())

        # Save board and initialize history
        self.repository.save(game_id, board)
        history = GameHistory()
        history.add_action(
            action=None,
            board=board.to_dict()
        )
        self.repository.save_history(game_id, history)

        return CreateGameResult(
            game_id=game_id,
            board=board.to_dict()
        )
""",

    "src/hexagons/game/application/use_cases/get_game_state.py": """from dataclasses import dataclass
from ..ports.game_repository import GameRepository

@dataclass
class GetGameStateQuery:
    game_id: str

@dataclass
class GetGameStateResult:
    board_state: dict

class GetGameStateUseCase:
    def __init__(self, repository: GameRepository):
        self.repository = repository

    def execute(self, query: GetGameStateQuery) -> GetGameStateResult:
        \"\"\"Get the current state of a game.\"\"\"
        board = self.repository.get(query.game_id)
        if board is None:
            raise ValueError(f"Game {query.game_id} not found")

        return GetGameStateResult(
            board=board.to_dict()
        )
""",

    "src/hexagons/game/application/use_cases/get_game_history.py": """from dataclasses import dataclass
from ..ports.game_repository import GameRepository

@dataclass
class GetGameHistoryQuery:
    game_id: str

@dataclass
class GetGameHistoryResult:
    history: dict

class GetGameHistoryUseCase:
    def __init__(self, repository: GameRepository):
        self.repository = repository

    def execute(self, query: GetGameHistoryQuery) -> GetGameHistoryResult:
        \"\"\"Get the history of a game.\"\"\"
        history = self.repository.get_history(query.game_id)
        if history is None:
            raise ValueError(f"Game {query.game_id} not found")

        return GetGameHistoryResult(
            history=history.to_dict()
        )
""",

    "src/hexagons/game/application/use_cases/rotate_robot.py": """from dataclasses import dataclass
from ..ports.game_repository import GameRepository
from ...domain.services.game_service import GameService
from ...domain.value_objects.direction import Direction
from ...domain.value_objects.action_type import ActionType
from ...domain.entities.game_history import Action
from ...domain.exceptions.game_exceptions import GameException

@dataclass
class RotateRobotCommand:
    game_id: str
    direction: Direction

@dataclass
class RotateRobotResult:
    success: bool
    board_state: dict
    message: str

class RotateRobotUseCase:
    def __init__(self, repository: GameRepository):
        self.repository = repository

    def execute(self, command: RotateRobotCommand) -> RotateRobotResult:
        \"\"\"Rotate the robot to face a direction.\"\"\"
        board = self.repository.get(command.game_id)
        if board is None:
            raise ValueError(f"Game {command.game_id} not found")

        history = self.repository.get_history(command.game_id)

        try:
            GameService.rotate_robot(board, command.direction)
            self.repository.save(command.game_id, board)

            action = Action(
                action_type=ActionType.ROTATE,
                direction=command.direction,
                success=True,
                message=f"Rotated to face {command.direction.value}"
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return RotateRobotResult(
                success=True,
                board=board.to_dict(),
                message=f"Robot rotated to face {command.direction.value}"
            )
        except GameException as e:
            action = Action(
                action_type=ActionType.ROTATE,
                direction=command.direction,
                success=False,
                message=str(e)
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return RotateRobotResult(
                success=False,
                board=board.to_dict(),
                message=f"Game Over: {str(e)}"
            )
""",

    "src/hexagons/game/application/use_cases/move_robot.py": """from dataclasses import dataclass
from ..ports.game_repository import GameRepository
from ...domain.services.game_service import GameService
from ...domain.value_objects.action_type import ActionType
from ...domain.entities.game_history import Action
from ...domain.exceptions.game_exceptions import GameException

@dataclass
class MoveRobotCommand:
    game_id: str

@dataclass
class MoveRobotResult:
    success: bool
    board_state: dict
    message: str

class MoveRobotUseCase:
    def __init__(self, repository: GameRepository):
        self.repository = repository

    def execute(self, command: MoveRobotCommand) -> MoveRobotResult:
        \"\"\"Move the robot in the direction it's facing.\"\"\"
        board = self.repository.get(command.game_id)
        if board is None:
            raise ValueError(f"Game {command.game_id} not found")

        history = self.repository.get_history(command.game_id)
        orientation = board.robot.orientation

        try:
            GameService.move_robot(board)
            self.repository.save(command.game_id, board)

            status = board.get_status().value
            message = "Move successful"
            if status == "victory":
                message = "Victory! All flowers delivered!"

            action = Action(
                action_type=ActionType.MOVE,
                direction=orientation,
                success=True,
                message=message
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return MoveRobotResult(
                success=True,
                board=board.to_dict(),
                message=message
            )
        except GameException as e:
            action = Action(
                action_type=ActionType.MOVE,
                direction=orientation,
                success=False,
                message=str(e)
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return MoveRobotResult(
                success=False,
                board=board.to_dict(),
                message=f"Game Over: {str(e)}"
            )
""",

    "src/hexagons/game/application/use_cases/pick_flower.py": """from dataclasses import dataclass
from ..ports.game_repository import GameRepository
from ...domain.services.game_service import GameService
from ...domain.value_objects.action_type import ActionType
from ...domain.entities.game_history import Action
from ...domain.exceptions.game_exceptions import GameException

@dataclass
class PickFlowerCommand:
    game_id: str

@dataclass
class PickFlowerResult:
    success: bool
    board_state: dict
    message: str

class PickFlowerUseCase:
    def __init__(self, repository: GameRepository):
        self.repository = repository

    def execute(self, command: PickFlowerCommand) -> PickFlowerResult:
        \"\"\"Pick a flower from an adjacent cell.\"\"\"
        board = self.repository.get(command.game_id)
        if board is None:
            raise ValueError(f"Game {command.game_id} not found")

        history = self.repository.get_history(command.game_id)
        orientation = board.robot.orientation

        try:
            GameService.pick_flower(board)
            self.repository.save(command.game_id, board)

            action = Action(
                action_type=ActionType.PICK,
                direction=orientation,
                success=True,
                message=f"Picked flower (holding {board.robot.flowers_held})"
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return PickFlowerResult(
                success=True,
                board=board.to_dict(),
                message=f"Flower picked successfully (holding {board.robot.flowers_held})"
            )
        except GameException as e:
            action = Action(
                action_type=ActionType.PICK,
                direction=orientation,
                success=False,
                message=str(e)
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return PickFlowerResult(
                success=False,
                board=board.to_dict(),
                message=f"Game Over: {str(e)}"
            )
""",

    "src/hexagons/game/application/use_cases/drop_flower.py": """from dataclasses import dataclass
from ..ports.game_repository import GameRepository
from ...domain.services.game_service import GameService
from ...domain.value_objects.action_type import ActionType
from ...domain.entities.game_history import Action
from ...domain.exceptions.game_exceptions import GameException

@dataclass
class DropFlowerCommand:
    game_id: str

@dataclass
class DropFlowerResult:
    success: bool
    board_state: dict
    message: str

class DropFlowerUseCase:
    def __init__(self, repository: GameRepository):
        self.repository = repository

    def execute(self, command: DropFlowerCommand) -> DropFlowerResult:
        \"\"\"Drop a flower on an adjacent empty cell.\"\"\"
        board = self.repository.get(command.game_id)
        if board is None:
            raise ValueError(f"Game {command.game_id} not found")

        history = self.repository.get_history(command.game_id)
        orientation = board.robot.orientation

        try:
            GameService.drop_flower(board)
            self.repository.save(command.game_id, board)

            action = Action(
                action_type=ActionType.DROP,
                direction=orientation,
                success=True,
                message=f"Dropped flower (holding {board.robot.flowers_held})"
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return DropFlowerResult(
                success=True,
                board=board.to_dict(),
                message=f"Flower dropped successfully (holding {board.robot.flowers_held})"
            )
        except GameException as e:
            action = Action(
                action_type=ActionType.DROP,
                direction=orientation,
                success=False,
                message=str(e)
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return DropFlowerResult(
                success=False,
                board=board.to_dict(),
                message=f"Game Over: {str(e)}"
            )
""",

    "src/hexagons/game/application/use_cases/give_flowers.py": """from dataclasses import dataclass
from ..ports.game_repository import GameRepository
from ...domain.services.game_service import GameService
from ...domain.value_objects.action_type import ActionType
from ...domain.entities.game_history import Action
from ...domain.exceptions.game_exceptions import GameException

@dataclass
class GiveFlowersCommand:
    game_id: str

@dataclass
class GiveFlowersResult:
    success: bool
    board_state: dict
    message: str

class GiveFlowersUseCase:
    def __init__(self, repository: GameRepository):
        self.repository = repository

    def execute(self, command: GiveFlowersCommand) -> GiveFlowersResult:
        \"\"\"Give flowers to the princess.\"\"\"
        board = self.repository.get(command.game_id)
        if board is None:
            raise ValueError(f"Game {command.game_id} not found")

        history = self.repository.get_history(command.game_id)
        orientation = board.robot.orientation

        try:
            GameService.give_flowers(board)
            self.repository.save(command.game_id, board)

            status = board.get_status().value
            message = f"Flowers delivered! ({board.flowers_delivered}/{board.initial_flower_count})"
            if status == "victory":
                message = "Victory! All flowers delivered to the princess!"

            action = Action(
                action_type=ActionType.GIVE,
                direction=orientation,
                success=True,
                message=message
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return GiveFlowersResult(
                success=True,
                board=board.to_dict(),
                message=message
            )
        except GameException as e:
            action = Action(
                action_type=ActionType.GIVE,
                direction=orientation,
                success=False,
                message=str(e)
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return GiveFlowersResult(
                success=False,
                board=board.to_dict(),
                message=f"Game Over: {str(e)}"
            )
""",

    "src/hexagons/game/application/use_cases/clean_obstacle.py": """from dataclasses import dataclass
from ..ports.game_repository import GameRepository
from ...domain.services.game_service import GameService
from ...domain.value_objects.action_type import ActionType
from ...domain.entities.game_history import Action
from ...domain.exceptions.game_exceptions import GameException

@dataclass
class CleanObstacleCommand:
    game_id: str

@dataclass
class CleanObstacleResult:
    success: bool
    board_state: dict
    message: str

class CleanObstacleUseCase:
    def __init__(self, repository: GameRepository):
        self.repository = repository

    def execute(self, command: CleanObstacleCommand) -> CleanObstacleResult:
        \"\"\"Clean an obstacle in the direction faced.\"\"\"
        board = self.repository.get(command.game_id)
        if board is None:
            raise ValueError(f"Game {command.game_id} not found")

        history = self.repository.get_history(command.game_id)
        orientation = board.robot.orientation

        try:
            GameService.clean_obstacle(board)
            self.repository.save(command.game_id, board)

            action = Action(
                action_type=ActionType.CLEAN,
                direction=orientation,
                success=True,
                message="Obstacle cleaned"
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return CleanObstacleResult(
                success=True,
                board=board.to_dict(),
                message="Obstacle cleaned successfully"
            )
        except GameException as e:
            action = Action(
                action_type=ActionType.CLEAN,
                direction=orientation,
                success=False,
                message=str(e)
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return CleanObstacleResult(
                success=False,
                board=board.to_dict(),
                message=f"Game Over: {str(e)}"
            )
""",

    "src/hexagons/game/application/use_cases/autoplay.py": """from dataclasses import dataclass
from copy import deepcopy
from ..ports.game_repository import GameRepository
from ...infrastructure.ai.solver import GameSolver
from ...domain.value_objects.action_type import ActionType
from ...domain.entities.game_history import Action

@dataclass
class AutoplayCommand:
    game_id: str

@dataclass
class AutoplayResult:
    success: bool
    actions_taken: int
    board_state: dict
    message: str

class AutoplayUseCase:
    def __init__(self, repository: GameRepository):
        self.repository = repository

    def execute(self, command: AutoplayCommand) -> AutoplayResult:
        \"\"\"Let AI solve the game automatically.\"\"\"
        board = self.repository.get(command.game_id)
        if board is None:
            raise ValueError(f"Game {command.game_id} not found")

        history = self.repository.get_history(command.game_id)

        # Create a copy for the solver
        board_copy = deepcopy(board)

        try:
            # Get solution from AI
            actions = GameSolver.solve(board_copy)

            # Apply actions to original board
            for action_type, direction in actions:
                if action_type == "rotate":
                    from ...domain.services.game_service import GameService
                    GameService.rotate_robot(board, direction)
                    action = Action(
                        action_type=ActionType.ROTATE,
                        direction=direction,
                        success=True,
                        message=f"AI: Rotated to {direction.value}"
                    )
                    history.add_action(action, board.to_dict())

                elif action_type == "move":
                    from ...domain.services.game_service import GameService
                    GameService.move_robot(board)
                    action = Action(
                        action_type=ActionType.MOVE,
                        direction=board.robot.orientation,
                        success=True,
                        message="AI: Moved"
                    )
                    history.add_action(action, board.to_dict())

                elif action_type == "pick":
                    from ...domain.services.game_service import GameService
                    GameService.pick_flower(board)
                    action = Action(
                        action_type=ActionType.PICK,
                        direction=board.robot.orientation,
                        success=True,
                        message="AI: Picked flower"
                    )
                    history.add_action(action, board.to_dict())

                elif action_type == "give":
                    from ...domain.services.game_service import GameService
                    GameService.give_flowers(board)
                    action = Action(
                        action_type=ActionType.GIVE,
                        direction=board.robot.orientation,
                        success=True,
                        message="AI: Gave flowers"
                    )
                    history.add_action(action, board.to_dict())

            self.repository.save(command.game_id, board)
            self.repository.save_history(command.game_id, history)

            status = board.get_status().value
            success = status == "victory"
            message = "AI completed the game successfully!" if success else "AI attempted to solve but couldn't complete"

            return AutoplayResult(
                success=success,
                actions_taken=len(actions),
                board=board.to_dict(),
                message=message
            )

        except Exception as e:
            return AutoplayResult(
                success=False,
                actions_taken=0,
                board=board.to_dict(),
                message=f"AI failed: {str(e)}"
            )
""",
   # ⬇️ PART 3: Infrastructure & Tests (from robot_princess_part3)
   # Infrastructure Layer - Persistence
    "src/hexagons/game/infrastructure/persistence/in_memory_game_repository.py": """from typing import Optional, Dict
from ...application.ports.game_repository import GameRepository
from ...domain.entities.game import Game
from ...domain.entities.game_history import GameHistory

class InMemoryGameRepository(GameRepository):
    \"\"\"In-memory implementation of game repository.\"\"\"

    def __init__(self) -> None:
        self._games: Dict[str, Game] = {}
        self._histories: Dict[str, GameHistory] = {}

    def save(self, game_id: str, board: Game) -> None:
        self._games[game_id] = board

    def get(self, game_id: str) -> Optional[Game]:
        return self._games.get(game_id)

    def delete(self, game_id: str) -> None:
        if game_id in self._games:
            del self._games[game_id]
        if game_id in self._histories:
            del self._histories[game_id]

    def exists(self, game_id: str) -> bool:
        return game_id in self._games

    def save_history(self, game_id: str, history: GameHistory) -> None:
        self._histories[game_id] = history

    def get_history(self, game_id: str) -> Optional[GameHistory]:
        return self._histories.get(game_id)
""",

    # Infrastructure Layer - API Schemas
    "src/hexagons/game/infrastructure/api/schemas/game_schema.py": """from pydantic import BaseModel, Field
from typing import Literal

class CreateGameRequest(BaseModel):
    rows: int = Field(ge=3, le=50, description="Number of rows (3-50)")
    cols: int = Field(ge=3, le=50, description="Number of columns (3-50)")

class RotateRequest(BaseModel):
    direction: Literal["north", "south", "east", "west"] = Field(description="Direction to face")

class GameStateResponse(BaseModel):
    game_id: str
    board: dict
    message: str = ""

class ActionResponse(BaseModel):
    success: bool
    game_id: str
    board: dict
    message: str

class GameHistoryResponse(BaseModel):
    game_id: str
    history: dict
""",

    # Infrastructure Layer - API Dependencies
    "src/hexagons/game/infrastructure/api/dependencies.py": """from functools import lru_cache
from ..persistence.in_memory_game_repository import InMemoryGameRepository
from ...application.ports.game_repository import GameRepository

@lru_cache()
def get_game_repository() -> GameRepository:
    \"\"\"Dependency injection for game repository.\"\"\"
    return InMemoryGameRepository()
""",

    # Infrastructure Layer - API Router
    "src/hexagons/game/infrastructure/api/routers/game_router.py": """from fastapi import APIRouter, Depends, HTTPException
from ..schemas.game_schema import (
    CreateGameRequest,
    RotateRequest,
    GameStateResponse,
    ActionResponse,
    GameHistoryResponse,
)
from ..dependencies import get_game_repository
from ....application.ports.game_repository import GameRepository
from ....domain.use_cases.create_game import CreateGameUseCase, CreateGameCommand
from ....domain.use_cases.get_game_state import GetGameStateUseCase, GetGameStateQuery
from ....domain.use_cases.get_game_history import GetGameHistoryUseCase, GetGameHistoryQuery
from ....domain.use_cases.rotate_robot import RotateRobotUseCase, RotateRobotCommand
from ....domain.use_cases.move_robot import MoveRobotUseCase, MoveRobotCommand
from ....domain.use_cases.pick_flower import PickFlowerUseCase, PickFlowerCommand
from ....domain.use_cases.drop_flower import DropFlowerUseCase, DropFlowerCommand
from ....domain.use_cases.give_flowers import GiveFlowersUseCase, GiveFlowersCommand
from ....domain.use_cases.clean_obstacle import CleanObstacleUseCase, CleanObstacleCommand
from ....domain.value_objects.direction import Direction

router = APIRouter(prefix="/api/v1/games", tags=["games"])


@router.post("/", response_model=GameStateResponse, status_code=201)
def create_game(
    request: CreateGameRequest,
    repository: GameRepository = Depends(get_game_repository),
) -> GameStateResponse:
    \"\"\"Create a new game with specified board size.\"\"\"
    try:
        use_case = CreateGameUseCase(repository)
        result = use_case.execute(
            CreateGameCommand(rows=request.rows, cols=request.cols)
        )
        return GameStateResponse(
            game_id=result.game_id,
            board=result.board_state,
            message="Game created successfully",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{game_id}", response_model=GameStateResponse)
def get_game_state(
    game_id: str,
    repository: GameRepository = Depends(get_game_repository),
) -> GameStateResponse:
    \"\"\"Get the current state of a game.\"\"\"
    try:
        use_case = GetGameStateUseCase(repository)
        result = use_case.execute(GetGameStateQuery(game_id=game_id))
        return GameStateResponse(
            game_id=game_id,
            board=result.board_state,
            message="Game state retrieved successfully",
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{game_id}/history", response_model=GameHistoryResponse)
def get_game_history(
    game_id: str,
    repository: GameRepository = Depends(get_game_repository),
) -> GameHistoryResponse:
    \"\"\"Get the history of a game.\"\"\"
    try:
        use_case = GetGameHistoryUseCase(repository)
        result = use_case.execute(GetGameHistoryQuery(game_id=game_id))
        return GameHistoryResponse(
            game_id=game_id,
            history=result.history,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{game_id}/action/rotate", response_model=ActionResponse)
def rotate_robot(
    game_id: str,
    request: RotateRequest,
    repository: GameRepository = Depends(get_game_repository),
) -> ActionResponse:
    \"\"\"Rotate the robot to face a direction.\"\"\"
    try:
        use_case = RotateRobotUseCase(repository)
        direction = Direction(request.direction)
        result = use_case.execute(
            RotateRobotCommand(game_id=game_id, direction=direction)
        )
        return ActionResponse(
            success=result.success,
            game_id=game_id,
            board=result.board_state,
            message=result.message,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{game_id}/action/move", response_model=ActionResponse)
def move_robot(
    game_id: str,
    repository: GameRepository = Depends(get_game_repository),
) -> ActionResponse:
    \"\"\"Move the robot in the direction it's facing.\"\"\"
    try:
        use_case = MoveRobotUseCase(repository)
    result = use_case.execute(MoveRobotCommand(game_id=game_id, direction=Direction.SOUTH))
        return ActionResponse(
            success=result.success,
            game_id=game_id,
            board=result.board_state,
            message=result.message,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{game_id}/action/pick", response_model=ActionResponse)
def pick_flower(
    game_id: str,
    repository: GameRepository = Depends(get_game_repository),
) -> ActionResponse:
    \"\"\"Pick a flower from an adjacent cell.\"\"\"
    try:
        use_case = PickFlowerUseCase(repository)
    result = use_case.execute(PickFlowerCommand(game_id=game_id, direction=Direction.SOUTH))
        return ActionResponse(
            success=result.success,
            game_id=game_id,
            board=result.board_state,
            message=result.message,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{game_id}/action/drop", response_model=ActionResponse)
def drop_flower(
    game_id: str,
    repository: GameRepository = Depends(get_game_repository),
) -> ActionResponse:
    \"\"\"Drop a flower on an adjacent empty cell.\"\"\"
    try:
        use_case = DropFlowerUseCase(repository)
    result = use_case.execute(DropFlowerCommand(game_id=game_id, direction=Direction.SOUTH))
        return ActionResponse(
            success=result.success,
            game_id=game_id,
            board=result.board_state,
            message=result.message,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{game_id}/action/give", response_model=ActionResponse)
def give_flowers(
    game_id: str,
    repository: GameRepository = Depends(get_game_repository),
) -> ActionResponse:
    \"\"\"Give flowers to the princess.\"\"\"
    try:
        use_case = GiveFlowersUseCase(repository)
    result = use_case.execute(GiveFlowersCommand(game_id=game_id, direction=Direction.SOUTH))
        return ActionResponse(
            success=result.success,
            game_id=game_id,
            board=result.board_state,
            message=result.message,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{game_id}/action/clean", response_model=ActionResponse)
def clean_obstacle(
    game_id: str,
    repository: GameRepository = Depends(get_game_repository),
) -> ActionResponse:
    \"\"\"Clean an obstacle in the direction faced.\"\"\"
    try:
        use_case = CleanObstacleUseCase(repository)
    result = use_case.execute(CleanObstacleCommand(game_id=game_id, direction=Direction.SOUTH))
        return ActionResponse(
            success=result.success,
            game_id=game_id,
            board=result.board_state,
            message=result.message,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{game_id}/autoplay", response_model=ActionResponse)
def autoplay(
    game_id: str,
    repository: GameRepository = Depends(get_game_repository),
) -> ActionResponse:
    \"\"\"Let AI solve the game automatically.\"\"\"
    try:
        from ....domain.use_cases.autoplay import AutoplayUseCase, AutoplayCommand
        use_case = AutoplayUseCase(repository)
        result = use_case.execute(AutoplayCommand(game_id=game_id))
        return ActionResponse(
            success=result.success,
            game_id=game_id,
            board=result.board_state,
            message=f"{result.message} (Actions taken: {result.actions_taken})",
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
""",

    # Infrastructure Layer - Main API
    "src/hexagons/game/infrastructure/api/main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import game_router

app = FastAPI(
    title="Robot-Flower-Princess Game API",
    description="A strategic puzzle game API where you guide a robot to collect flowers and deliver them to a princess",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(game_router.router)


@app.get("/")
def root() -> dict:
    \"\"\"Root endpoint.\"\"\"
    return {
        "message": "Welcome to Robot-Flower-Princess Game API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
def health_check() -> dict:
    \"\"\"Health check endpoint.\"\"\"
    return {"status": "healthy", "service": "robot-flower-princess-api"}
""",

    # Config
    "src/hexagons/game/config/settings.py": """from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    environment: str = "development"
    log_level: str = "info"
    api_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"

settings = Settings()
""",

    # AI Solver
    "src/hexagons/game/infrastructure/ai/solver.py": """from typing import List, Optional, Tuple
from collections import deque
from copy import deepcopy
from ...domain.entities.game import Game
from ...domain.entities.position import Position
from ...domain.value_objects.direction import Direction
from ...domain.services.game_service import GameService

class GameSolver:
    \"\"\"AI solver for the game using BFS.\"\"\"

    @staticmethod
    def solve(board: Game) -> List[Tuple[str, Optional[Direction]]]:
        \"\"\"
        Attempt to solve the game and return a list of actions.
        Returns a list of tuples: (action_type, direction)
        \"\"\"
        actions = []

        while board.flowers or board.robot.flowers_held > 0:
            # If holding flowers and need to deliver
            if board.robot.flowers_held > 0 and (
                board.robot.flowers_held == board.robot.max_flowers or
                len(board.flowers) == 0
            ):
                # Navigate to princess
                path = GameSolver._find_path(board, board.robot.position, board.princess_position)
                if not path:
                    break

                for next_pos in path:
                    direction = GameSolver._get_direction(board.robot.position, next_pos)
                    actions.append(("rotate", direction))
                    GameService.rotate_robot(board, direction)

                    actions.append(("move", None))
                    GameService.move_robot(board)

                # Face princess and give flowers
                direction = GameSolver._get_direction(board.robot.position, board.princess_position)
                actions.append(("rotate", direction))
                GameService.rotate_robot(board, direction)

                actions.append(("give", None))
                GameService.give_flowers(board)

            # If not holding max flowers and there are flowers to collect
            elif board.flowers and board.robot.can_pick():
                # Find nearest flower
                nearest_flower = min(
                    board.flowers,
                    key=lambda f: board.robot.position.manhattan_distance(f)
                )

                # Navigate adjacent to flower
                adjacent_positions = GameSolver._get_adjacent_positions(nearest_flower, board)
                if not adjacent_positions:
                    break

                target = min(
                    adjacent_positions,
                    key=lambda p: board.robot.position.manhattan_distance(p)
                )

                path = GameSolver._find_path(board, board.robot.position, target)
                if not path:
                    break

                for next_pos in path:
                    direction = GameSolver._get_direction(board.robot.position, next_pos)
                    actions.append(("rotate", direction))
                    GameService.rotate_robot(board, direction)

                    actions.append(("move", None))
                    GameService.move_robot(board)

                # Face flower and pick it
                direction = GameSolver._get_direction(board.robot.position, nearest_flower)
                actions.append(("rotate", direction))
                GameService.rotate_robot(board, direction)

                actions.append(("pick", None))
                GameService.pick_flower(board)
            else:
                break

        return actions

    @staticmethod
    def _find_path(board: Game, start: Position, goal: Position) -> List[Position]:
        \"\"\"Find path from start to goal using BFS.\"\"\"
        if start == goal:
            return []

        queue = deque([(start, [])])
        visited = {start}

        while queue:
            current, path = queue.popleft()

            for direction in Direction:
                row_delta, col_delta = direction.get_delta()
                next_pos = current.move(row_delta, col_delta)

                if next_pos == goal:
                    return path + [next_pos]

                if (board.is_valid_position(next_pos) and
                    board.is_empty(next_pos) and
                    next_pos not in visited):
                    visited.add(next_pos)
                    queue.append((next_pos, path + [next_pos]))

        return []

    @staticmethod
    def _get_adjacent_positions(pos: Position, board: Game) -> List[Position]:
        \"\"\"Get all valid adjacent empty positions.\"\"\"
        adjacent = []
        for direction in Direction:
            row_delta, col_delta = direction.get_delta()
            adj_pos = pos.move(row_delta, col_delta)
            if board.is_valid_position(adj_pos) and board.is_empty(adj_pos):
                adjacent.append(adj_pos)
        return adjacent

    @staticmethod
    def _get_direction(from_pos: Position, to_pos: Position) -> Direction:
        \"\"\"Get direction from one position to another (must be adjacent).\"\"\"
        row_diff = to_pos.row - from_pos.row
        col_diff = to_pos.col - from_pos.col

        if row_diff == -1:
            return Direction.NORTH
        elif row_diff == 1:
            return Direction.SOUTH
        elif col_diff == 1:
            return Direction.EAST
        else:
            return Direction.WEST
""",

    # Tests - conftest
    "tests/conftest.py": """import pytest
from hexagons.game.infrastructure.persistence.in_memory_game_repository import InMemoryGameRepository
from hexagons.game.domain.entities.game import Game
from hexagons.game.domain.entities.position import Position
from hexagons.game.domain.entities.robot import Robot
from hexagons.game.domain.value_objects.direction import Direction


@pytest.fixture
def game_repository():
    \"\"\"Fixture for game repository.\"\"\"
    return InMemoryGameRepository()


@pytest.fixture
def sample_board():
    \"\"\"Fixture for a simple test board.\"\"\"
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    princess_pos = Position(2, 2)
    flowers = {Position(1, 1)}
    obstacles = {Position(0, 1)}

    board = Game(
        rows=3,
        cols=3,
        robot=robot,
        princess_position=princess_pos,
        flowers=flowers,
        obstacles=obstacles,
    )
    board.initial_flower_count = len(flowers)
    return board
""",

    # Tests - Unit Tests
    "tests/unit/domain/test_position.py": """import pytest
from hexagons.game.domain.entities.position import Position


def test_position_creation():
    pos = Position(5, 10)
    assert pos.row == 5
    assert pos.col == 10


def test_position_move():
    pos = Position(5, 10)
    new_pos = pos.move(2, -3)
    assert new_pos.row == 7
    assert new_pos.col == 7


def test_position_manhattan_distance():
    pos1 = Position(0, 0)
    pos2 = Position(3, 4)
    assert pos1.manhattan_distance(pos2) == 7
""",

    "tests/unit/domain/test_robot.py": """import pytest
from hexagons.game.domain.entities.robot import Robot
from hexagons.game.domain.entities.position import Position
from hexagons.game.domain.value_objects.direction import Direction


def test_robot_creation():
    pos = Position(0, 0)
    robot = Robot(position=pos)
    assert robot.position == pos
    assert robot.orientation == Direction.EAST
    assert robot.flowers_held == 0


def test_robot_pick_flower():
    robot = Robot(position=Position(0, 0))
    robot.pick_flower()
    assert robot.flowers_held == 1

    # Test max flowers
    for _ in range(11):
        robot.pick_flower()
    assert robot.flowers_held == 12

    with pytest.raises(ValueError):
        robot.pick_flower()


def test_robot_drop_flower():
    robot = Robot(position=Position(0, 0))

    with pytest.raises(ValueError):
        robot.drop_flower()

    robot.pick_flower()
    robot.drop_flower()
    assert robot.flowers_held == 0


def test_robot_give_flowers():
    robot = Robot(position=Position(0, 0))
    robot.pick_flower()
    robot.pick_flower()

    delivered = robot.give_flowers()
    assert delivered == 2
    assert robot.flowers_held == 0
""",

    "tests/unit/domain/test_board.py": """import pytest
from hexagons.game.domain.entities.game import Game
from hexagons.game.domain.entities.position import Position
from hexagons.game.domain.value_objects.game_status import GameStatus


def test_board_creation():
    board = Game.create(rows=10, cols=10)
    assert board.rows == 10
    assert board.cols == 10
    assert board.robot.position == Position(0, 0)
    assert board.princess_position == Position(9, 9)


def test_board_invalid_size():
    with pytest.raises(ValueError):
        Game.create(rows=2, cols=5)

    with pytest.raises(ValueError):
        Game.create(rows=51, cols=5)


def test_board_victory():
    board = Game.create(rows=5, cols=5)
    assert board.get_status() == GameStatus.IN_PROGRESS

    board.flowers_delivered = board.initial_flower_count
    assert board.get_status() == GameStatus.VICTORY
""",

    "tests/integration/test_api.py": """import pytest
from fastapi.testclient import TestClient
from hexagons.game..main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_game():
    response = client.post("/api/v1/games/", json={"rows": 5, "cols": 5})
    assert response.status_code == 201
    data = response.json()
    assert "game_id" in data
    assert data["board"]["rows"] == 5


def test_get_game_state():
    create_response = client.post("/api/v1/games/", json={"rows": 5, "cols": 5})
    game_id = create_response.json()["game_id"]

    response = client.get(f"/api/v1/games/{game_id}")
    assert response.status_code == 200
    assert response.json()["game_id"] == game_id


def test_rotate_robot():
    create_response = client.post("/api/v1/games/", json={"rows": 5, "cols": 5})
    game_id = create_response.json()["game_id"]

    response = client.post(
        f"/api/v1/games/{game_id}/action/rotate",
        json={"direction": "south"}
    )
    assert response.status_code == 200
    assert response.json()["success"] == True


def test_get_game_history():
    create_response = client.post("/api/v1/games/", json={"rows": 5, "cols": 5})
    game_id = create_response.json()["game_id"]

    response = client.get(f"/api/v1/games/{game_id}/history")
    assert response.status_code == 200
    assert "history" in response.json()


def test_autoplay():
    create_response = client.post("/api/v1/games/", json={"rows": 5, "cols": 5})
    game_id = create_response.json()["game_id"]

    response = client.post(f"/api/v1/games/{game_id}/autoplay")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "board" in data
""",
}

# I'll continue adding all the source files in the next part
# This is just showing the complete header structure

def create_project():
    """Create the complete project structure."""

    print(f"🤖 Creating {PROJECT_NAME}...")
    print("=" * 60)

    # Create project directory
    os.makedirs(PROJECT_NAME, exist_ok=True)
    os.chdir(PROJECT_NAME)

    # Create all directories
    dirs = [
        "src/hexagons/game/domain/entities",
        "src/hexagons/game/domain/value_objects",
        "src/hexagons/game/domain/exceptions",
        "src/hexagons/game/domain/services",
        "src/hexagons/game/application/ports",
        "src/hexagons/game/application/use_cases",
        "src/hexagons/game/infrastructure/persistence",
        "src/hexagons/game/infrastructure/api/routers",
        "src/hexagons/game/infrastructure/api/schemas",
        "src/hexagons/game/infrastructure/ai",
        "src/hexagons/game/config",
        "tests/unit/domain",
        "tests/unit/application",
        "tests/integration",
        ".github/workflows",
    ]

    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        # Create __init__.py for Python packages
        if dir_path.startswith(("src/", "tests/")):
            init_file = Path(dir_path) / "__init__.py"
            init_file.touch()

    print(f"✅ Created {len(dirs)} directories")

    # NOTE: Add all FILES content here from the previous artifact
    # I'll provide the continuation with all source files

    # Create all files
    file_count = 0
    for filepath, content in FILES.items():
        file_path = Path(filepath)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(content)
        file_count += 1
        if file_count % 10 == 0:
            print(f"  ... created {file_count} files")

    print(f"\n✅ Created {file_count} files")

    # Create zip file
    zip_filename = f"{PROJECT_NAME}-{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    os.chdir("..")

    print(f"\n📦 Creating ZIP archive: {zip_filename}")
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(PROJECT_NAME):
            # Skip __pycache__ and other unwanted directories
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', '.pytest_cache', '__pycache__']]
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, '.')
                zipf.write(file_path, arcname)

    zip_size = os.path.getsize(zip_filename) / (1024 * 1024)  # Size in MB
    print(f"✅ ZIP archive created: {zip_filename} ({zip_size:.2f} MB)")

    print("\n" + "=" * 60)
    print("✨ Project created successfully!")
    print(f"\n📦 Download: {os.path.abspath(zip_filename)}")
    print(f"\n📋 Next steps:")
    print(f"  1. unzip {zip_filename}")
    print(f"  2. cd {PROJECT_NAME}")
    print("  3. pyenv install 3.13.0 && pyenv local 3.13.0")
    print("  4. poetry install")
    print("  5. make run")
    print("\n🐳 Or use Docker:")
    print("  docker-compose up --build")
    print("\n📚 API docs: http://localhost:8000/docs")
    print(f"\n✅ Total files created: {file_count}")
    print(f"✅ Total directories created: {len(dirs)}")
    print("\n🎉 Happy coding!")

if __name__ == "__main__":
    try:
        create_project()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()