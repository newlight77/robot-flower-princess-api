import pytest
from robot_flower_princess.infrastructure.persistence.in_memory_game_repository import (
    InMemoryGameRepository,
)
from robot_flower_princess.domain.entities.board import Board
from robot_flower_princess.domain.entities.position import Position
from robot_flower_princess.domain.entities.robot import Robot
from robot_flower_princess.domain.value_objects.direction import Direction


@pytest.fixture
def game_repository():
    """Fixture for game repository."""
    return InMemoryGameRepository()


@pytest.fixture
def sample_board():
    """Fixture for a simple test board."""
    robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
    princess_pos = Position(2, 2)
    flowers = {Position(1, 1)}
    obstacles = {Position(0, 1)}

    board = Board(
        rows=3,
        cols=3,
        robot=robot,
        princess_position=princess_pos,
        flowers=flowers,
        obstacles=obstacles,
    )
    board.initial_flower_count = len(flowers)
    return board
