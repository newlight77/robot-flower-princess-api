# Architecture Documentation

## Table of Contents
- [Overview](#overview)
- [Architectural Patterns](#architectural-patterns)
- [System Architecture](#system-architecture)
- [Domain-Driven Design](#domain-driven-design)
- [Project Structure](#project-structure)
- [Core Components](#core-components)
- [Design Patterns](#design-patterns)
- [Data Flow](#data-flow)
- [Key Design Decisions](#key-design-decisions)

---

## Overview

The **Robot Flower Princess** game backend is built using **Domain-Driven Design (DDD)** and **Hexagonal Architecture** (also known as Ports and Adapters). This architecture ensures:

- ✅ **Business Logic Independence**: Core domain logic is isolated from external concerns
- ✅ **Testability**: Easy to test with minimal mocking
- ✅ **Maintainability**: Clear separation of concerns
- ✅ **Flexibility**: Easy to swap implementations (database, API framework, etc.)
- ✅ **Scalability**: Clean boundaries for extending functionality

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **API Framework** | FastAPI 0.115 | RESTful API endpoints |
| **Language** | Python 3.13 | Core application |
| **Validation** | Pydantic v2 | Schema validation |
| **Dependency Mgmt** | Poetry 1.7+ | Package management |
| **Testing** | Pytest | Unit/Integration tests |
| **Coverage** | Coverage.py | Code coverage tracking |
| **Linting** | Ruff, Black | Code quality |
| **Container** | Docker | Deployment |
| **CI/CD** | GitHub Actions | Automated testing & deployment |

---

## Architectural Patterns

### 1. Hexagonal Architecture (Ports and Adapters)

The application follows the **Hexagonal Architecture** pattern, which organizes code into concentric layers:

```
┌─────────────────────────────────────────────────────────┐
│                    External World                        │
│  (HTTP Clients, Databases, External Services)           │
└─────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────┐
│                    Driver Adapters                       │
│            (FastAPI Routers, API Schemas)                │
│                   [Infrastructure]                       │
└─────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────┐
│                    Application Layer                     │
│                     (Use Cases)                          │
│               [Orchestration & Flow]                     │
└─────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────┐
│                     Domain Layer                         │
│         (Entities, Value Objects, Services)              │
│              [Business Logic - CORE]                     │
└─────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────┐
│                    Driven Adapters                       │
│          (In-Memory Repository, Persistence)             │
│                   [Infrastructure]                       │
└─────────────────────────────────────────────────────────┘
```

**Key Principles:**
- The **Domain** is at the center and has no dependencies on outer layers
- The **Application Layer** (use cases) orchestrates domain operations
- **Adapters** (infrastructure) depend on the domain, not vice versa
- **Ports** (interfaces) define contracts between layers

### 2. Domain-Driven Design (DDD)

The domain layer uses **tactical DDD patterns**:

- **Entities**: Objects with identity that persist over time (`Game`, `Robot`, `Princess`)
- **Value Objects**: Immutable objects defined by their values (`Position`, `Direction`, `Action`)
- **Aggregates**: Clusters of entities treated as a unit (`Game` is the aggregate root)
- **Domain Services**: Stateless operations on domain objects (`GameService`)
- **Repositories**: Abstractions for persistence (`GameRepository`)
- **Use Cases**: Application-specific business rules

---

## System Architecture

### High-Level Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         HTTP Client                               │
│                  (Web, Mobile, CLI, Tests)                        │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                        FastAPI Application                        │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                    API Router Layer                        │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │  │
│  │  │ Game Router  │  │ Root Endpoint│  │Health Endpoint│   │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │  │
│  └────────────────────────────────────────────────────────────┘  │
│                              │                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                    Pydantic Schemas                        │  │
│  │    (Request/Response validation & serialization)           │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                       Application Layer                           │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                      Use Cases                             │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐          │  │
│  │  │CreateGame  │  │ MoveRobot  │  │ Autoplay   │          │  │
│  │  │            │  │            │  │            │  ...      │  │
│  │  └────────────┘  └────────────┘  └────────────┘          │  │
│  └────────────────────────────────────────────────────────────┘  │
│                              │                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                      Ports (Interfaces)                    │  │
│  │                    GameRepository                          │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                         Domain Layer                              │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                      Entities                              │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐          │  │
│  │  │   Game     │  │   Robot    │  │  Princess  │          │  │
│  │  │   Board    │  │  Position  │  │GameHistory │          │  │
│  │  └────────────┘  └────────────┘  └────────────┘          │  │
│  └────────────────────────────────────────────────────────────┘  │
│                              │                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                   Value Objects                            │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐          │  │
│  │  │ Direction  │  │ ActionType │  │GameStatus  │          │  │
│  │  │  Position  │  │   Action   │  │            │          │  │
│  │  └────────────┘  └────────────┘  └────────────┘          │  │
│  └────────────────────────────────────────────────────────────┘  │
│                              │                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                   Domain Services                          │  │
│  │  ┌────────────┐  ┌────────────┐                           │  │
│  │  │GameService │  │GameSolver  │                           │  │
│  │  │            │  │  Player    │                           │  │
│  │  └────────────┘  └────────────┘                           │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                     Infrastructure Layer                          │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                    Persistence                             │  │
│  │  ┌────────────┐                                            │  │
│  │  │In-Memory   │  (Future: PostgreSQL, Redis)              │  │
│  │  │Repository  │                                            │  │
│  │  └────────────┘                                            │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Domain-Driven Design

### Domain Model

The core domain model revolves around a **Game** aggregate:

```python
Game (Aggregate Root)
├── Board (Value Object/Entity)
│   ├── rows: int
│   ├── cols: int
│   └── grid: List[List[str]]
│
├── Robot (Entity)
│   ├── position: Position
│   ├── orientation: Direction
│   ├── flowers_held: int
│   ├── flowers_collected: List[dict]
│   ├── flowers_delivered: List[dict]
│   └── obstacles_cleaned: List[dict]
│
├── Princess (Entity)
│   ├── position: Position
│   └── flowers_received: int
│
├── flowers: Set[Position]
├── obstacles: Set[Position]
└── status: GameStatus
```

### Bounded Context

This application has a single **bounded context**: **Game Management**

**Ubiquitous Language:**
- **Game**: A puzzle instance with a board, robot, princess, flowers, and obstacles
- **Board**: Grid representing the game space
- **Robot**: Player-controlled entity that collects and delivers flowers
- **Princess**: Goal entity that receives flowers
- **Flower**: Collectible item that must be delivered
- **Obstacle**: Blocking element that can be cleaned
- **Action**: A command executed by the robot (move, rotate, pick, drop, give, clean)
- **Position**: A coordinate (row, col) on the board
- **Direction**: Cardinal direction (north, south, east, west)
- **Autoplay**: AI solver that completes the game automatically

---

## Project Structure

```
Robot-Flower-Princess-Claude-API-FastAPI-v4/
├── src/
│   ├── hexagons/                            # Hexagonal Architecture Modules
│   │   ├── game/                            # Game Hexagon (Core Domain)
│   │   │   ├── domain/                      # Domain Layer (Business Logic)
│   │   │   │   ├── core/
│   │   │   │   │   ├── entities/            # Domain Entities
│   │   │   │   │   │   ├── game.py          # Game aggregate root
│   │   │   │   │   │   ├── board.py         # Board entity
│   │   │   │   │   │   ├── robot.py         # Robot entity
│   │   │   │   │   │   ├── princess.py      # Princess entity
│   │   │   │   │   │   └── game_history.py  # Game history entity
│   │   │   │   │   ├── value_objects/       # Immutable Value Objects
│   │   │   │   │   │   ├── position.py      # Position (row, col)
│   │   │   │   │   │   ├── direction.py     # Direction enum
│   │   │   │   │   │   ├── action_type.py   # Action type enum
│   │   │   │   │   │   └── game_status.py   # Game status enum
│   │   │   │   │   └── exceptions/          # Domain Exceptions
│   │   │   │   │       └── game_exceptions.py  # Custom exceptions
│   │   │   │   ├── ports/                   # Domain Interfaces
│   │   │   │   │   └── game_repository.py   # Repository interface
│   │   │   │   ├── services/                # Domain Services
│   │   │   │   │   └── game_service.py      # Game operations service
│   │   │   │   └── use_cases/               # Application Use Cases
│   │   │   │       ├── create_game.py       # Create new game
│   │   │   │       ├── get_game_state.py        # Retrieve game state
│   │   │   │       ├── get_game_history.py      # Retrieve game history
│   │   │   │       ├── move_robot.py            # Move robot action
│   │   │   │       ├── rotate_robot.py          # Rotate robot action
│   │   │   │       ├── pick_flower.py           # Pick flower action
│   │   │   │       ├── drop_flower.py           # Drop flower action
│   │   │   │       ├── give_flowers.py          # Give flowers action
│   │   │   │       └── clean_obstacle.py        # Clean obstacle action
│   │   │   ├── driven/                      # Infrastructure (Driven Adapters)
│   │   │   │   └── persistence/
│   │   │   │       └── in_memory_game_repository.py  # In-memory storage
│   │   │   └── driver/                      # Infrastructure (Driver Adapters)
│   │   │       └── bff/                     # Backend-for-Frontend
│   │   │           ├── routers/
│   │   │           │   └── game_router.py   # Game API endpoints
│   │   │           └── schemas/
│   │   │               └── game_schema.py   # Pydantic schemas
│   │   ├── aiplayer/                        # AIPlayer Hexagon (AI Solver)
│   │   │   ├── domain/
│   │   │   │   ├── core/
│   │   │   │   │   └── entities/
│   │   │   │   │       ├── ai_greedy_player.py   # Greedy AI strategy
│   │   │   │   │       └── ai_optimal_player.py  # Optimal AI strategy
│   │   │   │   └── use_cases/
│   │   │   │       └── autoplay.py          # Autoplay use case
│   │   │   └── driver/
│   │   │       └── bff/
│   │   │           └── routers/
│   │   │               └── aiplayer_router.py  # Autoplay API endpoint
│   │   └── health/                          # Health Hexagon (Monitoring)
│   │       └── driver/
│   │           └── bff/
│   │               └── routers/
│   │                   └── health_router.py  # Health check endpoint
│   ├── configurator/                        # Configuration (Shared)
│   │   ├── settings.py                      # App settings
│   │   └── dependencies.py                  # Dependency injection
│   ├── shared/                              # Shared Utilities
│   │   └── logging.py                       # Logging setup
│   └── main.py                              # FastAPI app entry point
├── tests/                                  # Test Suite
│   ├── unit/                               # Unit tests
│   ├── integration/                        # Integration tests
│   ├── feature-component/                  # Feature-component tests
│   └── conftest.py                         # Pytest fixtures
├── docs/                                   # Documentation
│   ├── ARCHITECTURE.md                     # This file
│   ├── API.md                              # API documentation
│   ├── DEPLOYMENT.md                       # Deployment guide
│   ├── CI_CD.md                            # CI/CD workflow
│   └── TESTING_STRATEGY.md                 # Testing strategy
├── .github/
│   └── workflows/
│       └── ci.yml                          # GitHub Actions CI/CD
├── Dockerfile                              # Docker image definition
├── pyproject.toml                          # Poetry dependencies
├── Makefile                                # Build & test commands
└── README.md                               # Project overview
```

---

## Core Components

### 1. Domain Layer

#### Entities

**Game (Aggregate Root)**
```python
@dataclass
class Game:
    """
    Aggregate root representing the entire game state.
    Encapsulates all game logic and enforces invariants.
    """
    rows: int
    cols: int
    robot: Robot
    princess: Princess
    flowers: Set[Position]
    obstacles: Set[Position]
    board: Board
    status: GameStatus = GameStatus.IN_PROGRESS

    def is_valid_position(self, pos: Position) -> bool:
        """Check if position is within board bounds."""

    def is_empty(self, pos: Position) -> bool:
        """Check if cell is empty (no robot, princess, flower, obstacle)."""

    def is_game_won(self) -> bool:
        """Check if all flowers delivered to princess."""
```

**Robot**
```python
@dataclass
class Robot:
    """
    Entity representing the robot player.
    Tracks position, orientation, and collected items.
    """
    position: Position
    orientation: Direction = Direction.NORTH
    flowers_held: int = 0
    max_flowers: int = 12
    flowers_collected: List[dict] = field(default_factory=list)
    flowers_delivered: List[dict] = field(default_factory=list)
    obstacles_cleaned: List[dict] = field(default_factory=list)

    def can_pick(self) -> bool:
        """Check if robot can pick more flowers."""

    def pick_flower(self) -> None:
        """Pick a flower at current position."""

    def give_flowers(self, princess_position: Position) -> int:
        """Give all held flowers to princess."""

    def to_dict(self) -> dict:
        """Serialize robot to dictionary."""
```

**Princess**
```python
@dataclass
class Princess:
    """Entity representing the princess (goal)."""
    position: Position
    flowers_received: int = 0

    def receive_flowers(self, count: int) -> None:
        """Receive flowers from robot."""

    def to_dict(self) -> dict:
        """Serialize princess to dictionary."""
```

**Board**
```python
@dataclass
class Board:
    """Entity representing the game grid."""
    rows: int
    cols: int
    grid: List[List[str]] = field(default_factory=list)

    def to_dict(self, robot_pos, princess_pos, flowers, obstacles) -> dict:
        """Serialize board with all entities to dictionary."""
```

#### Value Objects

**Position**
```python
@dataclass(frozen=True)
class Position:
    """Immutable value object representing a board coordinate."""
    row: int
    col: int

    def move(self, row_delta: int, col_delta: int) -> Position:
        """Return new Position after applying delta."""

    def manhattan_distance(self, other: Position) -> int:
        """Calculate Manhattan distance to another position."""
```

**Direction**
```python
class Direction(str, Enum):
    """Enum representing cardinal directions."""
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"

    def get_delta(self) -> Tuple[int, int]:
        """Get (row_delta, col_delta) for this direction."""
```

**ActionType**
```python
class ActionType(str, Enum):
    """Enum representing possible robot actions."""
    ROTATE = "rotate"
    MOVE = "move"
    PICK = "pickFlower"
    DROP = "dropFlower"
    GIVE = "giveFlower"
    CLEAN = "clean"
```

**GameStatus**
```python
class GameStatus(str, Enum):
    """Enum representing game state."""
    IN_PROGRESS = "in_progress"
    WON = "won"
    LOST = "lost"
```

#### Domain Services

**GameService**
```python
class GameService:
    """
    Stateless domain service for game operations.
    Provides low-level game mechanics used by use cases.
    """

    @staticmethod
    def move_robot(board: Game) -> None:
        """Move robot one cell forward in its orientation."""

    @staticmethod
    def rotate_robot(board: Game, direction: Direction) -> None:
        """Rotate robot to face a direction."""

    @staticmethod
    def pick_flower(board: Game) -> None:
        """Robot picks flower in front."""

    @staticmethod
    def drop_flower(board: Game) -> None:
        """Robot drops flower in front."""

    @staticmethod
    def give_flowers(board: Game) -> int:
        """Robot gives flowers to princess."""

    @staticmethod
    def clean_obstacle(board: Game) -> None:
        """Robot cleans obstacle in front."""
```

**GameSolverPlayer (AI)**
```python
class GameSolverPlayer:
    """
    Domain service that implements AI pathfinding and game solving.
    Uses BFS for pathfinding and strategic planning.
    """

    @staticmethod
    def solve(board: Game) -> List[Tuple[str, Optional[Direction]]]:
        """
        Solve the game automatically.
        Returns list of actions to complete the game.

        Strategy:
        1. Collect flowers (navigate adjacent, pick)
        2. Deliver to princess when full or no more flowers
        3. Clean obstacles if blocking path
        4. Drop-clean-repick if stuck with flowers
        """

    @staticmethod
    def _find_path(board: Game, start: Position, end: Position) -> List[Position]:
        """BFS pathfinding between two positions."""
```

### 2. Application Layer (Use Cases)

Each use case follows the **Command/Query pattern**:

```python
@dataclass
class CreateGameCommand:
    """Input data for creating a game."""
    rows: int
    cols: int
    name: str = ""

@dataclass
class CreateGameResult:
    """Output data from creating a game."""
    game_id: str
    board: Board
    robot: Robot
    princess: Princess
    flowers: Set[Position]
    obstacles: Set[Position]
    status: str
    message: str
    created_at: datetime
    updated_at: datetime

class CreateGameUseCase:
    """Use case for creating a new game."""

    def __init__(self, repository: GameRepository):
        self.repository = repository

    def execute(self, command: CreateGameCommand) -> CreateGameResult:
        """Execute the use case and return result."""
        # 1. Validate input
        # 2. Create game entities
        # 3. Save to repository
        # 4. Return result
```

**Available Use Cases:**
- `CreateGameUseCase` - Initialize a new game
- `GetGameStateUseCase` - Retrieve current game state
- `GetGameHistoryUseCase` - Retrieve action history
- `GetGamesUseCase` - List all games
- `MoveRobotUseCase` - Move robot action
- `RotateRobotUseCase` - Rotate robot action
- `PickFlowerUseCase` - Pick flower action
- `DropFlowerUseCase` - Drop flower action
- `GiveFlowersUseCase` - Give flowers action
- `CleanObstacleUseCase` - Clean obstacle action
- `AutoplayUseCase` - AI solve game

### 3. Infrastructure Layer

#### Driven Adapters (Persistence)

**InMemoryGameRepository**
```python
class InMemoryGameRepository(GameRepository):
    """
    In-memory implementation of game repository.
    Suitable for development and testing.
    """

    def __init__(self):
        self._games: Dict[str, Game] = {}
        self._histories: Dict[str, GameHistory] = {}

    def save(self, game_id: str, game: Game) -> None:
        """Save game state."""

    def get(self, game_id: str) -> Optional[Game]:
        """Retrieve game by ID."""

    def get_all(self) -> List[Tuple[str, Game]]:
        """Retrieve all games."""

    def save_history(self, game_id: str, history: GameHistory) -> None:
        """Save game history."""

    def get_history(self, game_id: str) -> Optional[GameHistory]:
        """Retrieve game history."""
```

#### Driver Adapters (API)

**FastAPI Router**
```python
router = APIRouter(prefix="/api/games", tags=["games"])

@router.post("/", response_model=GameStateResponse, status_code=201)
def create_game(
    request: CreateGameRequest,
    repository: GameRepository = Depends(get_game_repository),
) -> GameStateResponse:
    """Create a new game."""
    use_case = CreateGameUseCase(repository)
    result = use_case.execute(CreateGameCommand(**request.dict()))
    return GameStateResponse(...)

@router.post("/{game_id}/action", response_model=ActionResponse)
def perform_action(
    game_id: str,
    request: ActionRequest,
    repository: GameRepository = Depends(get_game_repository),
) -> ActionResponse:
    """Perform a game action."""
    # Route to appropriate use case based on action type
```

**Pydantic Schemas**
```python
class CreateGameRequest(BaseModel):
    """Request schema for creating a game."""
    rows: int = Field(ge=3, le=50)
    cols: int = Field(ge=3, le=50)
    name: str = Field(default="")

class GameStateResponse(BaseModel):
    """Response schema for game state."""
    id: str
    status: str
    board: dict
    robot: dict
    princess: dict
    obstacles: dict
    flowers: dict
    created_at: str
    updated_at: str
```

---

## Design Patterns

### 1. Repository Pattern

**Purpose**: Abstract data access logic from business logic.

```python
# Port (Interface)
class GameRepository(ABC):
    @abstractmethod
    def save(self, game_id: str, game: Game) -> None:
        pass

    @abstractmethod
    def get(self, game_id: str) -> Optional[Game]:
        pass

# Adapter (Implementation)
class InMemoryGameRepository(GameRepository):
    def save(self, game_id: str, game: Game) -> None:
        self._games[game_id] = game
```

**Benefits:**
- Easy to swap implementations (in-memory → PostgreSQL)
- Testable with mock repositories
- Business logic doesn't depend on persistence details

### 2. Dependency Injection

**Purpose**: Inject dependencies rather than hardcoding them.

```python
# Dependencies module
def get_game_repository() -> GameRepository:
    return InMemoryGameRepository()

# FastAPI automatic injection
@router.post("/")
def create_game(repository: GameRepository = Depends(get_game_repository)):
    use_case = CreateGameUseCase(repository)
    # ...
```

**Benefits:**
- Easy to override for testing
- Loose coupling
- Configuration in one place

### 3. Command/Query Separation (CQS)

**Purpose**: Separate read operations (queries) from write operations (commands).

```python
# Command (modifies state)
class CreateGameCommand:
    rows: int
    cols: int

# Query (reads state)
class GetGameStateQuery:
    game_id: str
```

**Benefits:**
- Clear intent (read vs write)
- Easier to optimize (caching queries)
- Supports CQRS if needed later

### 4. Value Object Pattern

**Purpose**: Represent concepts with no identity, defined by their values.

```python
@dataclass(frozen=True)
class Position:
    row: int
    col: int
    # Immutable, equality by value
```

**Benefits:**
- Immutability prevents bugs
- Type safety (can't mix up row/col with plain ints)
- Self-validating

### 5. Aggregate Pattern

**Purpose**: Ensure consistency within a cluster of related objects.

```python
class Game:  # Aggregate Root
    # All modifications to Robot, Princess go through Game
    # Game enforces invariants
```

**Benefits:**
- Clear transaction boundaries
- Consistency guarantees
- Encapsulation

---

## Data Flow

### Request Flow Example: Moving the Robot

```
1. HTTP Request
   POST /api/games/abc123/action
   Body: { "action": "move", "direction": "east" }

   ↓

2. FastAPI Router (game_router.py)
   - Validates request with Pydantic schema
   - Extracts game_id and action
   - Injects GameRepository dependency

   ↓

3. Use Case (move_robot.py)
   - MoveRobotUseCase.execute(MoveRobotCommand)
   - Retrieves Game from repository
   - Validates action is allowed

   ↓

4. Domain Service (game_service.py)
   - GameService.move_robot(game)
   - Calculates new position
   - Updates game state

   ↓

5. Domain Entity (game.py, robot.py)
   - Game validates position
   - Robot updates position
   - Game checks win condition

   ↓

6. Repository (in_memory_game_repository.py)
   - Saves updated game state
   - Saves action to history

   ↓

7. Use Case Returns Result
   - MoveRobotResult with updated state

   ↓

8. Router Serializes Response
   - Converts entities to dicts
   - Pydantic validates response schema
   - Returns JSON to client
```

### State Management

**Game State** is stored in-memory:
```
InMemoryGameRepository
├── _games: Dict[str, Game]
│   └── "abc123" → Game(...)
└── _histories: Dict[str, GameHistory]
    └── "abc123" → GameHistory(actions=[...])
```

**State Transitions:**
```
IN_PROGRESS → WON     (all flowers delivered)
IN_PROGRESS → LOST    (invalid action attempted)
```

---

## Key Design Decisions

### 1. Why Hexagonal Architecture?

**Decision**: Use Hexagonal Architecture instead of traditional layered architecture.

**Rationale:**
- ✅ **Testability**: Domain logic can be tested without FastAPI or database
- ✅ **Flexibility**: Easy to add new adapters (e.g., GraphQL, gRPC)
- ✅ **Maintainability**: Clear boundaries and responsibilities
- ✅ **Business Focus**: Domain logic is isolated and protected

**Trade-offs:**
- ❌ More upfront structure
- ❌ Requires discipline to maintain boundaries
- ✅ Worth it for maintainability and testability

### 2. Why In-Memory Repository?

**Decision**: Use in-memory storage instead of database.

**Rationale:**
- ✅ **Simplicity**: No database setup required
- ✅ **Fast**: No network I/O
- ✅ **Sufficient**: Games are short-lived
- ✅ **Easy to Test**: No database fixtures needed

**Trade-offs:**
- ❌ Data lost on restart
- ❌ Not suitable for production at scale
- ✅ Easy to replace with PostgreSQL/Redis later

### 3. Why Domain-Driven Design?

**Decision**: Apply DDD tactical patterns (entities, value objects, aggregates).

**Rationale:**
- ✅ **Rich Domain Model**: Game logic is complex, benefits from rich model
- ✅ **Encapsulation**: Business rules enforced by entities
- ✅ **Ubiquitous Language**: Team speaks same language as code
- ✅ **Maintainability**: Domain model is clear and expressive

**Trade-offs:**
- ❌ More classes and files
- ❌ Steeper learning curve
- ✅ Worth it for complex business logic

### 4. Why FastAPI?

**Decision**: Use FastAPI instead of Flask/Django.

**Rationale:**
- ✅ **Performance**: ASGI-based, high performance
- ✅ **Type Safety**: Pydantic integration for validation
- ✅ **Documentation**: Auto-generated OpenAPI docs
- ✅ **Modern**: Async support, Python 3.7+ features
- ✅ **Testing**: Built-in TestClient

**Trade-offs:**
- ❌ Smaller ecosystem than Flask
- ✅ Best choice for modern Python APIs

### 5. Why Separate Board from Game?

**Decision**: Extract `Board` as a separate entity from `Game`.

**Rationale:**
- ✅ **Separation of Concerns**: Board handles grid logic, Game handles game logic
- ✅ **Single Responsibility**: Board represents grid state only
- ✅ **Reusability**: Board can be serialized independently
- ✅ **Clarity**: Clearer distinction between grid and game rules

**Trade-offs:**
- ❌ More entities to manage
- ✅ Better organization and maintainability

### 6. Why Three Test Levels?

**Decision**: Unit, Integration, Feature-Component tests.

**Rationale:**
- ✅ **Unit**: Fast, isolated, test domain logic
- ✅ **Integration**: Test API contracts and layer interactions
- ✅ **Feature-Component**: Test complex end-to-end scenarios
- ✅ **Balance**: Right mix of speed, coverage, confidence

**Trade-offs:**
- ❌ More test infrastructure
- ✅ Comprehensive coverage and confidence

### 7. Why Dataclasses Over Regular Classes?

**Decision**: Use `@dataclass` for entities and value objects.

**Rationale:**
- ✅ **Boilerplate Reduction**: Auto-generates `__init__`, `__repr__`, `__eq__`
- ✅ **Type Hints**: Enforces type annotations
- ✅ **Immutability Option**: `frozen=True` for value objects
- ✅ **Standard Library**: No external dependency

**Trade-offs:**
- ❌ Less control over initialization
- ✅ Clean, readable code

---

## Future Enhancements

### Scalability

1. **Replace In-Memory Repository**
   - Add PostgreSQL adapter
   - Add Redis caching layer
   - Keep GameRepository interface unchanged

2. **Add Event Sourcing**
   - Store all actions as events
   - Rebuild state from event stream
   - Enable time-travel debugging

3. **Add CQRS**
   - Separate read and write models
   - Optimize queries with materialized views
   - Scale reads independently

### Features

1. **Multiplayer Support**
   - Add WebSocket support
   - Implement turn-based mechanics
   - Add player authentication

2. **Leaderboard**
   - Track solve times
   - Rank players by efficiency
   - Add achievements

3. **Custom Levels**
   - Level editor API
   - Save/load custom boards
   - Share levels between players

### Technical Improvements

1. **Observability**
   - Add structured logging
   - Add metrics (Prometheus)
   - Add distributed tracing (OpenTelemetry)

2. **API Versioning**
   - Add `/api/v1/`, `/api/v2/` prefixes
   - Support multiple API versions

3. **Rate Limiting**
   - Add rate limiting middleware
   - Prevent abuse

---

## References

- [Hexagonal Architecture (Alistair Cockburn)](https://alistair.cockburn.us/hexagonal-architecture/)
- [Domain-Driven Design (Eric Evans)](https://www.domainlanguage.com/ddd/)
- [Clean Architecture (Robert C. Martin)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Python Dataclasses](https://docs.python.org/3/library/dataclasses.html)

---

## Summary

This architecture provides:
- ✅ **Clean Separation**: Domain, Application, Infrastructure layers
- ✅ **Testability**: Easy to test at all levels
- ✅ **Maintainability**: Clear boundaries and responsibilities
- ✅ **Flexibility**: Easy to swap implementations
- ✅ **Scalability**: Ready for future enhancements
- ✅ **Type Safety**: Pydantic and type hints throughout
- ✅ **Best Practices**: DDD, Hexagonal Architecture, SOLID principles

The architecture is production-ready and suitable for complex business logic while remaining simple enough for a small team to maintain.
