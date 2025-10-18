from functools import lru_cache
from ..persistence.in_memory_game_repository import InMemoryGameRepository
from ...application.ports.game_repository import GameRepository

@lru_cache()
def get_game_repository() -> GameRepository:
    """Dependency injection for game repository."""
    return InMemoryGameRepository()
