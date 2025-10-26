from fastapi import APIRouter, Depends, HTTPException, Query
from shared.logging import get_logger
from configurator.dependencies import get_game_repository, get_ml_player_client
from hexagons.game.domain.ports.game_repository import GameRepository
from hexagons.aiplayer.domain.ports.ml_player_client import MLPlayerClientPort
from hexagons.aiplayer.domain.use_cases.autoplay import (
    AutoplayUseCase,
    AutoplayCommand,
    AutoplayResult,
    AIStrategy,
)
from hexagons.game.driver.bff.schemas.game_schema import ActionResponse

router = APIRouter(prefix="/api/games", tags=["aiplayer"])

logger = get_logger("aiplayer_router")


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


@router.post("/{game_id}/autoplay", response_model=ActionResponse)
async def autoplay(
    game_id: str,
    strategy: AIStrategy = Query(
        default="greedy",
        description="AI strategy: 'greedy' (safe, 75% success), 'optimal' (fast, 62% success, -25% actions), or 'ml' (hybrid ML/heuristic)",
    ),
    repository: GameRepository = Depends(get_game_repository),
    ml_client: MLPlayerClientPort = Depends(get_ml_player_client),
) -> ActionResponse:
    """
    Let AI solve the game automatically.

    Three strategies available:
    - **greedy** (default): Safe & reliable. 75% success rate. Checks safety before picking flowers.
    - **optimal**: Fast & efficient. 62% success rate, but 25% fewer actions. Uses A* pathfinding and multi-step planning.
    - **ml**: Hybrid ML/heuristic approach. Uses ML Player service for predictions. Learns from game patterns.
    """

    logger.info("autoplay: game_id=%s strategy=%s", game_id, strategy)

    try:
        use_case = AutoplayUseCase(repository, ml_client)
        result: AutoplayResult = await use_case.execute(
            AutoplayCommand(game_id=game_id, strategy=strategy)
        )

        return ActionResponse(
            success=result.success,
            game=result.game.to_dict(),
            message=f"{result.message} (Actions taken: {result.actions_taken})",
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
