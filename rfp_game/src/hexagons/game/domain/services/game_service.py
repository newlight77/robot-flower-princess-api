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
        logger.info("GameService.rotate_robot: game_id=%r direction=%r", game.game_id, direction)
        if game.get_status() != GameStatus.IN_PROGRESS:
            raise GameOverException(
                f"GameService.rotate_robot: Game is already over in direction={game.robot.orientation}"
            )

        if direction not in [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]:
            raise InvalidRotationException(f"GameService.rotate_robot: Invalid direction={direction}")

        action = game.robot.rotate(direction)
        if action.message:
            raise InvalidRotationException(f"GameService.rotate_robot: {action.message}")

        game.update_timestamp()
        logger.info("GameService.rotate_robot: game_id=%r action=%r", game.game_id, action)
        logger.info(
            "GameService.rotate_robot: game_id=%r game.robot.orientation=%r", game.game_id, game.robot.orientation
        )

    @staticmethod
    def move_robot(game: Game) -> None:
        """Move the robot in the direction it's facing."""
        logger.info(
            "GameService.move_robot: game_id=%r game.robot.orientation=%r", game.game_id, game.robot.orientation
        )

        if game.get_status() != GameStatus.IN_PROGRESS:
            logger.info(
                "GameService.move_robot: game_id=%r game.robot.orientation=%r game.robot.position=%r Game is already over",
                game.game_id,
                game.robot.orientation,
                game.robot.position,
            )
            raise GameOverException(
                f"GameService.move_robot: Game is already over in direction={game.robot.orientation} position={game.robot.position}"
            )

        # Calculate new position based on orientation
        row_delta, col_delta = game.robot.orientation.get_delta()
        new_position = game.robot.position.move(row_delta, col_delta)

        logger.info("GameService.move_robot: game_id=%r new_position=%r", game.game_id, new_position)

        # Validate move
        if not game.is_valid_position(new_position):
            logger.info("GameService.move_robot: game_id=%r new_position=%r is not valid", game.game_id, new_position)
            raise InvalidMoveException(
                f"GameService.move_robot: Move would go outside the board in direction={game.robot.orientation} position={new_position}"
            )

        if not game.is_empty(new_position):
            logger.info("GameService.move_robot: game_id=%r new_position=%r is not empty", game.game_id, new_position)
            cell_type = game.get_cell_type(new_position)
            raise InvalidMoveException(
                f"GameService.move_robot: Target cell is blocked by {cell_type.value} in direction={game.robot.orientation} position={new_position}"
            )

        # Execute move
        action = game.robot.move_to(new_position)
        if action.message:
            logger.info("GameService.move_robot: game_id=%r action.message=%r", game.game_id, action.message)
            raise InvalidMoveException(action.message)

        logger.info("GameService.move_robot: game_id=%r action=%r", game.game_id, action)

        game.board.move_robot(new_position)  # Update board position
        game.update_timestamp()

        logger.info("GameService.move_robot: game_id=%r", game.game_id)
        logger.info("GameService.move_robot: game_id=%r action=%r", game.game_id, action)
        logger.info("GameService.move_robot: game_id=%r game.robot.position=%r", game.game_id, game.robot.position)
        logger.info(
            "GameService.move_robot: game_id=%r game.robot.orientation=%r", game.game_id, game.robot.orientation
        )

    @staticmethod
    def pick_flower(game: Game) -> None:
        """Pick a flower from an adjacent cell."""
        logger.info("GameService.pick_flower: game_id=%r", game.game_id)

        if game.get_status() != GameStatus.IN_PROGRESS:
            raise GameOverException(
                f"GameService.pick_flower: Game is already over in direction={game.robot.orientation}"
            )

        if not game.robot.can_pick():
            raise InvalidPickException(
                f"GameService.pick_flower: Robot cannot hold more than {game.robot.max_flowers} flowers in direction={game.robot.orientation}"
            )

        # Get position in front of robot
        row_delta, col_delta = game.robot.orientation.get_delta()
        target_position = game.robot.position.move(row_delta, col_delta)

        if not game.is_valid_position(target_position):
            raise InvalidPickException(
                f"GameService.pick_flower: No flower to pick in that direction={game.robot.orientation} position={target_position}"
            )

        if target_position not in game.flowers:
            raise InvalidPickException(
                f"GameService.pick_flower: No flower in direction={game.robot.orientation} position={target_position}"
            )

        # Pick the flower
        action = game.robot.pick_flower(target_position)
        if action.message:
            raise InvalidPickException(f"GameService.pick_flower: {action.message}")

        game.board.pick_flower(target_position)  # Remove from board
        game.update_timestamp()

        logger.info("GameService.pick_flower: game_id=%r action=%r", game.game_id, action)
        logger.info(
            "GameService.pick_flower: game_id=%r game.robot.flowers_collected=%r",
            game.game_id,
            game.robot.flowers_collected,
        )

    @staticmethod
    def drop_flower(game: Game) -> None:
        """Drop a flower on an adjacent empty cell."""
        logger.info("GameService.drop_flower: game_id=%r", game.game_id)

        if game.get_status() != GameStatus.IN_PROGRESS:
            raise GameOverException(
                f"GameService.drop_flower: Game is already over in direction={game.robot.orientation}"
            )

        if game.robot.flowers_held == 0:
            raise InvalidDropException(
                f"GameService.drop_flower: Robot has no flowers to drop in direction={game.robot.orientation}"
            )

        # Get position in front of robot
        row_delta, col_delta = game.robot.orientation.get_delta()
        target_position = game.robot.position.move(row_delta, col_delta)

        if not game.is_valid_position(target_position):
            raise InvalidDropException(
                f"GameService.drop_flower: Cannot drop flower outside the board in direction={game.robot.orientation} position={target_position}",
                game.robot.orientation,
                target_position,
            )

        if not game.is_empty(target_position):
            raise InvalidDropException(
                f"GameService.drop_flower: Target cell is not empty in direction={game.robot.orientation} position={target_position}"
            )

        # Drop the flower
        action = game.robot.drop_flower(target_position)
        if action.message:
            raise InvalidDropException(f"GameService.drop_flower: {action.message}")

        game.board.drop_flower(target_position)  # Add to board
        game.update_timestamp()

        logger.info("GameService.drop_flower: game_id=%r action=%r", game.game_id, action)
        logger.info(
            "GameService.drop_flower: game_id=%r game.robot.flowers_collected=%r",
            game.game_id,
            game.robot.flowers_collected,
        )

    @staticmethod
    def give_flowers(game: Game) -> None:
        """Give flowers to the princess."""
        logger.info("GameService.give_flowers: game_id=%r", game.game_id)
        if game.get_status() != GameStatus.IN_PROGRESS:
            raise GameOverException(
                f"GameService.give_flowers: Game is already over in direction={game.robot.orientation}"
            )

        if len(game.robot.flowers_collected) == 0:
            raise InvalidGiveException(
                f"GameService.give_flowers: Robot has no flowers to give in direction={game.robot.orientation}"
            )

        # Get position in front of robot
        row_delta, col_delta = game.robot.orientation.get_delta()
        target_position = game.robot.position.move(row_delta, col_delta)

        if not game.is_valid_position(target_position):
            raise InvalidGiveException(
                f"GameService.give_flowers: No princess in that direction={game.robot.orientation} position={target_position}"
            )

        if target_position != game.princess.position:
            raise InvalidGiveException(
                f"GameService.give_flowers: Princess is not at target direction={game.robot.orientation} position={target_position}"
            )

        # Count flowers before giving
        flowers_count = len(game.robot.flowers_collected)

        # Give flowers
        action = game.robot.give_flowers(target_position)
        if action.message:
            raise InvalidGiveException(f"GameService.give_flowers: {action.message}")

        game.princess.receive_flowers(game.robot.flowers_delivered)
        game.flowers_delivered += flowers_count  # Update game-level counter
        game.update_timestamp()

        logger.info("GameService.give_flowers: game_id=%r action=%r", game.game_id, action)
        logger.info(
            "GameService.give_flowers: game_id=%r game.robot.flowers_delivered=%r",
            game.game_id,
            game.robot.flowers_delivered,
        )
        logger.info(
            "GameService.give_flowers: game_id=%r game.robot.flowers_collected=%r",
            game.game_id,
            game.robot.flowers_collected,
        )

    @staticmethod
    def clean_obstacle(game: Game) -> None:
        """Clean an obstacle in the direction faced."""
        logger.info("GameService.clean_obstacle: game_id=%r", game.game_id)

        if game.get_status() != GameStatus.IN_PROGRESS:
            logger.info("GameService.clean_obstacle: Game is already over=%r", game.get_status())
            raise GameOverException(
                f"GameService.clean_obstacle: Game is already over in direction={game.robot.orientation}"
            )

        if not game.robot.can_clean():
            logger.info("GameService.clean_obstacle: Cannot clean while holding flowers=%r", game.robot.flowers_held)
            raise InvalidCleanException(
                f"GameService.clean_obstacle: Cannot clean while holding flowers={game.robot.flowers_held} in direction={game.robot.orientation}"
            )

        # Get position in front of robot
        row_delta, col_delta = game.robot.orientation.get_delta()
        target_position = game.robot.position.move(row_delta, col_delta)

        if not game.is_valid_position(target_position):
            logger.info(
                "GameService.clean_obstacle: game_id=%r No obstacle to clean in that direction=%r position=%r",
                game.game_id,
                game.robot.orientation,
                target_position,
            )
            raise InvalidCleanException(
                f"GameService.clean_obstacle: No obstacle to clean in that direction={game.robot.orientation} position={target_position}"
            )

        if target_position not in game.obstacles:
            logger.info(
                "GameService.clean_obstacle: game_id=%r No obstacle in direction=%r position=%r",
                game.game_id,
                game.robot.orientation,
                target_position,
            )
            raise InvalidCleanException(
                f"GameService.clean_obstacle: No obstacle in direction={game.robot.orientation} position={target_position}"
            )

        # Remove obstacle
        action = game.robot.clean_obstacle(target_position)
        if action.message:
            logger.info("GameService.clean_obstacle: game_id=%r action.message=%r", game.game_id, action.message)
            raise InvalidCleanException(f"GameService.clean_obstacle: {action.message}")

        game.board.clean_obstacle(target_position)  # Remove from board
        game.update_timestamp()

        logger.info("GameService.clean_obstacle: game_id=%r action=%r", game.game_id, action)
        logger.info(
            "GameService.clean_obstacle: game_id=%r game.robot.flowers_collected=%r",
            game.game_id,
            game.robot.flowers_collected,
        )
        logger.info(
            "GameService.clean_obstacle: game_id=%r game.robot.obstacles_cleaned=%r",
            game.game_id,
            game.robot.obstacles_cleaned,
        )
