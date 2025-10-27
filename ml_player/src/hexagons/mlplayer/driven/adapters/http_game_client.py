"""HTTP client adapter for communicating with game service."""

import httpx

from hexagons.mlplayer.domain.ports.game_client import GameClientPort


class HttpGameClient(GameClientPort):
    """
    HTTP client implementation for fetching game state from the game service.
    """

    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize HTTP client.

        Args:
            base_url: Base URL of the game service
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def get_game_state(self, game_id: str) -> dict:
        """
        Fetch current game state from the game service.

        Args:
            game_id: Game identifier

        Returns:
            Dictionary containing game state

        Raises:
            httpx.HTTPError: If request fails
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/api/games/{game_id}")
            response.raise_for_status()
            return response.json()

    async def execute_action(self, game_id: str, action: str, direction: str = None) -> dict:
        """
        Execute an action in the game.

        Args:
            game_id: Game identifier
            action: Action type (move, pick, drop, give, clean, rotate)
            direction: Direction for the action (if applicable)

        Returns:
            Result of the action

        Raises:
            httpx.HTTPError: If request fails
        """
        payload = {"action": action}
        if direction:
            payload["direction"] = direction

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.base_url}/api/games/{game_id}/action", json=payload)
            response.raise_for_status()
            return response.json()
