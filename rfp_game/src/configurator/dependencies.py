from functools import lru_cache
from hexagons.game.driven.persistence.in_memory_game_repository import InMemoryGameRepository
from hexagons.game.domain.ports.game_repository import GameRepository
from hexagons.aiplayer.driven.adapters.http_ml_player_client import HttpMLPlayerClient
from hexagons.aiplayer.domain.ports.ml_player_client import MLPlayerClientPort
from configurator.settings import settings


@lru_cache()
def get_game_repository() -> GameRepository:
    """Dependency injection for game repository."""
    return InMemoryGameRepository()


@lru_cache()
def get_ml_player_client() -> MLPlayerClientPort:
    """Dependency injection for ML Player client."""
    return HttpMLPlayerClient(
        base_url=settings.ml_player_service_url,
        timeout=settings.ml_player_service_timeout
    )
