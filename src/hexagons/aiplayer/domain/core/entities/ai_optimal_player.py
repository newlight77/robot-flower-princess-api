from typing import List, Optional, Tuple
from hexagons.game.domain.core.entities.game import Game
from hexagons.game.domain.core.entities.position import Position
from hexagons.game.domain.core.value_objects.direction import Direction
from hexagons.game.domain.services.game_service import GameService


class AIOptimalPlayer:
    """
    Optimal AI player using A* pathfinding and multi-step planning.

    This strategy optimizes for EFFICIENCY (fewest actions) using:
    - A* pathfinding with Manhattan distance heuristic
    - Multi-step flower sequence planning (permutations or 2-step look-ahead)
    - Smart obstacle cleaning with look-ahead evaluation

    Success Rate: ~62%
    Efficiency: ~25% faster (fewer actions) than AIGreedyPlayer

    Trade-off: Lower success rate but more efficient when it succeeds.
    Use when efficiency matters more than reliability.
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
            adjacent_empty = AIOptimalPlayer._get_adjacent_positions(board.robot.position, board)
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
                board.robot.flowers_held
                >= min(3, board.robot.max_flowers)  # Deliver after 3 flowers
                or board.robot.flowers_held == board.robot.max_flowers  # Or when at max capacity
                or len(board.flowers) == 0  # Or when no more flowers left
            )

            if should_deliver:
                # Navigate adjacent to princess (not TO princess)
                adjacent_positions = AIOptimalPlayer._get_adjacent_positions(
                    board.princess_position, board
                )
                if not adjacent_positions:
                    # No empty adjacent positions near princess - need to clean obstacles
                    # But we can't clean while holding flowers, so drop them first
                    drop_positions = AIOptimalPlayer._get_adjacent_positions(
                        board.robot.position, board
                    )
                    if drop_positions:
                        # Drop all flowers
                        while board.robot.flowers_held > 0:
                            drop_pos = drop_positions[0]
                            direction = AIOptimalPlayer._get_direction(
                                board.robot.position, drop_pos
                            )
                            actions.append(("rotate", direction))
                            GameService.rotate_robot(board, direction)

                            actions.append(("drop", None))
                            GameService.drop_flower(board)

                        # Now try to clean an obstacle near princess
                        if AIOptimalPlayer._clean_obstacle_near_flower(
                            board, board.princess_position, actions
                        ):
                            continue

                    # If we still can't proceed, give up
                    break

                # Find closest adjacent position
                target = min(
                    adjacent_positions, key=lambda p: board.robot.position.manhattan_distance(p)
                )

                path = AIOptimalPlayer._find_path(board, board.robot.position, target)

                if not path:
                    # Can't reach princess while holding flowers
                    # Strategy: Drop flowers, clean obstacles, pick flowers back up

                    # Find an empty adjacent cell to drop flowers
                    drop_positions = AIOptimalPlayer._get_adjacent_positions(
                        board.robot.position, board
                    )
                    if drop_positions:
                        # Drop all flowers one by one
                        while board.robot.flowers_held > 0:
                            # Find direction to an empty adjacent cell
                            drop_pos = drop_positions[0]  # Just pick the first one
                            direction = AIOptimalPlayer._get_direction(
                                board.robot.position, drop_pos
                            )
                            actions.append(("rotate", direction))
                            GameService.rotate_robot(board, direction)

                            actions.append(("drop", None))
                            GameService.drop_flower(board)

                        # Now clean obstacles blocking path to princess
                        if AIOptimalPlayer._clean_blocking_obstacle(board, target, actions):
                            continue

                    # If we still can't proceed, give up
                    break

                for next_pos in path:
                    direction = AIOptimalPlayer._get_direction(board.robot.position, next_pos)
                    actions.append(("rotate", direction))
                    GameService.rotate_robot(board, direction)

                    actions.append(("move", None))
                    GameService.move_robot(board)

                # Face princess and give flowers
                direction = AIOptimalPlayer._get_direction(
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
                princess_adjacent = AIOptimalPlayer._get_adjacent_positions(
                    board.princess_position, board
                )

                if not princess_adjacent:
                    # Princess is completely surrounded! Must clean obstacles around her
                    if board.robot.flowers_held == 0:  # Can only clean without flowers
                        # Try to clean an obstacle adjacent to princess
                        cleaned = AIOptimalPlayer._clean_obstacle_near_flower(
                            board, board.princess_position, actions
                        )
                        if cleaned:
                            continue  # Successfully cleaned, check again

                        # If can't clean directly adjacent, try to clean blocking our path
                        # Find any obstacle we can reach and clean it
                        for direction in [
                            Direction.NORTH,
                            Direction.SOUTH,
                            Direction.EAST,
                            Direction.WEST,
                        ]:
                            row_delta, col_delta = direction.get_delta()
                            adj_pos = board.princess_position.move(row_delta, col_delta)
                            if board.is_valid_position(adj_pos) and adj_pos in board.obstacles:
                                # Try to reach this obstacle
                                # Find adjacent empty position to this obstacle
                                obstacle_adjacent = AIOptimalPlayer._get_adjacent_positions(
                                    adj_pos, board
                                )
                                if obstacle_adjacent:
                                    target = min(
                                        obstacle_adjacent,
                                        key=lambda p: board.robot.position.manhattan_distance(p),
                                    )
                                    path = AIOptimalPlayer._find_path(
                                        board, board.robot.position, target
                                    )
                                    if path:
                                        # Navigate to obstacle and clean it
                                        for next_pos in path:
                                            dir = AIOptimalPlayer._get_direction(
                                                board.robot.position, next_pos
                                            )
                                            actions.append(("rotate", dir))
                                            GameService.rotate_robot(board, dir)
                                            actions.append(("move", None))
                                            GameService.move_robot(board)

                                        # Clean the obstacle
                                        clean_dir = AIOptimalPlayer._get_direction(
                                            board.robot.position, adj_pos
                                        )
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
                        drop_positions = AIOptimalPlayer._get_adjacent_positions(
                            board.robot.position, board
                        )
                        if drop_positions:
                            while board.robot.flowers_held > 0:
                                drop_pos = drop_positions[0]
                                direction = AIOptimalPlayer._get_direction(
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
                path_to_princess = AIOptimalPlayer._find_path(
                    board, board.robot.position, closest_to_princess
                )

                # No path to princess = must clean obstacles OR be very careful
                if not path_to_princess:
                    if board.robot.flowers_held == 0:
                        # Not holding flowers yet - MUST clean obstacles before picking
                        # This prevents getting stuck after picking
                        cleaned = AIOptimalPlayer._clean_blocking_obstacle(
                            board, closest_to_princess, actions
                        )
                        if cleaned:
                            continue  # Successfully cleaned, check path again

                        # Can't clean any reachable obstacles
                        # As a last resort, try to find a different accessible flower
                        # that might give us a better position
                        accessible_flower_found = False
                        for flower in sorted(
                            board.flowers, key=lambda f: board.robot.position.manhattan_distance(f)
                        ):
                            adj_positions = AIOptimalPlayer._get_adjacent_positions(flower, board)
                            if adj_positions:
                                target = min(
                                    adj_positions,
                                    key=lambda p: board.robot.position.manhattan_distance(p),
                                )
                                path = AIOptimalPlayer._find_path(
                                    board, board.robot.position, target
                                )
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

                # MULTI-STEP PLANNING: Find the BEST order to pick flowers
                # Instead of greedy "nearest flower", we plan ahead

                # Get the optimal sequence of flowers to pick (max 3 before delivery)
                planned_flowers = AIOptimalPlayer._get_best_flower_order(
                    board,
                    board.flowers,
                    board.robot.position,
                    board.princess_position,
                    max_batch_size=3,
                )

                safe_flower = None
                safe_flower_target = None

                # Try to pick the first flower from the planned sequence
                for flower in planned_flowers:
                    # Check if we can reach adjacent to this flower
                    adj_to_flower = AIOptimalPlayer._get_adjacent_positions(flower, board)
                    if not adj_to_flower:
                        continue  # Flower surrounded, skip

                    target_near_flower = min(
                        adj_to_flower, key=lambda p: board.robot.position.manhattan_distance(p)
                    )
                    path_to_flower = AIOptimalPlayer._find_path(
                        board, board.robot.position, target_near_flower
                    )

                    if not path_to_flower:
                        continue  # Can't reach this flower right now, skip

                    # Found a reachable flower from the plan!
                    safe_flower = flower
                    safe_flower_target = target_near_flower
                    break

                # If no flowers from the plan are reachable, fall back to any accessible flower
                if not safe_flower and board.flowers:
                    for flower in sorted(
                        board.flowers, key=lambda f: board.robot.position.manhattan_distance(f)
                    ):
                        adj_to_flower = AIOptimalPlayer._get_adjacent_positions(flower, board)
                        if not adj_to_flower:
                            continue

                        target_near_flower = min(
                            adj_to_flower, key=lambda p: board.robot.position.manhattan_distance(p)
                        )
                        path_to_flower = AIOptimalPlayer._find_path(
                            board, board.robot.position, target_near_flower
                        )

                        if not path_to_flower:
                            continue

                        # Check if FROM this flower position, we can reach princess
                        path_from_flower_to_princess = AIOptimalPlayer._find_path(
                            board, target_near_flower, closest_to_princess
                        )

                        # Accept flower if safe or if we're willing to take risk
                        is_safe = (
                            path_from_flower_to_princess
                            or board.robot.flowers_held > 0
                            or len(board.flowers) == 1
                            or (board.robot.flowers_held == 0 and len(board.flowers) <= 3)
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
                        path_to_princess_now = AIOptimalPlayer._find_path(
                            board, board.robot.position, closest_to_princess
                        )
                        if path_to_princess_now:
                            # We CAN deliver! Force delivery on next iteration
                            # by continuing - the main loop will handle it
                            continue
                        else:
                            # Can't deliver - try drop-clean-repick
                            drop_positions = AIOptimalPlayer._get_adjacent_positions(
                                board.robot.position, board
                            )
                            if drop_positions:
                                # Drop all flowers
                                while board.robot.flowers_held > 0:
                                    drop_pos = drop_positions[0]
                                    direction = AIOptimalPlayer._get_direction(
                                        board.robot.position, drop_pos
                                    )
                                    actions.append(("rotate", direction))
                                    GameService.rotate_robot(board, direction)
                                    actions.append(("drop", None))
                                    GameService.drop_flower(board)

                                # Now try to clean obstacles
                                if AIOptimalPlayer._clean_blocking_obstacle(
                                    board, closest_to_princess, actions
                                ):
                                    continue
                    else:
                        # No flowers held - try cleaning obstacles to open up paths
                        if AIOptimalPlayer._clean_blocking_obstacle(
                            board, closest_to_princess, actions
                        ):
                            continue

                    # No safe moves, give up
                    break

                # Navigate to the safe flower
                path = AIOptimalPlayer._find_path(board, board.robot.position, safe_flower_target)
                if not path:
                    # Shouldn't happen since we verified above, but be safe
                    if not AIOptimalPlayer._clean_blocking_obstacle(
                        board, safe_flower_target, actions
                    ):
                        break
                    continue

                for next_pos in path:
                    direction = AIOptimalPlayer._get_direction(board.robot.position, next_pos)
                    actions.append(("rotate", direction))
                    GameService.rotate_robot(board, direction)

                    actions.append(("move", None))
                    GameService.move_robot(board)

                # Face the safe flower and pick it
                direction = AIOptimalPlayer._get_direction(board.robot.position, safe_flower)
                actions.append(("rotate", direction))
                GameService.rotate_robot(board, direction)

                actions.append(("pick", None))
                GameService.pick_flower(board)

                # CRITICAL FIX: After picking flower, board state changed!
                # Re-check if we now have a path to princess from new position
                # This is especially important when obstacles were cleaned or robot moved
                if board.robot.flowers_held >= min(3, board.robot.max_flowers):
                    # We have enough flowers to deliver, check if path exists NOW
                    princess_adjacent_now = AIOptimalPlayer._get_adjacent_positions(
                        board.princess_position, board
                    )
                    if princess_adjacent_now:
                        closest_now = min(
                            princess_adjacent_now,
                            key=lambda p: board.robot.position.manhattan_distance(p),
                        )
                        path_now = AIOptimalPlayer._find_path(
                            board, board.robot.position, closest_now
                        )
                        # If path exists now, continue to delivery phase on next iteration
                        # The main loop will handle delivery
                        if path_now:
                            continue
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
    def _score_flower_sequence(
        board: Game, flower_sequence: List[Position], start_pos: Position, princess_pos: Position
    ) -> tuple[int, bool]:
        """
        Score a flower picking sequence based on total path cost.

        Returns: (total_cost, is_valid)
        - total_cost: Sum of path lengths (robot -> flower1 -> flower2 -> ... -> princess)
        - is_valid: Whether all paths in the sequence exist
        """
        if not flower_sequence:
            return (0, True)

        total_cost = 0
        current_pos = start_pos

        # Cost to reach each flower in sequence
        for flower in flower_sequence:
            # Find adjacent position to flower
            adj_positions = AIOptimalPlayer._get_adjacent_positions(flower, board)
            if not adj_positions:
                return (99999, False)  # Can't reach this flower

            best_adj = min(adj_positions, key=lambda p: current_pos.manhattan_distance(p))
            path = AIOptimalPlayer._find_path(board, current_pos, best_adj)

            if not path:
                return (99999, False)  # No path to flower

            total_cost += len(path) + 1  # +1 for picking
            current_pos = best_adj

        # Cost to reach princess from last flower
        princess_adj = AIOptimalPlayer._get_adjacent_positions(princess_pos, board)
        if not princess_adj:
            return (99999, False)  # Can't reach princess

        best_princess_adj = min(princess_adj, key=lambda p: current_pos.manhattan_distance(p))
        path_to_princess = AIOptimalPlayer._find_path(board, current_pos, best_princess_adj)

        if not path_to_princess:
            return (99999, False)  # No path to princess

        total_cost += len(path_to_princess) + 1  # +1 for delivering

        return (total_cost, True)

    @staticmethod
    def _get_best_flower_order(
        board: Game,
        flowers: set[Position],
        robot_pos: Position,
        princess_pos: Position,
        max_batch_size: int = 3,
    ) -> List[Position]:
        """
        Find the best order to pick flowers using multi-step planning.

        For small sets (<=4 flowers), tries all permutations.
        For larger sets, uses greedy approach with look-ahead.

        Args:
            max_batch_size: Plan for picking this many flowers before delivery
        """
        if not flowers:
            return []

        flowers_list = list(flowers)

        # For very small sets, try all permutations (optimal)
        if len(flowers_list) <= 4:
            from itertools import permutations

            best_sequence = flowers_list
            best_cost = 99999

            for perm in permutations(flowers_list):
                cost, is_valid = AIOptimalPlayer._score_flower_sequence(
                    board, list(perm), robot_pos, princess_pos
                )
                if is_valid and cost < best_cost:
                    best_cost = cost
                    best_sequence = list(perm)

            return best_sequence

        # For larger sets, use greedy with 2-step look-ahead
        # Plan to pick max_batch_size flowers, then deliver
        best_sequence = []
        remaining = set(flowers_list)
        current_pos = robot_pos

        while remaining and len(best_sequence) < max_batch_size:
            best_flower = None
            best_2step_cost = 99999

            for flower in remaining:
                # Cost to reach this flower
                adj_positions = AIOptimalPlayer._get_adjacent_positions(flower, board)
                if not adj_positions:
                    continue

                best_adj = min(adj_positions, key=lambda p: current_pos.manhattan_distance(p))
                path_to_flower = AIOptimalPlayer._find_path(board, current_pos, best_adj)

                if not path_to_flower:
                    continue

                cost_to_flower = len(path_to_flower)

                # Look ahead: what's the best next flower after this one?
                remaining_after = remaining - {flower}
                if remaining_after:
                    min_next_cost = min(
                        flower.manhattan_distance(next_f) for next_f in remaining_after
                    )
                else:
                    # Last flower - cost to princess
                    princess_adj = AIOptimalPlayer._get_adjacent_positions(princess_pos, board)
                    if princess_adj:
                        min_next_cost = min(best_adj.manhattan_distance(p) for p in princess_adj)
                    else:
                        min_next_cost = 999

                # 2-step cost: this flower + estimated next move
                total_2step = cost_to_flower + min_next_cost

                if total_2step < best_2step_cost:
                    best_2step_cost = total_2step
                    best_flower = flower

            if best_flower is None:
                break

            best_sequence.append(best_flower)
            remaining.remove(best_flower)

            # Update current position for next iteration
            adj = AIOptimalPlayer._get_adjacent_positions(best_flower, board)
            if adj:
                current_pos = min(adj, key=lambda p: current_pos.manhattan_distance(p))

        return best_sequence

    @staticmethod
    def _evaluate_obstacle_cleaning_options(
        board: Game,
        robot_pos: Position,
        flowers: set[Position],
        princess_pos: Position,
        max_options: int = 3,
    ) -> List[tuple[Position, int]]:
        """
        Evaluate which obstacles, if cleaned, would open up the best paths.

        Returns: List of (obstacle_position, improvement_score) sorted by score (descending)

        Improvement score is based on:
        - How many flowers become accessible
        - How much closer we get to princess
        - How many new paths open up
        """
        # Find all obstacles we can reach
        reachable_obstacles = []
        for direction in [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]:
            row_delta, col_delta = direction.get_delta()

            # Check all distances up to 3 squares away
            for distance in range(1, 4):
                obstacle_pos = Position(
                    robot_pos.row + (row_delta * distance), robot_pos.col + (col_delta * distance)
                )

                if board.is_valid_position(obstacle_pos) and obstacle_pos in board.obstacles:

                    # Check if we can reach adjacent to this obstacle
                    adj_to_obstacle = []
                    for d in Direction:
                        dr, dc = d.get_delta()
                        adj_pos = obstacle_pos.move(dr, dc)
                        if board.is_valid_position(adj_pos) and board.is_empty(adj_pos):
                            adj_to_obstacle.append(adj_pos)

                    if adj_to_obstacle:
                        # Check if we can actually navigate to this obstacle
                        best_adj = min(
                            adj_to_obstacle, key=lambda p: robot_pos.manhattan_distance(p)
                        )
                        if AIOptimalPlayer._find_path(board, robot_pos, best_adj):
                            reachable_obstacles.append(obstacle_pos)
                            break  # Found one in this direction, move to next direction

        if not reachable_obstacles:
            return []

        # Score each obstacle by simulating its removal
        scored_obstacles = []

        for obstacle_pos in reachable_obstacles[:max_options]:  # Limit evaluation to top N
            score = 0

            # Simulate removing this obstacle (temporarily)
            board.obstacles.discard(obstacle_pos)

            try:
                # Score 1: How many flowers become accessible?
                accessible_flowers_before = 0
                accessible_flowers_after = 0

                board.obstacles.add(obstacle_pos)  # Add back
                for flower in flowers:
                    adj = AIOptimalPlayer._get_adjacent_positions(flower, board)
                    if adj and any(AIOptimalPlayer._find_path(board, robot_pos, a) for a in adj):
                        accessible_flowers_before += 1

                board.obstacles.discard(obstacle_pos)  # Remove again
                for flower in flowers:
                    adj = AIOptimalPlayer._get_adjacent_positions(flower, board)
                    if adj and any(AIOptimalPlayer._find_path(board, robot_pos, a) for a in adj):
                        accessible_flowers_after += 1

                score += (accessible_flowers_after - accessible_flowers_before) * 100

                # Score 2: Does it open path to princess?
                princess_adj = AIOptimalPlayer._get_adjacent_positions(princess_pos, board)
                if princess_adj:
                    path_to_princess = any(
                        AIOptimalPlayer._find_path(board, robot_pos, pa) for pa in princess_adj
                    )
                    if path_to_princess:
                        score += 50  # Big bonus for opening princess path

                # Score 3: Distance to obstacle (prefer closer obstacles)
                distance_penalty = robot_pos.manhattan_distance(obstacle_pos)
                score -= distance_penalty

            finally:
                # Always restore the obstacle
                board.obstacles.add(obstacle_pos)

            scored_obstacles.append((obstacle_pos, score))

        # Sort by score (descending)
        scored_obstacles.sort(key=lambda x: x[1], reverse=True)

        return scored_obstacles

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
        Try to clean an obstacle using SMART LOOK-AHEAD evaluation.

        Instead of just cleaning the closest obstacle to target, this method:
        1. Evaluates multiple reachable obstacles
        2. Scores them based on how many flowers they unlock and princess accessibility
        3. Cleans the obstacle with the highest improvement score

        Returns True if an obstacle was cleaned, False otherwise.
        """
        # Can't clean while holding flowers
        if board.robot.flowers_held > 0:
            return False

        # Use smart evaluation to find the BEST obstacle to clean
        scored_obstacles = AIOptimalPlayer._evaluate_obstacle_cleaning_options(
            board,
            board.robot.position,
            board.flowers,
            board.princess_position,
            max_options=5,  # Evaluate top 5 reachable obstacles
        )

        if not scored_obstacles:
            return False

        # Try to clean the highest-scored obstacle
        best_obstacle_pos, best_score = scored_obstacles[0]

        # Find adjacent positions to this obstacle
        adj_positions = []
        for direction in Direction:
            row_delta, col_delta = direction.get_delta()
            adj_pos = best_obstacle_pos.move(row_delta, col_delta)
            if board.is_valid_position(adj_pos) and board.is_empty(adj_pos):
                adj_positions.append(adj_pos)

        if not adj_positions:
            return False

        # Navigate to the closest adjacent position
        best_adj = min(adj_positions, key=lambda p: board.robot.position.manhattan_distance(p))
        path = AIOptimalPlayer._find_path(board, board.robot.position, best_adj)

        if not path:
            # Can't reach best obstacle, try the next one
            if len(scored_obstacles) > 1:
                second_best_pos, _ = scored_obstacles[1]
                adj_positions_2 = []
                for direction in Direction:
                    row_delta, col_delta = direction.get_delta()
                    adj_pos = second_best_pos.move(row_delta, col_delta)
                    if board.is_valid_position(adj_pos) and board.is_empty(adj_pos):
                        adj_positions_2.append(adj_pos)

                if adj_positions_2:
                    best_adj_2 = min(
                        adj_positions_2, key=lambda p: board.robot.position.manhattan_distance(p)
                    )
                    path_2 = AIOptimalPlayer._find_path(board, board.robot.position, best_adj_2)
                    if path_2:
                        path = path_2
                        best_adj = best_adj_2
                        best_obstacle_pos = second_best_pos
                    else:
                        return False
                else:
                    return False
            else:
                return False

        # Navigate to obstacle
        for next_pos in path:
            direction = AIOptimalPlayer._get_direction(board.robot.position, next_pos)
            actions.append(("rotate", direction))
            GameService.rotate_robot(board, direction)

            actions.append(("move", None))
            GameService.move_robot(board)

        # Face obstacle and clean it
        direction = AIOptimalPlayer._get_direction(board.robot.position, best_obstacle_pos)
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
                path = AIOptimalPlayer._find_path(board, board.robot.position, robot_pos)
                if not path:
                    continue

                for next_pos in path:
                    direction = AIOptimalPlayer._get_direction(board.robot.position, next_pos)
                    actions.append(("rotate", direction))
                    GameService.rotate_robot(board, direction)

                    actions.append(("move", None))
                    GameService.move_robot(board)

                # Face obstacle and clean it
                direction = AIOptimalPlayer._get_direction(board.robot.position, obstacle_pos)
                actions.append(("rotate", direction))
                GameService.rotate_robot(board, direction)

                actions.append(("clean", None))
                GameService.clean_obstacle(board)

                return True

        return False
