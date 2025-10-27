# Data Collection Test Script

## Overview

`test_data_collection.py` is an end-to-end test script that verifies data collection works correctly between the RFP Game and ML Player services.

**Location**: `testing/data_collection/test_data_collection.py`
**Run from root**: `python testing/data_collection/test_data_collection.py`

## Why Python Instead of Shell Script?

The original `test_data_collection.sh` has been replaced with a Python version for several reasons:

### Benefits of Python

✅ **Cross-Platform**: Works on Windows, macOS, and Linux without modification
✅ **Better Error Handling**: Structured exception handling and clearer error messages
✅ **No External Dependencies**: Doesn't require `curl`, `jq`, or other system tools
✅ **More Readable**: Cleaner syntax and better structure with functions
✅ **Type Hints**: Better IDE support and code clarity
✅ **Easier to Maintain**: Python code is easier to extend and modify
✅ **Colored Output**: Cross-platform colored terminal output with `colorama`
✅ **Native JSON**: Built-in JSON parsing without external tools
✅ **Better HTTP Client**: Uses `httpx` with proper timeout and error handling
✅ **Consistent**: Matches the rest of the codebase (Python-based)

### Limitations of Shell Script

❌ **Platform-Specific**: Bash syntax differs on Windows (requires Git Bash/WSL)
❌ **External Dependencies**: Requires `curl`, `jq`, `wc`, etc.
❌ **Error Handling**: Shell error handling is verbose and error-prone
❌ **Less Readable**: Shell syntax can be confusing for complex logic
❌ **JSON Parsing**: Requires `jq` which may not be installed

## Installation

### Prerequisites

```bash
pip install httpx colorama
```

Or if you're using the project's Poetry environment:

```bash
cd rfp_game  # or ml_player
poetry add --group dev httpx colorama
```

### Quick Install

```bash
pip install httpx colorama
```

## Usage

### Basic Usage

From the project root:
```bash
python testing/data_collection/test_data_collection.py
```

Or from the testing directory:
```bash
cd testing
python test_data_collection.py
```

### Make it Executable (Unix/macOS)

```bash
chmod +x testing/data_collection/test_data_collection.py
./testing/data_collection/test_data_collection.py
```

### What It Tests

The script performs the following verifications:

1. ✅ **Service Health Checks**
   - Checks if ML Player is running on port 8001
   - Checks if RFP Game is running on port 8000

2. ✅ **Game Creation**
   - Creates a new 5x5 game via API
   - Verifies game ID is returned

3. ✅ **Action Execution**
   - Performs multiple actions (move, rotate)
   - Verifies actions succeed

4. ✅ **Data Collection**
   - Waits for data to be written
   - Checks that JSONL file exists in ML Player
   - Verifies sample count increases
   - Inspects sample structure (game_id, action, direction, game_state, outcome)
   - Pretty-prints last collected sample

### Expected Output

```
==================================================
Data Collection Integration Test
==================================================


Step 1: Checking if ML Player service is running...
✓ ML Player is running

Step 2: Checking if RFP Game service is running...
✓ RFP Game is running

Step 3: Creating a test game...
✓ Game created: abc123-def456-789

Step 4: Performing test actions...
  - Performing action: move SOUTH
    ✓ Action successful
  - Performing action: rotate EAST
    ✓ Action successful
  - Performing action: move EAST
    ✓ Action successful

Actions performed: 3/3

Step 5: Verifying data was collected...
✓ Data collection file exists: ml_player/data/training/samples_2025-10-27.jsonl
  Total samples in file: 42

Step 6: Inspecting last collected sample...
  Game ID: abc123-def456-789
  Action: move
  Direction: EAST
  Has game_state: True
  Has outcome: True
✓ Sample game_id matches

Last collected sample (formatted):
{
  "timestamp": "2025-10-27T03:00:00.000000",
  "game_id": "abc123-def456-789",
  "game_state": {...},
  "action": "move",
  "direction": "EAST",
  "outcome": {"success": true, "message": "action performed successfully"}
}

==================================================
✓ All tests passed!
==================================================

Summary:
  - Both services are running
  - Game was created successfully
  - Actions were performed
  - Data was collected and stored in ML Player
  - Sample structure is correct

Data collection is working correctly! 🎉
```

## Troubleshooting

### Services Not Running

If you see:
```
✗ ML Player is not running
```

**Solution**: Start the services:
```bash
# Terminal 1: ML Player
cd ml_player
make run

# Terminal 2: RFP Game
cd rfp_game
ENABLE_DATA_COLLECTION=true make run
```

### Data Collection Not Enabled

If data file is not found:
```
✗ Data collection file not found: ml_player/data/training/samples_2025-10-27.jsonl
```

**Solution**: Make sure `ENABLE_DATA_COLLECTION=true` is set when starting RFP Game:
```bash
cd rfp_game
ENABLE_DATA_COLLECTION=true make run
```

### Missing Dependencies

If you see:
```
Missing dependencies. Please install:
  pip install httpx colorama
```

**Solution**:
```bash
pip install httpx colorama
```

### Connection Refused

If you see connection errors:
```
Error checking ML Player: [Errno 61] Connection refused
```

**Solution**:
- Verify services are running on the correct ports (8000, 8001)
- Check for firewall blocking localhost connections
- Ensure no other services are using those ports

## Code Structure

The script is organized into clear functions:

```python
# Service health checks
check_service_health(url, service_name) -> bool

# Game operations
create_game(rows, cols) -> str | None
perform_action(game_id, action, direction) -> bool

# Data verification
verify_data_collection(game_id) -> bool

# Output formatting
print_header(text)
print_step(step, text)
print_success(text)
print_error(text)
print_warning(text)
print_info(text, indent)

# Main test runner
run_tests() -> int  # Returns exit code
```

## Integration with CI/CD

The script returns appropriate exit codes:
- `0` - All tests passed
- `1` - Tests failed
- `130` - Interrupted by user (Ctrl+C)

This makes it suitable for CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Test Data Collection
  run: |
    python testing/data_collection/test_data_collection.py
```

## Extending the Script

The script is designed to be easily extended. For example, to add more test actions:

```python
actions = [
    ("move", "SOUTH"),
    ("rotate", "EAST"),
    ("move", "EAST"),
    ("pick", "EAST"),      # Add more actions
    ("drop", "SOUTH"),
]
```

Or to test different game configurations:

```python
# Test larger board
game_id = create_game(rows=10, cols=10)
```

## Dependencies

### Runtime Dependencies

```
httpx >= 0.27.0      # HTTP client for API calls
colorama >= 0.4.6    # Cross-platform colored terminal output
```

### Standard Library

```python
json       # JSON parsing
sys        # Exit codes
time       # Delays
pathlib    # File path handling
datetime   # Timestamp formatting
typing     # Type hints
```

## Migration from Shell Script

The old `test_data_collection.sh` is kept for reference but **the Python version is recommended**:

```bash
# Shell script (still works, but deprecated)
./testing/test_data_collection.sh

# Python script (recommended)
python testing/data_collection/test_data_collection.py
```

The Python version offers better cross-platform support, clearer error messages, and easier maintenance.

## Related Documentation

- [Data Collection Guide](docs/DATA_COLLECTION.md) - Complete data collection documentation
- [ML Implementation](docs/machine_learning/ML_IMPLEMENTATION.md) - ML Player implementation
- [Testing Strategy](docs/TESTING_STRATEGY.md) - Overall testing approach

## Summary

✅ **Modern**: Python 3.12+ with type hints
✅ **Cross-Platform**: Works everywhere Python runs
✅ **No External Tools**: Pure Python solution
✅ **Better UX**: Colored output and clear messages
✅ **Maintainable**: Clean code structure
✅ **Extensible**: Easy to add more tests
✅ **CI/CD Ready**: Proper exit codes

Use `python testing/data_collection/test_data_collection.py` to verify your data collection setup! 🚀
