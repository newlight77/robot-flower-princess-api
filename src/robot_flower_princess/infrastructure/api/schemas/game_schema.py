from pydantic import BaseModel, Field
from typing import Literal, List

class CreateGameRequest(BaseModel):
    rows: int = Field(ge=3, le=50, description="Number of rows (3-50)")
    cols: int = Field(ge=3, le=50, description="Number of columns (3-50)")

class RotateRequest(BaseModel):
    direction: Literal["north", "south", "east", "west"] = Field(description="Direction to face")

class GameStateResponse(BaseModel):
    id: str
    board: dict
    message: str = ""

class ActionResponse(BaseModel):
    success: bool
    id: str
    board: dict
    message: str

class GameHistoryResponse(BaseModel):
    id: str
    history: dict

class GameSummary(BaseModel):
    id: str
    status: str
    board: dict

class GamesResponse(BaseModel):
    games: List[GameSummary]
    total: int
