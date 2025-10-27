#!make

# Robot Flower Princess - Makefile

SHELL := /bin/sh

.PHONY: help install setup test test-cov lint format run docker-up docker-down coverage-unit coverage-integration coverage-feature-component coverage-combine clean clean-poetry

# Prefer `.venv/bin/python -m` if a local venv exists; otherwise prefer `poetry run` when poetry is installed
VENV_PY := $(shell [ -x .venv/bin/python ] && echo .venv/bin/python || true)
POETRY_EXISTS := $(shell command -v poetry 2>/dev/null || true)
ifeq ($(strip $(VENV_PY)),)
ifeq ($(strip $(POETRY_EXISTS)),)
RUN := .venv/bin/python -m
else
RUN := poetry run
endif
else
RUN := .venv/bin/python -m
endif

help:
	@echo "Robot-Flower-Princess-Back - Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make test        - Run tests"
	@echo "  make test-cov    - Run tests with coverage"
	@echo "  make lint        - Run linters"
	@echo "  make format      - Format code"
	@echo "  make run         - Run the application"
	@echo "  make docker-up   - Start with Docker"
	@echo "  make docker-down - Stop Docker containers"
	@echo "  make clean       - Clean cache files"

install:
	brew install
	poetry install

setup:
	pyenv local 3.13.0
	poetry install

test:
	poetry run pytest -v

test-all: test-unit test-integration test-feature-component

test-cov:
	poetry run pytest --cov=src/hexagons/game --cov-report=html --cov-report=term

test-unit:
	poetry run pytest tests/unit -v

test-integration:
	poetry run pytest tests/integration -v

test-feature-component:
	poetry run pytest tests/feature-component -v

coverage: coverage-unit coverage-integration coverage-feature-component coverage-combine

coverage-unit:
	@# If a regular file named .coverage exists, move it out of the way; then ensure directory exists
	@test -d coverage/unit || mkdir -p coverage/unit
	${RUN} pytest --cov=src --cov-report=xml:coverage/unit/coverage-unit.xml --cov-report=html:coverage/unit/coverage-unit.html --cov-report=lcov:coverage/unit/coverage-unit.lcov tests/unit
	@mv .coverage coverage/unit/coverage-unit.cov

coverage-integration:
	@# If a regular file named .coverage exists, move it out of the way; then ensure directory exists
	@test -d coverage/integration || mkdir -p coverage/integration
	${RUN} pytest --cov=src --cov-report=xml:coverage/integration/coverage-integration.xml --cov-report=html:coverage/integration/coverage-integration.html --cov-report=lcov:coverage/integration/coverage-integration.lcov tests/integration
	@mv .coverage coverage/integration/coverage-integration.cov

coverage-feature-component:
	@# If a regular file named .coverage exists, move it out of the way; then ensure directory exists
	@test -d coverage/feature-component || mkdir -p coverage/feature-component
	${RUN} pytest --cov=src --cov-report=xml:coverage/feature-component/coverage-feature-component.xml --cov-report=html:coverage/feature-component/coverage-feature-component.html --cov-report=lcov:coverage/feature-component/coverage-feature-component.lcov tests/feature-component
	@mv .coverage coverage/feature-component/coverage-feature-component.cov

coverage-combine:
	@echo "combine all coverage.* files into one and create XML + HTML"
	${RUN} coverage combine --keep --data-file=coverage/coverage.combined coverage/*/coverage-*.cov || true
	${RUN} coverage lcov --data-file=coverage/coverage.combined -o coverage/coverage-combined.lcov || true
	${RUN} coverage xml --data-file=coverage/coverage.combined -o coverage/coverage-combined.xml || true
	${RUN} coverage html --data-file=coverage/coverage.combined --directory=coverage/coverage-combined.html || true
	${RUN} coverage report --data-file=coverage/coverage.combined --fail-under=80 || true

lint:
	poetry run ruff check src/ tests/
	# poetry run mypy src/

format:
	poetry run black src/ tests/
	poetry run ruff check --fix src/ tests/

run:
	poetry env activate
	poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000

docker-build: ## Build Docker image
	docker build -t robot-flower-princess-api:latest .

docker-run: ## Run Docker container
	docker run -p 8000:80 robot-flower-princess-api:latest

docker-stop: ## Stop Docker container
	docker stop $(docker ps -q --filter ancestor=robot-flower-princess:latest)

docker-up:
	docker compose up --build

docker-down:
	docker compose down


clean-poetry:
	POETRY_LOCATION=`poetry env info -p` || true
	echo "Poetry is $$POETRY_LOCATION"
	rm -rf "$$POETRY_LOCATION" || true
	poetry env remove --all || true

clean:
	# Repo-level cleanup (pyc, caches, coverage files)
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	rm -rf .coverage || true
