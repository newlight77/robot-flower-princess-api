from robot_flower_princess.domain.entities.position import Position


def test_position_creation():
    pos = Position(5, 10)
    assert pos.row == 5
    assert pos.col == 10


def test_position_move():
    pos = Position(5, 10)
    new_pos = pos.move(2, -3)
    assert new_pos.row == 7
    assert new_pos.col == 7


def test_position_manhattan_distance():
    pos1 = Position(0, 0)
    pos2 = Position(3, 4)
    assert pos1.manhattan_distance(pos2) == 7
