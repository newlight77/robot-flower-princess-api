"""Dependency injection for ML Player service."""

from functools import lru_cache

from hexagons.mlplayer.domain.ports.game_client import GameClientPort
from hexagons.mlplayer.driven.adapters.http_game_client import HttpGameClient
from hexagons.mlplayer.domain.ml.data_collector import GameDataCollector

from .settings import settings


def get_game_client() -> GameClientPort:
    """Get game client instance."""
    return HttpGameClient(base_url=settings.game_service_url, timeout=settings.game_service_timeout)


@lru_cache()
def get_data_collector() -> GameDataCollector:
    """Get data collector instance (singleton)."""
    return GameDataCollector()
