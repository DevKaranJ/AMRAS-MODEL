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

            return json.dumps(self._generate_mock_from_schema(response_format))
        return "This is a mock AI response to: " + prompt[:20]

    def _generate_mock_from_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        mock_resp: Dict[str, Any] = {}
        for k, v in schema.get("properties", {}).items():
            mock_resp[k] = self._generate_mock_value(k, v)
        return mock_resp

    def _generate_mock_value(self, key: str, schema: Dict[str, Any]) -> Any:
        prop_type = schema.get("type", "string")
        if prop_type == "array":
            return self._generate_mock_array(schema)
        elif prop_type == "object":
            return self._generate_mock_object(schema)
        elif prop_type == "integer":
            return 1
        elif prop_type == "number":
            return 1.0
        elif prop_type == "boolean":
            return True
        else:
            return f"mocked_{key}"

    def _generate_mock_array(self, schema: Dict[str, Any]) -> list[Any]:
        items_schema = schema.get("items", {})
        if items_schema.get("type") == "object":
            return [self._generate_mock_from_schema(items_schema)]
        return ["mocked_item"]

    def _generate_mock_object(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        mock_obj: Dict[str, Any] = {}
        for k, v in schema.get("properties", {}).items():
            mock_obj[k] = self._generate_mock_value(k, v)
        return mock_obj

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
