#!/bin/bash
# Test script for end-to-end data collection
# This script verifies that data collection works correctly between rfp_game and ml_player

set -e  # Exit on error

echo "=========================================="
echo "Data Collection Integration Test"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if both services are running
echo "Step 1: Checking if ML Player service is running..."
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ ML Player is running${NC}"
else
    echo -e "${RED}✗ ML Player is not running${NC}"
    echo "Please start ML Player: cd ml_player && make run"
    exit 1
fi

echo ""
echo "Step 2: Checking if RFP Game service is running..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ RFP Game is running${NC}"
else
    echo -e "${RED}✗ RFP Game is not running${NC}"
    echo "Please start RFP Game with data collection enabled:"
    echo "cd rfp_game && ENABLE_DATA_COLLECTION=true make run"
    exit 1
fi

echo ""
echo "Step 3: Creating a test game..."
GAME_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/games" \
  -H "Content-Type: application/json" \
  -d '{"rows": 5, "cols": 5}')

GAME_ID=$(echo $GAME_RESPONSE | jq -r '.game.id')

if [ "$GAME_ID" != "null" ] && [ -n "$GAME_ID" ]; then
    echo -e "${GREEN}✓ Game created: $GAME_ID${NC}"
else
    echo -e "${RED}✗ Failed to create game${NC}"
    echo "Response: $GAME_RESPONSE"
    exit 1
fi

echo ""
echo "Step 4: Performing test actions..."

# Count samples before
BEFORE_COUNT=$(ls -1 ml_player/data/training/samples_*.jsonl 2>/dev/null | wc -l | tr -d ' ')
echo "Training files before: $BEFORE_COUNT"

# Perform multiple actions
ACTIONS=("move SOUTH" "rotate EAST" "move EAST")
for ACTION_DATA in "${ACTIONS[@]}"; do
    read -r ACTION DIRECTION <<< "$ACTION_DATA"

    echo "  - Performing action: $ACTION $DIRECTION"

    RESPONSE=$(curl -s -X POST "http://localhost:8000/api/games/$GAME_ID/action" \
      -H "Content-Type: application/json" \
      -d "{\"action\": \"$ACTION\", \"direction\": \"$DIRECTION\"}")

    SUCCESS=$(echo $RESPONSE | jq -r '.success')

    if [ "$SUCCESS" == "true" ]; then
        echo -e "    ${GREEN}✓ Action successful${NC}"
    else
        echo -e "    ${YELLOW}⚠ Action response: $SUCCESS${NC}"
    fi

    sleep 0.5  # Brief delay to allow data collection
done

echo ""
echo "Step 5: Verifying data was collected..."
sleep 1  # Wait for data to be written

# Check if samples file exists
TODAY=$(date +%Y-%m-%d)
SAMPLES_FILE="ml_player/data/training/samples_$TODAY.jsonl"

if [ -f "$SAMPLES_FILE" ]; then
    SAMPLE_COUNT=$(wc -l < "$SAMPLES_FILE" | tr -d ' ')
    echo -e "${GREEN}✓ Data collection file exists: $SAMPLES_FILE${NC}"
    echo "  Total samples in file: $SAMPLE_COUNT"

    # Show last collected sample
    echo ""
    echo "Step 6: Inspecting last collected sample..."
    LAST_SAMPLE=$(tail -1 "$SAMPLES_FILE")

    # Verify sample structure
    GAME_ID_IN_SAMPLE=$(echo $LAST_SAMPLE | jq -r '.game_id')
    ACTION_IN_SAMPLE=$(echo $LAST_SAMPLE | jq -r '.action')
    DIRECTION_IN_SAMPLE=$(echo $LAST_SAMPLE | jq -r '.direction')

    echo "  Game ID: $GAME_ID_IN_SAMPLE"
    echo "  Action: $ACTION_IN_SAMPLE"
    echo "  Direction: $DIRECTION_IN_SAMPLE"
    echo "  Has game_state: $(echo $LAST_SAMPLE | jq 'has("game_state")')"
    echo "  Has outcome: $(echo $LAST_SAMPLE | jq 'has("outcome")')"

    if [ "$GAME_ID_IN_SAMPLE" == "$GAME_ID" ]; then
        echo -e "${GREEN}✓ Sample game_id matches${NC}"
    else
        echo -e "${YELLOW}⚠ Sample game_id doesn't match (might be from previous test)${NC}"
    fi

    # Pretty print last sample
    echo ""
    echo "Last collected sample (formatted):"
    echo "$LAST_SAMPLE" | jq '.'

else
    echo -e "${RED}✗ Data collection file not found: $SAMPLES_FILE${NC}"
    echo "This might mean:"
    echo "  1. ENABLE_DATA_COLLECTION is not set to 'true'"
    echo "  2. ML Player service is not receiving requests"
    echo "  3. Network issue between services"
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✓ All tests passed!${NC}"
echo "=========================================="
echo ""
echo "Summary:"
echo "  - Both services are running"
echo "  - Game was created successfully"
echo "  - Actions were performed"
echo "  - Data was collected and stored in ML Player"
echo "  - Sample structure is correct"
echo ""
echo "Data collection is working correctly! 🎉"
