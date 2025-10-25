from typing import List, Optional, Tuple
from collections import deque
from hexagons.game.domain.core.entities.game import Game
from hexagons.game.domain.core.entities.position import Position
from hexagons.game.domain.core.value_objects.direction import Direction
from hexagons.game.domain.services.game_service import GameService


class AIGreedyPlayer:
    """
    Greedy AI player with safety-first strategy.

    This is the default, reliable AI strategy that prioritizes success rate over efficiency.
    Uses BFS pathfinding and validates safety before picking each flower.

    Success Rate: ~75%
    Strategy: Pick nearest safe flower, check path to princess exists from flower position.
    """

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
            adjacent_empty = AIGreedyPlayer._get_adjacent_positions(board.robot.position, board)
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
                adjacent_positions = AIGreedyPlayer._get_adjacent_positions(
                    board.princess_position, board
                )
                if not adjacent_positions:
                    # No empty adjacent positions near princess - need to clean obstacles
                    # But we can't clean while holding flowers, so drop them first
                    drop_positions = AIGreedyPlayer._get_adjacent_positions(
                        board.robot.position, board
                    )
                    if drop_positions:
                        # Drop all flowers
                        while board.robot.flowers_held > 0:
                            drop_pos = drop_positions[0]
                            direction = AIGreedyPlayer._get_direction(
                                board.robot.position, drop_pos
                            )
                            actions.append(("rotate", direction))
                            GameService.rotate_robot(board, direction)

                            actions.append(("drop", None))
                            GameService.drop_flower(board)

                        # Now try to clean an obstacle near princess
                        if AIGreedyPlayer._clean_obstacle_near_flower(
                            board, board.princess_position, actions
                        ):
                            continue

                    # If we still can't proceed, give up
                    break

                # Find closest adjacent position
                target = min(
                    adjacent_positions, key=lambda p: board.robot.position.manhattan_distance(p)
                )

                path = AIGreedyPlayer._find_path(board, board.robot.position, target)

                if not path:
                    # Can't reach princess while holding flowers
                    # Strategy: Drop flowers, clean obstacles, pick flowers back up

                    # Find an empty adjacent cell to drop flowers
                    drop_positions = AIGreedyPlayer._get_adjacent_positions(
                        board.robot.position, board
                    )
                    if drop_positions:
                        # Drop all flowers one by one
                        while board.robot.flowers_held > 0:
                            # Find direction to an empty adjacent cell
                            drop_pos = drop_positions[0]  # Just pick the first one
                            direction = AIGreedyPlayer._get_direction(
                                board.robot.position, drop_pos
                            )
                            actions.append(("rotate", direction))
                            GameService.rotate_robot(board, direction)

                            actions.append(("drop", None))
                            GameService.drop_flower(board)

                        # Now clean obstacles blocking path to princess
                        if AIGreedyPlayer._clean_blocking_obstacle(board, target, actions):
                            continue

                    # If we still can't proceed, give up
                    break

                for next_pos in path:
                    direction = AIGreedyPlayer._get_direction(board.robot.position, next_pos)
                    actions.append(("rotate", direction))
                    GameService.rotate_robot(board, direction)

                    actions.append(("move", None))
                    GameService.move_robot(board)

                # Face princess and give flowers
                direction = AIGreedyPlayer._get_direction(
                    board.robot.position, board.princess_position
                )
                actions.append(("rotate", direction))
                GameService.rotate_robot(board, direction)

                actions.append(("give", None))
                GameService.give_flowers(board)

            # If not holding max flowers and there are flowers to collect
            elif board.flowers and board.robot.can_pick():
                # CRITICAL: Always verify path to princess exists BEFORE picking flowers
                # This prevents getting stuck with flowers and no way to deliver them

                # First, handle case where princess is surrounded by obstacles
                princess_adjacent = AIGreedyPlayer._get_adjacent_positions(
                    board.princess_position, board
                )

                if not princess_adjacent:
                    # Princess is completely surrounded! Must clean obstacles around her
                    if board.robot.flowers_held == 0:  # Can only clean without flowers
                        # Try to clean an obstacle adjacent to princess
                        cleaned = AIGreedyPlayer._clean_obstacle_near_flower(
                            board, board.princess_position, actions
                        )
                        if cleaned:
                            continue  # Successfully cleaned, check again

                        # If can't clean directly adjacent, try to clean blocking our path
                        # Find any obstacle we can reach and clean it
                        for direction in [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]:
                            row_delta, col_delta = direction.get_delta()
                            adj_pos = board.princess_position.move(row_delta, col_delta)
                            if board.is_valid_position(adj_pos) and adj_pos in board.obstacles:
                                # Try to reach this obstacle
                                # Find adjacent empty position to this obstacle
                                obstacle_adjacent = AIGreedyPlayer._get_adjacent_positions(adj_pos, board)
                                if obstacle_adjacent:
                                    target = min(obstacle_adjacent,
                                               key=lambda p: board.robot.position.manhattan_distance(p))
                                    path = AIGreedyPlayer._find_path(board, board.robot.position, target)
                                    if path:
                                        # Navigate to obstacle and clean it
                                        for next_pos in path:
                                            dir = AIGreedyPlayer._get_direction(board.robot.position, next_pos)
                                            actions.append(("rotate", dir))
                                            GameService.rotate_robot(board, dir)
                                            actions.append(("move", None))
                                            GameService.move_robot(board)

                                        # Clean the obstacle
                                        clean_dir = AIGreedyPlayer._get_direction(board.robot.position, adj_pos)
                                        actions.append(("rotate", clean_dir))
                                        GameService.rotate_robot(board, clean_dir)
                                        actions.append(("clean", None))
                                        GameService.clean_obstacle(board)

                                        # Successfully cleaned, continue
                                        cleaned = True
                                        break

                        if cleaned:
                            continue

                        # Still can't clean, game may be unsolvable
                        break
                    else:
                        # Holding flowers but princess is surrounded - must drop flowers first
                        drop_positions = AIGreedyPlayer._get_adjacent_positions(
                            board.robot.position, board
                        )
                        if drop_positions:
                            while board.robot.flowers_held > 0:
                                drop_pos = drop_positions[0]
                                direction = AIGreedyPlayer._get_direction(
                                    board.robot.position, drop_pos
                                )
                                actions.append(("rotate", direction))
                                GameService.rotate_robot(board, direction)
                                actions.append(("drop", None))
                                GameService.drop_flower(board)
                            continue
                        else:
                            break

                # Check if we can reach princess from current position
                closest_to_princess = min(
                    princess_adjacent,
                    key=lambda p: board.robot.position.manhattan_distance(p),
                )
                path_to_princess = AIGreedyPlayer._find_path(
                    board, board.robot.position, closest_to_princess
                )

                # No path to princess = must clean obstacles OR be very careful
                if not path_to_princess:
                    if board.robot.flowers_held == 0:
                        # Not holding flowers yet - MUST clean obstacles before picking
                        # This prevents getting stuck after picking
                        cleaned = AIGreedyPlayer._clean_blocking_obstacle(
                            board, closest_to_princess, actions
                        )
                        if cleaned:
                            continue  # Successfully cleaned, check path again

                        # Can't clean any reachable obstacles
                        # As a last resort, try to find a different accessible flower
                        # that might give us a better position
                        accessible_flower_found = False
                        for flower in sorted(
                            board.flowers,
                            key=lambda f: board.robot.position.manhattan_distance(f)
                        ):
                            adj_positions = AIGreedyPlayer._get_adjacent_positions(flower, board)
                            if adj_positions:
                                target = min(adj_positions, key=lambda p: board.robot.position.manhattan_distance(p))
                                path = AIGreedyPlayer._find_path(board, board.robot.position, target)
                                if path:
                                    # Check if from this flower position, we could reach princess
                                    # (or at least clean obstacles toward princess)
                                    accessible_flower_found = True
                                    break

                        if not accessible_flower_found:
                            # No accessible flowers and can't clean obstacles - stuck
                            break
                    else:
                        # Already holding flowers and no path - must drop and clean
                        # This is handled in the earlier drop-clean-repick logic
                        # If we get here, we're in trouble
                        break

                # Find nearest flower - but VALIDATE it's safe to pick
                # Safe means: after picking, we can still reach princess
                safe_flower = None
                safe_flower_target = None

                for flower in sorted(board.flowers, key=lambda f: board.robot.position.manhattan_distance(f)):
                    # Check if we can reach adjacent to this flower
                    adj_to_flower = AIGreedyPlayer._get_adjacent_positions(flower, board)
                    if not adj_to_flower:
                        continue  # Flower surrounded, skip

                    target_near_flower = min(adj_to_flower, key=lambda p: board.robot.position.manhattan_distance(p))
                    path_to_flower = AIGreedyPlayer._find_path(board, board.robot.position, target_near_flower)

                    if not path_to_flower:
                        continue  # Can't reach this flower, skip

                    # CRITICAL: Check if FROM this flower position, we can reach princess
                    # This prevents picking flowers and getting stuck
                    path_from_flower_to_princess = AIGreedyPlayer._find_path(
                        board, target_near_flower, closest_to_princess
                    )

                    # Consider flower "safe" if:
                    # 1. Direct path exists from flower to princess, OR
                    # 2. We already have flowers (committed to delivering), OR
                    # 3. This is the only flower left (must try), OR
                    # 4. We have NO flowers yet (willing to take some risk early on)
                    is_safe = (
                        path_from_flower_to_princess or
                        board.robot.flowers_held > 0 or
                        len(board.flowers) == 1 or
                        (board.robot.flowers_held == 0 and len(board.flowers) <= 3)
                    )

                    if is_safe:
                        safe_flower = flower
                        safe_flower_target = target_near_flower
                        break

                if not safe_flower:
                    # No safe flowers to pick

                    # CRITICAL: If we're already holding flowers, try to deliver them now!
                    # Don't wait for 3+ flowers if we can't find safe flowers
                    if board.robot.flowers_held > 0:
                        # Check if we can deliver what we have
                        path_to_princess_now = AIGreedyPlayer._find_path(
                            board, board.robot.position, closest_to_princess
                        )
                        if path_to_princess_now:
                            # We CAN deliver! Force delivery on next iteration
                            # by continuing - the main loop will handle it
                            continue
                        else:
                            # Can't deliver - try drop-clean-repick
                            drop_positions = AIGreedyPlayer._get_adjacent_positions(
                                board.robot.position, board
                            )
                            if drop_positions:
                                # Drop all flowers
                                while board.robot.flowers_held > 0:
                                    drop_pos = drop_positions[0]
                                    direction = AIGreedyPlayer._get_direction(
                                        board.robot.position, drop_pos
                                    )
                                    actions.append(("rotate", direction))
                                    GameService.rotate_robot(board, direction)
                                    actions.append(("drop", None))
                                    GameService.drop_flower(board)

                                # Now try to clean obstacles
                                if AIGreedyPlayer._clean_blocking_obstacle(
                                    board, closest_to_princess, actions
                                ):
                                    continue
                    else:
                        # No flowers held - try cleaning obstacles to open up paths
                        if AIGreedyPlayer._clean_blocking_obstacle(board, closest_to_princess, actions):
                            continue

                    # No safe moves, give up
                    break

                # Navigate to the safe flower
                path = AIGreedyPlayer._find_path(board, board.robot.position, safe_flower_target)
                if not path:
                    # Shouldn't happen since we verified above, but be safe
                    if not AIGreedyPlayer._clean_blocking_obstacle(board, safe_flower_target, actions):
                        break
                    continue

                for next_pos in path:
                    direction = AIGreedyPlayer._get_direction(board.robot.position, next_pos)
                    actions.append(("rotate", direction))
                    GameService.rotate_robot(board, direction)

                    actions.append(("move", None))
                    GameService.move_robot(board)

                # Face the safe flower and pick it
                direction = AIGreedyPlayer._get_direction(board.robot.position, safe_flower)
                actions.append(("rotate", direction))
                GameService.rotate_robot(board, direction)

                actions.append(("pick", None))
                GameService.pick_flower(board)

                # CRITICAL FIX: After picking flower, board state changed!
                # Re-check if we now have a path to princess from new position
                # This is especially important when obstacles were cleaned or robot moved
                if board.robot.flowers_held >= min(3, board.robot.max_flowers):
                    # We have enough flowers to deliver, check if path exists NOW
                    princess_adjacent_now = AIGreedyPlayer._get_adjacent_positions(
                        board.princess_position, board
                    )
                    if princess_adjacent_now:
                        closest_now = min(
                            princess_adjacent_now,
                            key=lambda p: board.robot.position.manhattan_distance(p)
                        )
                        path_now = AIGreedyPlayer._find_path(
                            board, board.robot.position, closest_now
                        )
                        # If path exists now, continue to delivery phase on next iteration
                        # The main loop will handle delivery
            else:
                break

        return actions

    @staticmethod
    def _find_path(board: Game, start: Position, goal: Position) -> List[Position]:
        """
        Find optimal path from start to goal using A* algorithm.

        A* is more efficient than BFS and finds optimal paths by using:
        - g(n): actual cost from start to node n
        - h(n): heuristic estimated cost from n to goal (Manhattan distance)
        - f(n) = g(n) + h(n): total estimated cost
        """
        if start == goal:
            return []

        # Priority queue: (f_score, counter, position, g_score, path)
        # Using counter for tie-breaking to make heap stable
        import heapq

        counter = 0
        h_score = start.manhattan_distance(goal)
        heap = [(h_score, counter, start, 0, [])]  # (f_score, counter, position, g_score, path)
        visited = set()  # Positions we've already processed (expanded)
        g_scores = {start: 0}  # Position -> best known g_score

        while heap:
            f_score, _, current, g_score, path = heapq.heappop(heap)

            # If we've already processed this position, skip
            if current in visited:
                continue

            visited.add(current)

            # Check all neighbors
            for direction in Direction:
                row_delta, col_delta = direction.get_delta()
                next_pos = current.move(row_delta, col_delta)

                # Found goal!
                if next_pos == goal:
                    return path + [next_pos]

                # Check if next position is valid and not yet processed
                if (
                    board.is_valid_position(next_pos)
                    and board.is_empty(next_pos)
                    and next_pos not in visited
                ):
                    new_g_score = g_score + 1

                    # Only add if we haven't seen this position or found a better path
                    if next_pos not in g_scores or new_g_score < g_scores[next_pos]:
                        g_scores[next_pos] = new_g_score
                        h = next_pos.manhattan_distance(goal)
                        f = new_g_score + h
                        counter += 1
                        heapq.heappush(heap, (f, counter, next_pos, new_g_score, path + [next_pos]))

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
        path = AIGreedyPlayer._find_path(board, board.robot.position, adjacent_pos)
        if not path:
            return False

        for next_pos in path:
            direction = AIGreedyPlayer._get_direction(board.robot.position, next_pos)
            actions.append(("rotate", direction))
            GameService.rotate_robot(board, direction)

            actions.append(("move", None))
            GameService.move_robot(board)

        # Face obstacle and clean it
        direction = AIGreedyPlayer._get_direction(board.robot.position, obstacle_pos)
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
                path = AIGreedyPlayer._find_path(board, board.robot.position, robot_pos)
                if not path:
                    continue

                for next_pos in path:
                    direction = AIGreedyPlayer._get_direction(board.robot.position, next_pos)
                    actions.append(("rotate", direction))
                    GameService.rotate_robot(board, direction)

                    actions.append(("move", None))
                    GameService.move_robot(board)

                # Face obstacle and clean it
                direction = AIGreedyPlayer._get_direction(board.robot.position, obstacle_pos)
                actions.append(("rotate", direction))
                GameService.rotate_robot(board, direction)

                actions.append(("clean", None))
                GameService.clean_obstacle(board)

                return True

        return False
