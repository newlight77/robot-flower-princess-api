from dataclasses import dataclass
import uuid
from ..ports.game_repository import GameRepository
from ...domain.entities.board import Board
from ...domain.entities.game_history import GameHistory
from ...logging import get_logger


@dataclass
class CreateGameCommand:
    rows: int
    cols: int


@dataclass
class CreateGameResult:
    game_id: str
    board_state: dict


class CreateGameUseCase:
    def __init__(self, repository: GameRepository):
        self.logger = get_logger(self)
        self.logger.debug("Initializing CreateGameUseCase repository=%r", repository)
        self.repository = repository

    def execute(self, command: CreateGameCommand) -> CreateGameResult:
        """Create a new game with the specified board size."""
        self.logger.info("execute: CreateGameCommand rows=%s cols=%s", command.rows, command.cols)
        board = Board.create(rows=command.rows, cols=command.cols)
        game_id = str(uuid.uuid4())

        # Save board and initialize history
        self.repository.save(game_id, board)
        history = GameHistory()
        history.add_action(action=None, board_state=board.to_dict())
        self.repository.save_history(game_id, history)

        return CreateGameResult(game_id=game_id, board_state=board.to_dict())
