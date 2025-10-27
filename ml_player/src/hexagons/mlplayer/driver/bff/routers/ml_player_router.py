"""FastAPI router for ML Player endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from configurator.dependencies import get_game_client, get_data_collector
from hexagons.mlplayer.domain.core.value_objects import StrategyConfig
from hexagons.mlplayer.domain.ports.game_client import GameClientPort
from hexagons.mlplayer.domain.ml.data_collector import GameDataCollector
from hexagons.mlplayer.domain.use_cases.predict_action import (
    PredictActionCommand,
    PredictActionUseCase,
)
from hexagons.mlplayer.driver.bff.schemas.ml_player_schema import (
    PredictActionRequest,
    PredictActionResponse,
    StrategyConfigResponse,
)
from hexagons.mlplayer.driver.bff.schemas.data_collection_schema import (
    CollectDataRequest,
    CollectDataResponse,
)
from shared.logging import logger

router = APIRouter(prefix="/api/ml-player", tags=["ML Player"])


@router.post("/predict/{game_id}", response_model=PredictActionResponse)
async def predict_action(
    game_id: str,
    request: PredictActionRequest,
    game_client: GameClientPort = Depends(get_game_client),
) -> PredictActionResponse:
    """
    Predict the next best action for a game using ML player.

    Args:
        game_id: Game identifier
        request: Prediction request with strategy
        game_client: Game service client (injected)

    Returns:
        Predicted action with confidence and metadata

    Raises:
        HTTPException: If game not found or prediction fails
    """
    logger.info(f"Predicting action for game_id={game_id} with strategy={request.strategy}")

    try:
        use_case = PredictActionUseCase(game_client)
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

        result = await use_case.execute(command)

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


@router.post("/collect", response_model=CollectDataResponse)
async def collect_gameplay_data(
    request: CollectDataRequest,
    data_collector: GameDataCollector = Depends(get_data_collector),
) -> CollectDataResponse:
    """
    Collect gameplay data for ML training.

    Args:
        request: Gameplay data to collect
        data_collector: Data collector (injected)

    Returns:
        Collection confirmation with statistics

    Raises:
        HTTPException: If data collection fails
    """
    logger.info(f"Collecting gameplay data for game_id={request.game_id}, action={request.action}")

    try:
        # Collect the sample
        data_collector.collect_sample(
            game_id=request.game_id,
            game_state=request.game_state,
            action=request.action,
            direction=request.direction,
            outcome=request.outcome,
            timestamp=request.timestamp,
        )

        # Get statistics
        stats = data_collector.get_statistics()

        logger.info(f"Data collected successfully. Total samples: {stats['total_samples']}")

        return CollectDataResponse(
            success=True,
            message="Data collected successfully",
            samples_collected=stats["total_samples"],
        )

    except Exception as e:
        logger.error(f"Failed to collect gameplay data: {e}")
        raise HTTPException(status_code=500, detail=f"Data collection failed: {str(e)}")
