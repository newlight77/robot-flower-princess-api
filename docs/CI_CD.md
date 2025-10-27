# CI/CD Workflow Documentation

## Table of Contents
- [Overview](#overview)
- [GitHub Actions Workflow](#github-actions-workflow)
- [Pipeline Stages](#pipeline-stages)
- [Coverage Workflow](#coverage-workflow)
- [Docker Build & Deploy](#docker-build--deploy)
- [Environment Variables & Secrets](#environment-variables--secrets)
- [Branch Strategy](#branch-strategy)
- [Pull Request Workflow](#pull-request-workflow)
- [Troubleshooting CI Issues](#troubleshooting-ci-issues)

---

## Overview

The project uses **GitHub Actions** for Continuous Integration and Continuous Deployment (CI/CD). The pipeline ensures code quality, runs comprehensive tests, checks coverage, and deploys to production.

This project contains **two separate services**, each with its own CI workflow:
- **RFP Game** (`rfp_game/`) - Main game service
- **ML Player** (`ml_player/`) - Machine learning player service

### Pipeline Goals

- ✅ **Automated Testing**: Run all tests on every push/PR
- ✅ **Code Quality**: Lint and format checks
- ✅ **Coverage**: Maintain 80%+ test coverage
- ✅ **Docker Build**: Verify containerization works
- ✅ **Fast Feedback**: Parallel test execution
- ✅ **Isolation**: Each service has independent CI pipeline
- ✅ **Deployment**: Automated deployment on successful builds

### Workflow Triggers

**RFP Game CI** (`.github/workflows/ci.yml`):
```yaml
on:
  push:
    branches: [ main ]
    paths:
      - 'rfp_game/**'
      - '.github/workflows/ci.yml'
      - '.gitignore'
  pull_request:
    branches: [ main ]
    paths:
      - 'rfp_game/**'
      - '.github/workflows/ci.yml'
      - '.gitignore'
```

**ML Player CI** (`.github/workflows/ml_player-ci.yml`):
```yaml
on:
  push:
    branches: [ main ]
    paths:
      - 'ml_player/**'
      - '.github/workflows/ml_player-ci.yml'
      - '.gitignore'
  pull_request:
    branches: [ main ]
    paths:
      - 'ml_player/**'
      - '.github/workflows/ml_player-ci.yml'
      - '.gitignore'
```

**Triggers**:
- Push to `main` branch (only when files in respective project change)
- Pull requests targeting `main` branch (only when files in respective project change)
- Changes to the workflow file itself
- Changes to `.gitignore`

**Benefits**:
- ⚡ **Faster CI**: Only runs tests for changed services
- 💰 **Cost Efficient**: Reduces unnecessary CI runs
- 🔒 **Isolation**: Changes to one service don't trigger tests for the other
- 🎯 **Clear Feedback**: CI results are specific to the changed service

---

## GitHub Actions Workflows

### Workflow Files

**RFP Game CI**: `.github/workflows/ci.yml`
**ML Player CI**: `.github/workflows/ml_player-ci.yml`

**RFP Game Workflow Overview**:
```
┌─────────────────────────────────────────────────────────────┐
│                   RFP Game CI Workflow                       │
└─────────────────────────────────────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
         ┌─────────┐  ┌──────────┐  ┌──────────────┐
         │  Unit   │  │Integration│  │Feature-Comp. │
         │  Tests  │  │  Tests    │  │   Tests      │
         └─────────┘  └──────────┘  └──────────────┘
              │             │             │
              └─────────────┼─────────────┘
                            ▼
                  ┌──────────────────┐
                  │  Code Coverage   │
                  │  Quality Check   │
                  └──────────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │    Lint     │
                     └─────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │Docker Build  │
                    │  & Test      │
                    └──────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │   Deploy    │
                     │ (if main)   │
                     └─────────────┘
```

**ML Player Workflow Overview**:
```
┌─────────────────────────────────────────────────────────────┐
│                   ML Player CI Workflow                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                       ┌─────────┐
                       │  Unit   │
                       │  Tests  │
                       └─────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │  Code Coverage   │
                  │  Quality Check   │
                  └──────────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │    Lint     │
                     └─────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │Docker Build  │
                    │  & Test      │
                    └──────────────┘
```

**Key Differences**:
- RFP Game has full test pyramid (unit, integration, feature-component)
- ML Player currently has unit tests only (integration/feature tests pending)
- Both enforce 80% coverage threshold
- Both build and test Docker images
- Workflows run independently based on file changes

---

## Pipeline Stages

### Stage 1: Unit Tests

**Job**: `unit`

**Purpose**: Test domain logic in isolation

**Steps**:
1. Checkout code
2. Set up Python 3.13
3. Install Poetry
4. Install dependencies (main + dev)
5. Run unit tests with coverage
6. Upload coverage artifacts

**Configuration**:
```yaml
unit:
  name: Unit tests
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v5

    - name: Set up Python
      uses: actions/setup-python@v6
      with:
        python-version: 3.13

    - name: Install Poetry
      run: |
        python -m pip install --upgrade pip
        python -m pip install poetry

    - name: Install dependencies
      run: |
        poetry config virtualenvs.create false
        poetry install --only main --no-interaction --no-ansi
        poetry install --only dev --no-interaction --no-ansi

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
        ls -la coverage/unit || true
        test -f coverage/unit/coverage-unit.cov && \
          echo "✓ Coverage database file created" || \
          echo "✗ WARNING: Coverage database file not found!"

    - name: Upload unit coverage artifacts
      uses: actions/upload-artifact@v4
      with:
        name: coverage-unit
        path: |
          coverage/unit/coverage-unit.cov
          coverage/unit/coverage-unit.lcov
          coverage/unit/coverage-unit.xml
          coverage/unit/coverage-unit.html
```

**Duration**: ~30 seconds

---

### Stage 2: Integration Tests

**Job**: `integration`

**Purpose**: Test API endpoints and layer interactions

**Steps**: Same as unit tests, but runs `tests/integration`

**Configuration**:
```yaml
integration:
  name: Integration tests
  runs-on: ubuntu-latest
  steps:
    # ... (similar to unit tests)

    - name: Run integration tests with coverage
      run: |
        mkdir -p coverage/integration
        pytest -q \
          --cov=src \
          --cov-report=xml:coverage/integration/coverage-integration.xml \
          --cov-report=html:coverage/integration/coverage-integration.html \
          --cov-report=lcov:coverage/integration/coverage-integration.lcov \
          tests/integration
        mv .coverage coverage/integration/coverage-integration.cov
```

**Duration**: ~45 seconds

---

### Stage 3: Feature-Component Tests

**Job**: `feature-component`

**Purpose**: Test end-to-end workflows (e.g., autoplay scenarios)

**Steps**: Same structure, runs `tests/feature-component`

**Configuration**:
```yaml
feature-component:
  name: Feature-Component tests
  runs-on: ubuntu-latest
  steps:
    # ... (similar structure)

    - name: Run feature-component tests with coverage
      run: |
        mkdir -p coverage/feature-component
        pytest -q \
          --cov=src \
          --cov-report=xml:coverage/feature-component/coverage-feature-component.xml \
          --cov-report=html:coverage/feature-component/coverage-feature-component.html \
          --cov-report=lcov:coverage/feature-component/coverage-feature-component.lcov \
          tests/feature-component
        mv .coverage coverage/feature-component/coverage-feature-component.cov
```

**Duration**: ~60 seconds

---

### Stage 4: Code Coverage Quality Check

**Job**: `code-coverage`

**Purpose**: Combine coverage from all test suites and enforce 80% minimum

**Dependencies**: Requires `unit`, `integration`, `feature-component` to complete

**Steps**:
1. Download all coverage artifacts
2. Merge coverage data
3. Generate combined reports
4. Enforce 80% coverage threshold
5. Upload combined coverage report

**Configuration**:
```yaml
code-coverage:
  name: Coverage quality check
  runs-on: ubuntu-latest
  needs: [unit, integration, feature-component]
  steps:
    - uses: actions/checkout@v5

    - name: Set up Python
      uses: actions/setup-python@v6
      with:
        python-version: 3.13

    - name: Install Poetry
      run: |
        python -m pip install --upgrade pip
        python -m pip install poetry

    - name: Install dependencies
      run: |
        poetry config virtualenvs.create false
        poetry install --only main --no-interaction --no-ansi
        poetry install --only dev --no-interaction --no-ansi

    - name: Download coverage artifacts
      uses: actions/download-artifact@v5
      with:
        path: coverage-artifacts

    - name: Merge coverage data
      run: |
        mkdir -p coverage || true
        mv coverage-artifacts/coverage-unit coverage/unit || true
        mv coverage-artifacts/coverage-integration coverage/integration || true
        mv coverage-artifacts/coverage-feature-component coverage/feature-component || true

        # Verify directories exist
        test -d coverage/unit/ && echo "✓ Coverage unit directory found" || echo "✗ WARNING: Coverage unit directory not found!"
        test -d coverage/integration/ && echo "✓ Coverage integration directory found" || echo "✗ WARNING: Coverage integration directory not found!"
        test -d coverage/feature-component/ && echo "✓ Coverage feature-component directory found" || echo "✗ WARNING: Coverage feature-component directory not found!"

        # Combine coverage data
        coverage combine --keep --data-file=coverage/coverage.combined coverage/*/coverage-*.cov || true
        coverage lcov --data-file=coverage/coverage.combined -o coverage/coverage-combined.lcov
        coverage xml --data-file=coverage/coverage.combined -o coverage/coverage-combined.xml
        coverage html --data-file=coverage/coverage.combined --directory=coverage/coverage-combined.html

    - name: Extract coverage percentage
      id: coverage
      run: |
        COVERAGE=$(coverage report --data-file=coverage/coverage.combined | grep TOTAL | awk '{print $4}' | sed 's/%//')
        echo "percentage=$COVERAGE" >> $GITHUB_OUTPUT
        echo "Coverage: $COVERAGE%"

    - name: Generate Job Summary
      if: always()
      run: |
        # Generates a beautiful coverage report in GitHub Actions UI
        # Shows coverage percentage, test suite status, and artifact links
        COVERAGE=${{ steps.coverage.outputs.percentage }}
        THRESHOLD=80
        echo "# 🧪 Test Coverage Report" >> $GITHUB_STEP_SUMMARY
        # ... (full implementation generates tables with emojis and status)

    - name: Coverage quality check
      run: |
        coverage report --data-file=coverage/coverage.combined --fail-under=80

    - name: Comment coverage on PR
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v7
      with:
        script: |
          # Posts a comprehensive coverage report as a PR comment
          # Includes coverage %, test suite status, and artifact links

    - name: Upload combined coverage report
      uses: actions/upload-artifact@v4
      with:
        name: coverage-combined
        path: |
          coverage/unit/coverage-unit.cov
          coverage/unit/coverage-unit.lcov
          coverage/unit/coverage-unit.xml
          coverage/unit/coverage-unit.html
          coverage/integration/coverage-integration.cov
          coverage/integration/coverage-integration.lcov
          coverage/integration/coverage-integration.xml
          coverage/integration/coverage-integration.html
          coverage/feature-component/coverage-feature-component.cov
          coverage/feature-component/coverage-feature-component.lcov
          coverage/feature-component/coverage-feature-component.xml
          coverage/feature-component/coverage-feature-component.html
          coverage/coverage.combined
          coverage/coverage-combined.lcov
          coverage/coverage-combined.xml
          coverage/coverage-combined.html
```

**Duration**: ~20 seconds

**Key Points**:
- Uses `actions/download-artifact@v5` which creates subdirectories per artifact
- Combines `.coverage.*` files from all test suites
- Generates multiple report formats (LCOV, XML, HTML)
- Fails if coverage < 80%

**📊 Job Summary Feature**:

The workflow automatically generates a beautiful coverage report in the GitHub Actions UI with:

✅ **Coverage Summary**: Shows total coverage percentage with pass/fail status
🧩 **Test Suite Status**: Displays all test suites with counts (50 total tests)
📈 **Coverage Details**: Breakdown by test level with execution times
📦 **Artifact Links**: Quick access to downloadable reports
🎯 **Coverage by Hexagon**: Shows test distribution across architecture layers

**Example Output**:
```
# 🧪 Test Coverage Report

## 📊 Coverage Summary
| Metric              | Value  | Status    |
|---------------------|--------|-----------|
| Total Coverage      | 95.2%  | ✅ PASS   |
| Coverage Threshold  | 80%    | -         |

## 🧩 Test Suites
| Test Suite              | Count | Status        |
|-------------------------|-------|---------------|
| Unit Tests              | 32    | ✅ Passed     |
| Integration Tests       | 11    | ✅ Passed     |
| Feature-Component Tests | 7     | ✅ Passed     |
| Total                   | 50    | ✅ All Passed |
```

💡 **How to View**: Navigate to any workflow run → Click the "Summary" tab at the top

**📝 PR Comment Feature**:

For pull requests, the workflow automatically posts a comment with the coverage report directly on the PR:

✅ **Automatically triggers** on every PR push
📊 **Comprehensive metrics** including coverage %, test counts, and status
🎯 **Hexagon breakdown** showing coverage across architecture layers
🔗 **Quick links** to detailed reports and workflow runs
⏰ **Timestamp** showing when the report was generated

**Example PR Comment**:
```
## ✅ Test Coverage Report

### 📊 Coverage Summary
| Metric              | Value  | Status         |
|---------------------|--------|----------------|
| Total Coverage      | 95.2%  | ✅ PASSED      |
| Coverage Threshold  | 80%    | -              |

### 🧩 Test Suites
| Test Suite              | Count | Status        |
|-------------------------|-------|---------------|
| Unit Tests              | 32    | ✅ Passed     |
| Integration Tests       | 11    | ✅ Passed     |
| Feature-Component Tests | 7     | ✅ Passed     |
| Total                   | 50    | ✅ All Passed |

### 📈 Coverage Details
| Test Level         | Tests | Percentage | Speed           |
|--------------------|-------|------------|-----------------|
| Unit               | 32    | 64%        | ⚡⚡⚡ Very Fast |
| Integration        | 11    | 22%        | ⚡⚡ Fast        |
| Feature-Component  | 7     | 14%        | ⚡ Normal       |

### 🎯 Coverage by Hexagon
| Hexagon      | Tests | Status           |
|--------------|-------|------------------|
| game         | 42    | ✅ Well-tested   |
| aiplayer     | 10    | ✅ Good coverage |
| configurator | 0     | ⚠️ Needs tests   |
| shared       | 0     | ⚠️ Needs tests   |

---

📊 View detailed coverage report | 📦 Download HTML report
```

💡 **Benefits**:
- **Instant feedback** on PR coverage without leaving the PR page
- **Easy comparison** between commits as coverage changes
- **Team visibility** - everyone can see test health at a glance
- **Historical record** - comments are preserved for future reference

---

### Stage 5: Lint & Format

**Job**: `lint`

**Purpose**: Enforce code style and quality

**Dependencies**: Requires `code-coverage` to complete

**Steps**:
1. Check code formatting with Black
2. Lint with Ruff
3. (Optional) Type check with MyPy

**Configuration**:
```yaml
lint:
  runs-on: ubuntu-latest
  needs:
    - code-coverage
  steps:
    - uses: actions/checkout@v5

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.13'

    - name: Install Poetry
      run: |
        curl -sSL https://install.python-poetry.org | python3 -
        echo "$HOME/.local/bin" >> $GITHUB_PATH

    - name: Install dependencies
      run: |
        poetry config virtualenvs.create false
        poetry install --only main --no-interaction --no-ansi
        poetry install --only dev --no-interaction --no-ansi

    - name: Run linters
      run: |
        poetry run black --check src/ tests/
        poetry run ruff check src/ tests/
        # poetry run mypy src/  # Optional: enable type checking
```

**Duration**: ~15 seconds

**Linting Tools**:
- **Black**: Code formatter (PEP 8 compliant)
- **Ruff**: Fast Python linter
- **MyPy**: Static type checker (commented out by default)

---

### Stage 6: Docker Build & Test

**Job**: `docker`

**Purpose**: Verify containerization works and image is healthy

**Dependencies**: Requires `lint` to complete

**Steps**:
1. Build Docker image
2. Run container
3. Test health endpoint
4. Stop container

**Configuration**:
```yaml
docker:
  runs-on: ubuntu-latest
  needs: lint
  steps:
    - uses: actions/checkout@v5

    - name: Build Docker image
      run: docker build -t robot-flower-princess:test .

    - name: Test Docker image
      run: |
        docker run -d -p 8000:8000 --name test-api robot-flower-princess:test
        sleep 10
        curl -f http://localhost:8000/health || exit 1
        docker stop test-api
```

**Duration**: ~2 minutes

**Image Details**:
- Base: `python:3.13-slim`
- Size: ~150MB
- Includes production dependencies only
- Health check configured

---

## Coverage Workflow

### Coverage File Structure

```
coverage/
├── unit/
│   ├── coverage-unit.cov        # Coverage database
│   ├── coverage-unit.lcov       # LCOV format
│   ├── coverage-unit.xml        # XML format (for tools)
│   └── coverage-unit.html/      # HTML report
├── integration/
│   ├── coverage-integration.cov
│   ├── coverage-integration.lcov
│   ├── coverage-integration.xml
│   └── coverage-integration.html/
├── feature-component/
│   ├── coverage-feature-component.cov
│   ├── coverage-feature-component.lcov
│   ├── coverage-feature-component.xml
│   └── coverage-feature-component.html/
└── coverage.combined             # Combined coverage database
    ├── coverage-combined.lcov   # Combined LCOV
    ├── coverage-combined.xml    # Combined XML
    └── coverage-combined.html/  # Combined HTML report
```

### Coverage Artifact Handling

**Upload Artifacts** (per job):
```yaml
- name: Upload unit coverage artifacts
  uses: actions/upload-artifact@v4
  with:
    name: coverage-unit
    path: |
      coverage/unit/coverage-unit.cov
      coverage/unit/coverage-unit.lcov
      coverage/unit/coverage-unit.xml
      coverage/unit/coverage-unit.html
```

**Download Artifacts** (merge job):
```yaml
- name: Download coverage artifacts
  uses: actions/download-artifact@v5
  with:
    path: coverage-artifacts
```

**Note**: `actions/download-artifact@v5` creates subdirectories named after each artifact:
```
coverage-artifacts/
├── coverage-unit/
│   └── coverage/unit/...
├── coverage-integration/
│   └── coverage/integration/...
└── coverage-feature-component/
    └── coverage/feature-component/...
```

### Coverage Combination

```bash
# Move artifacts to expected locations
mv coverage-artifacts/coverage-unit coverage/unit
mv coverage-artifacts/coverage-integration coverage/integration
mv coverage-artifacts/coverage-feature-component coverage/feature-component

# Combine coverage databases
coverage combine --keep --data-file=coverage/coverage.combined coverage/*/coverage-*.cov

# Generate reports
coverage lcov --data-file=coverage/coverage.combined -o coverage/coverage-combined.lcov
coverage xml --data-file=coverage/coverage.combined -o coverage/coverage-combined.xml
coverage html --data-file=coverage/coverage.combined --directory=coverage/coverage-combined.html

# Enforce threshold
coverage report --data-file=coverage/coverage.combined --fail-under=80
```

### Coverage Thresholds

| Test Suite | Target | Enforced |
|------------|--------|----------|
| Unit | 90%+ | No |
| Integration | 85%+ | No |
| Feature-Component | N/A | No |
| **Combined** | **80%+** | **Yes** |

---

## Docker Build & Deploy

### Build Arguments

```dockerfile
# Build-time arguments
ARG PYTHON_VERSION=3.13
ARG PORT=8000

FROM python:${PYTHON_VERSION}-slim

# Runtime environment
ENV PORT=${PORT}
ENV PYTHONUNBUFFERED=1

EXPOSE ${PORT}
```

### Multi-Stage Build (Future)

For smaller images:
```dockerfile
# Stage 1: Build
FROM python:3.13-slim AS builder
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry export -f requirements.txt --output requirements.txt

# Stage 2: Runtime
FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
CMD ["uvicorn", ".main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Push to Registry (Future)

**Docker Hub**:
```yaml
- name: Login to Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKER_USERNAME }}
    password: ${{ secrets.DOCKER_PASSWORD }}

- name: Build and push
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: yourusername/robot-flower-princess:latest
```

**AWS ECR**:
```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: us-east-1

- name: Login to Amazon ECR
  uses: aws-actions/amazon-ecr-login@v2

- name: Build and push to ECR
  run: |
    docker build -t robot-flower-princess:latest .
    docker tag robot-flower-princess:latest $ECR_REGISTRY/robot-flower-princess:latest
    docker push $ECR_REGISTRY/robot-flower-princess:latest
```

---

## Environment Variables & Secrets

### GitHub Secrets

**Repository Secrets** (Settings > Secrets and variables > Actions):

| Secret | Purpose | Example |
|--------|---------|---------|
| `DOCKER_USERNAME` | Docker Hub username | `yourusername` |
| `DOCKER_PASSWORD` | Docker Hub password/token | `dckr_pat_...` |
| `AWS_ACCESS_KEY_ID` | AWS credentials | `AKIA...` |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials | `wJalr...` |
| `GCP_SA_KEY` | GCP service account key | `{"type":"service_account",...}` |
| `DEPLOY_SSH_KEY` | SSH key for deployment | `-----BEGIN RSA PRIVATE KEY-----` |

### Using Secrets in Workflow

```yaml
env:
  DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
  DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}

steps:
  - name: Login to Docker Hub
    run: echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
```

### Environment Variables

**Global**:
```yaml
env:
  PYTHON_VERSION: "3.13"
  POETRY_VERSION: "1.7.1"
```

**Per Job**:
```yaml
jobs:
  unit:
    env:
      COVERAGE_FILE: coverage/unit/coverage-unit.cov
```

**Per Step**:
```yaml
- name: Run tests
  env:
    LOG_LEVEL: debug
  run: pytest tests/
```

---

## Branch Strategy

### Branch Types

| Branch | Purpose | Protected | CI Runs |
|--------|---------|-----------|---------|
| `main` | Production code | Yes | Full pipeline + deploy |
| `develop` | Development integration | Yes | Full pipeline |
| `feature/*` | New features | No | Tests + lint |
| `bugfix/*` | Bug fixes | No | Tests + lint |
| `hotfix/*` | Production fixes | No | Full pipeline |

### Branch Protection Rules

**Main Branch** (Settings > Branches > Branch protection rules):

- [x] Require a pull request before merging
- [x] Require approvals (1)
- [x] Dismiss stale pull request approvals
- [x] Require status checks to pass before merging
  - [x] `unit`
  - [x] `integration`
  - [x] `feature-component`
  - [x] `code-coverage`
  - [x] `lint`
  - [x] `docker`
- [x] Require branches to be up to date before merging
- [x] Require conversation resolution before merging
- [ ] Require signed commits (optional)
- [x] Include administrators

### Merge Strategy

**Squash and Merge** (recommended):
- Keeps history clean
- One commit per PR
- Easy to revert

```bash
git merge --squash feature/new-feature
git commit -m "feat: add new feature (#42)"
```

---

## Pull Request Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/my-new-feature
```

### 2. Make Changes & Test Locally

```bash
# Run tests
make test-all

# Check coverage
make coverage
make coverage-combine

# Lint and format
make format
make lint

# Build Docker (optional)
make docker-build
```

### 3. Commit & Push

```bash
git add .
git commit -m "feat: add my new feature"
git push origin feature/my-new-feature
```

### 4. Open Pull Request

**PR Title Format**:
- `feat: add new feature` (new feature)
- `fix: resolve bug in robot movement` (bug fix)
- `docs: update API documentation` (documentation)
- `refactor: improve game service` (refactoring)
- `test: add tests for autoplay` (tests)
- `chore: update dependencies` (maintenance)

**PR Description Template**:
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Feature-component tests pass
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added where necessary
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests added/updated
- [ ] Coverage maintained (80%+)
```

### 5. CI Checks

GitHub Actions automatically runs:
1. Unit tests
2. Integration tests
3. Feature-component tests
4. Coverage check (80%+)
5. Linting
6. Docker build

**View Status**: Check in PR "Checks" tab

### 6. Code Review

- Reviewer checks code quality
- Runs tests locally if needed
- Approves or requests changes

### 7. Merge

Once approved and all checks pass:
```bash
# Squash and merge via GitHub UI
# Or manually:
git checkout main
git merge --squash feature/my-new-feature
git push origin main
```

### 8. Cleanup

```bash
git branch -d feature/my-new-feature
git push origin --delete feature/my-new-feature
```

---

## Troubleshooting CI Issues

### Issue 1: Coverage Artifacts Not Found

**Error**: `cp: cannot stat 'coverage-artifacts/coverage-unit/.coverage.unit': No such file or directory`

**Cause**: `actions/download-artifact@v5` changed directory structure

**Solution**: Update paths in merge step
```yaml
- name: Merge coverage data
  run: |
    mv coverage-artifacts/coverage-unit coverage/unit
    mv coverage-artifacts/coverage-integration coverage/integration
    mv coverage-artifacts/coverage-feature-component coverage/feature-component
```

### Issue 2: Coverage Below 80%

**Error**: `Total coverage must be at least 80%`

**Solution**:
1. Check which files have low coverage:
   ```bash
   make coverage
   coverage report --data-file=coverage/coverage.combined
   ```
2. Add missing tests
3. Re-run CI

### Issue 3: Poetry Installation Fails

**Error**: `ERROR: Could not find a version that satisfies the requirement poetry`

**Solution**: Use official install script
```yaml
- name: Install Poetry
  run: |
    curl -sSL https://install.python-poetry.org | python3 -
    echo "$HOME/.local/bin" >> $GITHUB_PATH
```

### Issue 4: Docker Build Timeout

**Error**: `The job running on runner GitHub Actions X has exceeded the maximum execution time of 60 minutes`

**Solution**:
1. Use layer caching:
   ```yaml
   - name: Set up Docker Buildx
     uses: docker/setup-buildx-action@v3

   - name: Build with cache
     uses: docker/build-push-action@v5
     with:
       cache-from: type=gha
       cache-to: type=gha,mode=max
   ```
2. Reduce image size
3. Use multi-stage builds

### Issue 5: Tests Pass Locally But Fail in CI

**Possible Causes**:
1. **Environment differences**: Missing dependencies
2. **Test isolation**: Shared state between tests
3. **Timing issues**: Race conditions

**Solutions**:
1. Run tests in Docker locally:
   ```bash
   docker build -t robot-flower-princess:test .
   docker run robot-flower-princess:test pytest tests/
   ```
2. Check test isolation:
   ```bash
   pytest tests/ --random-order
   ```
3. Add retries for flaky tests:
   ```python
   @pytest.mark.flaky(reruns=3)
   def test_flaky_operation():
       pass
   ```

### Issue 6: Linting Fails

**Error**: `Black would reformat file.py`

**Solution**: Format locally and commit
```bash
make format
git add .
git commit -m "chore: format code"
git push
```

---

## Performance Optimization

### 1. Parallel Test Execution

Run test suites in parallel (already implemented):
```yaml
jobs:
  unit:
    # runs in parallel
  integration:
    # runs in parallel
  feature-component:
    # runs in parallel
```

**Time Saved**: 60% faster than sequential

### 2. Dependency Caching

Cache Poetry dependencies:
```yaml
- name: Cache Poetry dependencies
  uses: actions/cache@v4
  with:
    path: ~/.cache/pypoetry
    key: ${{ runner.os }}-poetry-${{ hashFiles('**/poetry.lock') }}
    restore-keys: |
      ${{ runner.os }}-poetry-
```

**Time Saved**: 30-60 seconds per job

### 3. Docker Layer Caching

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build with cache
  uses: docker/build-push-action@v5
  with:
    context: .
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

**Time Saved**: 1-2 minutes on Docker builds

---

## Monitoring CI Health

### GitHub Actions Insights

**View Metrics**: Repository > Actions > View workflow runs

**Metrics to Track**:
- Success rate
- Average runtime
- Failure patterns
- Most failing jobs

### Notifications

**Enable Notifications**:
- Settings > Notifications > Actions
- Get notified on workflow failures
- Configure email/Slack webhooks

**Slack Integration**:
```yaml
- name: Notify Slack on failure
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "CI pipeline failed: ${{ github.workflow }}"
      }
```

---

## Future Enhancements

### 1. Deployment Automation

```yaml
deploy:
  name: Deploy to Production
  runs-on: ubuntu-latest
  needs: [docker]
  if: github.ref == 'refs/heads/main'
  steps:
    - name: Deploy to Cloud Run
      run: |
        gcloud run deploy robot-flower-princess-api \
          --image gcr.io/$PROJECT_ID/robot-flower-princess:${{ github.sha }} \
          --platform managed \
          --region us-central1
```

### 2. Performance Testing

```yaml
performance:
  name: Performance Tests
  runs-on: ubuntu-latest
  steps:
    - name: Run load tests
      run: |
        locust -f tests/performance/locustfile.py \
          --headless \
          --users 100 \
          --spawn-rate 10 \
          --run-time 1m
```

### 3. Security Scanning

```yaml
security:
  name: Security Scan
  runs-on: ubuntu-latest
  steps:
    - name: Run Trivy scan
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: robot-flower-princess:latest
        format: 'sarif'
        output: 'trivy-results.sarif'
```

---

## Summary

### CI/CD Pipeline Benefits

- ✅ **Automated Testing**: All tests run automatically
- ✅ **Fast Feedback**: ~5 minutes for full pipeline
- ✅ **High Confidence**: 80%+ coverage enforced
- ✅ **Parallel Execution**: 60% faster than sequential
- ✅ **Docker Validation**: Ensures containerization works
- ✅ **Code Quality**: Linting and formatting enforced
- ✅ **Branch Protection**: No broken code in main

### Key Metrics

| Metric | Value |
|--------|-------|
| **Total Pipeline Time** | ~5 minutes |
| **Test Coverage** | 80%+ (enforced) |
| **Jobs** | 6 (unit, integration, feature-component, coverage, lint, docker) |
| **Parallel Jobs** | 3 (test suites) |
| **Artifacts** | 4 coverage reports |

---

## Related Documentation

- [Testing Strategy](TESTING_STRATEGY.md) - Comprehensive testing guide
- [Deployment](DEPLOYMENT.md) - Deployment instructions
- [Architecture](ARCHITECTURE.md) - System architecture
- [API](API.md) - API documentation
