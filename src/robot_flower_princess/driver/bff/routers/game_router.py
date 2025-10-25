from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Any, cast
from shared.logging import get_logger

from ..schemas.game_schema import (
    CreateGameRequest,
    ActionRequest,
    ActionType,
    GameStateResponse,
    ActionResponse,
    GameHistoryResponse,
    GamesResponse,
)
from ....configurator.dependencies import get_game_repository
from ....domain.ports.game_repository import GameRepository
from ....domain.use_cases.create_game import CreateGameUseCase, CreateGameCommand
from ....domain.use_cases.get_game_state import GetGameStateUseCase, GetGameStateQuery
from ....domain.use_cases.get_game_history import GetGameHistoryUseCase, GetGameHistoryQuery
from ....domain.use_cases.rotate_robot import RotateRobotUseCase, RotateRobotCommand
from ....domain.use_cases.move_robot import MoveRobotUseCase, MoveRobotCommand
from ....domain.use_cases.pick_flower import PickFlowerUseCase, PickFlowerCommand
from ....domain.use_cases.drop_flower import DropFlowerUseCase, DropFlowerCommand
from ....domain.use_cases.give_flowers import GiveFlowersUseCase, GiveFlowersCommand
from ....domain.use_cases.clean_obstacle import CleanObstacleUseCase, CleanObstacleCommand
from ....domain.use_cases.get_games import GetGamesResult, GetGamesUseCase, GetGamesQuery
from ....domain.core.value_objects.direction import Direction
from ....domain.use_cases.autoplay import AutoplayResult
from ....domain.use_cases.create_game import CreateGameResult
from ....domain.use_cases.get_game_state import GetGameStateResult
from ....domain.use_cases.get_game_history import GetGameHistoryResult


router = APIRouter(prefix="/api/games", tags=["games"])

logger = get_logger("game_router")


def obstacles_to_dict(obstacles: set, robot) -> dict:
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


@router.post("/", response_model=GameStateResponse, status_code=201)
def create_game(
    request: CreateGameRequest,
    repository: GameRepository = Depends(get_game_repository),
) -> GameStateResponse:
    """Create a new game with specified board size."""

    logger.info("get_games: rows=%s cols=%s", request.rows, request.cols)

    try:
        use_case = CreateGameUseCase(repository)
        result: CreateGameResult = use_case.execute(
            CreateGameCommand(rows=request.rows, cols=request.cols, name=request.name)
        )

        # Convert Board, Robot, Princess objects to dicts for the API response
        board_dict = result.board.to_dict(
            robot_pos=result.robot.position,
            princess_pos=result.princess.position,
            flowers=result.flowers,
            obstacles=result.obstacles,
        )

        return GameStateResponse(
            id=result.game_id,
            message=result.message,
            status=result.status,
            board=board_dict,
            robot=result.robot.to_dict(),
            princess=result.princess.to_dict(),
            obstacles=obstacles_to_dict(result.obstacles, result.robot),
            flowers=flowers_to_dict(result.flowers),
            created_at=result.created_at.isoformat() + "Z",
            updated_at=result.updated_at.isoformat() + "Z",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


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

        # Convert dataclass GameSummary to Pydantic GameSummary
        from ..schemas.game_schema import GameSummary as PydanticGameSummary

        pydantic_games = []
        for game_summary in result.games:
            # Get the full game from the repository to access all fields
            game = repository.get(game_summary.game_id)
            if game:
                board_dict = game_summary.board.to_dict(
                    robot_pos=game.robot.position,
                    princess_pos=game.princess.position,
                    flowers=game.flowers,
                    obstacles=game.obstacles,
                )
                pydantic_games.append(
                    PydanticGameSummary(
                        id=game_summary.game_id,
                        status=game_summary.status,
                        created_at=game_summary.created_at.isoformat() + "Z",
                        updated_at=game_summary.updated_at.isoformat() + "Z",
                        board=board_dict,
                        robot=game.robot.to_dict(),
                        princess=game.princess.to_dict(),
                        obstacles=obstacles_to_dict(game.obstacles, game.robot),
                        flowers=flowers_to_dict(game.flowers, game.initial_flower_count),
                    )
                )

        return GamesResponse(gamess=pydantic_games, total=len(pydantic_games))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{game_id}", response_model=GameStateResponse)
def get_game_state(
    game_id: str,
    repository: GameRepository = Depends(get_game_repository),
) -> GameStateResponse:
    """Get the current state of a game."""

    logger.info("get_game_state: game_id=%s", game_id)

    try:
        use_case = GetGameStateUseCase(repository)
        result: GetGameStateResult = use_case.execute(GetGameStateQuery(game_id=game_id))
        if result is None:
            raise HTTPException(status_code=404, detail=f"Game {game_id} not found")

        # Convert Board, Robot, Princess objects to dicts for the API response
        board_dict = result.board.to_dict(
            robot_pos=result.robot.position,
            princess_pos=result.princess.position,
            flowers=result.flowers,
            obstacles=result.obstacles,
        )

        # Get the full game object to access created_at and updated_at
        game = repository.get(game_id)

        return GameStateResponse(
            id=game_id,
            status=result.status,
            message="Game state retrieved successfully",
            board=board_dict,
            robot=result.robot.to_dict(),
            princess=result.princess.to_dict(),
            obstacles=obstacles_to_dict(result.obstacles, result.robot),
            flowers=flowers_to_dict(result.flowers),
            created_at=game.created_at.isoformat() + "Z",
            updated_at=game.updated_at.isoformat() + "Z",
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{game_id}/history", response_model=GameHistoryResponse)
def get_game_history(
    game_id: str,
    repository: GameRepository = Depends(get_game_repository),
) -> GameHistoryResponse:
    """Get the history of a game."""

    logger.info("get_game_history: game_id=%s", game_id)

    try:
        use_case = GetGameHistoryUseCase(repository)
        result: GetGameHistoryResult = use_case.execute(GetGameHistoryQuery(game_id=game_id))
        return GameHistoryResponse(
            id=game_id,
            history=result.history.to_dict(),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


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
                    "value": {"action": "rotate", "direction": "south"},
                },
                "move": {
                    "summary": "Move robot",
                    "value": {"action": "move", "direction": "south"},
                },
                "pickFlower": {
                    "summary": "Pick a flower",
                    "value": {"action": "pickFlower", "direction": "south"},
                },
                "dropFlower": {
                    "summary": "Drop a flower",
                    "value": {"action": "dropFlower", "direction": "south"},
                },
                "giveFlower": {
                    "summary": "Give flowers",
                    "value": {"action": "giveFlower", "direction": "south"},
                },
                "clean": {
                    "summary": "Clean obstacle",
                    "value": {"action": "clean", "direction": "south"},
                },
            },
        ),
    ),
    repository: GameRepository = Depends(get_game_repository),
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

        if action == ActionType.rotate:
            use_case = RotateRobotUseCase(repository)
            result = use_case.execute(RotateRobotCommand(game_id=game_id, direction=direction))
        elif action == ActionType.move:
            use_case = MoveRobotUseCase(repository)
            result = use_case.execute(MoveRobotCommand(game_id=game_id, direction=direction))
        elif action == ActionType.pickFlower:
            use_case = PickFlowerUseCase(repository)
            result = use_case.execute(PickFlowerCommand(game_id=game_id, direction=direction))
        elif action == ActionType.dropFlower:
            use_case = DropFlowerUseCase(repository)
            result = use_case.execute(DropFlowerCommand(game_id=game_id, direction=direction))
        elif action == ActionType.giveFlower:
            use_case = GiveFlowersUseCase(repository)
            result = use_case.execute(GiveFlowersCommand(game_id=game_id, direction=direction))
        elif action == ActionType.clean:
            use_case = CleanObstacleUseCase(repository)
            result = use_case.execute(CleanObstacleCommand(game_id=game_id, direction=direction))
        else:
            raise ValueError(f"Unknown action: {action}")

        # Convert Board, Robot, Princess objects to dicts for the API response
        board_dict = result.board.to_dict(
            robot_pos=result.robot.position,
            princess_pos=result.princess.position,
            flowers=result.flowers,
            obstacles=result.obstacles,
        )

        return ActionResponse(
            success=result.success,
            id=game_id,
            status=result.status,
            board=board_dict,
            robot=result.robot.to_dict(),
            princess=result.princess.to_dict(),
            obstacles=obstacles_to_dict(result.obstacles, result.robot),
            flowers=flowers_to_dict(result.flowers),
            message=result.message,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{game_id}/autoplay", response_model=ActionResponse)
def autoplay(
    game_id: str,
    repository: GameRepository = Depends(get_game_repository),
) -> ActionResponse:
    """Let AI solve the game automatically."""

    logger.info("autoplay: game_id=%s", game_id)

    try:
        from ....domain.use_cases.autoplay import AutoplayUseCase, AutoplayCommand

        use_case = AutoplayUseCase(repository)
        result: AutoplayResult = use_case.execute(AutoplayCommand(game_id=game_id))

        # Convert Board, Robot, Princess objects to dicts for the API response
        board_dict = result.board.to_dict(
            robot_pos=result.robot.position,
            princess_pos=result.princess.position,
            flowers=result.flowers,
            obstacles=result.obstacles,
        )

        return ActionResponse(
            success=result.success,
            id=game_id,
            status=result.status,
            board=board_dict,
            robot=result.robot.to_dict(),
            princess=result.princess.to_dict(),
            obstacles=obstacles_to_dict(result.obstacles, result.robot),
            flowers=flowers_to_dict(result.flowers),
            message=f"{result.message} (Actions taken: {result.actions_taken})",
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
