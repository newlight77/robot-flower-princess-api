from enum import Enum


class CellType(str, Enum):
    EMPTY = "empty"
    ROBOT = "robot"
    PRINCESS = "princess"
    FLOWER = "flower"
    OBSTACLE = "obstacle"
