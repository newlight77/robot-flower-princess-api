"""Port for communicating with the ML Player service."""

from abc import ABC, abstractmethod
from typing import Dict, List


class MLPlayerClientPort(ABC):
    """
    Port for interacting with the ML Player service.

    This allows external services to request predictions and strategy information
    from the ML Player service.
    """

    @abstractmethod
    async def predict_action(
        self,
        game_id: str,
        strategy: str,
        game_state: Dict
    ) -> Dict:
        """
        Request an action prediction from the ML Player.

        Args:
            game_id: Game identifier
            strategy: Strategy to use ("default", "aggressive", "conservative")
            game_state: Current game state including board, robot, princess, etc.

        Returns:
            Dictionary containing predicted action, direction, confidence, etc.
        """
        pass

    @abstractmethod
    async def get_strategies(self) -> List[Dict]:
        """
        Get list of available strategies.

        Returns:
            List of strategy configurations
        """
        pass

    @abstractmethod
    async def get_strategy(self, strategy_name: str) -> Dict:
        """
        Get configuration for a specific strategy.

        Args:
            strategy_name: Name of the strategy

        Returns:
            Strategy configuration dictionary
        """
        pass
