import asyncio
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

    @abstractmethod
    async def generate_speech(
        self,
        text: str,
        voice_id: str,
        model: Optional[str] = None,
        speed: float = 1.0,
    ) -> bytes:
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
        try:
            res: str = await asyncio.wait_for(provider.generate_text(*args, **kwargs), timeout=30.0)
        except asyncio.TimeoutError as err:
            raise TimeoutError(f"Provider {provider_name} timed out after 30 seconds") from err
        return res

    async def generate_speech(self, *args: Any, provider_name: Optional[str] = None, **kwargs: Any) -> bytes:
        provider = self.get_provider(provider_name)
        try:
            res: bytes = await asyncio.wait_for(provider.generate_speech(*args, **kwargs), timeout=300.0)
        except asyncio.TimeoutError as err:
            raise TimeoutError(f"Provider {provider_name} timed out after 300 seconds") from err
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

            # Mock response generator based on schema types
            mock_resp = {}
            for k, v in response_format.get("properties", {}).items():
                prop_type = v.get("type", "string")
                if prop_type == "array":
                    # Generate a mock array with one item matching the items schema
                    items_schema = v.get("items", {})
                    if items_schema.get("type") == "object":
                        # Create a mock object based on items properties
                        mock_item = {}
                        for item_k, item_v in items_schema.get("properties", {}).items():
                            item_type = item_v.get("type", "string")
                            if item_type == "integer":
                                mock_item[item_k] = 1
                            elif item_type == "number":
                                mock_item[item_k] = 1.0
                            elif item_type == "boolean":
                                mock_item[item_k] = True
                            else:
                                mock_item[item_k] = f"mocked_{item_k}"
                        mock_resp[k] = [mock_item]
                    else:
                        mock_resp[k] = ["mocked_item"]
                elif prop_type == "object":
                    mock_resp[k] = {}
                elif prop_type == "integer":
                    mock_resp[k] = 1
                elif prop_type == "number":
                    mock_resp[k] = 1.0
                elif prop_type == "boolean":
                    mock_resp[k] = True
                else:
                    mock_resp[k] = "mocked_" + k
            return json.dumps(mock_resp)
        return "This is a mock AI response to: " + prompt[:20]

    async def generate_speech(
        self,
        text: str,
        voice_id: str,
        model: Optional[str] = None,
        speed: float = 1.0,
    ) -> bytes:
        import struct

        payload = b"mock_audio_for: " + text.encode("utf-8")
        data_size = len(payload)
        file_size = 36 + data_size
        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",
            file_size,
            b"WAVE",
            b"fmt ",
            16,
            1,
            1,
            44100,
            88200,
            2,
            16,
            b"data",
            data_size,
        )
        return header + payload


ai_provider_manager.register_provider("mock", MockAIProvider(), is_default=True)
