"""FastAPI router for ML Player endpoints."""

from fastapi import APIRouter, HTTPException

from hexagons.mlplayer.domain.core.value_objects import StrategyConfig
from hexagons.mlplayer.domain.use_cases.predict_action import (
    PredictActionCommand,
    PredictActionUseCase,
)
from hexagons.mlplayer.driver.bff.schemas.ml_player_schema import (
    PredictActionRequest,
    PredictActionResponse,
    StrategyConfigResponse,
)
from shared.logging import logger

router = APIRouter(prefix="/api/ml-player", tags=["ML Player"])


@router.post("/predict/{game_id}", response_model=PredictActionResponse)
def predict_action(
    game_id: str,
    request: PredictActionRequest,
) -> PredictActionResponse:
    """
    Predict the next best action for a game using ML player.

    Args:
        game_id: Game identifier
        request: Prediction request with game state and strategy

    Returns:
        Predicted action with confidence and metadata

    Raises:
        HTTPException: If prediction fails
    """
    logger.info(f"Predicting action for game_id={game_id} with strategy={request.strategy}")

    try:
        use_case = PredictActionUseCase()
        command = PredictActionCommand(
            strategy=request.strategy,
            game_id=game_id,
            board=request.board,
            robot=request.robot,
            princess=request.princess,
            obstacles=request.obstacles,
            flowers=request.flowers,
        )

        logger.info(f"Executing predict action use case for game_id={game_id} with strategy={request.strategy}")

        result = use_case.execute(command)

        logger.info(f"Predicted action={result.action}, dir={result.direction}, conf={result.confidence:.2f}")

        return PredictActionResponse(
            game_id=game_id,
            action=result.action,
            direction=result.direction,
            confidence=result.confidence,
            board_score=result.board_score,
            config_used=result.config_used,
        )

    except Exception as e:
        logger.error(f"Failed to predict action for game_id={game_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/strategies", response_model=list[StrategyConfigResponse])
async def list_strategies() -> list[StrategyConfigResponse]:
    """
    List available strategies with their configurations.

    Returns:
        List of available strategies
    """
    logger.info("Listing available strategies")

    strategies = [
        StrategyConfigResponse(strategy_name="default", config=StrategyConfig.default().to_dict()),
        StrategyConfigResponse(strategy_name="aggressive", config=StrategyConfig.aggressive().to_dict()),
        StrategyConfigResponse(strategy_name="conservative", config=StrategyConfig.conservative().to_dict()),
    ]

    return strategies


@router.get("/strategies/{strategy_name}", response_model=StrategyConfigResponse)
async def get_strategy(strategy_name: str) -> StrategyConfigResponse:
    """
    Get configuration for a specific strategy.

    Args:
        strategy_name: Name of the strategy

    Returns:
        Strategy configuration

    Raises:
        HTTPException: If strategy not found
    """
    logger.info(f"Getting strategy configuration for {strategy_name}")

    try:
        if strategy_name == "default":
            config = StrategyConfig.default()
        elif strategy_name == "aggressive":
            config = StrategyConfig.aggressive()
        elif strategy_name == "conservative":
            config = StrategyConfig.conservative()
        else:
            raise HTTPException(status_code=404, detail=f"Strategy '{strategy_name}' not found")

        return StrategyConfigResponse(strategy_name=strategy_name, config=config.to_dict())

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get strategy {strategy_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
