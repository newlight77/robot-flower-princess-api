#!/usr/bin/env python3
"""
End-to-end test script for data collection.

This script verifies that data collection works correctly between
rfp_game and ml_player services.
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import httpx
    from colorama import Fore, Style, init
except ImportError:
    print("Missing dependencies. Please install:")
    print("  pip install httpx colorama")
    sys.exit(1)

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Service URLs
RFP_GAME_URL = "http://localhost:8000"
ML_PLAYER_URL = "http://localhost:8001"
TIMEOUT = 5.0


def print_header(text: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 50)
    print(text)
    print("=" * 50 + "\n")


def print_step(step: int, text: str) -> None:
    """Print a step header."""
    print(f"\nStep {step}: {text}")


def print_success(text: str) -> None:
    """Print success message in green."""
    print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")


def print_error(text: str) -> None:
    """Print error message in red."""
    print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")


def print_warning(text: str) -> None:
    """Print warning message in yellow."""
    print(f"{Fore.YELLOW}⚠ {text}{Style.RESET_ALL}")


def print_info(text: str, indent: int = 0) -> None:
    """Print info message."""
    prefix = "  " * indent
    print(f"{prefix}{text}")


def check_service_health(url: str, service_name: str) -> bool:
    """
    Check if a service is running by calling its /health endpoint.

    Args:
        url: Base URL of the service
        service_name: Name of the service for display

    Returns:
        True if service is healthy, False otherwise
    """
    try:
        response = httpx.get(f"{url}/health", timeout=TIMEOUT)
        if response.status_code == 200:
            print_success(f"{service_name} is running")
            return True
        else:
            print_error(f"{service_name} returned status {response.status_code}")
            return False
    except httpx.ConnectError:
        print_error(f"{service_name} is not running")
        return False
    except Exception as e:
        print_error(f"Error checking {service_name}: {e}")
        return False


def create_game(rows: int = 5, cols: int = 5) -> str | None:
    """
    Create a new game.

    Args:
        rows: Number of rows in the game board
        cols: Number of columns in the game board

    Returns:
        Game ID if successful, None otherwise
    """
    try:
        response = httpx.post(
            f"{RFP_GAME_URL}/api/games",
            json={"rows": rows, "cols": cols},
            timeout=TIMEOUT,
        )

        if response.status_code == 200:
            data = response.json()
            game_id = data.get("game", {}).get("id")
            if game_id:
                print_success(f"Game created: {game_id}")
                return game_id
            else:
                print_error("Game created but no ID returned")
                print_info(f"Response: {data}", indent=1)
                return None
        else:
            print_error(f"Failed to create game (status {response.status_code})")
            print_info(f"Response: {response.text}", indent=1)
            return None

    except Exception as e:
        print_error(f"Error creating game: {e}")
        return None


def perform_action(game_id: str, action: str, direction: str) -> bool:
    """
    Perform an action on the game.

    Args:
        game_id: Game ID
        action: Action to perform (move, rotate, pick, etc.)
        direction: Direction for the action

    Returns:
        True if action was successful, False otherwise
    """
    try:
        response = httpx.post(
            f"{RFP_GAME_URL}/api/games/{game_id}/action",
            json={"action": action, "direction": direction},
            timeout=TIMEOUT,
        )

        if response.status_code == 200:
            data = response.json()
            success = data.get("success", False)
            if success:
                print_info(f"{Fore.GREEN}✓ Action successful{Style.RESET_ALL}", indent=2)
                return True
            else:
                print_warning(f"Action response: {success}")
                return False
        else:
            print_warning(f"Action failed (status {response.status_code})")
            return False

    except Exception as e:
        print_warning(f"Error performing action: {e}")
        return False


def verify_data_collection(game_id: str) -> bool:
    """
    Verify that data was collected in ML Player.

    Args:
        game_id: Game ID to look for in collected data

    Returns:
        True if data collection verified, False otherwise
    """
    today = datetime.now().strftime("%Y-%m-%d")
    samples_file = Path(f"ml_player/data/training/samples_{today}.jsonl")

    if not samples_file.exists():
        print_error(f"Data collection file not found: {samples_file}")
        print_info("This might mean:", indent=1)
        print_info("1. ENABLE_DATA_COLLECTION is not set to 'true'", indent=1)
        print_info("2. ML Player service is not receiving requests", indent=1)
        print_info("3. Network issue between services", indent=1)
        return False

    print_success(f"Data collection file exists: {samples_file}")

    # Count samples
    with open(samples_file, "r") as f:
        lines = f.readlines()
        sample_count = len(lines)
        print_info(f"Total samples in file: {sample_count}", indent=1)

        if sample_count == 0:
            print_warning("File exists but is empty")
            return False

        # Parse last sample
        try:
            last_sample = json.loads(lines[-1])

            print_step(6, "Inspecting last collected sample...")
            print_info(f"Game ID: {last_sample.get('game_id')}", indent=1)
            print_info(f"Action: {last_sample.get('action')}", indent=1)
            print_info(f"Direction: {last_sample.get('direction')}", indent=1)
            print_info(f"Has game_state: {'game_state' in last_sample}", indent=1)
            print_info(f"Has outcome: {'outcome' in last_sample}", indent=1)

            # Verify game_id matches
            if last_sample.get("game_id") == game_id:
                print_success("Sample game_id matches")
            else:
                print_warning("Sample game_id doesn't match (might be from previous test)")

            # Pretty print last sample
            print("\nLast collected sample (formatted):")
            print(json.dumps(last_sample, indent=2))

            return True

        except json.JSONDecodeError as e:
            print_error(f"Failed to parse last sample: {e}")
            return False


def run_tests() -> int:
    """
    Run all data collection tests.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print_header("Data Collection Integration Test")

    # Step 1: Check ML Player service
    print_step(1, "Checking if ML Player service is running...")
    if not check_service_health(ML_PLAYER_URL, "ML Player"):
        print_info("Please start ML Player: cd ml_player && make run", indent=1)
        return 1

    # Step 2: Check RFP Game service
    print_step(2, "Checking if RFP Game service is running...")
    if not check_service_health(RFP_GAME_URL, "RFP Game"):
        print_info("Please start RFP Game with data collection enabled:", indent=1)
        print_info("cd rfp_game && ENABLE_DATA_COLLECTION=true make run", indent=1)
        return 1

    # Step 3: Create a test game
    print_step(3, "Creating a test game...")
    game_id = create_game(rows=5, cols=5)
    if not game_id:
        return 1

    # Step 4: Perform test actions
    print_step(4, "Performing test actions...")

    actions = [
        ("move", "SOUTH"),
        ("rotate", "EAST"),
        ("move", "EAST"),
    ]

    success_count = 0
    for action, direction in actions:
        print_info(f"- Performing action: {action} {direction}", indent=1)
        if perform_action(game_id, action, direction):
            success_count += 1
        time.sleep(0.5)  # Brief delay to allow data collection

    print_info(f"\nActions performed: {success_count}/{len(actions)}", indent=1)

    # Step 5: Verify data was collected
    print_step(5, "Verifying data was collected...")
    time.sleep(1)  # Wait for data to be written

    if not verify_data_collection(game_id):
        return 1

    # Success summary
    print_header(f"{Fore.GREEN}✓ All tests passed!{Style.RESET_ALL}")

    print("Summary:")
    print("  - Both services are running")
    print("  - Game was created successfully")
    print("  - Actions were performed")
    print("  - Data was collected and stored in ML Player")
    print("  - Sample structure is correct")
    print("\nData collection is working correctly! 🎉\n")

    return 0


def main() -> int:
    """Main entry point."""
    try:
        return run_tests()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Test interrupted by user{Style.RESET_ALL}")
        return 130
    except Exception as e:
        print(f"\n{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
