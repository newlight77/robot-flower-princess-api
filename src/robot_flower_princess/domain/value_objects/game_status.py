from enum import Enum


class GameStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    VICTORY = "victory"
    GAME_OVER = "game_over"
