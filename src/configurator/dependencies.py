from functools import lru_cache
from robot_flower_princess.driven.persistence.in_memory_game_repository import InMemoryGameRepository
from robot_flower_princess.domain.ports.game_repository import GameRepository


@lru_cache()
def get_game_repository() -> GameRepository:
    """Dependency injection for game repository."""
    return InMemoryGameRepository()
