from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class AIProviderInterface(ABC):
    """Provider-agnostic interface for AI operations."""

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> str:
        pass


class AIProviderManager:
    """Manages AI providers and routes requests."""

    def __init__(self) -> None:
        self._providers: Dict[str, Any] = {}
        self._default_provider: Optional[str] = None

    def register_provider(self, name: str, provider: AIProviderInterface, is_default: bool = False) -> None:
        self._providers[name] = provider
        if is_default or self._default_provider is None:
            self._default_provider = name

    def get_provider(self, name: Optional[str] = None) -> Any:
        provider_name = name or self._default_provider
        if not provider_name or provider_name not in self._providers:
            raise ValueError(f"Provider {provider_name} not found")
        return self._providers[provider_name]

    async def generate_text(self, *args: Any, provider_name: Optional[str] = None, **kwargs: Any) -> str:
        provider = self.get_provider(provider_name)
        res: str = await provider.generate_text(*args, **kwargs)
        return res


# Singleton instance
ai_provider_manager = AIProviderManager()


# Dummy Mock Provider for testing/development since no real providers are injected yet
class MockAIProvider(AIProviderInterface):
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> str:
        if response_format:
            import json

            # Extremely naive mock response generator based on schema
            mock_resp = {}
            for k in response_format.get("properties", {}).keys():
                mock_resp[k] = "mocked_" + k
            return json.dumps(mock_resp)
        return "This is a mock AI response to: " + prompt[:20]


ai_provider_manager.register_provider("mock", MockAIProvider(), is_default=True)
