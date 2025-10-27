"""
Data collection schemas for the ML Player API.
"""

from pydantic import BaseModel, Field
from typing import Any


class CollectDataRequest(BaseModel):
    """Request to collect gameplay data."""

    game_id: str = Field(..., description="Game identifier")
    timestamp: str = Field(..., description="ISO timestamp of the action")
    game_state: dict[str, Any] = Field(..., description="Game state before action")
    action: str = Field(..., description="Action type (move, rotate, pick, drop, give, clean)")
    direction: str = Field(..., description="Direction (NORTH, SOUTH, EAST, WEST)")
    outcome: dict[str, Any] = Field(..., description="Action outcome (success, message)")


class CollectDataResponse(BaseModel):
    """Response after collecting data."""

    success: bool = Field(..., description="Whether data was collected successfully")
    message: str = Field(..., description="Result message")
    samples_collected: int = Field(..., description="Total samples collected so far")
