#!make

# Robot Flower Princess - Makefile

SHELL := /bin/sh

.PHONY: help install setup test test-cov lint format run docker-up docker-down clean

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

clean:
	POETRY_LOCATION=`poetry env info -p`
	echo "Poetry is $POETRY_LOCATION"
	rm -rf "$POETRY_LOCATION"
	poetry deactivate

test:
	poetry run pytest -v

test-cov:
	poetry run pytest --cov=src/robot_flower_princess --cov-report=html --cov-report=term

lint:
	poetry run ruff check src/ tests/
	# poetry run mypy src/

format:
	poetry run black src/ tests/
	poetry run ruff check --fix src/ tests/

run:
	poetry env activate
	poetry run uvicorn robot_flower_princess.infrastructure.api.main:app --reload --host 0.0.0.0 --port 8000

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
