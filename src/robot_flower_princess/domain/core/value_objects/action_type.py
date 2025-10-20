from enum import Enum


class ActionType(str, Enum):
    ROTATE = "rotate"
    MOVE = "move"
    PICK = "pick"
    DROP = "drop"
    GIVE = "give"
    CLEAN = "clean"
