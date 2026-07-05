from abc import ABC, abstractmethod


class BaseIngestionAgent(ABC):
    """Base class for all ingestion agents."""

    @abstractmethod
    def _is_agent(self) -> bool:
        pass
