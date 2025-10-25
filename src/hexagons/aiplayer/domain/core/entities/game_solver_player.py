from typing import List, Optional, Tuple
from collections import deque
from hexagons.game.domain.core.entities.game import Game
from hexagons.game.domain.core.entities.position import Position
from hexagons.game.domain.core.value_objects.direction import Direction
from hexagons.game.domain.services.game_service import GameService


class GameSolverPlayer:
    """AI solver for the game using BFS."""

    @staticmethod
    def solve(board: Game) -> List[Tuple[str, Optional[Direction]]]:
        """
        Attempt to solve the game and return a list of actions.
        Returns a list of tuples: (action_type, direction)
        """
        actions = []
        max_iterations = 1000  # Prevent infinite loops

        iteration = 0
        while (board.flowers or board.robot.flowers_held > 0) and iteration < max_iterations:
            iteration += 1

            # Check if robot is completely blocked (no adjacent empty cells)
            adjacent_empty = GameSolverPlayer._get_adjacent_positions(board.robot.position, board)
            if not adjacent_empty:
                # Robot is blocked - must clean an adjacent obstacle to proceed
                adjacent_obstacles = []
                for direction in Direction:
                    row_delta, col_delta = direction.get_delta()
                    adj_pos = board.robot.position.move(row_delta, col_delta)
                    if board.is_valid_position(adj_pos) and adj_pos in board.obstacles:
                        adjacent_obstacles.append((adj_pos, direction))

                if adjacent_obstacles:
                    # Clean the first adjacent obstacle
                    obstacle_pos, direction = adjacent_obstacles[0]
                    actions.append(("rotate", direction))
                    GameService.rotate_robot(board, direction)

                    actions.append(("clean", None))
                    GameService.clean_obstacle(board)
                    continue
                else:
                    # No adjacent obstacles to clean and no empty cells - robot is stuck
                    break

            # If holding flowers and need to deliver
            # Strategy: Deliver incrementally (every 2-3 flowers) to avoid getting stuck
            should_deliver = board.robot.flowers_held > 0 and (
                board.robot.flowers_held >= min(3, board.robot.max_flowers) or  # Deliver after 3 flowers
                board.robot.flowers_held == board.robot.max_flowers or  # Or when at max capacity
                len(board.flowers) == 0  # Or when no more flowers left
            )

            if should_deliver:
                # Navigate adjacent to princess (not TO princess)
                adjacent_positions = GameSolverPlayer._get_adjacent_positions(
                    board.princess_position, board
                )
                if not adjacent_positions:
                    # No empty adjacent positions near princess - need to clean obstacles
                    # But we can't clean while holding flowers, so drop them first
                    drop_positions = GameSolverPlayer._get_adjacent_positions(
                        board.robot.position, board
                    )
                    if drop_positions:
                        # Drop all flowers
                        while board.robot.flowers_held > 0:
                            drop_pos = drop_positions[0]
                            direction = GameSolverPlayer._get_direction(
                                board.robot.position, drop_pos
                            )
                            actions.append(("rotate", direction))
                            GameService.rotate_robot(board, direction)

                            actions.append(("drop", None))
                            GameService.drop_flower(board)

                        # Now try to clean an obstacle near princess
                        if GameSolverPlayer._clean_obstacle_near_flower(
                            board, board.princess_position, actions
                        ):
                            continue

                    # If we still can't proceed, give up
                    break

                # Find closest adjacent position
                target = min(
                    adjacent_positions, key=lambda p: board.robot.position.manhattan_distance(p)
                )

                path = GameSolverPlayer._find_path(board, board.robot.position, target)

                if not path:
                    # Can't reach princess while holding flowers
                    # Strategy: Drop flowers, clean obstacles, pick flowers back up

                    # Find an empty adjacent cell to drop flowers
                    drop_positions = GameSolverPlayer._get_adjacent_positions(
                        board.robot.position, board
                    )
                    if drop_positions:
                        # Drop all flowers one by one
                        while board.robot.flowers_held > 0:
                            # Find direction to an empty adjacent cell
                            drop_pos = drop_positions[0]  # Just pick the first one
                            direction = GameSolverPlayer._get_direction(
                                board.robot.position, drop_pos
                            )
                            actions.append(("rotate", direction))
                            GameService.rotate_robot(board, direction)

                            actions.append(("drop", None))
                            GameService.drop_flower(board)

                        # Now clean obstacles blocking path to princess
                        if GameSolverPlayer._clean_blocking_obstacle(board, target, actions):
                            continue

                    # If we still can't proceed, give up
                    break

                for next_pos in path:
                    direction = GameSolverPlayer._get_direction(board.robot.position, next_pos)
                    actions.append(("rotate", direction))
                    GameService.rotate_robot(board, direction)

                    actions.append(("move", None))
                    GameService.move_robot(board)

                # Face princess and give flowers
                direction = GameSolverPlayer._get_direction(
                    board.robot.position, board.princess_position
                )
                actions.append(("rotate", direction))
                GameService.rotate_robot(board, direction)

                actions.append(("give", None))
                GameService.give_flowers(board)

            # If not holding max flowers and there are flowers to collect
            elif board.flowers and board.robot.can_pick():
                # IMPORTANT: Before picking flowers, check if we can reach the princess
                # (because we can't clean obstacles while holding flowers)
                # Only do this check if we're about to fill up or this is the last flower
                should_check_princess_path = (
                    board.robot.flowers_held >= board.robot.max_flowers - 1
                    or len(board.flowers) == 1
                )

                if should_check_princess_path:
                    princess_adjacent = GameSolverPlayer._get_adjacent_positions(
                        board.princess_position, board
                    )
                    if princess_adjacent:
                        # Check if any path exists to princess from our current position
                        closest_to_princess = min(
                            princess_adjacent,
                            key=lambda p: board.robot.position.manhattan_distance(p),
                        )
                        path_to_princess = GameSolverPlayer._find_path(
                            board, board.robot.position, closest_to_princess
                        )

                        if not path_to_princess and board.robot.flowers_held == 0:
                            # No path to princess and we have no flowers yet
                            # Try to clean obstacles to create a path before picking flowers
                            if GameSolverPlayer._clean_blocking_obstacle(
                                board, closest_to_princess, actions
                            ):
                                continue
                            # If we can't clean, proceed anyway and try to pick flowers

                # Find nearest flower
                nearest_flower = min(
                    board.flowers, key=lambda f: board.robot.position.manhattan_distance(f)
                )

                # Navigate adjacent to flower
                adjacent_positions = GameSolverPlayer._get_adjacent_positions(nearest_flower, board)
                if not adjacent_positions:
                    # No empty adjacent positions - flower might be surrounded by obstacles
                    # Try to clean an obstacle adjacent to the flower
                    if not GameSolverPlayer._clean_obstacle_near_flower(
                        board, nearest_flower, actions
                    ):
                        # Can't clean around this flower, try another one
                        if len(board.flowers) > 1:
                            # Skip this flower and try another
                            board.flowers.remove(nearest_flower)
                            board.flowers.add(nearest_flower)  # Add it back for later
                            continue
                        break
                    continue

                target = min(
                    adjacent_positions, key=lambda p: board.robot.position.manhattan_distance(p)
                )

                path = GameSolverPlayer._find_path(board, board.robot.position, target)
                if not path:
                    # Try to clean an obstacle blocking the path
                    if not GameSolverPlayer._clean_blocking_obstacle(board, target, actions):
                        break
                    continue

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
    def _find_path(board: Game, start: Position, goal: Position) -> List[Position]:
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
    def _get_adjacent_positions(pos: Position, board: Game) -> List[Position]:
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

    @staticmethod
    def _clean_blocking_obstacle(board: Game, target: Position, actions: List) -> bool:
        """
        Try to clean an obstacle that's blocking the path to the target.
        Returns True if an obstacle was cleaned, False otherwise.
        """
        # Can't clean while holding flowers
        if board.robot.flowers_held > 0:
            return False

        # Find obstacles that might be blocking the path
        # Use BFS to find reachable obstacles
        queue = deque([board.robot.position])
        visited = {board.robot.position}
        reachable_obstacles = []

        while queue:
            current = queue.popleft()

            for direction in Direction:
                row_delta, col_delta = direction.get_delta()
                next_pos = current.move(row_delta, col_delta)

                if not board.is_valid_position(next_pos):
                    continue

                # Found an obstacle we can reach
                if next_pos in board.obstacles and current not in board.obstacles:
                    reachable_obstacles.append((next_pos, current))
                    continue

                # Continue searching through empty cells
                if board.is_empty(next_pos) and next_pos not in visited:
                    visited.add(next_pos)
                    queue.append(next_pos)

        if not reachable_obstacles:
            return False

        # Find the obstacle closest to the target
        best_obstacle = min(reachable_obstacles, key=lambda x: x[0].manhattan_distance(target))
        obstacle_pos, adjacent_pos = best_obstacle

        # Navigate to adjacent position
        path = GameSolverPlayer._find_path(board, board.robot.position, adjacent_pos)
        if not path:
            return False

        for next_pos in path:
            direction = GameSolverPlayer._get_direction(board.robot.position, next_pos)
            actions.append(("rotate", direction))
            GameService.rotate_robot(board, direction)

            actions.append(("move", None))
            GameService.move_robot(board)

        # Face obstacle and clean it
        direction = GameSolverPlayer._get_direction(board.robot.position, obstacle_pos)
        actions.append(("rotate", direction))
        GameService.rotate_robot(board, direction)

        actions.append(("clean", None))
        GameService.clean_obstacle(board)

        return True

    @staticmethod
    def _clean_obstacle_near_flower(board: Game, flower_pos: Position, actions: List) -> bool:
        """
        Try to clean an obstacle adjacent to a flower.
        Returns True if an obstacle was cleaned, False otherwise.
        """
        # Can't clean while holding flowers
        if board.robot.flowers_held > 0:
            return False

        # Find obstacles adjacent to the flower
        adjacent_obstacles = []
        for direction in Direction:
            row_delta, col_delta = direction.get_delta()
            adj_pos = flower_pos.move(row_delta, col_delta)
            if board.is_valid_position(adj_pos) and adj_pos in board.obstacles:
                adjacent_obstacles.append(adj_pos)

        if not adjacent_obstacles:
            return False

        # Try to clean the closest obstacle
        for obstacle_pos in sorted(
            adjacent_obstacles, key=lambda p: board.robot.position.manhattan_distance(p)
        ):
            # Find a position adjacent to the obstacle we can reach
            for direction in Direction:
                row_delta, col_delta = direction.get_delta()
                robot_pos = obstacle_pos.move(row_delta, col_delta)

                if not board.is_valid_position(robot_pos) or not board.is_empty(robot_pos):
                    continue

                # Try to navigate there
                path = GameSolverPlayer._find_path(board, board.robot.position, robot_pos)
                if not path:
                    continue

                for next_pos in path:
                    direction = GameSolverPlayer._get_direction(board.robot.position, next_pos)
                    actions.append(("rotate", direction))
                    GameService.rotate_robot(board, direction)

                    actions.append(("move", None))
                    GameService.move_robot(board)

                # Face obstacle and clean it
                direction = GameSolverPlayer._get_direction(board.robot.position, obstacle_pos)
                actions.append(("rotate", direction))
                GameService.rotate_robot(board, direction)

                actions.append(("clean", None))
                GameService.clean_obstacle(board)

                return True

        return False
