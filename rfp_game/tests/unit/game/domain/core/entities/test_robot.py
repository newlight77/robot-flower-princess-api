import pytest
from hexagons.game.domain.core.entities.robot import Robot
from hexagons.game.domain.core.entities.position import Position
from hexagons.game.domain.core.value_objects.direction import Direction


def test_robot_creation():
    pos = Position(0, 0)
    robot = Robot(position=pos)
    assert robot.position == pos
    assert robot.orientation == Direction.EAST
    assert robot.flowers_held == 0


def test_robot_pick_flower():
    robot = Robot(position=Position(0, 0))
    flower_pos = Position(1, 1)

    action = robot.pick_flower(flower_pos)
    assert robot.flowers_held == 1
    assert action.message is None  # Success
    assert action.type.value == "pickFlower"

    # Test max flowers
    for i in range(11):
        robot.pick_flower(Position(i, i))
    assert robot.flowers_held == 12

    # Test exceeding max
    action = robot.pick_flower(Position(5, 5))
    assert robot.flowers_held == 12  # Should not increase
    assert "Cannot hold more than" in action.message


def test_robot_drop_flower():
    robot = Robot(position=Position(0, 0))
    drop_pos = Position(2, 2)

    # Try to drop when no flowers held
    action = robot.drop_flower(drop_pos)
    assert "No flowers to drop" in action.message

    # Pick and then drop
    flower_pos = Position(1, 1)
    robot.pick_flower(flower_pos)
    action = robot.drop_flower(flower_pos)
    assert robot.flowers_held == 0
    assert action.message is None  # Success


def test_robot_give_flowers():
    robot = Robot(position=Position(0, 0))
    robot.pick_flower(Position(1, 1))
    robot.pick_flower(Position(2, 2))

    princess_pos = Position(0, 1)
    action = robot.give_flowers(princess_pos)
    assert robot.flowers_held == 0
    assert action.message is None  # Success
    # Verify that flowers_delivered list has one entry per flower delivered
    assert len(robot.flowers_delivered) == 2


def test_robot_give_flowers_multiple_times():
    """Test that giving flowers multiple times accumulates correctly in the delivered list."""
    robot = Robot(position=Position(0, 0))
    princess_pos = Position(0, 1)

    # First delivery: 2 flowers
    robot.pick_flower(Position(1, 1))
    robot.pick_flower(Position(2, 2))
    action1 = robot.give_flowers(princess_pos)
    assert action1.message is None
    assert len(robot.flowers_delivered) == 2

    # Second delivery: 3 flowers
    robot.pick_flower(Position(3, 3))
    robot.pick_flower(Position(4, 4))
    robot.pick_flower(Position(5, 5))
    action2 = robot.give_flowers(princess_pos)
    assert action2.message is None
    assert len(robot.flowers_delivered) == 5  # Total: 2 + 3 = 5

    # Third delivery: 1 flower
    robot.pick_flower(Position(6, 6))
    action3 = robot.give_flowers(princess_pos)
    assert action3.message is None
    assert len(robot.flowers_delivered) == 6  # Total: 2 + 3 + 1 = 6
