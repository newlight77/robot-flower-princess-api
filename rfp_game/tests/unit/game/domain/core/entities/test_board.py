import pytest
from hexagons.game.domain.core.entities.game import Game
from hexagons.game.domain.core.entities.position import Position
from hexagons.game.domain.core.value_objects.game_status import GameStatus


def test_game_creation():
    game = Game.create(rows=10, cols=10)
    assert game.rows == 10
    assert game.cols == 10
    assert game.robot.position == Position(0, 0)
    assert game.princess.position == Position(9, 9)
    assert game.flowers_delivered == 0
    assert game.board.rows == 10
    assert game.board.cols == 10
    assert game.board.robot_position == Position(0, 0)
    assert game.board.princess_position == Position(9, 9)


def test_game_invalid_size():
    with pytest.raises(ValueError):
        Game.create(rows=2, cols=5)

    with pytest.raises(ValueError):
        Game.create(rows=51, cols=5)


def test_game_victory():
    game = Game.create(rows=5, cols=5)
    assert game.get_status() == GameStatus.IN_PROGRESS

    game.flowers_delivered = game.initial_flower_count
    assert game.get_status() == GameStatus.VICTORY
