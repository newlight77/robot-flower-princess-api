from pydantic import BaseModel, Field
from typing import Literal, List
from enum import Enum


class CreateGameRequest(BaseModel):
    rows: int = Field(ge=3, le=50, description="Number of rows (3-50)")
    cols: int = Field(ge=3, le=50, description="Number of columns (3-50)")
    name: str = Field(default="", description="Optional game name")

class CreateGameResponse(BaseModel):
    id: str
    status: str
    message: str = ""
    created_at: str
    updated_at: str
    board: dict
    robot: dict
    princess: dict
    obstacles: dict
    flowers: dict


class GameSchema(BaseModel):
    id: str
    status: str
    created_at: str
    updated_at: str
    board: dict
    robot: dict
    princess: dict
    obstacles: dict
    flowers: dict


class GamesResponse(BaseModel):
    games: List[GameSchema]
    total: int


class GetGameResponse(BaseModel):
    id: str
    status: str
    message: str = ""
    created_at: str
    updated_at: str
    board: dict
    robot: dict
    princess: dict
    obstacles: dict
    flowers: dict



class GameHistoryResponse(BaseModel):
    id: str
    history: dict



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
