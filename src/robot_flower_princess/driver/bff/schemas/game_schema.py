from pydantic import BaseModel, Field
from typing import Literal, List
from enum import Enum


class CreateGameRequest(BaseModel):
    rows: int = Field(ge=3, le=50, description="Number of rows (3-50)")
    cols: int = Field(ge=3, le=50, description="Number of columns (3-50)")
    name: str = Field(default="", description="Optional game name")


class RotateRequest(BaseModel):
    direction: Literal["north", "south", "east", "west"] = Field(description="Direction to face")


class ActionType(str, Enum):
    rotate = "rotate"
    move = "move"
    pickFlower = "pickFlower"
    dropFlower = "dropFlower"
    giveFlower = "giveFlower"
    clean = "clean"


class ActionRequest(BaseModel):
    action: ActionType
    # Direction is now required for all actions (frontend always provides direction)
    direction: Literal["north", "south", "east", "west"]


class GameStateResponse(BaseModel):
    id: str
    status: str
    message: str = ""
    board: dict
    robot: dict
    princess: dict
    obstacles: dict
    flowers: dict
    created_at: str
    updated_at: str


class ActionResponse(BaseModel):
    success: bool
    id: str
    status: str
    board: dict
    robot: dict
    princess: dict
    obstacles: dict
    flowers: dict
    message: str


class GameHistoryResponse(BaseModel):
    id: str
    history: dict


class GameSummary(BaseModel):
    id: str
    board: dict
    robot: dict
    princess: dict
    obstacles: dict
    flowers: dict
    status: str
    created_at: str
    updated_at: str


class GamesResponse(BaseModel):
    gamess: List[GameSummary]
    total: int
