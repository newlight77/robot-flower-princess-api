#!make

# ML Player - Makefile

SHELL := /bin/sh

.PHONY: help install setup test test-cov lint format run docker-up docker-down coverage clean

help:
	@echo "ML Player - Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make test         - Run tests"
	@echo "  make test-cov     - Run tests with coverage"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code"
	@echo "  make run          - Run the application"
	@echo "  make docker-up    - Start with Docker"
	@echo "  make docker-down  - Stop Docker containers"
	@echo "  make clean        - Clean cache files"

install:
	poetry install

setup:
	pyenv local 3.13.0
	poetry install

test:
	poetry run pytest -v

test-all: test-unit test-integration test-feature-component

test-cov:
	poetry run pytest --cov=src/hexagons/mlplayer --cov-report=html --cov-report=term

test-unit:
	poetry run pytest tests/unit -v

test-integration:
	poetry run pytest tests/integration -v

test-feature-component:
	poetry run pytest tests/feature-component -v

coverage:
	@mkdir -p coverage/unit coverage/integration coverage/feature-component
	poetry run pytest --cov=src --cov-report=xml:coverage/unit/coverage-unit.xml --cov-report=html:coverage/unit/coverage-unit.html tests/unit
	@mv .coverage coverage/unit/coverage-unit.cov
	poetry run pytest --cov=src --cov-report=xml:coverage/integration/coverage-integration.xml --cov-report=html:coverage/integration/coverage-integration.html tests/integration
	@mv .coverage coverage/integration/coverage-integration.cov
	poetry run pytest --cov=src --cov-report=xml:coverage/feature-component/coverage-feature-component.xml --cov-report=html:coverage/feature-component/coverage-feature-component.html tests/feature-component
	@mv .coverage coverage/feature-component/coverage-feature-component.cov

lint:
	poetry run ruff check src/ tests/

format:
	poetry run black src/ tests/
	poetry run ruff check --fix src/ tests/

run:
	poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8001 --app-dir src

docker-build:
	docker build -t ml-player-api:latest .

docker-run:
	docker run -p 8001:8001 ml-player-api:latest

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	rm -rf coverage || true
