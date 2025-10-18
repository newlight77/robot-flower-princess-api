import pytest
from robot_flower_princess.domain.entities.robot import Robot
from robot_flower_princess.domain.entities.position import Position
from robot_flower_princess.domain.value_objects.direction import Direction


def test_robot_creation():
    pos = Position(0, 0)
    robot = Robot(position=pos)
    assert robot.position == pos
    assert robot.orientation == Direction.EAST
    assert robot.flowers_held == 0


def test_robot_pick_flower():
    robot = Robot(position=Position(0, 0))
    robot.pick_flower()
    assert robot.flowers_held == 1

    # Test max flowers
    for _ in range(11):
        robot.pick_flower()
    assert robot.flowers_held == 12

    with pytest.raises(ValueError):
        robot.pick_flower()


def test_robot_drop_flower():
    robot = Robot(position=Position(0, 0))

    with pytest.raises(ValueError):
        robot.drop_flower()

    robot.pick_flower()
    robot.drop_flower()
    assert robot.flowers_held == 0


def test_robot_give_flowers():
    robot = Robot(position=Position(0, 0))
    robot.pick_flower()
    robot.pick_flower()

    delivered = robot.give_flowers()
    assert delivered == 2
    assert robot.flowers_held == 0
