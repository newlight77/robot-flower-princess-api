"""Pydantic schemas for ML Player API."""

from typing import Optional

from pydantic import BaseModel, Field


class PredictActionRequest(BaseModel):
    """Request schema for action prediction."""

    strategy: str = Field(
        default="default",
        description="Strategy to use: 'default', 'aggressive', or 'conservative'",
        pattern="^(default|aggressive|conservative)$",
    ),
    game_id: str = Field(description="Game identifier")
    board: dict
    robot: dict
    princess: dict
    obstacles: dict
    flowers: dict


class PredictActionResponse(BaseModel):
    """Response schema for action prediction."""

    game_id: str = Field(description="Game identifier")
    action: str = Field(description="Predicted action (move, pick, drop, give, clean, rotate)")
    direction: Optional[str] = Field(None, description="Direction for the action (if applicable)")
    confidence: float = Field(description="Confidence score for the prediction (0.0 to 1.0)")
    board_score: float = Field(description="Heuristic evaluation score of the current board state")
    config_used: dict = Field(description="Strategy configuration used for prediction")

    class Config:
        json_schema_extra = {
            "example": {
                "game_id": "123e4567-e89b-12d3-a456-426614174000",
                "action": "move",
                "direction": "NORTH",
                "confidence": 0.85,
                "board_score": 12.5,
                "config_used": {
                    "distance_to_flower_weight": -2.5,
                    "distance_to_princess_weight": -1.0,
                    "risk_aversion": 0.7,
                },
            }
        }


class StrategyConfigResponse(BaseModel):
    """Response schema for strategy configuration."""

    strategy_name: str
    config: dict

    class Config:
        json_schema_extra = {
            "example": {
                "strategy_name": "default",
                "config": {
                    "distance_to_flower_weight": -2.5,
                    "distance_to_princess_weight": -1.0,
                    "obstacle_density_weight": -3.0,
                    "path_clearance_weight": 2.0,
                    "flower_cluster_bonus": 1.5,
                    "flower_isolation_penalty": -0.5,
                    "risk_aversion": 0.7,
                    "exploration_factor": 0.3,
                    "lookahead_depth": 3,
                },
            }
        }
