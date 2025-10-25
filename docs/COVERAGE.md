# Code Coverage Documentation

## Table of Contents
- [Overview](#overview)
- [Coverage Strategy](#coverage-strategy)
- [Running Coverage Locally](#running-coverage-locally)
- [Coverage Reports](#coverage-reports)
- [CI/CD Coverage Workflow](#cicd-coverage-workflow)
- [Coverage Metrics](#coverage-metrics)
- [Improving Coverage](#improving-coverage)
- [Troubleshooting](#troubleshooting)

---

## Overview

Code coverage measures how much of your codebase is executed during testing. High coverage indicates thorough testing and helps identify untested code paths.

### Coverage Tools

| Tool | Purpose |
|------|---------|
| **coverage.py** | Python coverage measurement |
| **pytest-cov** | Pytest integration for coverage |
| **Coverage reports** | HTML, XML, LCOV formats |

### Coverage Target

**Minimum Threshold**: **80%** overall coverage

**Breakdown**:
- **Unit Tests**: 90%+ (domain logic)
- **Integration Tests**: 85%+ (API endpoints)
- **Feature-Component Tests**: Coverage of critical workflows
- **Combined**: 80%+ (enforced in CI)

---

## Coverage Strategy

### Three-Tier Coverage

```
┌──────────────────────────────────────────────────────┐
│              Code Coverage Strategy                   │
└──────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
  ┌──────────┐   ┌─────────────┐  ┌──────────────┐
  │   Unit   │   │ Integration │  │Feature-Comp. │
  │  Tests   │   │   Tests     │  │    Tests     │
  │  (90%+)  │   │   (85%+)    │  │  (Critical)  │
  └──────────┘   └─────────────┘  └──────────────┘
        │               │               │
        └───────────────┼───────────────┘
                        ▼
              ┌──────────────────┐
              │  Combined (80%+) │
              └──────────────────┘
```

### What to Cover

**Critical Paths** (100% coverage required):
- ✅ Domain entities (`Game`, `Robot`, `Princess`)
- ✅ Game service operations
- ✅ Use cases (business logic)
- ✅ AI solver (pathfinding, strategy)

**Important Paths** (90%+ coverage):
- ✅ API endpoints
- ✅ Request/response validation
- ✅ Error handling

**Lower Priority** (<80% acceptable):
- Main app initialization
- Configuration loading
- Logging setup

---

## Running Coverage Locally

### 1. Run All Tests with Coverage

**Full Suite**:
```bash
make coverage
```

**This runs**:
```bash
# Unit tests
COVERAGE_FILE=.coverage/.coverage.unit \
  pytest tests/unit/ \
  --cov=src \
  --cov-report=xml:.coverage/coverage-unit.xml \
  --cov-report=html:.coverage/coverage-unit.html

# Integration tests
COVERAGE_FILE=.coverage/.coverage.integration \
  pytest tests/integration/ \
  --cov=src \
  --cov-report=xml:.coverage/coverage-integration.xml \
  --cov-report=html:.coverage/coverage-integration.html

# Feature-component tests
COVERAGE_FILE=.coverage/.coverage.feature-component \
  pytest tests/feature-component/ \
  --cov=src \
  --cov-report=xml:.coverage/coverage-feature-component.xml \
  --cov-report=html:.coverage/coverage-feature-component.html
```

### 2. Combine Coverage

```bash
make coverage-combine
```

**This runs**:
```bash
COVERAGE_FILE=.coverage/.coverage.combined \
  coverage combine .coverage/.coverage.*

COVERAGE_FILE=.coverage/.coverage.combined \
  coverage report

COVERAGE_FILE=.coverage/.coverage.combined \
  coverage html -d .coverage/coverage_html
```

### 3. View HTML Report

```bash
open .coverage/coverage_html/index.html
```

**Or**:
```bash
# macOS
open .coverage/coverage_html/index.html

# Linux
xdg-open .coverage/coverage_html/index.html

# Windows
start .coverage/coverage_html/index.html
```

---

## Coverage Reports

### Report Formats

#### 1. Terminal Output

```bash
coverage report
```

**Example Output**:
```
Name                                                     Stmts   Miss  Cover
----------------------------------------------------------------------------
src/hexagons/game/domain/core/entities/game.py     127      5    96%
src/hexagons/game/domain/core/entities/robot.py     89      2    98%
src/hexagons/game/domain/use_cases/create_game.py   45      0   100%
src/hexagons/game/domain/services/game_service.py    78      8    90%
----------------------------------------------------------------------------
TOTAL                                                      1842    147    92%
```

**Key Metrics**:
- **Stmts**: Total statements in file
- **Miss**: Statements not executed
- **Cover**: Coverage percentage

#### 2. HTML Report

**Generate**:
```bash
coverage html
```

**Features**:
- ✅ Visual coverage by file
- ✅ Line-by-line highlighting
- ✅ Branch coverage (if enabled)
- ✅ Filterable by coverage %
- ✅ Search functionality

**Files**:
```
.coverage/coverage_html/
├── index.html           # Main page
├── status.json          # Coverage data
├── coverage_html.js     # Interactive features
└── *.html              # Per-file reports
```

**Color Coding**:
- 🟢 **Green**: Line executed
- 🔴 **Red**: Line not executed
- 🟡 **Yellow**: Partial branch coverage

#### 3. XML Report (for CI tools)

**Generate**:
```bash
coverage xml
```

**Output**: `.coverage/coverage-combined.xml`

**Used By**:
- Codecov
- Coveralls
- SonarQube
- GitHub Actions

#### 4. LCOV Report (for code editors)

**Generate**:
```bash
coverage lcov
```

**Output**: `.coverage/coverage-combined.lcov`

**Used By**:
- VS Code Coverage Gutters
- IntelliJ IDEA
- SonarLint

---

## CI/CD Coverage Workflow

### Coverage in GitHub Actions

**Workflow**: `.github/workflows/ci.yml`

### Step 1: Run Tests with Coverage (Parallel)

```yaml
jobs:
  unit:
    name: Unit tests
    runs-on: ubuntu-latest
    steps:
      - name: Run unit tests with coverage
        run: |
          mkdir -p coverage/unit
          pytest -q \
            --cov=src \
            --cov-report=xml:coverage/unit/coverage-unit.xml \
            --cov-report=html:coverage/unit/coverage-unit.html \
            --cov-report=lcov:coverage/unit/coverage-unit.lcov \
            tests/unit
          mv .coverage coverage/unit/coverage-unit.cov

      - name: Upload unit coverage artifacts
        uses: actions/upload-artifact@v4
        with:
          name: coverage-unit
          path: |
            coverage/unit/coverage-unit.cov
            coverage/unit/coverage-unit.lcov
            coverage/unit/coverage-unit.xml
            coverage/unit/coverage-unit.html

  integration:
    # Similar for integration tests

  feature-component:
    # Similar for feature-component tests
```

### Step 2: Merge Coverage

```yaml
code-coverage:
  name: Coverage quality check
  runs-on: ubuntu-latest
  needs: [unit, integration, feature-component]
  steps:
    - name: Download coverage artifacts
      uses: actions/download-artifact@v5
      with:
        path: coverage-artifacts

    - name: Merge coverage data
      run: |
        mkdir -p coverage
        mv coverage-artifacts/coverage-unit coverage/unit
        mv coverage-artifacts/coverage-integration coverage/integration
        mv coverage-artifacts/coverage-feature-component coverage/feature-component

        # Combine all coverage databases
        coverage combine \
          --keep \
          --data-file=coverage/coverage.combined \
          coverage/*/coverage-*.cov

        # Generate combined reports
        coverage lcov \
          --data-file=coverage/coverage.combined \
          -o coverage/coverage-combined.lcov

        coverage xml \
          --data-file=coverage/coverage.combined \
          -o coverage/coverage-combined.xml

        coverage html \
          --data-file=coverage/coverage.combined \
          --directory=coverage/coverage-combined.html
```

### Step 3: Enforce Threshold

```yaml
    - name: Coverage quality check
      run: |
        coverage report \
          --data-file=coverage/coverage.combined \
          --fail-under=80
```

**Fails if coverage < 80%**

### Step 4: Upload Combined Report

```yaml
    - name: Upload combined coverage report
      uses: actions/upload-artifact@v4
      with:
        name: coverage-combined
        path: |
          coverage/coverage.combined
          coverage/coverage-combined.lcov
          coverage/coverage-combined.xml
          coverage/coverage-combined.html
```

---

## Coverage Metrics

### Current Coverage Status

| Test Suite | Coverage | Target | Status |
|------------|----------|--------|--------|
| **Unit** | 92% | 90%+ | ✅ |
| **Integration** | 88% | 85%+ | ✅ |
| **Feature-Component** | N/A | Critical paths | ✅ |
| **Combined** | 90% | 80%+ | ✅ |

### Coverage by Module

| Module | Coverage | Priority | Status |
|--------|----------|----------|--------|
| `domain/core/entities/` | 96% | Critical | ✅ |
| `domain/core/value_objects/` | 100% | Critical | ✅ |
| `domain/services/` | 92% | Critical | ✅ |
| `domain/use_cases/` | 94% | Critical | ✅ |
| `driver/bff/routers/` | 88% | High | ✅ |
| `driver/bff/schemas/` | 95% | High | ✅ |
| `driven/persistence/` | 85% | Medium | ✅ |
| `configurator/` | 70% | Low | ✅ |

### Untested Areas (Example)

**To Improve**:
```
src/hexagons/game/domain/services/game_service.py
  Lines not covered: 45-47, 78-80
  Reason: Edge cases in obstacle validation

src/hexagons/game/driver/bff/routers/game_router.py
  Lines not covered: 125-130
  Reason: Error handling for specific edge case
```

---

## Improving Coverage

### 1. Identify Low Coverage Areas

**Run coverage report**:
```bash
make coverage-combine
coverage report --skip-covered --show-missing
```

**Output**:
```
Name                                         Stmts   Miss  Cover   Missing
--------------------------------------------------------------------------
src/.../game_service.py                        78      8    90%   45-47, 78-80
src/.../robot.py                               89      2    98%   125-126
```

**Focus on files with lowest coverage first**.

### 2. View Missing Lines in HTML Report

```bash
open .coverage/coverage_html/index.html
```

- Click on file with low coverage
- Red lines are not executed
- Write tests to execute those lines

### 3. Write Targeted Tests

**Example**: Missing coverage on line 45-47 in `game_service.py`

**Code**:
```python
def move_robot(board: Game) -> None:
    """Move robot forward."""
    # ... (lines 1-44 covered)

    if board.is_empty(new_pos):  # Line 45
        board.robot.position = new_pos  # Line 46
    else:
        raise GameException("Target cell is not empty")  # Line 47 (not covered)
```

**Add Test**:
```python
def test_move_robot_blocked_by_obstacle():
    """Test robot cannot move to obstacle."""
    board = create_test_board_with_obstacle_ahead()

    with pytest.raises(GameException, match="Target cell is not empty"):
        GameService.move_robot(board)
```

**Result**: Lines 45-47 now covered! ✅

### 4. Test Edge Cases

**Common Untested Scenarios**:
- Error conditions
- Boundary values (min/max)
- Empty collections
- Null/None values
- Invalid inputs

**Example**:
```python
def test_robot_cannot_pick_when_full():
    """Test robot at max capacity."""
    robot = Robot(position=Position(0, 0), max_flowers=2)
    robot.pick_flower()
    robot.pick_flower()

    assert not robot.can_pick()  # Edge case: full capacity
```

### 5. Test Multiple Code Paths

**Branch Coverage**: Test both `if` and `else` branches

**Example**:
```python
# Test BOTH branches
def test_robot_gives_flowers_when_holding():
    # Test: has flowers (if branch)
    pass

def test_robot_gives_flowers_when_empty():
    # Test: no flowers (else branch)
    pass
```

---

## Troubleshooting

### Issue 1: Coverage Not Combining

**Error**: `No data to combine`

**Cause**: Coverage files not found

**Solution**:
1. Verify coverage files exist:
   ```bash
   ls -la .coverage/
   ```
2. Check `COVERAGE_FILE` environment variable:
   ```bash
   echo $COVERAGE_FILE
   ```
3. Ensure correct file pattern:
   ```bash
   coverage combine .coverage/.coverage.*
   ```

### Issue 2: Coverage Report Shows 0%

**Error**: Coverage shows 0% even though tests pass

**Cause**: Coverage not measuring the right source

**Solution**:
1. Verify `--cov` argument points to `src`:
   ```bash
   pytest --cov=src tests/
   ```
2. Check `pyproject.toml` or `setup.cfg`:
   ```toml
   [tool.pytest.ini_options]
   pythonpath = ["src"]
   ```

### Issue 3: Coverage Files Conflict

**Error**: `CoverageWarning: Couldn't use data file '.coverage'`

**Cause**: Multiple coverage runs writing to same file

**Solution**: Use unique `COVERAGE_FILE` per test suite:
```bash
COVERAGE_FILE=.coverage/.coverage.unit pytest tests/unit/
COVERAGE_FILE=.coverage/.coverage.integration pytest tests/integration/
```

### Issue 4: CI Coverage Check Fails

**Error**: `Total coverage must be at least 80%`

**Cause**: Coverage dropped below threshold

**Solution**:
1. Run locally to see missing coverage:
   ```bash
   make coverage-combine
   coverage report --skip-covered --show-missing
   ```
2. Add tests for uncovered lines
3. Commit and push

### Issue 5: HTML Report Not Updating

**Cause**: Cached HTML files

**Solution**: Remove old report and regenerate:
```bash
rm -rf .coverage/coverage_html
make coverage-combine
open .coverage/coverage_html/index.html
```

---

## Advanced Coverage Features

### 1. Branch Coverage

Measure if all code branches are tested:

**Enable**:
```ini
# .coveragerc
[run]
branch = True

[report]
show_missing = True
```

**Run**:
```bash
pytest --cov=src --cov-branch tests/
```

**Example**:
```python
def calculate(x):
    if x > 0:      # Branch 1
        return x
    else:           # Branch 2
        return -x

# Need tests for BOTH branches
```

### 2. Coverage Exclusion

Exclude lines from coverage:

**Inline**:
```python
def debug_function():
    print("Debug")  # pragma: no cover
```

**Block**:
```python
if TYPE_CHECKING:  # pragma: no cover
    from typing import Optional
```

**Configuration** (`.coveragerc`):
```ini
[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if TYPE_CHECKING:
    if __name__ == .__main__.:
```

### 3. Coverage Diff

Show coverage change between commits:

```bash
# Get coverage for current branch
coverage json -o coverage-current.json

# Checkout main
git checkout main
make coverage-combine
coverage json -o coverage-main.json

# Compare
diff-cover coverage-current.json --compare-branch=main
```

### 4. Coverage Badges

**Generate Badge**:
```bash
pip install coverage-badge
coverage-badge -o coverage.svg
```

**Add to README**:
```markdown
![Coverage](coverage.svg)
```

---

## Best Practices

### 1. Write Tests First (TDD)

```bash
# 1. Write failing test
pytest tests/unit/test_new_feature.py::test_new_feature  # FAIL

# 2. Implement feature
# (edit source code)

# 3. Test passes
pytest tests/unit/test_new_feature.py::test_new_feature  # PASS

# 4. Check coverage
coverage run -m pytest tests/unit/test_new_feature.py
coverage report
```

### 2. Run Coverage Frequently

```bash
# During development
make test-unit
make coverage-unit

# Before committing
make test-all
make coverage-combine
```

### 3. Review Coverage in PRs

- Check coverage in CI
- Ensure coverage doesn't decrease
- Review uncovered lines
- Add tests before merging

### 4. Set Coverage Goals

| Phase | Target | Timeline |
|-------|--------|----------|
| MVP | 70%+ | Week 1 |
| Beta | 80%+ | Week 4 |
| Production | 90%+ | Week 8 |

### 5. Don't Over-Optimize

**Remember**:
- 100% coverage ≠ bug-free code
- Focus on testing **important** paths
- Quality > Quantity
- Test **behavior**, not **implementation**

---

## Coverage Tools Integration

### 1. VS Code

**Extension**: Coverage Gutters

**Install**:
```bash
code --install-extension ryanluker.vscode-coverage-gutters
```

**Configure** (`.vscode/settings.json`):
```json
{
  "coverage-gutters.coverageFileNames": [
    ".coverage/coverage-combined.lcov"
  ],
  "coverage-gutters.showLineCoverage": true,
  "coverage-gutters.showRulerCoverage": true
}
```

**Usage**:
1. Run `make coverage-combine`
2. Open file in VS Code
3. Click "Watch" in status bar
4. See coverage in gutter

### 2. PyCharm/IntelliJ

**Built-in Coverage**:
1. Right-click test file
2. "Run with Coverage"
3. View coverage in editor

**Or use external**:
1. Run `make coverage-combine`
2. Import coverage XML
3. View in Coverage tool window

### 3. Codecov (Cloud)

**Setup**:
```yaml
# .github/workflows/ci.yml
- name: Upload to Codecov
  uses: codecov/codecov-action@v4
  with:
    files: ./coverage/coverage-combined.xml
    fail_ci_if_error: true
```

**Features**:
- Coverage trends
- PR comments
- Coverage diffs
- Sunburst charts

### 4. SonarQube

**Setup**:
```bash
# Run analysis
sonar-scanner \
  -Dsonar.projectKey=robot-flower-princess \
  -Dsonar.sources=src \
  -Dsonar.python.coverage.reportPaths=coverage/coverage-combined.xml
```

**Features**:
- Code smells
- Security issues
- Coverage tracking
- Technical debt

---

## Summary

### Key Takeaways

- ✅ **80% minimum** coverage enforced in CI
- ✅ **Three-tier** coverage strategy (unit, integration, feature-component)
- ✅ **Parallel execution** for fast feedback
- ✅ **Multiple formats** (HTML, XML, LCOV)
- ✅ **Automated** in GitHub Actions
- ✅ **Focus on critical paths** (domain logic, use cases)

### Coverage Commands Cheat Sheet

```bash
# Run all tests with coverage
make coverage

# Combine coverage reports
make coverage-combine

# View HTML report
open .coverage/coverage_html/index.html

# Terminal report
coverage report

# Show missing lines
coverage report --show-missing

# Only show files with low coverage
coverage report --skip-covered

# Generate badge
coverage-badge -o coverage.svg

# Check threshold
coverage report --fail-under=80
```

### Coverage Checklist

- [ ] All tests passing
- [ ] Coverage ≥ 80% overall
- [ ] Critical paths covered (100%)
- [ ] Edge cases tested
- [ ] Error handling tested
- [ ] HTML report reviewed
- [ ] CI checks passing

---

## Related Documentation

- [Testing Strategy](TESTING_STRATEGY.md) - Comprehensive testing guide
- [CI/CD Workflow](CI_CD.md) - Coverage in CI/CD
- [Architecture](ARCHITECTURE.md) - What to test
- [API Documentation](API.md) - Integration test scenarios
