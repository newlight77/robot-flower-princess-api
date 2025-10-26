from pydantic import BaseModel, Field
from typing import Literal, List
from enum import Enum


class CreateGameRequest(BaseModel):
    rows: int = Field(ge=3, le=50, description="Number of rows (3-50)")
    cols: int = Field(ge=3, le=50, description="Number of columns (3-50)")
    name: str = Field(default="", description="Optional game name")

class CreateGameResponse(BaseModel):
    game: dict
    message: str = ""


class GamesResponse(BaseModel):
    games: List[dict]
    total: int


class GetGameResponse(BaseModel):
    game: dict
    message: str = ""



class GameHistoryResponse(BaseModel):
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
    game: dict
    message: str
