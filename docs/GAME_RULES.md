# Robot Flower Princess - Game Rules

## 📖 Overview

**Robot Flower Princess** is a grid-based puzzle game where a robot must collect flowers from a board and deliver them to a princess. The robot must navigate around obstacles and make strategic decisions to complete the objective efficiently.

---

## 🎯 Game Objective

**Win Condition**: Collect all flowers on the board and deliver them to the princess.

**Success Criteria**:
- ✅ All flowers have been picked up by the robot
- ✅ All collected flowers have been delivered to the princess
- ✅ Robot is adjacent to the princess when delivering

---

## 🎮 Game Setup

### Board

The game is played on a **rectangular grid** (rows × columns):
- **Default sizes**: 5×5, 7×7, 10×10, or custom dimensions
- Each cell can contain:
  - Empty space
  - Robot (starting position)
  - Princess (fixed position)
  - Flower (to be collected)
  - Obstacle (blocks movement)

### Initial State

When a game starts:
1. **Board** is created with specified dimensions
2. **Princess** is placed at a fixed position (typically center or predefined location)
3. **Robot** is placed at its starting position
4. **Flowers** are randomly distributed on the board (configurable count)
5. **Obstacles** are randomly distributed on the board (configurable count)

### Example Board Layout

```
5×5 Board:
┌─────┬─────┬─────┬─────┬─────┐
│  R  │     │  🌸  │     │  X  │  Row 0
├─────┼─────┼─────┼─────┼─────┤
│     │  X  │     │  🌸  │     │  Row 1
├─────┼─────┼─────┼─────┼─────┤
│  🌸  │     │  👸  │     │     │  Row 2
├─────┼─────┼─────┼─────┼─────┤
│     │     │     │  X  │  🌸  │  Row 3
├─────┼─────┼─────┼─────┼─────┤
│  X  │  🌸  │     │     │     │  Row 4
└─────┴─────┴─────┴─────┴─────┘

Legend:
  R  = Robot
  👸 = Princess
  🌸 = Flower
  X  = Obstacle
     = Empty cell
```

---

## 🤖 Game Entities

### Robot

**Attributes**:
- **Position**: Current location on the board (row, col)
- **Orientation**: Direction the robot is facing (NORTH, SOUTH, EAST, WEST)
- **Collected Flowers**: List of flowers currently held by the robot
- **Capacity**: Maximum number of flowers the robot can carry (default: 10)
- **Delivered Flowers**: Count of flowers successfully delivered to the princess
- **Cleaned Obstacles**: List of obstacles removed by the robot

**Capabilities**:
- Move in four directions (after rotating to face that direction)
- Rotate to face any cardinal direction
- Pick up flowers from adjacent cells
- Drop flowers in adjacent cells
- Deliver flowers to the princess (when adjacent)
- Clean obstacles from adjacent cells

### Princess

**Attributes**:
- **Position**: Fixed location on the board (row, col)
- **Flowers Received**: List of flowers delivered by the robot
- **Mood**: Current mood state (neutral, happy)

**Behavior**:
- Stays in a fixed position throughout the game
- Receives flowers from the robot when it's adjacent
- Changes mood based on flowers received

### Flowers

**Attributes**:
- **Position**: Location on the board (row, col)
- **Type**: Flower type (for future extensions)

**Behavior**:
- Remain stationary until picked up by the robot
- Can be picked up when the robot is adjacent
- Must be delivered to the princess to win

### Obstacles

**Attributes**:
- **Position**: Location on the board (row, col)

**Behavior**:
- Block robot movement
- Can be cleaned/removed by the robot
- Remain stationary unless cleaned

---

## 🎲 Actions & Mechanics

### 1. Rotate

**Purpose**: Change the robot's orientation

**Parameters**:
- `direction`: Target direction (NORTH, SOUTH, EAST, WEST)

**Rules**:
- ✅ Can rotate to any cardinal direction instantly
- ✅ No restrictions on rotation
- ✅ Does not consume a turn

**Example**:
```
Robot at (2,2) facing NORTH
Action: rotate(EAST)
Result: Robot at (2,2) now facing EAST
```

### 2. Move

**Purpose**: Move the robot forward in its current orientation

**Parameters**: None (uses robot's current orientation)

**Rules**:
- ✅ Robot moves one cell in the direction it's facing
- ❌ Cannot move if target cell is blocked by an obstacle
- ❌ Cannot move outside the board boundaries
- ✅ Movement is validated before execution

**Directions**:
- **NORTH**: Row decreases (row - 1)
- **SOUTH**: Row increases (row + 1)
- **EAST**: Column increases (col + 1)
- **WEST**: Column decreases (col - 1)

**Example**:
```
Robot at (2,2) facing NORTH
Action: move()
Result: Robot moves to (1,2)
```

**Error Cases**:
- `InvalidMoveException`: Target cell is blocked or out of bounds

### 3. Pick

**Purpose**: Pick up a flower from an adjacent cell

**Parameters**: None (uses robot's current orientation)

**Rules**:
- ✅ Robot must be adjacent to a flower
- ✅ Flower must be in the direction the robot is facing
- ❌ Cannot pick if robot's capacity is full
- ✅ Flower is removed from the board and added to robot's inventory

**Example**:
```
Robot at (2,2) facing NORTH, flower at (1,2)
Action: pick()
Result: Flower removed from (1,2), added to robot's inventory
```

**Error Cases**:
- `InvalidPickException`: No flower in target cell or capacity full

### 4. Drop

**Purpose**: Drop a flower in an adjacent cell

**Parameters**: None (uses robot's current orientation)

**Rules**:
- ✅ Robot must have at least one flower in inventory
- ✅ Target cell must be empty
- ✅ Target cell must be in the direction the robot is facing
- ✅ Flower is removed from robot's inventory and placed on the board

**Example**:
```
Robot at (2,2) facing NORTH, holding 1 flower
Action: drop()
Result: Flower placed at (1,2), removed from robot's inventory
```

**Error Cases**:
- `InvalidDropException`: No flowers to drop or target cell not empty

### 5. Give

**Purpose**: Deliver all flowers to the princess

**Parameters**: None (uses robot's current orientation)

**Rules**:
- ✅ Robot must be adjacent to the princess
- ✅ Princess must be in the direction the robot is facing
- ✅ Robot must have at least one flower in inventory
- ✅ All flowers are transferred from robot to princess
- ✅ Princess's mood may change (becomes happy)

**Example**:
```
Robot at (2,2) facing EAST, princess at (2,3), holding 3 flowers
Action: give()
Result: 3 flowers transferred to princess, robot's inventory empty
```

**Error Cases**:
- `InvalidGiveException`: Not adjacent to princess or no flowers to give

### 6. Clean

**Purpose**: Remove an obstacle from an adjacent cell

**Parameters**: None (uses robot's current orientation)

**Rules**:
- ✅ Robot must be adjacent to an obstacle
- ✅ Obstacle must be in the direction the robot is facing
- ✅ Obstacle is removed from the board
- ✅ Cell becomes passable after cleaning

**Example**:
```
Robot at (2,2) facing NORTH, obstacle at (1,2)
Action: clean()
Result: Obstacle removed from (1,2), cell is now empty
```

**Error Cases**:
- `InvalidCleanException`: No obstacle in target cell

---

## 🏆 Victory Conditions

The game is won when **ALL** of the following conditions are met:

1. ✅ **All flowers have been collected**: No flowers remain on the board
2. ✅ **All flowers have been delivered**: Robot's inventory is empty
3. ✅ **Princess has received all flowers**: Princess's flower count matches initial flower count

**Game Status**:
- `"In Progress"`: Game is still active
- `"Victory"`: All victory conditions met
- `"Game Over"`: Maximum actions exceeded or game terminated

---

## 📏 Game Rules & Constraints

### Movement Rules

1. **Grid Boundaries**: Robot cannot move outside the board
2. **Obstacle Blocking**: Robot cannot move through obstacles (must clean them first)
3. **Single Occupancy**: Each cell can only hold one entity (robot, princess, flower, or obstacle)
4. **Directional Actions**: All actions (except rotate) operate in the direction the robot is facing

### Inventory Rules

1. **Capacity Limit**: Robot can carry a maximum of 10 flowers (configurable)
2. **Bulk Delivery**: Give action delivers ALL flowers at once
3. **Flower Conservation**: Flowers cannot be destroyed, only moved

### Action Rules

1. **Sequential Execution**: Actions are executed one at a time
2. **Validation**: Each action is validated before execution
3. **State Persistence**: Game state is updated after each successful action
4. **Error Handling**: Invalid actions throw exceptions and don't modify state

### Strategy Considerations

**Optimal Strategy**:
1. **Plan Ahead**: Calculate the shortest path to collect all flowers
2. **Efficient Routing**: Minimize total distance traveled
3. **Obstacle Management**: Clean obstacles only when necessary
4. **Batch Collection**: Collect multiple flowers before delivering (up to capacity)
5. **Direct Delivery**: Deliver flowers when near the princess

**Common Pitfalls**:
- ❌ Collecting flowers one at a time (inefficient)
- ❌ Cleaning unnecessary obstacles
- ❌ Poor path planning (zigzagging)
- ❌ Not utilizing full carrying capacity

---

## 🎯 Example Game Flow

### Scenario: 5×5 Board with 3 Flowers

**Initial State**:
```
┌─────┬─────┬─────┬─────┬─────┐
│  R  │     │  🌸  │     │     │
├─────┼─────┼─────┼─────┼─────┤
│     │     │     │     │     │
├─────┼─────┼─────┼─────┼─────┤
│  🌸  │     │  👸  │     │  🌸  │
└─────┴─────┴─────┴─────┴─────┘

Robot: (0,0), Facing NORTH, Flowers: 0
Princess: (2,2)
Flowers on board: (0,2), (2,0), (2,4)
```

**Optimal Solution** (9 actions):

1. **rotate(EAST)** → Robot faces EAST
2. **move()** → Robot at (0,1)
3. **move()** → Robot at (0,2)
4. **pick()** → Pick flower at (0,2), inventory: 1
5. **rotate(SOUTH)** → Robot faces SOUTH
6. **move()** → Robot at (1,2)
7. **move()** → Robot at (2,2)
8. **rotate(WEST)** → Robot faces WEST
9. **move()** → Robot at (2,1)
10. **move()** → Robot at (2,0)
11. **pick()** → Pick flower at (2,0), inventory: 2
12. **rotate(EAST)** → Robot faces EAST
13. **move()** → Robot at (2,1)
14. **move()** → Robot at (2,2)
15. **move()** → Robot at (2,3)
16. **move()** → Robot at (2,4)
17. **pick()** → Pick flower at (2,4), inventory: 3
18. **rotate(WEST)** → Robot faces WEST
19. **move()** → Robot at (2,3)
20. **give()** → Give 3 flowers to princess → **VICTORY!**

**Final State**:
```
┌─────┬─────┬─────┬─────┬─────┐
│     │     │     │     │     │
├─────┼─────┼─────┼─────┼─────┤
│     │     │     │     │     │
├─────┼─────┼─────┼─────┼─────┤
│     │     │  👸  │  R  │     │
└─────┴─────┴─────┴─────┴─────┘

Robot: (2,3), Facing WEST, Flowers: 0
Princess: (2,2), Flowers Received: 3
Status: VICTORY! 🎉
```

---

## 🤖 AI Players

The game supports multiple AI strategies:

### 1. Greedy Player
- **Strategy**: Always pick the nearest flower
- **Characteristics**:
  - Simple heuristic-based approach
  - Good for small boards
  - May not find optimal solution

### 2. Optimal Player
- **Strategy**: A* pathfinding to find optimal paths
- **Characteristics**:
  - Considers all flowers and obstacles
  - Finds near-optimal solutions
  - Good balance of speed and efficiency

### 3. ML Proxy Player
- **Strategy**: Uses machine learning model to predict actions
- **Characteristics**:
  - Learns from successful games
  - Can discover novel strategies
  - Requires trained model

---

## 📊 Game Metrics

Games are evaluated on several metrics:

- **Total Actions**: Number of actions taken to win
- **Efficiency**: Ratio of optimal actions to actual actions
- **Path Length**: Total distance traveled
- **Collection Efficiency**: Flowers collected per trip
- **Time to Completion**: Total time taken

---

## 🔗 Related Documentation

- **[API Documentation](API.md)** - API endpoints for game actions
- **[Architecture](ARCHITECTURE.md)** - System design and components
- **[ML Strategy](machine_learning/ML_GUIDE.md)** - Machine learning implementation
- **[Testing Guide](TESTING_GUIDE.md)** - How the game logic is tested

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Oct 2025 | Initial game rules documentation |

---

**Last Updated**: October 28, 2025
