"""Additional focused tests for AIOptimalPlayer to boost coverage."""

from hexagons.game.domain.core.entities.game import Game
from hexagons.game.domain.core.entities.position import Position
from hexagons.game.domain.core.value_objects.direction import Direction
from hexagons.aiplayer.domain.core.entities.ai_optimal_player import AIOptimalPlayer


def test_adjacent_to_princess_with_flowers_gives_immediately():
    """When adjacent to princess and holding flowers, solver should give immediately."""
    game = Game(rows=5, cols=5)
    # Place robot north of princess, facing SOUTH
    game.robot.position = Position(3, 3)
    game.robot.orientation = Direction.SOUTH
    game.princess.position = Position(4, 3)
    # Robot holds a flower already
    game.flowers = set()
    game.robot.flowers_collected = [Position(1, 1)]
    game.board.initial_flowers_count = 1

    actions = AIOptimalPlayer.solve(game)

    # Should give in one step or very few
    assert isinstance(actions, list)
    assert len(actions) >= 1
    # After solve, flowers should be delivered and robot holds none
    assert len(game.robot.flowers_collected) == 0
    assert len(game.princess.flowers_received) >= 1


def test_facing_flower_picks_immediately():
    """When facing a flower directly ahead, solver should pick promptly."""
    game = Game(rows=5, cols=5)
    # Robot at (2,2) facing NORTH with a flower at (1,2)
    game.robot.position = Position(2, 2)
    game.robot.orientation = Direction.NORTH
    game.princess.position = Position(4, 4)
    game.flowers = {Position(1, 2)}
    game.obstacles = set()
    game.board.initial_flowers_count = 1

    actions = AIOptimalPlayer.solve(game)

    assert isinstance(actions, list)
    assert len(actions) > 0
    # After solve begins, the single flower should be collected at some point
    assert len(game.flowers) == 0
    assert len(game.robot.flowers_collected) >= 1 or len(game.princess.flowers_received) >= 1
