# Gameplay Data Collection for ML Training

This document describes the gameplay data collection feature integrated into the RFP Game API.

## Overview

The gameplay data collection system captures real gameplay actions and game states, which can be used to:
- Train and improve ML models for the AI player
- Analyze player behavior and game difficulty
- Generate real-world training data beyond synthetic samples

## Architecture

### Components

1. **GameplayDataCollector** (`src/hexagons/game/driven/adapters/gameplay_data_collector.py`)
   - Driven adapter that collects and stores gameplay data
   - Writes data in JSONL format (one JSON object per line)
   - Compatible with the ML Player's data format

2. **Integration Points**
   - `/api/games/{game_id}/action` endpoint - Collects all manual actions
   - Data collection happens transparently without affecting API responses

### Data Format

Each collected sample includes:

```json
{
  "game_id": "unique-game-id",
  "timestamp": "2025-10-27T03:00:00.000000",
  "game_state": {
    "board": {...},
    "robot": {...},
    "princess": {...},
    "flowers": {...},
    "obstacles": {...}
  },
  "action": "move|rotate|pick|drop|give|clean",
  "direction": "NORTH|SOUTH|EAST|WEST",
  "outcome": {
    "success": true,
    "message": "action performed successfully"
  }
}
```

## Configuration

### Enabling Data Collection

Data collection is **disabled by default**. To enable it, set the environment variable:

```bash
export ENABLE_DATA_COLLECTION=true
```

Or in your `.env` file:

```env
ENABLE_DATA_COLLECTION=true
```

### Data Storage Location

By default, gameplay data is stored in:
```
rfp_game/data/gameplay/
```

Files are named by date: `gameplay_YYYYMMDD.jsonl`

## Usage

### 1. Enable Data Collection

```bash
# In your shell or .env file
export ENABLE_DATA_COLLECTION=true
```

### 2. Play Games

Make API calls to the action endpoint as normal:

```bash
curl -X POST "http://localhost:8000/api/games/{game_id}/action" \
  -H "Content-Type: application/json" \
  -d '{"action": "move", "direction": "south"}'
```

Data will be collected automatically in the background.

### 3. Check Collection Statistics

You can check how much data has been collected programmatically:

```python
from hexagons.game.driven.adapters.gameplay_data_collector import GameplayDataCollector

collector = GameplayDataCollector()
stats = collector.get_statistics()
print(stats)
```

Expected output:
```python
{
    "enabled": True,
    "total_samples": 1234,
    "data_files": 3,
    "files": ["gameplay_20251027.jsonl", "gameplay_20251026.jsonl", ...],
    "data_dir": "data/gameplay"
}
```

### 4. Use Collected Data for ML Training

The collected gameplay data can be used directly with the ML Player's training pipeline:

```bash
# Copy gameplay data to ML Player's training directory
cp rfp_game/data/gameplay/*.jsonl ml_player/data/training/

# Or create a symbolic link
ln -s $(pwd)/rfp_game/data/gameplay ml_player/data/training/gameplay

# Train models with the collected data
cd ml_player
make ml-train
```

## Data Privacy & Ethics

**Important Considerations:**

1. **User Consent**: If collecting data from real users (not just testing), ensure proper consent and disclosure
2. **Data Retention**: Implement appropriate data retention policies
3. **Anonymization**: Consider anonymizing game IDs if needed
4. **GDPR Compliance**: If operating in EU, ensure compliance with data protection regulations

## Performance Impact

Data collection is designed to have minimal impact:
- **Asynchronous writes**: Data is written to disk asynchronously
- **Conditional execution**: Only runs when `ENABLE_DATA_COLLECTION=true`
- **Error handling**: Failures in data collection don't affect API responses
- **Overhead**: ~1-2ms per action (negligible)

## Testing

To test data collection:

```bash
# 1. Enable data collection
export ENABLE_DATA_COLLECTION=true

# 2. Start the API server
cd rfp_game
make run

# 3. Play a game (in another terminal)
# Create game
GAME_ID=$(curl -X POST "http://localhost:8000/api/games" \
  -H "Content-Type: application/json" \
  -d '{"rows": 5, "cols": 5}' | jq -r '.game.id')

# Perform actions
curl -X POST "http://localhost:8000/api/games/$GAME_ID/action" \
  -H "Content-Type: application/json" \
  -d '{"action": "move", "direction": "south"}'

# 4. Check collected data
ls -lh data/gameplay/
cat data/gameplay/gameplay_$(date +%Y%m%d).jsonl | wc -l
```

## Future Enhancements

Potential improvements to consider:

1. **Batch Upload**: Periodically upload collected data to ML Player service
2. **Data Quality Filtering**: Filter out incomplete or invalid games
3. **Sampling Strategy**: Collect only a percentage of actions to reduce storage
4. **Compression**: Compress older data files automatically
5. **Dashboard**: Create a simple dashboard to monitor collection statistics
6. **A/B Testing**: Collect data with strategy labels to compare AI strategies

## Troubleshooting

### Data Not Being Collected

1. Check environment variable:
   ```bash
   echo $ENABLE_DATA_COLLECTION
   ```
2. Check logs for initialization:
   ```
   GameplayDataCollector initialized: enabled=true, data_dir=data/gameplay
   ```
3. Verify directory permissions:
   ```bash
   ls -ld data/gameplay
   ```

### File Permission Errors

Ensure the application has write permissions:
```bash
chmod 755 data
chmod 755 data/gameplay
```

### Large File Sizes

Data files can grow quickly. Monitor disk usage:
```bash
du -sh data/gameplay/
```

Consider implementing rotation or compression for production use.

## Related Documentation

- [ML Guide](../../ml_player/ML_GUIDE.md) - ML Player training documentation
- [Architecture](../docs/ARCHITECTURE.md) - Overall system architecture
- [API Contract](../docs/API_CONTRACT.md) - API endpoint documentation
