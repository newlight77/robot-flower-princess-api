"""HTTP client adapter for communicating with ML Player service."""

import httpx

from hexagons.mlplayer.domain.ports.ml_player_client import MLPlayerClientPort


class HttpMLPlayerClient(MLPlayerClientPort):
    """
    HTTP client implementation for interacting with the ML Player service.

    This adapter allows external services (e.g., rfp_game) to request predictions
    and strategy information from the ML Player service.
    """

    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize HTTP client.

        Args:
            base_url: Base URL of the ML Player service (e.g., http://localhost:8001)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def predict_action(self, game_id: str, strategy: str, game_state: dict) -> dict:
        """
        Request an action prediction from the ML Player.

        Args:
            game_id: Game identifier
            strategy: Strategy to use ("default", "aggressive", "conservative")
            game_state: Current game state including:
                - status: Game status
                - board: Board configuration (rows, cols)
                - robot: Robot state (position, orientation, flowers)
                - princess: Princess state (position, flowers)
                - obstacles: Obstacle positions
                - flowers: Flower positions

        Returns:
            Dictionary containing:
                - game_id: Game identifier
                - action: Predicted action (move, pick, drop, give, clean, rotate)
                - direction: Direction for the action (if applicable)
                - confidence: Confidence score (0.0 to 1.0)
                - board_score: Heuristic evaluation score
                - config_used: Strategy configuration used

        Raises:
            httpx.HTTPError: If request fails
        """
        payload = {
            "strategy": strategy,
            "game_id": game_id,
            "status": game_state.get("status", "In Progress"),
            "board": game_state["board"],
            "robot": game_state["robot"],
            "princess": game_state["princess"],
            "obstacles": game_state.get("obstacles", {"positions": []}),
            "flowers": game_state.get("flowers", {"positions": []}),
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.base_url}/api/ml-player/predict/{game_id}", json=payload)
            response.raise_for_status()
            return response.json()

    async def get_strategies(self) -> list[dict]:
        """
        Get list of available strategies.

        Returns:
            List of dictionaries containing:
                - strategy_name: Name of the strategy
                - config: Strategy configuration (weights, parameters)

        Raises:
            httpx.HTTPError: If request fails
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/api/ml-player/strategies")
            response.raise_for_status()
            return response.json()

    async def get_strategy(self, strategy_name: str) -> dict:
        """
        Get configuration for a specific strategy.

        Args:
            strategy_name: Name of the strategy ("default", "aggressive", "conservative")

        Returns:
            Dictionary containing:
                - strategy_name: Name of the strategy
                - config: Strategy configuration (weights, parameters)

        Raises:
            httpx.HTTPError: If request fails or strategy not found
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/api/ml-player/strategies/{strategy_name}")
            response.raise_for_status()
            return response.json()

    async def health_check(self) -> dict:
        """
        Check if ML Player service is healthy.

        Returns:
            Health status dictionary

        Raises:
            httpx.HTTPError: If service is unhealthy or unreachable
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
