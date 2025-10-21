from dataclasses import dataclass
from typing import Literal
from .position import Position


@dataclass
class Princess:
    position: Position
    flowers_received: int = 0
    mood: Literal["happy", "sad", "angry", "neutral"] = "neutral"

    def receive_flowers(self, count: int) -> None:
        """Receive flowers from the robot and update mood accordingly."""
        self.flowers_received += count
        self._update_mood()

    def _update_mood(self) -> None:
        """Update mood based on flowers received."""
        if self.flowers_received == 0:
            self.mood = "sad"
        elif self.flowers_received < 3:
            self.mood = "neutral"
        elif self.flowers_received < 6:
            self.mood = "happy"
        else:
            self.mood = "happy"  # Very happy with many flowers
