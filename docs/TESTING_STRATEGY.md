# Testing Strategy

> **🎯 Purpose**: Practical guide for **writing, running, and debugging tests**
>
> This document is your go-to resource when you need to:
> - ✅ Write a new test (with code examples)
> - ✅ Run tests locally or in CI/CD
> - ✅ Debug failing tests
> - ✅ Configure coverage
> - ✅ Follow best practices
>
> 📖 **Looking for test analysis and inventory?** See [TESTING_GUIDE.md](TESTING_GUIDE.md) for:
> - Comprehensive analysis of all 50 tests (intention, purpose, benefits)
> - E2E overlap evaluation and recommendations
> - Test metrics and distribution by hexagon
> - When to write each type of test

---

## Table of Contents
- [Overview](#overview)
- [Test Suite Structure](#test-suite-structure)
- [Test Types](#test-types)
  - [Unit Tests](#unit-tests)
  - [Integration Tests](#integration-tests)
  - [Feature-Component Tests](#feature-component-tests)
- [Best Practices](#best-practices)
- [Running Tests](#running-tests)
- [CI/CD Integration](#cicd-integration)
- [Coverage Requirements](#coverage-requirements)
- [Troubleshooting](#troubleshooting)

---

## Overview

**Quick Stats**: 50 tests | ~0.3s execution | 90%+ coverage

We use a **three-tier testing approach**:
- 32 unit tests (64%) - Domain logic
- 11 integration tests (22%) - API endpoints
- 7 feature-component tests (14%) - E2E workflows

> 💡 For detailed test analysis and methodology, see [TESTING_GUIDE.md](TESTING_GUIDE.md)

---

## Test Suite Structure

```
tests/
├── unit/                           # Unit tests (domain & application logic)
│   ├── domain/
│   │   ├── test_game.py           # Game entity tests
│   │   ├── test_position.py       # Position value object tests
│   │   ├── test_direction.py      # Direction enum tests
│   │   └── test_game_solver_player.py  # AI solver tests
│   └── application/
│       └── test_game_service.py   # Game service tests
├── integration/                    # Integration tests (API endpoints)
│   ├── test_root_endpoint.py      # Root & health check endpoints
│   ├── test_create_game.py        # POST /api/games/
│   ├── test_get_game_state.py     # GET /api/games/{id}
│   ├── test_action_endpoint.py    # POST /api/games/{id}/action
│   ├── test_get_game_history.py   # GET /api/games/{id}/history
│   └── test_autoplay_endpoint.py  # POST /api/games/{id}/autoplay
├── feature-component/              # Feature-component tests (end-to-end)
│   └── test_autoplay_end_to_end.py  # Complete autoplay scenarios
└── conftest.py                     # Shared fixtures and configuration
```

---

## Test Types

> 💡 **For detailed test analysis** (intention, purpose, benefits), see [Unit Tests](TESTING_GUIDE.md#unit-tests) in TESTING_GUIDE.md

### Unit Tests

**Quick Tips**:
- Fast (< 1ms) | Isolated | No external dependencies
- Use AAA pattern: Arrange → Act → Assert
- Test behavior, not implementation

**Example: Testing a Domain Entity**

```python
# tests/unit/domain/test_robot.py

from src.hexagons.game.domain.core.entities.robot import Robot
from src.hexagons.game.domain.core.value_objects.position import Position
from src.hexagons.game.domain.core.value_objects.direction import Direction


def test_robot_initialization():
    """Test robot is created with correct default values."""
    robot = Robot(position=Position(0, 0))

    assert robot.position == Position(0, 0)
    assert robot.orientation == Direction.NORTH
    assert robot.flowers_held == 0
    assert robot.max_flowers == 12
    assert len(robot.flowers_collected) == 0


def test_robot_pick_flower():
    """Test robot can pick a flower."""
    robot = Robot(position=Position(1, 2))

    robot.pick_flower()

    assert robot.flowers_held == 1
    assert len(robot.flowers_collected) == 1
    assert robot.flowers_collected[0]["position"]["row"] == 1
    assert robot.flowers_collected[0]["position"]["col"] == 2


def test_robot_give_flowers():
    """Test robot correctly gives flowers and updates delivered list."""
    robot = Robot(position=Position(0, 0))
    robot.pick_flower()
    robot.pick_flower()

    princess_pos = Position(0, 1)
    delivered = robot.give_flowers(princess_pos)

    assert delivered == 2
    assert robot.flowers_held == 0
    # Verify one entry per flower delivered
    assert len(robot.flowers_delivered) == 2
    assert all(
        entry["position"]["row"] == princess_pos.row
        and entry["position"]["col"] == princess_pos.col
        for entry in robot.flowers_delivered
    )


def test_robot_cannot_pick_when_full():
    """Test robot cannot pick flowers beyond max capacity."""
    robot = Robot(position=Position(0, 0), max_flowers=2)

    robot.pick_flower()
    robot.pick_flower()

    assert not robot.can_pick()
    assert robot.flowers_held == 2
```

---

### Integration Tests

**Quick Tips**:
- Use `TestClient` from FastAPI | Test HTTP contracts
- Verify status codes, response schemas, error handling
- Use fixtures for seeded test data

**Example: Testing an API Endpoint**

```python
# tests/integration/test_action_endpoint.py

import pytest
from src.hexagons.game.domain.core.entities.game import Game
from src.hexagons.game.domain.core.entities.robot import Robot
from src.hexagons.game.domain.core.entities.princess import Princess
from src.hexagons.game.domain.core.value_objects.position import Position
from src.hexagons.game.domain.core.value_objects.direction import Direction


@pytest.fixture
def seeded_board(game_repository):
    """Create a game with predefined state for testing."""
    def _seed(game_id: str = "test-game"):
        board = Game(
            rows=5,
            cols=5,
            robot=Robot(position=Position(0, 0), orientation=Direction.NORTH),
            princess=Princess(position=Position(2, 2)),
            flowers=set(),
            obstacles=set()
        )
        game_repository.save(game_id, board)
        return game_id, board
    return _seed


def test_rotate_changes_orientation(client, seeded_board):
    """Test that rotating the robot changes its orientation."""
    game_id, _ = seeded_board("rotate-test")

    # Act: Rotate robot to EAST
    resp = client.post(
        f"/api/games/{game_id}/action",
        json={"action": "rotate", "direction": "east"}
    )

    # Assert: Response is successful
    assert resp.status_code == 200
    data = resp.json()

    assert data["success"] is True
    assert data["robot"]["orientation"] == "east"


def test_robot_move(client, seeded_board):
    """Test that robot can move in a direction."""
    game_id, _ = seeded_board("move-test")

    # First, face EAST
    client.post(
        f"/api/games/{game_id}/action",
        json={"action": "rotate", "direction": "east"}
    )

    # Then move
    resp = client.post(
        f"/api/games/{game_id}/action",
        json={"action": "move"}
    )

    assert resp.status_code == 200
    data = resp.json()

    assert data["success"] is True
    assert data["robot"]["position"]["row"] == 0
    assert data["robot"]["position"]["col"] == 1  # Moved one cell east


def test_invalid_direction_payload(client, seeded_board):
    """Test that invalid direction values are rejected with proper error."""
    game_id, _ = seeded_board("invalid-dir")

    # Send an invalid direction value
    resp = client.post(
        f"/api/games/{game_id}/action",
        json={"action": "move", "direction": "upwards"}
    )

    assert resp.status_code == 422
    assert "detail" in resp.json()

    # Pydantic v2 returns detailed error messages
    error_detail = resp.json()["detail"][0]
    error_msg = error_detail["msg"]

    # Check that error mentions valid directions
    assert "north" in error_msg.lower() and "south" in error_msg.lower()
    assert error_detail["type"] == "literal_error"
```

---

### Feature-Component Tests

**Quick Tips**:
- Test complete workflows | Validate state transitions
- Focus on business-critical features (e.g., AI autoplay)
- Test realistic scenarios with obstacles, multiple flowers

**Example: Testing Autoplay Feature**

```python
# tests/feature-component/test_autoplay_end_to_end.py

import pytest
from src.hexagons.game.domain.core.entities.game import Game
from src.hexagons.game.domain.core.entities.robot import Robot
from src.hexagons.game.domain.core.entities.princess import Princess
from src.hexagons.game.domain.core.value_objects.position import Position
from src.hexagons.game.domain.core.value_objects.direction import Direction
from src.hexagons.game.domain.use_cases.autoplay import AutoplayUseCase
from src.hexagons.game.domain.core.entities.game_history import GameHistory


def test_autoplay_normal_delivery_clear_path():
    """
    Test autoplay successfully delivers flowers when path is clear.

    Scenario:
    - Robot at (0,0), Princess at (2,2)
    - Flower at (1,1)
    - Clear path to flower and princess

    Expected:
    - Robot picks flower
    - Robot navigates to princess
    - Robot delivers flower
    - Game completes successfully
    """
    # Arrange
    robot = Robot(position=Position(0, 0), orientation=Direction.NORTH)
    princess = Princess(position=Position(2, 2))
    flowers = {Position(1, 1)}

    board = Game(
        rows=3,
        cols=3,
        robot=robot,
        princess=princess,
        flowers=flowers,
        obstacles=set()
    )
    history = GameHistory()

    # Act
    result = AutoplayUseCase.execute(board, history)

    # Assert
    assert result.success is True
    assert len(board.flowers) == 0  # All flowers collected
    assert board.robot.flowers_held == 0  # All flowers delivered
    assert princess.flowers_received == 1
    assert len(history.actions) > 0  # Actions were recorded


def test_autoplay_blocked_path_drop_and_clean():
    """
    Test autoplay handles obstacle blocking path to princess.

    Scenario:
    - Robot at (0,0), Princess at (2,0)
    - Flower at (0,1)
    - Obstacle at (1,0) blocking direct path

    Strategy:
    - Robot picks flower at (0,1)
    - Robot cannot reach princess due to obstacle
    - Robot drops flower temporarily
    - Robot cleans obstacle at (1,0)
    - Robot picks flower back up
    - Robot delivers to princess

    Expected:
    - Robot successfully completes delivery
    - Uses drop-clean-repick strategy
    """
    # Arrange
    robot = Robot(position=Position(0, 0), orientation=Direction.NORTH, max_flowers=1)
    princess = Princess(position=Position(2, 0))
    flowers = {Position(0, 1)}
    obstacles = {Position(1, 0)}  # Blocks direct path

    board = Game(
        rows=3,
        cols=3,
        robot=robot,
        princess=princess,
        flowers=flowers,
        obstacles=obstacles
    )
    history = GameHistory()

    # Act
    result = AutoplayUseCase.execute(board, history)

    # Assert
    assert result.success is True
    assert len(board.flowers) == 0  # Flower collected
    assert board.robot.flowers_held == 0  # Flower delivered
    assert princess.flowers_received == 1

    # Verify obstacle was cleaned
    assert Position(1, 0) not in board.obstacles

    # Verify drop and clean actions occurred
    action_types = [action.action_type.value for action in history.actions]
    assert "drop" in action_types
    assert "clean" in action_types


def test_autoplay_multiple_flowers_with_obstacles():
    """
    Test autoplay handles multiple flowers with obstacles in the way.

    Scenario:
    - Robot at (0,0), Princess at (4,4)
    - Multiple flowers scattered across board
    - Obstacles blocking some paths

    Expected:
    - Robot picks multiple flowers
    - Robot cleans obstacles as needed
    - Robot makes multiple delivery trips if needed
    - All flowers delivered successfully
    """
    # Arrange
    robot = Robot(position=Position(0, 0), orientation=Direction.NORTH, max_flowers=2)
    princess = Princess(position=Position(4, 4))
    flowers = {Position(1, 0), Position(0, 2), Position(3, 3)}
    obstacles = {Position(2, 0), Position(1, 2)}

    board = Game(
        rows=5,
        cols=5,
        robot=robot,
        princess=princess,
        flowers=flowers,
        obstacles=obstacles
    )
    history = GameHistory()

    # Act
    result = AutoplayUseCase.execute(board, history)

    # Assert
    assert result.success is True
    assert len(board.flowers) == 0  # All flowers collected
    assert board.robot.flowers_held == 0  # All flowers delivered
    assert princess.flowers_received == 3

    # Verify some obstacles were cleaned if needed
    assert len(board.obstacles) <= 2  # At most, some obstacles cleaned
```

---

## Best Practices

> 💡 **For test analysis and when to write each type**, see [Test Decision Guide](TESTING_GUIDE.md#when-to-write-each-type-of-test) in TESTING_GUIDE.md

### General Testing Principles

1. **Test Naming Convention**
   ```python
   def test_<feature>_<scenario>_<expected_outcome>():
       """Docstring explaining the test scenario."""
       pass
   ```

2. **AAA Pattern** (Arrange-Act-Assert)
   ```python
   def test_robot_move():
       # Arrange: Set up test data
       robot = Robot(position=Position(0, 0))

       # Act: Perform the action
       robot.move(Direction.EAST)

       # Assert: Verify the outcome
       assert robot.position == Position(0, 1)
   ```

3. **Test Isolation**
   - Each test should be independent
   - Use fixtures to reset state
   - Avoid shared mutable state
   - Clean up after tests

4. **Fixture Organization**
   ```python
   # conftest.py - Shared fixtures
   @pytest.fixture
   def game_repository():
       """Provide a clean game repository for each test."""
       return InMemoryGameRepository()

   @pytest.fixture
   def client(game_repository):
       """Provide a FastAPI test client."""
       from src.hexagons.game.driver.bff.app import app
       from src.hexagons.game.driver.bff.dependencies import get_game_repository

       app.dependency_overrides[get_game_repository] = lambda: game_repository
       return TestClient(app)
   ```

5. **Parametrized Tests**
   ```python
   @pytest.mark.parametrize("direction,expected_row,expected_col", [
       (Direction.NORTH, -1, 0),
       (Direction.SOUTH, 1, 0),
       (Direction.EAST, 0, 1),
       (Direction.WEST, 0, -1),
   ])
   def test_direction_deltas(direction, expected_row, expected_col):
       row, col = direction.get_delta()
       assert row == expected_row
       assert col == expected_col
   ```

### Coverage Guidelines

- **Target**: 80%+ overall coverage
- **Critical paths**: 100% coverage (game logic, AI solver)
- **Unit tests**: Aim for 90%+ domain coverage
- **Integration tests**: Cover all API endpoints
- **Feature-component tests**: Cover critical user flows

### What NOT to Test

- ❌ Third-party library internals
- ❌ Python standard library
- ❌ FastAPI framework behavior
- ❌ Pydantic validation (unless custom)
- ❌ Trivial getters/setters

### What TO Test

- ✅ Business logic
- ✅ Domain rules and invariants
- ✅ API contracts and error handling
- ✅ State transitions
- ✅ Complex algorithms (AI solver)
- ✅ Edge cases and boundary conditions

---

## Running Tests

### Local Development

**Run all tests:**
```bash
make test-all
```

**Run specific test suites:**
```bash
# Unit tests only
make test-unit

# Integration tests only
make test-integration

# Feature-component tests only
make test-feature-component
```

**Run with coverage:**
```bash
# All tests with coverage
make coverage

# Specific suite with coverage
make coverage-unit
make coverage-integration
make coverage-feature-component

# Combine coverage from all suites
make coverage-combine
```

**Run specific test file:**
```bash
poetry run pytest tests/unit/domain/test_game.py -v
```

**Run specific test function:**
```bash
poetry run pytest tests/unit/domain/test_game.py::test_game_initialization -v
```

**Run with verbose output and show print statements:**
```bash
poetry run pytest tests/ -v -s
```

**Run failed tests only:**
```bash
poetry run pytest --lf
```

### Makefile Targets

| Target | Description |
|--------|-------------|
| `test-unit` | Run unit tests |
| `test-integration` | Run integration tests |
| `test-feature-component` | Run feature-component tests |
| `test-all` | Run all test suites |
| `coverage-unit` | Run unit tests with coverage |
| `coverage-integration` | Run integration tests with coverage |
| `coverage-feature-component` | Run feature-component tests with coverage |
| `coverage` | Run all tests with coverage |
| `coverage-combine` | Combine coverage from all suites |
| `coverage-html` | Generate HTML coverage report |
| `coverage-xml` | Generate XML coverage report (for CI) |

---

## CI/CD Integration

### GitHub Actions Workflow

The project uses **parallel test execution** in CI with separate jobs for each test suite.

**Workflow Structure:**
```yaml
# .github/workflows/ci.yml

jobs:
  unit:
    name: Unit Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run unit tests
        run: |
          COVERAGE_FILE=.coverage/.coverage.unit poetry run pytest tests/unit/ \
            --cov=src \
            --cov-report=term-missing \
            --cov-report=xml:.coverage/coverage-unit.xml
      - name: Upload coverage artifact
        uses: actions/upload-artifact@v5
        with:
          name: coverage-unit
          path: .coverage/

  integration:
    name: Integration Tests
    # Similar structure for integration tests

  feature-component:
    name: Feature-Component Tests
    # Similar structure for feature-component tests

  coverage_quality:
    name: Coverage Quality Check
    needs: [unit, integration, feature-component]
    runs-on: ubuntu-latest
    steps:
      - name: Download all coverage artifacts
        uses: actions/download-artifact@v5
        with:
          path: coverage-artifacts

      - name: Merge coverage data
        run: |
          mkdir -p coverage
          cp coverage-artifacts/coverage-unit/.coverage.unit coverage/
          cp coverage-artifacts/coverage-integration/.coverage.integration coverage/
          cp coverage-artifacts/coverage-feature-component/.coverage.feature-component coverage/

          COVERAGE_FILE=.coverage/.coverage.combined \
            poetry run coverage combine coverage/.coverage.*

      - name: Generate reports
        run: |
          poetry run coverage report --fail-under=80
          poetry run coverage html
```

### Coverage File Management

**Important**: The project uses a specific coverage file structure to avoid permission errors:

```
.coverage/
├── .coverage.unit
├── .coverage.integration
├── .coverage.feature-component
└── .coverage.combined
```

**Environment Variable:**
```bash
COVERAGE_FILE=.coverage/.coverage.<test-type>
```

This structure ensures:
- ✅ No conflicts between test runs
- ✅ Proper artifact handling in CI
- ✅ Clean merging of coverage data
- ✅ No permission errors

### CI Environment Variables

Set these in GitHub Actions:
```yaml
env:
  PYTHON_VERSION: "3.11"
  POETRY_VERSION: "1.7.1"
  COVERAGE_FILE: .coverage/.coverage.<type>
```

### Pull Request Checks

CI runs the following checks on every PR:
1. ✅ All unit tests pass
2. ✅ All integration tests pass
3. ✅ All feature-component tests pass
4. ✅ Code coverage ≥ 80%
5. ✅ No linting errors
6. ✅ Code formatting (Black, isort)

---

## Coverage Requirements

### Coverage Targets

| Test Suite | Target | Critical Paths |
|------------|--------|----------------|
| Unit | 90%+ | 100% |
| Integration | 85%+ | 100% (all endpoints) |
| Feature-Component | N/A | All critical flows |
| **Overall** | **80%+** | **100%** |

### Critical Paths Requiring 100% Coverage

1. **Game Logic** (`src/hexagons/game/domain/core/entities/game.py`)
   - Cell validation
   - Move validation
   - Flower/obstacle management

2. **Robot Entity** (`src/hexagons/game/domain/core/entities/robot.py`)
   - Flower collection/delivery
   - Movement and rotation
   - State tracking

3. **AI Solver** (`src/hexagons/game/domain/core/entities/game_solver_player.py`)
   - Pathfinding logic
   - Obstacle handling
   - Delivery strategy

4. **Use Cases** (`src/hexagons/game/domain/use_cases/`)
   - All business operations
   - Error handling
   - State transitions

### Viewing Coverage Reports

**Terminal Output:**
```bash
make coverage
# Shows coverage percentages and missing lines
```

**HTML Report:**
```bash
make coverage-html
open htmlcov/index.html
```

**Coverage Report Example:**
```
Name                                                    Stmts   Miss  Cover   Missing
-------------------------------------------------------------------------------------
src/hexagons/game/domain/core/entities/game.py    127      5    96%   45-47
src/hexagons/game/domain/core/entities/robot.py    89      2    98%   78-79
-------------------------------------------------------------------------------------
TOTAL                                                    1842    147    92%
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Permission Error on Coverage Files

**Error:**
```
PermissionError: [Errno 1] Operation not permitted: '.coverage'
```

**Solution:**
Set explicit `COVERAGE_FILE` environment variable:
```bash
COVERAGE_FILE=.coverage/.coverage.combined make coverage-combine
```

Or update `Makefile`:
```makefile
coverage-combine:
	COVERAGE_FILE=.coverage/.coverage.combined \
		poetry run coverage combine .coverage/.coverage.*
```

---

#### 2. Coverage Artifacts Not Found in CI

**Error:**
```
cp: cannot stat 'coverage-artifacts/coverage/.coverage.*': No such file or directory
```

**Solution:**
Adjust paths in CI workflow - `actions/download-artifact@v5` creates subdirectories:
```yaml
- name: Merge coverage data
  run: |
    mkdir -p coverage
    cp coverage-artifacts/coverage-unit/.coverage.unit coverage/
    cp coverage-artifacts/coverage-integration/.coverage.integration coverage/
    cp coverage-artifacts/coverage-feature-component/.coverage.feature-component coverage/
```

---

#### 3. Pydantic v2 Validation Errors in Tests

**Error:**
```python
assert error_detail["type"] == "value_error.enum"  # Old Pydantic v1 format
# AssertionError: 'literal_error' != 'value_error.enum'
```

**Solution:**
Update assertions for Pydantic v2 error format:
```python
error_detail = resp.json()["detail"][0]
assert error_detail["type"] == "literal_error"  # Pydantic v2 format
assert "north" in error_detail["msg"].lower()
```

---

#### 4. Test Isolation Issues

**Problem:** Tests pass individually but fail when run together.

**Solution:**
1. Check for shared state:
   ```python
   # BAD: Shared mutable state
   SHARED_CACHE = {}

   # GOOD: Use fixtures
   @pytest.fixture
   def cache():
       return {}
   ```

2. Use proper fixture scope:
   ```python
   @pytest.fixture(scope="function")  # New instance per test
   def game_repository():
       return InMemoryGameRepository()
   ```

3. Clean up after tests:
   ```python
   @pytest.fixture
   def temp_file():
       file_path = "temp.txt"
       yield file_path
       if os.path.exists(file_path):
           os.remove(file_path)
   ```

---

#### 5. Autoplay Solver Tests Timing Out

**Problem:** Solver tests take too long or hang indefinitely.

**Solution:**
1. Add `max_iterations` to solver:
   ```python
   iteration = 0
   max_iterations = 1000
   while condition and iteration < max_iterations:
       iteration += 1
       # ... solver logic
   ```

2. Use timeout in pytest:
   ```python
   @pytest.mark.timeout(5)  # 5 seconds max
   def test_autoplay_complex_scenario():
       pass
   ```

---

#### 6. Import Errors in Tests

**Error:**
```
ModuleNotFoundError: No module named 'src'
```

**Solution:**
Ensure proper Python path in `conftest.py`:
```python
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
```

---

#### 7. Fixture Not Found

**Error:**
```
fixture 'game_repository' not found
```

**Solution:**
1. Check fixture is defined in `conftest.py` or imported
2. Verify fixture scope matches test needs
3. Check for typos in fixture name
4. Ensure `conftest.py` is in the correct directory

---

#### 8. Coverage Not Combining

**Problem:** `coverage combine` shows no data or errors.

**Solution:**
1. Verify coverage files exist:
   ```bash
   ls -la .coverage/
   ```

2. Check `COVERAGE_FILE` is set correctly:
   ```bash
   # In each test run
   COVERAGE_FILE=.coverage/.coverage.unit pytest tests/unit/
   ```

3. Use correct pattern for combine:
   ```bash
   poetry run coverage combine .coverage/.coverage.*
   ```

---

#### 9. Test Database State Persisting

**Problem:** Test data from previous runs affecting current tests.

**Solution:**
Use in-memory repository pattern:
```python
class InMemoryGameRepository:
    def __init__(self):
        self._games = {}  # Fresh dictionary each time

    def save(self, game_id: str, game: Game):
        self._games[game_id] = game

    def get(self, game_id: str) -> Game:
        return self._games.get(game_id)
```

---

#### 10. FastAPI TestClient Issues

**Problem:** Dependency injection not working in tests.

**Solution:**
Override dependencies properly:
```python
@pytest.fixture
def client(game_repository):
    from src.hexagons.game.driver.bff.app import app
    from src.hexagons.game.driver.bff.dependencies import get_game_repository

    # Override dependency
    app.dependency_overrides[get_game_repository] = lambda: game_repository

    client = TestClient(app)
    yield client

    # Clean up
    app.dependency_overrides.clear()
```

---

## Additional Resources

### Useful Commands

```bash
# Run tests with coverage and show missing lines
poetry run pytest --cov=src --cov-report=term-missing

# Run tests matching a pattern
poetry run pytest -k "test_robot" -v

# Run tests with markers
poetry run pytest -m "slow" -v

# Show test durations
poetry run pytest --durations=10

# Run tests in parallel (requires pytest-xdist)
poetry run pytest -n auto

# Generate coverage badge
poetry run coverage-badge -o coverage.svg
```

### Pytest Markers

Define custom markers in `pytest.ini`:
```ini
[pytest]
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    feature: marks tests as feature tests
```

Use markers in tests:
```python
@pytest.mark.slow
def test_complex_autoplay_scenario():
    pass
```

### Testing Best Practices Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Testing Strategies by Martin Fowler](https://martinfowler.com/testing/)
- [The Testing Trophy](https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications)

---

## Summary

This document provides practical guidance for writing and running tests. For comprehensive test analysis, metrics, and E2E evaluation, see [TESTING_GUIDE.md](TESTING_GUIDE.md).

**Key Takeaways**:
- ✅ 50 tests running in ~0.3s (32 unit, 11 integration, 7 feature-component)
- ✅ 80%+ coverage requirement enforced in CI/CD
- ✅ Use AAA pattern, descriptive names, and fixtures
- ✅ Keep tests isolated, fast, and focused

**Quick Commands**:
```bash
make test-all          # Run all tests
make coverage          # Run with coverage
make coverage-combine  # Combine coverage reports
```

📖 **Related Documentation**:
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Complete test inventory and analysis
- [CI_CD.md](CI_CD.md) - CI/CD workflow and pipeline
- [COVERAGE.md](COVERAGE.md) - Coverage strategy and tools

Happy testing! 🎉
