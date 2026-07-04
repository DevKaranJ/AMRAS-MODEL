from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAgent(ABC):
    """Base interface for all AI Agents in AMRAS."""

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the agent."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the agent does."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Version of the agent."""
        pass

    @abstractmethod
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's main logic.

        Args:
            payload: Input data for the agent.

        Returns:
            Dict containing the execution results.
        """
        pass

    @abstractmethod
    async def validate(self, payload: Dict[str, Any]) -> bool:
        """
        Validate the input payload before execution.

        Args:
            payload: Input data to validate.

        Returns:
            True if valid, False otherwise (or raise an exception).
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the agent and its dependencies are healthy and ready to process.

        Returns:
            True if healthy, False otherwise.
        """
        pass

    @abstractmethod
    async def rollback(self, context_id: str) -> bool:
        """
        Rollback any partial state changes if execution failed.

        Args:
            context_id: Identifier for the execution context to rollback.

        Returns:
            True if rollback successful, False otherwise.
        """
        pass
