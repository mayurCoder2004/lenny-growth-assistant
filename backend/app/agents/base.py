from abc import ABC, abstractmethod
from typing import Any


class Agent(ABC):
    """Base interface for application agents."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the agent name."""
        raise NotImplementedError

    @abstractmethod
    def execute(self, **kwargs: Any) -> dict:
        """Execute the agent."""
        raise NotImplementedError
