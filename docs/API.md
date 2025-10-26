# API Documentation

## Table of Contents
- [Overview](#overview)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
  - [Health & Status](#health--status)
  - [Game Management](#game-management)
  - [Game Actions](#game-actions)
  - [AI Autoplay](#ai-autoplay)
- [Request/Response Schemas](#requestresponse-schemas)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Examples](#examples)

---

## Overview

The **Robot Flower Princess API** is a RESTful API built with FastAPI that provides endpoints for managing puzzle games where a robot collects flowers and delivers them to a princess.

### Key Features
- ✅ **Create and manage games** with custom board sizes
- ✅ **Control robot actions** (move, rotate, pick, drop, give, clean)
- ✅ **AI autoplay** to automatically solve games
- ✅ **Game history tracking** for all actions
- ✅ **Validation** with Pydantic v2
- ✅ **Interactive documentation** with Swagger UI and ReDoc

### API Version
**Version**: 1.0.0

### Content Type
All requests and responses use `application/json` unless otherwise specified.

---

## Base URL

### Local Development
```
http://localhost:8000
```

### Production
```
https://your-domain.com
```

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Authentication

**Current Status**: No authentication required.

The API is currently open and does not require authentication. In production, you should implement:
- API keys
- OAuth 2.0
- JWT tokens

See [Deployment Documentation](DEPLOYMENT.md) for security recommendations.

---

## API Endpoints

### Health & Status

#### GET /health - Health Check

Check API health status.

**Response 200 OK**
```json
{
  "status": "healthy",
  "service": "robot-flower-princess-api"
}
```

**cURL Example**
```bash
curl http://localhost:8000/health
```

**Use Case**: Health checks, load balancer probes, monitoring systems.

---

### Game Management

#### POST /api/games - Create Game

Create a new game with specified board size.

**Request Body**
```json
{
  "rows": 10,
  "cols": 10,
  "name": "My Game"  // Optional
}
```

**Parameters**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `rows` | integer | Yes | 3-50 | Number of rows on the board |
| `cols` | integer | Yes | 3-50 | Number of columns on the board |
| `name` | string | No | - | Optional game name (default: auto-generated) |

**Response 201 Created**
```json
{
  "id": "abc123",
  "status": "in_progress",
  "message": "Game created successfully",
  "board": {
    "rows": 10,
    "cols": 10,
    "grid": [
      ["🤖", "⬜", "⬜", "🌸", "⬜", "⬜", "🗑️", "⬜", "⬜", "⬜"],
      ["⬜", "⬜", "⬜", "⬜", "⬜", "🗑️", "⬜", "⬜", "⬜", "⬜"],
      // ... more rows
      ["⬜", "⬜", "⬜", "⬜", "⬜", "⬜", "⬜", "⬜", "⬜", "👑"]
    ]
  },
  "robot": {
    "position": { "row": 0, "col": 0 },
    "orientation": "north",
    "flowers": {
      "collected": [],
      "delivered": [],
      "collection_capacity": 12
    },
    "obstacles": {
      "cleaned": []
    },
    "executed_actions": []
  },
  "princess": {
    "position": { "row": 9, "col": 9 },
    "flowers_received": 0,
    "mood": "neutral"
  },
  "obstacles": {
    "remaining": 30,
    "total": 30
  },
  "flowers": {
    "remaining": 10,
    "total": 10
  },
  "created_at": "2025-10-24T12:00:00Z",
  "updated_at": "2025-10-24T12:00:00Z"
}
```

**Errors**

| Status Code | Description |
|-------------|-------------|
| 400 | Invalid board size (out of range 3-50) |
| 422 | Validation error (invalid request format) |

**cURL Example**
```bash
curl -X POST "http://localhost:8000/api/games" \
  -H "Content-Type: application/json" \
  -d '{
    "rows": 10,
    "cols": 10,
    "name": "My First Game"
  }'
```

**Game Generation Rules**:
- Robot starts at top-left (0, 0) facing NORTH
- Princess placed at bottom-right
- Flowers: randomly placed, ~10% of board cells
- Obstacles: randomly placed, ~30% of board cells
- No entities overlap initially

---

#### GET /api/games - List Games

Get a list of all games, optionally filtered by status.

**Query Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | 10 | Maximum number of games to return |
| `status` | string | No | "in_progress" | Filter by game status |

**Valid Status Values**: `in_progress`, `won`, `lost`

**Response 200 OK**
```json
{
  "gamess": [  // Note: typo in field name (legacy)
    {
      "id": "abc123",
      "board": { /* board data */ },
      "robot": { /* robot data */ },
      "princess": { /* princess data */ },
      "obstacles": { "remaining": 25, "total": 30 },
      "flowers": { "remaining": 5, "total": 10 },
      "status": "in_progress",
      "created_at": "2025-10-24T12:00:00Z",
      "updated_at": "2025-10-24T12:05:30Z"
    }
  ],
  "total": 1
}
```

**cURL Example**
```bash
# Get last 10 in-progress games
curl "http://localhost:8000/api/games?limit=10&status=in_progress"

# Get all games
curl "http://localhost:8000/api/games?limit=100"
```

---

#### GET /api/games/{game_id} - Get Game State

Retrieve the current state of a specific game.

**Path Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `game_id` | string | Yes | Unique game identifier |

**Response 200 OK**
```json
{
  "id": "abc123",
  "status": "in_progress",
  "message": "",
  "board": { /* board grid */ },
  "robot": {
    "position": { "row": 2, "col": 3 },
    "orientation": "east",
    "flowers": {
      "collected": [
        { "position": { "row": 1, "col": 2 } },
        { "position": { "row": 2, "col": 2 } }
      ],
      "delivered": [],
      "collection_capacity": 12
    },
    "obstacles": {
      "cleaned": [
        { "position": { "row": 1, "col": 1 } }
      ]
    },
    "executed_actions": [
      { "type": "rotate", "direction": "east" },
      { "type": "move", "direction": "east" }
    ]
  },
  "princess": {
    "position": { "row": 9, "col": 9 },
    "flowers_received": 0,
    "mood": "neutral"
  },
  "obstacles": {
    "remaining": 29,
    "total": 30
  },
  "flowers": {
    "remaining": 8,
    "total": 10
  },
  "created_at": "2025-10-24T12:00:00Z",
  "updated_at": "2025-10-24T12:05:30Z"
}
```

**Errors**

| Status Code | Description |
|-------------|-------------|
| 404 | Game not found |

**cURL Example**
```bash
curl "http://localhost:8000/api/games/abc123"
```

---

#### GET /api/games/{game_id}/history - Get Game History

Retrieve the action history for a specific game.

**Path Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `game_id` | string | Yes | Unique game identifier |

**Response 200 OK**
```json
{
  "id": "abc123",
  "history": {
    "game_id": "abc123",
    "actions": [
      {
        "action_type": "rotate",
        "direction": "east",
        "success": true,
        "message": "Robot rotated to face east",
        "timestamp": "2025-10-24T12:01:00Z"
      },
      {
        "action_type": "move",
        "direction": "east",
        "success": true,
        "message": "Robot moved east",
        "timestamp": "2025-10-24T12:01:05Z"
      },
      {
        "action_type": "pickFlower",
        "direction": "east",
        "success": true,
        "message": "Robot picked flower",
        "timestamp": "2025-10-24T12:01:10Z"
      }
    ],
    "created_at": "2025-10-24T12:00:00Z",
    "updated_at": "2025-10-24T12:01:10Z",
    "actions_count": 3
  }
}
```

**Errors**

| Status Code | Description |
|-------------|-------------|
| 404 | Game not found |

**cURL Example**
```bash
curl "http://localhost:8000/api/games/abc123/history"
```

---

### Game Actions

#### POST /api/games/{game_id}/action - Perform Action

Execute a game action (move, rotate, pick, drop, give, clean).

**Path Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `game_id` | string | Yes | Unique game identifier |

**Request Body**
```json
{
  "action": "move",
  "direction": "east"
}
```

**Parameters**

| Field | Type | Required | Valid Values | Description |
|-------|------|----------|-------------|-------------|
| `action` | string | Yes | `rotate`, `move`, `pickFlower`, `dropFlower`, `giveFlower`, `clean` | Action to perform |
| `direction` | string | Yes | `north`, `south`, `east`, `west` | Direction for the action |

**Action Types**

| Action | Description | Requirements |
|--------|-------------|------------|
| `rotate` | Turn robot to face direction | None |
| `move` | Move robot one cell forward | Cell must be empty |
| `pickFlower` | Pick flower in front of robot | Flower must be adjacent, robot not full |
| `dropFlower` | Drop flower in front of robot | Robot must hold flowers, cell must be empty |
| `giveFlower` | Give flowers to princess | Princess must be adjacent, robot must hold flowers |
| `clean` | Remove obstacle in front | Obstacle must be adjacent, robot must not hold flowers |

**Response 200 OK**
```json
{
  "success": true,
  "id": "abc123",
  "status": "in_progress",
  "board": { /* updated board */ },
  "robot": { /* updated robot */ },
  "princess": { /* updated princess */ },
  "obstacles": { "remaining": 29, "total": 30 },
  "flowers": { "remaining": 9, "total": 10 },
  "message": "Robot moved east"
}
```

**Response 200 OK (Failed Action)**
```json
{
  "success": false,
  "id": "abc123",
  "status": "in_progress",
  "board": { /* unchanged board */ },
  "robot": { /* unchanged robot */ },
  "princess": { /* unchanged princess */ },
  "obstacles": { "remaining": 30, "total": 30 },
  "flowers": { "remaining": 10, "total": 10 },
  "message": "Target cell is blocked by obstacle"
}
```

**Response 200 OK (Game Won)**
```json
{
  "success": true,
  "id": "abc123",
  "status": "won",
  "board": { /* final board */ },
  "robot": { /* final robot */ },
  "princess": {
    "position": { "row": 9, "col": 9 },
    "flowers_received": 10,
    "mood": "happy"
  },
  "obstacles": { "remaining": 25, "total": 30 },
  "flowers": { "remaining": 0, "total": 10 },
  "message": "Congratulations! All flowers delivered to the princess!"
}
```

**Errors**

| Status Code | Description |
|-------------|-------------|
| 404 | Game not found |
| 422 | Invalid action or direction value |

**cURL Examples**

```bash
# Rotate to face east
curl -X POST "http://localhost:8000/api/games/abc123/action" \
  -H "Content-Type: application/json" \
  -d '{"action": "rotate", "direction": "east"}'

# Move forward
curl -X POST "http://localhost:8000/api/games/abc123/action" \
  -H "Content-Type: application/json" \
  -d '{"action": "move", "direction": "east"}'

# Pick flower
curl -X POST "http://localhost:8000/api/games/abc123/action" \
  -H "Content-Type: application/json" \
  -d '{"action": "pickFlower", "direction": "east"}'

# Give flowers to princess
curl -X POST "http://localhost:8000/api/games/abc123/action" \
  -H "Content-Type: application/json" \
  -d '{"action": "giveFlower", "direction": "south"}'

# Clean obstacle
curl -X POST "http://localhost:8000/api/games/abc123/action" \
  -H "Content-Type: application/json" \
  -d '{"action": "clean", "direction": "north"}'

# Drop flower
curl -X POST "http://localhost:8000/api/games/abc123/action" \
  -H "Content-Type: application/json" \
  -d '{"action": "dropFlower", "direction": "south"}'
```

---

### AI Autoplay

#### POST /api/games/{game_id}/autoplay - AI Solve Game

Let the AI automatically solve the game using pathfinding and strategic planning.

**Path Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `game_id` | string | Yes | Unique game identifier |

**Query Parameters**

| Parameter | Type | Required | Default | Valid Values | Description |
|-----------|------|----------|---------|--------------|-------------|
| `strategy` | string | No | `greedy` | `greedy`, `optimal`, `ml` | AI strategy to use |

**Strategy Options**:
- **`greedy`** (default): Safe & reliable. 75% success rate. Uses BFS pathfinding. Best for learning and guaranteed completion.
- **`optimal`**: Fast & efficient. 62% success rate, but 25% fewer actions. Uses A* pathfinding and multi-step planning. Best for speed.
- **`ml`**: ML-powered hybrid. Uses ML Player service for predictions. Heuristic-based MVP with ML upgrade path. Best for adaptive behavior.

**Request Body**
Empty (no body required)

**Response 200 OK (Success)**
```json
{
  "success": true,
  "id": "abc123",
  "status": "won",
  "board": { /* final board */ },
  "robot": {
    "position": { "row": 8, "col": 9 },
    "orientation": "south",
    "flowers": {
      "collected": [
        { "position": { "row": 1, "col": 2 } },
        { "position": { "row": 3, "col": 5 } },
        // ... all flowers
      ],
      "delivered": [
        { "position": { "row": 9, "col": 9 } },
        { "position": { "row": 9, "col": 9 } },
        // ... all deliveries
      ],
      "collection_capacity": 12
    },
    "obstacles": {
      "cleaned": [
        { "position": { "row": 2, "col": 3 } },
        { "position": { "row": 5, "col": 6 } }
      ]
    },
    "executed_actions": [ /* 50+ actions */ ]
  },
  "princess": {
    "position": { "row": 9, "col": 9 },
    "flowers_received": 10,
    "mood": "happy"
  },
  "obstacles": { "remaining": 28, "total": 30 },
  "flowers": { "remaining": 0, "total": 10 },
  "message": "AI solved the game! All flowers delivered. (Actions taken: 52)"
}
```

**Response 200 OK (Failed)**
```json
{
  "success": false,
  "id": "abc123",
  "status": "in_progress",
  "board": { /* partial progress */ },
  "robot": { /* robot state */ },
  "princess": { /* princess state */ },
  "obstacles": { "remaining": 29, "total": 30 },
  "flowers": { "remaining": 5, "total": 10 },
  "message": "AI attempted to solve but couldn't complete (Actions taken: 23)"
}
```

**Errors**

| Status Code | Description |
|-------------|-------------|
| 404 | Game not found |
| 400 | Game already completed |

**cURL Examples**
```bash
# Use default greedy strategy
curl -X POST "http://localhost:8000/api/games/abc123/autoplay"

# Use optimal strategy (faster, fewer actions)
curl -X POST "http://localhost:8000/api/games/abc123/autoplay?strategy=optimal"

# Use ML strategy (adaptive, learns from patterns)
curl -X POST "http://localhost:8000/api/games/abc123/autoplay?strategy=ml"
```

**AI Strategy Comparison**:

| Strategy | Success Rate | Actions | Algorithm | Best For |
|----------|-------------|---------|-----------|----------|
| `greedy` | 75% | Baseline | BFS pathfinding | Guaranteed completion |
| `optimal` | 62% | -25% | A* + Planning | Speed & efficiency |
| `ml` | TBD | Variable | Heuristic (ML-ready) | Adaptive behavior |

**Common AI Strategy**:
1. **Collect flowers**: Navigate to nearest flower, pick it up
2. **Deliver flowers**: When full or no more flowers, navigate to princess and deliver
3. **Clean obstacles**: If path blocked, clean obstacles strategically
4. **Drop-clean-repick**: If stuck with flowers, drop them, clean obstacles, pick up again
5. **Navigate adjacent**: Move adjacent to princess/flower (not onto them)

**Performance**: The AI typically solves games in 50-200 actions depending on board size, complexity, and strategy chosen.

---

## Request/Response Schemas

### CreateGameRequest

```json
{
  "rows": 10,          // integer, 3-50, required
  "cols": 10,          // integer, 3-50, required
  "name": "My Game"    // string, optional
}
```

### ActionRequest

```json
{
  "action": "move",      // enum: rotate|move|pickFlower|dropFlower|giveFlower|clean
  "direction": "east"    // enum: north|south|east|west
}
```

### GameStateResponse

```json
{
  "id": "string",
  "status": "in_progress|won|lost",
  "message": "string",
  "board": {
    "rows": 10,
    "cols": 10,
    "grid": [ /* 2D array of emoji strings */ ]
  },
  "robot": {
    "position": { "row": 0, "col": 0 },
    "orientation": "north|south|east|west",
    "flowers": {
      "collected": [ { "position": { "row": 0, "col": 0 } } ],
      "delivered": [ { "position": { "row": 0, "col": 0 } } ],
      "collection_capacity": 12
    },
    "obstacles": {
      "cleaned": [ { "position": { "row": 0, "col": 0 } } ]
    },
    "executed_actions": [
      { "type": "move", "direction": "east" }
    ]
  },
  "princess": {
    "position": { "row": 9, "col": 9 },
    "flowers_received": 0,
    "mood": "neutral|happy"
  },
  "obstacles": {
    "remaining": 30,
    "total": 30
  },
  "flowers": {
    "remaining": 10,
    "total": 10
  },
  "created_at": "2025-10-24T12:00:00Z",
  "updated_at": "2025-10-24T12:00:00Z"
}
```

### ActionResponse

Same as GameStateResponse, with additional field:
```json
{
  "success": true,  // boolean indicating if action succeeded
  // ... all GameStateResponse fields
}
```

### GameHistoryResponse

```json
{
  "id": "string",
  "history": {
    "game_id": "string",
    "actions": [
      {
        "action_type": "move",
        "direction": "east",
        "success": true,
        "message": "Robot moved east",
        "timestamp": "2025-10-24T12:00:00Z"
      }
    ],
    "created_at": "2025-10-24T12:00:00Z",
    "updated_at": "2025-10-24T12:00:00Z",
    "actions_count": 10
  }
}
```

### GamesResponse

```json
{
  "gamess": [  // Note: typo in field name (legacy)
    {
      "id": "string",
      "board": { /* board data */ },
      "robot": { /* robot data */ },
      "princess": { /* princess data */ },
      "obstacles": { "remaining": 30, "total": 30 },
      "flowers": { "remaining": 10, "total": 10 },
      "status": "in_progress|won|lost",
      "created_at": "2025-10-24T12:00:00Z",
      "updated_at": "2025-10-24T12:00:00Z"
    }
  ],
  "total": 1
}
```

---

## Error Handling

### Error Response Format

All errors follow this format:

```json
{
  "detail": "Error message or array of validation errors"
}
```

### HTTP Status Codes

| Code | Description | When |
|------|-------------|------|
| 200 | OK | Successful request |
| 201 | Created | Game created successfully |
| 400 | Bad Request | Invalid input (business logic) |
| 404 | Not Found | Game not found |
| 422 | Unprocessable Entity | Validation error (schema) |
| 500 | Internal Server Error | Server error |

### Validation Errors (422)

Pydantic v2 validation errors return detailed information:

```json
{
  "detail": [
    {
      "type": "literal_error",
      "loc": ["body", "direction"],
      "msg": "Input should be 'north', 'south', 'east' or 'west'",
      "input": "upwards"
    }
  ]
}
```

**Fields**:
- `type`: Error type (e.g., `literal_error`, `int_parsing`, `missing`)
- `loc`: Location of error (e.g., `["body", "direction"]`)
- `msg`: Human-readable error message
- `input`: The invalid input value

### Business Logic Errors (400)

```json
{
  "detail": "Target cell is blocked by obstacle"
}
```

### Common Error Messages

| Message | Cause |
|---------|-------|
| `"Game not found"` | Invalid game_id |
| `"Invalid board size"` | rows or cols out of range (3-50) |
| `"Target cell is blocked by obstacle"` | Move action blocked |
| `"No flower at target position"` | Pick action with no flower |
| `"Robot cannot pick more flowers"` | Robot at max capacity (12) |
| `"Princess is not adjacent to robot"` | Give action too far from princess |
| `"Robot has no flowers to give"` | Give action with empty hands |
| `"Cannot clean while holding flowers"` | Clean action while holding flowers |

---

## Rate Limiting

**Current Status**: No rate limiting implemented.

**Recommendation for Production**:
- Implement rate limiting per IP or API key
- Suggested limits: 100 requests/minute per client
- Use middleware like `slowapi` or reverse proxy (Nginx)

---

## Examples

### Complete Game Flow

```bash
# 1. Create game
GAME_ID=$(curl -s -X POST "http://localhost:8000/api/games" \
  -H "Content-Type: application/json" \
  -d '{"rows": 5, "cols": 5}' | jq -r '.id')

echo "Game created: $GAME_ID"

# 2. Get game state
curl -s "http://localhost:8000/api/games/$GAME_ID" | jq '.robot.position'

# 3. Rotate robot to face east
curl -s -X POST "http://localhost:8000/api/games/$GAME_ID/action" \
  -H "Content-Type: application/json" \
  -d '{"action": "rotate", "direction": "east"}' | jq '.success'

# 4. Move robot
curl -s -X POST "http://localhost:8000/api/games/$GAME_ID/action" \
  -H "Content-Type: application/json" \
  -d '{"action": "move", "direction": "east"}' | jq '.success'

# 5. Pick flower (if adjacent)
curl -s -X POST "http://localhost:8000/api/games/$GAME_ID/action" \
  -H "Content-Type: application/json" \
  -d '{"action": "pickFlower", "direction": "east"}' | jq '.success'

# 6. Get game history
curl -s "http://localhost:8000/api/games/$GAME_ID/history" | jq '.history.actions_count'

# 7. Let AI solve the rest
curl -s -X POST "http://localhost:8000/api/games/$GAME_ID/autoplay" | jq '.status'
```

### Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Create game
response = requests.post(f"{BASE_URL}/api/games", json={"rows": 10, "cols": 10})
game_id = response.json()["id"]
print(f"Game created: {game_id}")

# Perform action
action_response = requests.post(
    f"{BASE_URL}/api/games/{game_id}/action",
    json={"action": "move", "direction": "east"}
)
print(f"Action success: {action_response.json()['success']}")

# Get game state
state_response = requests.get(f"{BASE_URL}/api/games/{game_id}")
robot_pos = state_response.json()["robot"]["position"]
print(f"Robot at: ({robot_pos['row']}, {robot_pos['col']})")

# Autoplay
autoplay_response = requests.post(f"{BASE_URL}/api/games/{game_id}/autoplay")
print(f"Autoplay result: {autoplay_response.json()['message']}")

# Get history
history_response = requests.get(f"{BASE_URL}/api/games/{game_id}/history")
actions_count = history_response.json()["history"]["actions_count"]
print(f"Total actions: {actions_count}")
```

### JavaScript (Fetch) Example

```javascript
const BASE_URL = 'http://localhost:8000';

// Create game
async function createGame() {
  const response = await fetch(`${BASE_URL}/api/games`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ rows: 10, cols: 10 })
  });
  const data = await response.json();
  return data.id;
}

// Perform action
async function performAction(gameId, action, direction) {
  const response = await fetch(`${BASE_URL}/api/games/${gameId}/action`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action, direction })
  });
  return await response.json();
}

// Get game state
async function getGameState(gameId) {
  const response = await fetch(`${BASE_URL}/api/games/${gameId}`);
  return await response.json();
}

// Autoplay
async function autoplay(gameId) {
  const response = await fetch(`${BASE_URL}/api/games/${gameId}/autoplay`, {
    method: 'POST'
  });
  return await response.json();
}

// Example usage
(async () => {
  const gameId = await createGame();
  console.log(`Game created: ${gameId}`);

  const moveResult = await performAction(gameId, 'move', 'east');
  console.log(`Move success: ${moveResult.success}`);

  const state = await getGameState(gameId);
  console.log(`Robot at: (${state.robot.position.row}, ${state.robot.position.col})`);

  const autoplayResult = await autoplay(gameId);
  console.log(`Autoplay: ${autoplayResult.message}`);
})();
```

---

## Versioning

**Current Version**: v1 (implicit)

**Future Versioning Strategy**:
- API versioning in URL path: `/api/v1/games`, `/api/v2/games`
- Maintain backward compatibility
- Deprecation notices in headers

---

## CORS Configuration

**Current Configuration**: Allow all origins (development mode)

```python
allow_origins=["*"]
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```

**Production Recommendation**:
- Restrict `allow_origins` to specific domains
- Use environment variables for configuration
- Consider API gateway for advanced CORS handling

---

## OpenAPI Schema

The API automatically generates an OpenAPI 3.0 schema available at:

- **JSON**: http://localhost:8000/openapi.json
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You can use the OpenAPI schema to:
- Generate client libraries
- Import into Postman/Insomnia
- Generate documentation
- Validate requests/responses

---

## Best Practices

### Client Implementation

1. **Error Handling**: Always check `success` field in action responses
2. **Validation**: Validate inputs before sending to API
3. **Retries**: Implement exponential backoff for retries
4. **Timeouts**: Set reasonable request timeouts (e.g., 30 seconds)
5. **Caching**: Cache game state to reduce API calls

### Performance

1. **Batch Operations**: Use autoplay for AI-driven completion
2. **Polling**: Don't poll too frequently (recommend 1-2 seconds minimum)
3. **Connection Pooling**: Reuse HTTP connections

### Security

1. **Input Validation**: Never trust client input
2. **HTTPS**: Always use HTTPS in production
3. **Authentication**: Implement API keys or OAuth
4. **Rate Limiting**: Prevent abuse with rate limits

---

## Changelog

### v1.0.0 (2025-10-24)
- Initial release
- Unified action endpoint
- AI autoplay feature
- Game history tracking
- Pydantic v2 validation

---

## Support

For issues, feature requests, or questions:
- **GitHub Issues**: https://github.com/yourusername/robot-flower-princess/issues
- **Documentation**: https://your-docs-site.com
- **Email**: support@your-domain.com

---

## Related Documentation

- [Architecture](ARCHITECTURE.md) - System architecture and design
- [Testing Strategy](TESTING_STRATEGY.md) - How to test the API
- [Deployment](DEPLOYMENT.md) - How to deploy the API
- [CI/CD](CI_CD.md) - Continuous integration and deployment
