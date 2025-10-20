from typing import List, Optional, Tuple
from collections import deque
from .board import Board
from .position import Position
from ..value_objects.direction import Direction
from ...services.game_service import GameService


class GameSolverPlayer:
    """AI solver for the game using BFS."""

    @staticmethod
    def solve(board: Board) -> List[Tuple[str, Optional[Direction]]]:
        """
        Attempt to solve the game and return a list of actions.
        Returns a list of tuples: (action_type, direction)
        """
        actions = []

        while board.flowers or board.robot.flowers_held > 0:
            # If holding flowers and need to deliver
            if board.robot.flowers_held > 0 and (
                board.robot.flowers_held == board.robot.max_flowers or len(board.flowers) == 0
            ):
                # Navigate to princess
                path = GameSolverPlayer._find_path(board, board.robot.position, board.princess_position)
                if not path:
                    break

                for next_pos in path:
                    direction = GameSolverPlayer._get_direction(board.robot.position, next_pos)
                    actions.append(("rotate", direction))
                    GameService.rotate_robot(board, direction)

                    actions.append(("move", None))
                    GameService.move_robot(board)

                # Face princess and give flowers
                direction = GameSolverPlayer._get_direction(board.robot.position, board.princess_position)
                actions.append(("rotate", direction))
                GameService.rotate_robot(board, direction)

                actions.append(("give", None))
                GameService.give_flowers(board)

            # If not holding max flowers and there are flowers to collect
            elif board.flowers and board.robot.can_pick():
                # Find nearest flower
                nearest_flower = min(
                    board.flowers, key=lambda f: board.robot.position.manhattan_distance(f)
                )

                # Navigate adjacent to flower
                adjacent_positions = GameSolverPlayer._get_adjacent_positions(nearest_flower, board)
                if not adjacent_positions:
                    break

                target = min(
                    adjacent_positions, key=lambda p: board.robot.position.manhattan_distance(p)
                )

                path = GameSolverPlayer._find_path(board, board.robot.position, target)
                if not path:
                    break

                for next_pos in path:
                    direction = GameSolverPlayer._get_direction(board.robot.position, next_pos)
                    actions.append(("rotate", direction))
                    GameService.rotate_robot(board, direction)

                    actions.append(("move", None))
                    GameService.move_robot(board)

                # Face flower and pick it
                direction = GameSolverPlayer._get_direction(board.robot.position, nearest_flower)
                actions.append(("rotate", direction))
                GameService.rotate_robot(board, direction)

                actions.append(("pick", None))
                GameService.pick_flower(board)
            else:
                break

        return actions

    @staticmethod
    def _find_path(board: Board, start: Position, goal: Position) -> List[Position]:
        """Find path from start to goal using BFS."""
        if start == goal:
            return []

        queue = deque([(start, [])])
        visited = {start}

        while queue:
            current, path = queue.popleft()

            for direction in Direction:
                row_delta, col_delta = direction.get_delta()
                next_pos = current.move(row_delta, col_delta)

                if next_pos == goal:
                    return path + [next_pos]

                if (
                    board.is_valid_position(next_pos)
                    and board.is_empty(next_pos)
                    and next_pos not in visited
                ):
                    visited.add(next_pos)
                    queue.append((next_pos, path + [next_pos]))

        return []

    @staticmethod
    def _get_adjacent_positions(pos: Position, board: Board) -> List[Position]:
        """Get all valid adjacent empty positions."""
        adjacent = []
        for direction in Direction:
            row_delta, col_delta = direction.get_delta()
            adj_pos = pos.move(row_delta, col_delta)
            if board.is_valid_position(adj_pos) and board.is_empty(adj_pos):
                adjacent.append(adj_pos)
        return adjacent

    @staticmethod
    def _get_direction(from_pos: Position, to_pos: Position) -> Direction:
        """Get direction from one position to another (must be adjacent)."""
        row_diff = to_pos.row - from_pos.row
        col_diff = to_pos.col - from_pos.col

        if row_diff == -1:
            return Direction.NORTH
        elif row_diff == 1:
            return Direction.SOUTH
        elif col_diff == 1:
            return Direction.EAST
        else:
            return Direction.WEST
