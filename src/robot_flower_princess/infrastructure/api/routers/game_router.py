from fastapi import APIRouter, Depends, HTTPException
from ..schemas.game_schema import (
    CreateGameRequest,
    RotateRequest,
    GameStateResponse,
    ActionResponse,
    GameHistoryResponse,
    EndedGamesResponse,
)
from ..dependencies import get_game_repository
from ....application.ports.game_repository import GameRepository
from ....application.use_cases.create_game import CreateGameUseCase, CreateGameCommand
from ....application.use_cases.get_game_state import GetGameStateUseCase, GetGameStateQuery
from ....application.use_cases.get_game_history import GetGameHistoryUseCase, GetGameHistoryQuery
from ....application.use_cases.rotate_robot import RotateRobotUseCase, RotateRobotCommand
from ....application.use_cases.move_robot import MoveRobotUseCase, MoveRobotCommand
from ....application.use_cases.pick_flower import PickFlowerUseCase, PickFlowerCommand
from ....application.use_cases.drop_flower import DropFlowerUseCase, DropFlowerCommand
from ....application.use_cases.give_flowers import GiveFlowersUseCase, GiveFlowersCommand
from ....application.use_cases.clean_obstacle import CleanObstacleUseCase, CleanObstacleCommand
from ....application.use_cases.get_ended_games import GetEndedGamesUseCase, GetEndedGamesQuery
from ....domain.value_objects.direction import Direction

router = APIRouter(prefix="/api/games", tags=["games"])


@router.post("/", response_model=GameStateResponse, status_code=201)
def create_game(
    request: CreateGameRequest,
    repository: GameRepository = Depends(get_game_repository),
) -> GameStateResponse:
    """Create a new game with specified board size."""
    try:
        use_case = CreateGameUseCase(repository)
        result = use_case.execute(
            CreateGameCommand(rows=request.rows, cols=request.cols)
        )
        return GameStateResponse(
            game_id=result.game_id,
            board=result.board_state,
            message="Game created successfully",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=EndedGamesResponse)
def get_ended_games(
    limit: int = 10,
    repository: GameRepository = Depends(get_game_repository),
) -> EndedGamesResponse:
    """Get the last N games that have ended (victory or game_over)."""
    try:
        use_case = GetEndedGamesUseCase(repository)
        result = use_case.execute(GetEndedGamesQuery(limit=limit))
        return EndedGamesResponse(
            games=result.games,
            total=len(result.games)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{game_id}", response_model=GameStateResponse)
def get_game_state(
    game_id: str,
    repository: GameRepository = Depends(get_game_repository),
) -> GameStateResponse:
    """Get the current state of a game."""
    try:
        use_case = GetGameStateUseCase(repository)
        result = use_case.execute(GetGameStateQuery(game_id=game_id))
        return GameStateResponse(
            game_id=game_id,
            board=result.board_state,
            message="Game state retrieved successfully",
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{game_id}/history", response_model=GameHistoryResponse)
def get_game_history(
    game_id: str,
    repository: GameRepository = Depends(get_game_repository),
) -> GameHistoryResponse:
    """Get the history of a game."""
    try:
        use_case = GetGameHistoryUseCase(repository)
        result = use_case.execute(GetGameHistoryQuery(game_id=game_id))
        return GameHistoryResponse(
            game_id=game_id,
            history=result.history,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{game_id}/actions/rotate", response_model=ActionResponse)
def rotate_robot(
    game_id: str,
    request: RotateRequest,
    repository: GameRepository = Depends(get_game_repository),
) -> ActionResponse:
    """Rotate the robot to face a direction."""
    try:
        use_case = RotateRobotUseCase(repository)
        direction = Direction(request.direction)
        result = use_case.execute(
            RotateRobotCommand(game_id=game_id, direction=direction)
        )
        return ActionResponse(
            success=result.success,
            game_id=game_id,
            board=result.board_state,
            message=result.message,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{game_id}/actions/move", response_model=ActionResponse)
def move_robot(
    game_id: str,
    repository: GameRepository = Depends(get_game_repository),
) -> ActionResponse:
    """Move the robot in the direction it's facing."""
    try:
        use_case = MoveRobotUseCase(repository)
        result = use_case.execute(MoveRobotCommand(game_id=game_id))
        return ActionResponse(
            success=result.success,
            game_id=game_id,
            board=result.board_state,
            message=result.message,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{game_id}/actions/pick", response_model=ActionResponse)
def pick_flower(
    game_id: str,
    repository: GameRepository = Depends(get_game_repository),
) -> ActionResponse:
    """Pick a flower from an adjacent cell."""
    try:
        use_case = PickFlowerUseCase(repository)
        result = use_case.execute(PickFlowerCommand(game_id=game_id))
        return ActionResponse(
            success=result.success,
            game_id=game_id,
            board=result.board_state,
            message=result.message,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{game_id}/actions/drop", response_model=ActionResponse)
def drop_flower(
    game_id: str,
    repository: GameRepository = Depends(get_game_repository),
) -> ActionResponse:
    """Drop a flower on an adjacent empty cell."""
    try:
        use_case = DropFlowerUseCase(repository)
        result = use_case.execute(DropFlowerCommand(game_id=game_id))
        return ActionResponse(
            success=result.success,
            game_id=game_id,
            board=result.board_state,
            message=result.message,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{game_id}/actions/give", response_model=ActionResponse)
def give_flowers(
    game_id: str,
    repository: GameRepository = Depends(get_game_repository),
) -> ActionResponse:
    """Give flowers to the princess."""
    try:
        use_case = GiveFlowersUseCase(repository)
        result = use_case.execute(GiveFlowersCommand(game_id=game_id))
        return ActionResponse(
            success=result.success,
            game_id=game_id,
            board=result.board_state,
            message=result.message,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{game_id}/actions/clean", response_model=ActionResponse)
def clean_obstacle(
    game_id: str,
    repository: GameRepository = Depends(get_game_repository),
) -> ActionResponse:
    """Clean an obstacle in the direction faced."""
    try:
        use_case = CleanObstacleUseCase(repository)
        result = use_case.execute(CleanObstacleCommand(game_id=game_id))
        return ActionResponse(
            success=result.success,
            game_id=game_id,
            board=result.board_state,
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
    try:
        from ....application.use_cases.autoplay import AutoplayUseCase, AutoplayCommand
        use_case = AutoplayUseCase(repository)
        result = use_case.execute(AutoplayCommand(game_id=game_id))
        return ActionResponse(
            success=result.success,
            game_id=game_id,
            board=result.board_state,
            message=f"{result.message} (Actions taken: {result.actions_taken})",
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
