from pydantic import BaseModel, Field
from typing import Literal, List

class CreateGameRequest(BaseModel):
    rows: int = Field(ge=3, le=50, description="Number of rows (3-50)")
    cols: int = Field(ge=3, le=50, description="Number of columns (3-50)")

class RotateRequest(BaseModel):
    direction: Literal["north", "south", "east", "west"] = Field(description="Direction to face")

class GameStateResponse(BaseModel):
    game_id: str
    board: dict
    message: str = ""

class ActionResponse(BaseModel):
    success: bool
    game_id: str
    board: dict
    message: str

class GameHistoryResponse(BaseModel):
    game_id: str
    history: dict

class GameSummary(BaseModel):
    game_id: str
    status: str
    board: dict

class EndedGamesResponse(BaseModel):
    games: List[GameSummary]
    total: int
