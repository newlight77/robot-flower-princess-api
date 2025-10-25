import pytest
from hexagons.game.domain.core.entities.game import Game
from hexagons.game.domain.core.entities.position import Position
from hexagons.game.domain.core.value_objects.game_status import GameStatus


def test_board_creation():
    board = Game.create(rows=10, cols=10)
    assert board.rows == 10
    assert board.cols == 10
    assert board.robot.position == Position(0, 0)
    assert board.princess_position == Position(9, 9)


def test_board_invalid_size():
    with pytest.raises(ValueError):
        Game.create(rows=2, cols=5)

    with pytest.raises(ValueError):
        Game.create(rows=51, cols=5)


def test_board_victory():
    board = Game.create(rows=5, cols=5)
    assert board.get_status() == GameStatus.IN_PROGRESS

    board.flowers_delivered = board.initial_flower_count
    assert board.get_status() == GameStatus.VICTORY
