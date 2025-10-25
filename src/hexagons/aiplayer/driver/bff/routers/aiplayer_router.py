from fastapi import APIRouter, Depends, HTTPException
from shared.logging import get_logger
from configurator.dependencies import get_game_repository
from hexagons.game.domain.ports.game_repository import GameRepository
from hexagons.aiplayer.domain.use_cases.autoplay import AutoplayUseCase, AutoplayCommand, AutoplayResult
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
def autoplay(
    game_id: str,
    repository: GameRepository = Depends(get_game_repository),
) -> ActionResponse:
    """Let AI solve the game automatically."""

    logger.info("autoplay: game_id=%s", game_id)

    try:
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
