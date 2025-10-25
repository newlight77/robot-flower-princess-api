"""Strategy configuration value object for ML player."""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class StrategyConfig:
    """
    Configuration for ML-inspired strategy using weighted heuristics.

    These weights can be "learned" through optimization algorithms:
    - Grid search
    - Genetic algorithms
    - Simulated annealing
    - Or future: actual ML training
    """

    # Movement heuristics (negative = minimize, positive = maximize)
    distance_to_flower_weight: float = -2.5  # Prefer closer flowers
    distance_to_princess_weight: float = -1.0  # Consider princess proximity
    obstacle_density_weight: float = -3.0  # Avoid obstacle-dense areas
    path_clearance_weight: float = 2.0  # Prefer clear paths

    # Flower selection heuristics
    flower_cluster_bonus: float = 1.5  # Bonus for clustered flowers
    flower_isolation_penalty: float = -0.5  # Penalty for isolated flowers

    # Risk/reward heuristics
    risk_aversion: float = 0.7  # 0.0 = aggressive, 1.0 = conservative
    exploration_factor: float = 0.3  # Balance exploration vs exploitation

    # Planning horizon
    lookahead_depth: int = 3  # How many moves to plan ahead

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for serialization."""
        return {
            'distance_to_flower_weight': self.distance_to_flower_weight,
            'distance_to_princess_weight': self.distance_to_princess_weight,
            'obstacle_density_weight': self.obstacle_density_weight,
            'path_clearance_weight': self.path_clearance_weight,
            'flower_cluster_bonus': self.flower_cluster_bonus,
            'flower_isolation_penalty': self.flower_isolation_penalty,
            'risk_aversion': self.risk_aversion,
            'exploration_factor': self.exploration_factor,
            'lookahead_depth': self.lookahead_depth,
        }

    @classmethod
    def default(cls) -> "StrategyConfig":
        """Create default configuration."""
        return cls()

    @classmethod
    def aggressive(cls) -> "StrategyConfig":
        """Create aggressive configuration (lower risk aversion)."""
        return cls(
            risk_aversion=0.3,
            exploration_factor=0.5,
            lookahead_depth=2,
        )

    @classmethod
    def conservative(cls) -> "StrategyConfig":
        """Create conservative configuration (higher risk aversion)."""
        return cls(
            risk_aversion=0.9,
            exploration_factor=0.1,
            lookahead_depth=4,
        )
