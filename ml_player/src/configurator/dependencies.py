"""Dependency injection for ML Player service."""

from functools import lru_cache

from hexagons.mltraining.domain.ml import GameDataCollector

from .settings import settings


@lru_cache
def get_data_collector() -> GameDataCollector:
    """Get data collector instance (singleton)."""
    return GameDataCollector(data_dir=settings.data_dir)
