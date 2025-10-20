from pydantic import BaseModel, Field
from typing import Literal, List, Optional
from enum import Enum
from pydantic import model_validator


class CreateGameRequest(BaseModel):
    rows: int = Field(ge=3, le=50, description="Number of rows (3-50)")
    cols: int = Field(ge=3, le=50, description="Number of columns (3-50)")


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
    # Optional direction only used when action == rotate
    direction: Optional[Literal["north", "south", "east", "west"]] = None

    @model_validator(mode="before")
    def check_direction_for_rotate(cls, values):
        action = values.get("action")
        direction = values.get("direction")
        if action == ActionType.rotate and not direction:
            raise ValueError("'direction' is required when action is 'rotate'")
        return values


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
