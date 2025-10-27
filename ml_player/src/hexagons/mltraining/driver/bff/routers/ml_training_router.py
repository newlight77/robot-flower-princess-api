"""ML Training Router - API endpoints for data collection and model training."""

from fastapi import APIRouter, Depends, HTTPException

from hexagons.mltraining.domain.ml import GameDataCollector
from hexagons.mltraining.driver.bff.schemas.data_collection_schema import CollectDataRequest, CollectDataResponse
from shared.logging import logger
from configurator.dependencies import get_data_collector

router = APIRouter(prefix="/api/ml-training", tags=["ml-training"])


@router.post("/collect", response_model=CollectDataResponse)
async def collect_gameplay_data(
    request: CollectDataRequest,
    data_collector: GameDataCollector = Depends(get_data_collector),
) -> CollectDataResponse:
    """
    Collect gameplay data for ML training.

    This endpoint receives game state, action, and outcome data from the game service
    and stores it for future model training.

    Args:
        request: Data collection request with game state and action
        data_collector: Data collector dependency

    Returns:
        Collection confirmation with statistics
    """
    try:
        logger.info(f"Collecting data for game_id={request.game_id}, action={request.action}")

        # Store the sample
        data_collector.collect_sample(
            game_id=request.game_id,
            game_state=request.game_state,
            action=request.action,
            direction=request.direction,
            outcome=request.outcome.model_dump() if request.outcome else None,
            timestamp=request.timestamp,
        )

        # Get updated statistics
        stats = data_collector.get_statistics()

        return CollectDataResponse(
            success=True,
            message="Data collected successfully",
            samples_collected=stats.get("total_samples", 0),
        )

    except Exception as e:
        logger.error(f"Failed to collect data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to collect data: {str(e)}")


@router.get("/statistics")
async def get_collection_statistics(
    data_collector: GameDataCollector = Depends(get_data_collector),
) -> dict:
    """
    Get statistics about collected training data.

    Returns:
        Dictionary with collection statistics
    """
    try:
        stats = data_collector.get_statistics()
        return {
            "success": True,
            "statistics": stats,
        }
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")
