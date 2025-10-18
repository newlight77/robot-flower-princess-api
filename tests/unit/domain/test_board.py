import pytest
from robot_flower_princess.domain.entities.board import Board
from robot_flower_princess.domain.entities.position import Position
from robot_flower_princess.domain.value_objects.game_status import GameStatus


def test_board_creation():
    board = Board.create(rows=10, cols=10)
    assert board.rows == 10
    assert board.cols == 10
    assert board.robot.position == Position(0, 0)
    assert board.princess_position == Position(9, 9)


def test_board_invalid_size():
    with pytest.raises(ValueError):
        Board.create(rows=2, cols=5)

    with pytest.raises(ValueError):
        Board.create(rows=51, cols=5)


def test_board_victory():
    board = Board.create(rows=5, cols=5)
    assert board.get_status() == GameStatus.IN_PROGRESS

    board.flowers_delivered = board.initial_flower_count
    assert board.get_status() == GameStatus.VICTORY
