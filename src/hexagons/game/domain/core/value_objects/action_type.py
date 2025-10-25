from enum import Enum


class ActionType(str, Enum):
    ROTATE = "rotate"
    MOVE = "move"
    PICK = "pickFlower"
    DROP = "dropFlower"
    GIVE = "giveFlower"
    CLEAN = "clean"
