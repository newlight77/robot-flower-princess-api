from functools import lru_cache
import os
from hexagons.game.driven.persistence.in_memory_game_repository import InMemoryGameRepository
from hexagons.game.domain.ports.game_repository import GameRepository
from hexagons.game.driven.adapters.ml_autoplay_data_collector import MLAutoplayDataCollector
from hexagons.game.domain.ports.ml_autoplay_data_collector import MLAutoplayDataCollectorPort
from hexagons.aiplayer.driven.adapters.ml_autoplay_client import MLAutoplayClient
from hexagons.aiplayer.domain.ports.ml_player_client import MLPlayerClientPort
from configurator.settings import settings


@lru_cache()
def get_game_repository() -> GameRepository:
    """Dependency injection for game repository."""
    return InMemoryGameRepository()


@lru_cache()
def get_ml_player_client() -> MLPlayerClientPort:
    """Dependency injection for ML Player client."""
    return MLAutoplayClient(
        base_url=settings.ml_player_service_url or os.getenv("ML_PLAYER_SERVICE_URL", "http://localhost:8001"),
        timeout=settings.ml_player_service_timeout or 5.0,
    )


@lru_cache()
def get_mltraining_data_collector() -> MLAutoplayDataCollectorPort:
    """Dependency injection for gameplay data collector."""
    # Use settings value (can be overridden by ENABLE_DATA_COLLECTION env var)
    enabled = (
        os.getenv("ENABLE_DATA_COLLECTION", str(settings.ml_player_service_data_collection_enabled)).lower() == "true"
    )

    return MLAutoplayDataCollector(
        ml_training_url=settings.ml_player_service_url,
        timeout=settings.ml_player_service_timeout,
        data_collection_enabled=enabled,
    )
