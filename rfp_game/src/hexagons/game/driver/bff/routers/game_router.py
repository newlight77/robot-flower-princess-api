from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Any, cast
from shared.logging import get_logger

from ..schemas.game_schema import (
    CreateGameRequest,
    CreateGameResponse,
    ActionRequest,
    ActionType,
    GetGameResponse,
    ActionResponse,
    GamesResponse,
)
from configurator.dependencies import get_game_repository, get_mltraining_data_collector
from ....domain.ports.game_repository import GameRepository
from ....domain.ports.mltraining_data_collector import MLTrainingDataCollectorPort
from ....domain.use_cases.create_game import CreateGameUseCase, CreateGameCommand
from ....domain.use_cases.get_game_state import GetGameStateUseCase, GetGameStateQuery
from ....domain.use_cases.rotate_robot import RotateRobotUseCase, RotateRobotCommand
from ....domain.use_cases.move_robot import MoveRobotUseCase, MoveRobotCommand
from ....domain.use_cases.pick_flower import PickFlowerUseCase, PickFlowerCommand
from ....domain.use_cases.drop_flower import DropFlowerUseCase, DropFlowerCommand
from ....domain.use_cases.give_flowers import GiveFlowersUseCase, GiveFlowersCommand
from ....domain.use_cases.clean_obstacle import CleanObstacleUseCase, CleanObstacleCommand
from ....domain.use_cases.get_games import GetGamesResult, GetGamesUseCase, GetGamesQuery
from ....domain.core.value_objects.direction import Direction
from ....domain.core.entities.position import Position
from ....domain.core.entities.robot import Robot
from ....domain.use_cases.create_game import CreateGameResult
from ....domain.use_cases.get_game_state import GetGameStateResult


router = APIRouter(prefix="/api/games", tags=["games"])

logger = get_logger("game_router")


def obstacles_to_dict(obstacles: set[Position], robot: Robot) -> dict:
    """Convert obstacles set to API dict format."""
    return {
        "remaining": len(obstacles),
        "total": len(obstacles) + len(robot.obstacles_cleaned),
    }


def flowers_to_dict(flowers: set, total: int = None) -> dict:
    """Convert flowers set to API dict format."""
    return {
        "remaining": len(flowers),
        "total": total if total is not None else len(flowers),
    }


@router.post("/", response_model=CreateGameResponse, status_code=201)
def create_game(
    request: CreateGameRequest,
    repository: GameRepository = Depends(get_game_repository),
) -> CreateGameResponse:
    """Create a new game with specified board size."""

    logger.info("get_games: rows=%s cols=%s", request.rows, request.cols)

    try:
        use_case = CreateGameUseCase(repository)
        result: CreateGameResult = use_case.execute(
            CreateGameCommand(rows=request.rows, cols=request.cols, name=request.name)
        )

        return CreateGameResponse(
            game=result.game.to_dict(),
            message=result.message,
        )
    except ValueError as e:
        logger.error(f"Failed to create game: {e} for request={request}")
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/", response_model=GamesResponse)
def get_games(
    limit: int = 10,
    status: str = "in_progress",
    repository: GameRepository = Depends(get_game_repository),
) -> GamesResponse:
    """Get the last N games, optionally filtered by status."""

    logger.info("get_games: limit=%s status=%s", limit, status)

    try:
        use_case = GetGamesUseCase(repository)
        result: GetGamesResult = use_case.execute(GetGamesQuery(limit=limit, status=status))
        logger.info("get_games: result=%s", result)

        return GamesResponse(
            games=[game.to_dict() for game in result.games],
            total=result.total,
            message=result.message,
        )
    except ValueError as e:
        logger.error(f"Failed to get games: {e} for limit={limit}, status={status}")
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/{game_id}", response_model=GetGameResponse)
def get_game_state(
    game_id: str,
    repository: GameRepository = Depends(get_game_repository),
) -> GetGameResponse:
    """Get the current state of a game."""

    logger.info("get_game_state: game_id=%s", game_id)

    try:
        use_case = GetGameStateUseCase(repository)
        result: GetGameStateResult = use_case.execute(GetGameStateQuery(game_id=game_id))

        return GetGameResponse(
            game=result.game.to_dict(),
            message=f"Game {game_id} state retrieved successfully",
        )

    except ValueError as e:
        logger.error(f"Failed to get game state: {e} for game_id={game_id}")
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/{game_id}/action", response_model=ActionResponse)
def perform_action(
    game_id: str,
    request: ActionRequest = Body(
        ...,
        examples=cast(
            Any,
            {
                "rotate": {
                    "summary": "Rotate robot",
                    "value": {"action": "rotate", "direction": "SOUTH"},
                },
                "move": {
                    "summary": "Move robot",
                    "value": {"action": "move", "direction": "SOUTH"},
                },
                "pickFlower": {
                    "summary": "Pick a flower",
                    "value": {"action": "pickFlower", "direction": "SOUTH"},
                },
                "dropFlower": {
                    "summary": "Drop a flower",
                    "value": {"action": "dropFlower", "direction": "SOUTH"},
                },
                "giveFlower": {
                    "summary": "Give flowers",
                    "value": {"action": "giveFlower", "direction": "SOUTH"},
                },
                "clean": {
                    "summary": "Clean obstacle",
                    "value": {"action": "clean", "direction": "SOUTH"},
                },
            },
        ),
    ),
    repository: GameRepository = Depends(get_game_repository),
    data_collector: MLTrainingDataCollectorPort = Depends(get_mltraining_data_collector),
) -> ActionResponse:
    """Perform an action on the game. The request.action selects the operation.

    If action is 'rotate', provide a 'direction' field.
    """

    logger.info(
        "perform_action: game_id=%s and action=%s and direction=%s",
        game_id,
        request.action.name,
        request.direction,
    )

    try:
        action = request.action

        # direction required for all actions now
        direction = Direction(request.direction)

        # Map action types to string names for data collection
        action_name_map = {
            ActionType.rotate: "rotate",
            ActionType.move: "move",
            ActionType.pickFlower: "pick",
            ActionType.dropFlower: "drop",
            ActionType.giveFlower: "give",
            ActionType.clean: "clean",
        }

        logger.info(f"Action: {action}, Direction: {direction}")

        if action == ActionType.rotate:
            use_case = RotateRobotUseCase(repository, data_collector)
            result = use_case.execute(RotateRobotCommand(game_id=game_id, direction=direction))
        elif action == ActionType.move:
            use_case = MoveRobotUseCase(repository, data_collector)
            result = use_case.execute(MoveRobotCommand(game_id=game_id, direction=direction))
        elif action == ActionType.pickFlower:
            use_case = PickFlowerUseCase(repository, data_collector)
            result = use_case.execute(PickFlowerCommand(game_id=game_id, direction=direction))
        elif action == ActionType.dropFlower:
            use_case = DropFlowerUseCase(repository, data_collector)
            result = use_case.execute(DropFlowerCommand(game_id=game_id, direction=direction))
        elif action == ActionType.giveFlower:
            use_case = GiveFlowersUseCase(repository, data_collector)
            result = use_case.execute(GiveFlowersCommand(game_id=game_id, direction=direction))
        elif action == ActionType.clean:
            use_case = CleanObstacleUseCase(repository, data_collector)
            result = use_case.execute(CleanObstacleCommand(game_id=game_id, direction=direction))
        else:
            raise ValueError(f"Unknown action: {action}")

        return ActionResponse(
            success=result.success,
            game=result.game.to_dict(),
            message=("action performed successfully" if result.success else "failed to perform action"),
        )
    except ValueError as e:
        logger.error(
            f"Failed to perform action: {e} for game_id={game_id}, action={action_name_map[action]}, direction={direction.value}"
        )
        raise HTTPException(status_code=500, detail=str(e)) from e
