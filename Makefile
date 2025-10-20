#!make

# Robot Flower Princess - Makefile

SHELL := /bin/sh

.PHONY: help install setup test test-cov lint format run docker-up docker-down coverage-unit coverage-integration coverage-e2e coverage-combine clean clean-poetry 

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

test-cov:
	poetry run pytest --cov=src/robot_flower_princess --cov-report=html --cov-report=term

coverage-unit:
	@# If a regular file named .coverage exists, move it out of the way; then ensure directory exists
	@test -d .coverage || mkdir -p .coverage
	COVERAGE_FILE=.coverage/.coverage.unit $(RUN) pytest --cov=src --cov-report=xml:.coverage/coverage-unit.xml tests/unit

coverage-integration:
	@# If a regular file named .coverage exists, move it out of the way; then ensure directory exists
	@test -d .coverage || mkdir -p .coverage
	COVERAGE_FILE=.coverage/.coverage.integration $(RUN) pytest --cov=src --cov-report=xml:.coverage/coverage-integration.xml tests/integration

coverage-e2e:
	@# If a regular file named .coverage exists, move it out of the way; then ensure directory exists
	@test -d .coverage || mkdir -p .coverage
	COVERAGE_FILE=.coverage/.coverage.e2e $(RUN) pytest --cov=src --cov-report=xml:.coverage/coverage-e2e.xml tests/integration/test_autoplay_end_to_end.py

coverage-combine:
	@# If a regular file named .coverage exists, move it out of the way; then ensure directory exists
	@test -d .coverage || mkdir -p .coverage
	@echo "combine all .coverage.* files into one and create XML + HTML"
	$(RUN) coverage combine .coverage/.coverage.* || true
	$(RUN) coverage xml -o .coverage/coverage-combined.xml
	$(RUN) coverage html -d .coverage/coverage_html

lint:
	poetry run ruff check src/ tests/
	# poetry run mypy src/

format:
	poetry run black src/ tests/
	poetry run ruff check --fix src/ tests/

run:
	poetry env activate
	poetry run uvicorn robot_flower_princess.main:app --reload --host 0.0.0.0 --port 8000

docker-build: ## Build Docker image
	docker build -t robot-flower-princess-api:latest .

docker-run: ## Run Docker container
	docker run -p 8000:80 robot-flower-princess-api:latest

docker-stop: ## Stop Docker container
	docker stop $(docker ps -q --filter ancestor=robot-flower-princess:latest)

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down


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
