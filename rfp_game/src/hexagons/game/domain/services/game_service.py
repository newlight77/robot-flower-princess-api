from ..core.entities.game import Game
from ..core.value_objects.direction import Direction
from ..core.value_objects.game_status import GameStatus
from ..core.exceptions.game_exceptions import (
    InvalidMoveException,
    GameOverException,
    InvalidPickException,
    InvalidDropException,
    InvalidGiveException,
    InvalidCleanException,
    InvalidRotationException,
)
from shared.logging import get_logger

logger = get_logger("GameService")


class GameService:
    """Domain service for game logic."""

    @staticmethod
    def rotate_robot(board: Game, direction: Direction) -> None:
        """Rotate the robot to face a direction."""
        logger.info("rotate_robot: board_id=%r direction=%s", getattr(board, "id", None), direction)
        if board.get_status() != GameStatus.IN_PROGRESS:
            raise GameOverException("Game is already over")

        action = board.robot.rotate(direction)
        if action.message:
            raise InvalidRotationException(action.message)

        board.update_timestamp()

    @staticmethod
    def move_robot(board: Game) -> None:
        """Move the robot in the direction it's facing."""
        if board.get_status() != GameStatus.IN_PROGRESS:
            raise GameOverException("Game is already over")

        # Calculate new position based on orientation
        row_delta, col_delta = board.robot.orientation.get_delta()
        new_position = board.robot.position.move(row_delta, col_delta)

        # Validate move
        if not board.is_valid_position(new_position):
            raise InvalidMoveException("Move would go outside the board")

        if not board.is_empty(new_position):
            cell_type = board.get_cell_type(new_position)
            raise InvalidMoveException(f"Target cell is blocked by {cell_type.value}")

        # Execute move
        action = board.robot.move_to(new_position)
        if action.message:
            raise InvalidMoveException(action.message)

        board.board.move_robot(new_position)  # Update board position
        board.update_timestamp()

    @staticmethod
    def pick_flower(board: Game) -> None:
        """Pick a flower from an adjacent cell."""
        if board.get_status() != GameStatus.IN_PROGRESS:
            raise GameOverException("Game is already over")

        if not board.robot.can_pick():
            raise InvalidPickException(
                f"Robot cannot hold more than {board.robot.max_flowers} flowers"
            )

        # Get position in front of robot
        row_delta, col_delta = board.robot.orientation.get_delta()
        target_position = board.robot.position.move(row_delta, col_delta)

        if not board.is_valid_position(target_position):
            raise InvalidPickException("No flower to pick in that direction")

        if target_position not in board.flowers:
            raise InvalidPickException("No flower at target position")

        # Pick the flower
        action = board.robot.pick_flower(target_position)
        if action.message:
            raise InvalidPickException(action.message)

        board.board.pick_flower(target_position)  # Remove from board
        board.update_timestamp()

    @staticmethod
    def drop_flower(board: Game) -> None:
        """Drop a flower on an adjacent empty cell."""
        if board.get_status() != GameStatus.IN_PROGRESS:
            raise GameOverException("Game is already over")

        if board.robot.flowers_held == 0:
            raise InvalidDropException("Robot has no flowers to drop")

        # Get position in front of robot
        row_delta, col_delta = board.robot.orientation.get_delta()
        target_position = board.robot.position.move(row_delta, col_delta)

        if not board.is_valid_position(target_position):
            raise InvalidDropException("Cannot drop flower outside the board")

        if not board.is_empty(target_position):
            raise InvalidDropException("Target cell is not empty")

        # Drop the flower
        action = board.robot.drop_flower(target_position)
        if action.message:
            raise InvalidDropException(action.message)

        board.board.drop_flower(target_position)  # Add to board
        board.update_timestamp()

    @staticmethod
    def give_flowers(board: Game) -> None:
        """Give flowers to the princess."""
        if board.get_status() != GameStatus.IN_PROGRESS:
            raise GameOverException("Game is already over")

        if len(board.robot.flowers_collected) == 0:
            raise InvalidGiveException("Robot has no flowers to give")

        # Get position in front of robot
        row_delta, col_delta = board.robot.orientation.get_delta()
        target_position = board.robot.position.move(row_delta, col_delta)

        if not board.is_valid_position(target_position):
            raise InvalidGiveException("No princess in that direction")

        if target_position != board.princess.position:
            raise InvalidGiveException("Princess is not at target position")

        # Count flowers before giving
        flowers_count = len(board.robot.flowers_collected)

        # Give flowers
        action = board.robot.give_flowers(target_position)
        if action.message:
            raise InvalidGiveException(action.message)

        board.princess.receive_flowers(board.robot.flowers_delivered)
        board.flowers_delivered += flowers_count  # Update game-level counter
        board.update_timestamp()

    @staticmethod
    def clean_obstacle(board: Game) -> None:
        """Clean an obstacle in the direction faced."""
        if board.get_status() != GameStatus.IN_PROGRESS:
            raise GameOverException("Game is already over")

        if not board.robot.can_clean():
            raise InvalidCleanException("Cannot clean while holding flowers")

        # Get position in front of robot
        row_delta, col_delta = board.robot.orientation.get_delta()
        target_position = board.robot.position.move(row_delta, col_delta)

        if not board.is_valid_position(target_position):
            raise InvalidCleanException("No obstacle to clean in that direction")

        if target_position not in board.obstacles:
            raise InvalidCleanException("No obstacle at target position")

        # Remove obstacle
        action = board.robot.clean_obstacle(target_position)
        if action.message:
            raise InvalidCleanException(action.message)

        board.board.clean_obstacle(target_position)  # Remove from board
        board.update_timestamp()
