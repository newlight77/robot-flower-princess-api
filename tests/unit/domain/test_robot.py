import pytest
from robot_flower_princess.domain.core.entities.robot import Robot
from robot_flower_princess.domain.core.entities.position import Position
from robot_flower_princess.domain.core.value_objects.direction import Direction


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

    princess_pos = Position(0, 1)
    delivered = robot.give_flowers(princess_pos)
    assert delivered == 2
    assert robot.flowers_held == 0
    # Verify that flowers_delivered list has one entry per flower delivered
    assert len(robot.flowers_delivered) == 2
    assert all(
        entry["position"]["row"] == princess_pos.row
        and entry["position"]["col"] == princess_pos.col
        for entry in robot.flowers_delivered
    )


def test_robot_give_flowers_multiple_times():
    """Test that giving flowers multiple times accumulates correctly in the delivered list."""
    robot = Robot(position=Position(0, 0))
    princess_pos = Position(0, 1)

    # First delivery: 2 flowers
    robot.pick_flower()
    robot.pick_flower()
    delivered1 = robot.give_flowers(princess_pos)
    assert delivered1 == 2
    assert len(robot.flowers_delivered) == 2

    # Second delivery: 3 flowers
    robot.pick_flower()
    robot.pick_flower()
    robot.pick_flower()
    delivered2 = robot.give_flowers(princess_pos)
    assert delivered2 == 3
    assert len(robot.flowers_delivered) == 5  # Total: 2 + 3 = 5

    # Third delivery: 1 flower
    robot.pick_flower()
    delivered3 = robot.give_flowers(princess_pos)
    assert delivered3 == 1
    assert len(robot.flowers_delivered) == 6  # Total: 2 + 3 + 1 = 6
