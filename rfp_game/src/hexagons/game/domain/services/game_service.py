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
    def rotate_robot(game: Game, direction: Direction) -> None:
        """Rotate the robot to face a direction."""
        logger.info("rotate_robot: game_id=%r direction=%s", getattr(game, "id", None), direction)
        if game.get_status() != GameStatus.IN_PROGRESS:
            raise GameOverException("Game is already over")

        action = game.robot.rotate(direction)
        if action.message:
            raise InvalidRotationException(action.message)

        game.update_timestamp()

    @staticmethod
    def move_robot(game: Game) -> None:
        """Move the robot in the direction it's facing."""
        if game.get_status() != GameStatus.IN_PROGRESS:
            raise GameOverException("Game is already over")

        # Calculate new position based on orientation
        row_delta, col_delta = game.robot.orientation.get_delta()
        new_position = game.robot.position.move(row_delta, col_delta)

        # Validate move
        if not game.is_valid_position(new_position):
            raise InvalidMoveException("Move would go outside the board")

        if not game.is_empty(new_position):
            cell_type = game.get_cell_type(new_position)
            raise InvalidMoveException(f"Target cell is blocked by {cell_type.value}")

        # Execute move
        action = game.robot.move_to(new_position)
        if action.message:
            raise InvalidMoveException(action.message)

        game.board.move_robot(new_position)  # Update board position
        game.update_timestamp()

    @staticmethod
    def pick_flower(game: Game) -> None:
        """Pick a flower from an adjacent cell."""
        if game.get_status() != GameStatus.IN_PROGRESS:
            raise GameOverException("Game is already over")

        if not game.robot.can_pick():
            raise InvalidPickException(f"Robot cannot hold more than {game.robot.max_flowers} flowers")

        # Get position in front of robot
        row_delta, col_delta = game.robot.orientation.get_delta()
        target_position = game.robot.position.move(row_delta, col_delta)

        if not game.is_valid_position(target_position):
            raise InvalidPickException("No flower to pick in that direction")

        if target_position not in game.flowers:
            raise InvalidPickException("No flower at target position")

        # Pick the flower
        action = game.robot.pick_flower(target_position)
        if action.message:
            raise InvalidPickException(action.message)

        game.board.pick_flower(target_position)  # Remove from board
        game.update_timestamp()

    @staticmethod
    def drop_flower(game: Game) -> None:
        """Drop a flower on an adjacent empty cell."""
        if game.get_status() != GameStatus.IN_PROGRESS:
            raise GameOverException("Game is already over")

        if game.robot.flowers_held == 0:
            raise InvalidDropException("Robot has no flowers to drop")

        # Get position in front of robot
        row_delta, col_delta = game.robot.orientation.get_delta()
        target_position = game.robot.position.move(row_delta, col_delta)

        if not game.is_valid_position(target_position):
            raise InvalidDropException("Cannot drop flower outside the board")

        if not game.is_empty(target_position):
            raise InvalidDropException("Target cell is not empty")

        # Drop the flower
        action = game.robot.drop_flower(target_position)
        if action.message:
            raise InvalidDropException(action.message)

        game.board.drop_flower(target_position)  # Add to board
        game.update_timestamp()

    @staticmethod
    def give_flowers(game: Game) -> None:
        """Give flowers to the princess."""
        if game.get_status() != GameStatus.IN_PROGRESS:
            raise GameOverException("Game is already over")

        if len(game.robot.flowers_collected) == 0:
            raise InvalidGiveException("Robot has no flowers to give")

        # Get position in front of robot
        row_delta, col_delta = game.robot.orientation.get_delta()
        target_position = game.robot.position.move(row_delta, col_delta)

        if not game.is_valid_position(target_position):
            raise InvalidGiveException("No princess in that direction")

        if target_position != game.princess.position:
            raise InvalidGiveException("Princess is not at target position")

        # Count flowers before giving
        flowers_count = len(game.robot.flowers_collected)

        # Give flowers
        action = game.robot.give_flowers(target_position)
        if action.message:
            raise InvalidGiveException(action.message)

        game.princess.receive_flowers(game.robot.flowers_delivered)
        game.flowers_delivered += flowers_count  # Update game-level counter
        game.update_timestamp()

    @staticmethod
    def clean_obstacle(game: Game) -> None:
        """Clean an obstacle in the direction faced."""
        if game.get_status() != GameStatus.IN_PROGRESS:
            raise GameOverException("Game is already over")

        if not game.robot.can_clean():
            raise InvalidCleanException("Cannot clean while holding flowers")

        # Get position in front of robot
        row_delta, col_delta = game.robot.orientation.get_delta()
        target_position = game.robot.position.move(row_delta, col_delta)

        if not game.is_valid_position(target_position):
            raise InvalidCleanException("No obstacle to clean in that direction")

        if target_position not in game.obstacles:
            raise InvalidCleanException("No obstacle at target position")

        # Remove obstacle
        action = game.robot.clean_obstacle(target_position)
        if action.message:
            raise InvalidCleanException(action.message)

        game.board.clean_obstacle(target_position)  # Remove from board
        game.update_timestamp()
