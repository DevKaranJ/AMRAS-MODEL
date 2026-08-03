import asyncio
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import httpx

from app.core.logger import get_logger
from app.shared.providers.base import AIProviderInterface

logger = get_logger("amras.providers.openrouter")


@dataclass
class APIKeyState:
    key: str
    requests_today: int = 0
    last_request_time: float = 0.0
    is_rate_limited: bool = False
    rate_limit_reset_time: float = 0.0
    total_requests: int = 0


@dataclass
class RateLimitConfig:
    requests_per_minute: int = 20
    requests_per_day_free: int = 50
    requests_per_day_with_credits: int = 1000


class OpenRouterProvider(AIProviderInterface):
    """Multi-key OpenRouter provider with automatic failover and rate limit handling."""

    BASE_URL = "https://openrouter.ai/api/v1"

    DEFAULT_MODEL_CHAIN = [
        "nvidia/nemotron-3-ultra-550b-a55b:free",
        "google/gemma-4-26b-a4b-it:free",
        "nvidia/nemotron-nano-12b-v2-vl:free",
    ]

    def __init__(
        self,
        api_keys: List[str],
        model_chain: Optional[List[str]] = None,
        rate_config: Optional[RateLimitConfig] = None,
    ) -> None:
        if not api_keys:
            raise ValueError("At least one API key is required")

        self._keys = [APIKeyState(key=k) for k in api_keys]
        self._model_chain = model_chain or self.DEFAULT_MODEL_CHAIN
        self._rate_config = rate_config or RateLimitConfig()
        self._current_key_index = 0
        self._current_model_index = 0
        self._lock = asyncio.Lock()

        logger.info(
            "openrouter_provider_initialized",
            key_count=len(self._keys),
            models=self._model_chain,
        )

    def _get_available_key(self) -> Optional[APIKeyState]:
        """Find the next available API key that isn't rate limited."""
        now = time.time()

        for _ in range(len(self._keys)):
            key_state = self._keys[self._current_key_index]

            # Check if rate limit has reset
            if key_state.is_rate_limited and now > key_state.rate_limit_reset_time:
                key_state.is_rate_limited = False
                key_state.requests_today = 0
                logger.info("rate_limit_reset", key_prefix=key_state.key[:10])

            # Check daily limit
            if key_state.requests_today >= self._rate_config.requests_per_day_free:
                self._current_key_index = (self._current_key_index + 1) % len(self._keys)
                continue

            # Check if enough time has passed for rate limit (rpm)
            time_since_last = now - key_state.last_request_time
            if time_since_last < (60.0 / self._rate_config.requests_per_minute):
                self._current_key_index = (self._current_key_index + 1) % len(self._keys)
                continue

            return key_state

        return None

    def _get_current_model(self) -> str:
        """Get the current model and advance to fallback if needed."""
        return self._model_chain[self._current_model_index % len(self._model_chain)]

    def _advance_to_next_model(self) -> str:
        """Move to the next model in the fallback chain."""
        if self._current_model_index < len(self._model_chain) - 1:
            self._current_model_index += 1
            model = self._model_chain[self._current_model_index]
            logger.warning(
                "switching_model",
                new_model=model,
                model_index=self._current_model_index,
            )
            return model
        return self._model_chain[-1]

    def _reset_model_chain(self) -> None:
        """Reset to the primary model after successful request."""
        self._current_model_index = 0

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate text using OpenRouter with automatic failover."""
        target_model = model or self._get_current_model()
        last_error = None

        for attempt in range(len(self._keys) * len(self._model_chain)):
            key_state = self._get_available_key()
            if not key_state:
                logger.error("no_available_keys")
                raise RuntimeError("All API keys are rate limited or exhausted")

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            payload: Dict[str, Any] = {
                "model": target_model,
                "messages": messages,
                "temperature": temperature,
            }
            if max_tokens:
                payload["max_tokens"] = max_tokens
            if response_format:
                payload["response_format"] = {"type": "json_object"}

            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        f"{self.BASE_URL}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {key_state.key}",
                            "Content-Type": "application/json",
                            "HTTP-Referer": "https://amras.app",
                            "X-Title": "AMRAS Manga Recap System",
                        },
                        json=payload,
                    )

                    # Update key usage
                    key_state.last_request_time = time.time()
                    key_state.requests_today += 1
                    key_state.total_requests += 1

                    if response.status_code == 200:
                        data = response.json()
                        content = data["choices"][0]["message"]["content"]
                        self._reset_model_chain()
                        logger.info(
                            "text_generated",
                            model=target_model,
                            key_prefix=key_state.key[:10],
                            tokens=data.get("usage", {}).get("total_tokens", 0),
                        )
                        return content

                    elif response.status_code == 429:
                        # Rate limited
                        retry_after = int(response.headers.get("Retry-After", 60))
                        key_state.is_rate_limited = True
                        key_state.rate_limit_reset_time = time.time() + retry_after
                        logger.warning(
                            "rate_limited",
                            key_prefix=key_state.key[:10],
                            retry_after=retry_after,
                        )
                        # Try next key
                        self._current_key_index = (self._current_key_index + 1) % len(self._keys)
                        continue

                    elif response.status_code == 402:
                        # Payment required - key exhausted
                        key_state.is_rate_limited = True
                        key_state.rate_limit_reset_time = time.time() + 86400  # 24h
                        logger.warning("key_exhausted", key_prefix=key_state.key[:10])
                        self._current_key_index = (self._current_key_index + 1) % len(self._keys)
                        continue

                    else:
                        last_error = f"HTTP {response.status_code}: {response.text[:200]}"
                        logger.error("api_error", status=response.status_code, error=last_error)
                        # Try next model
                        target_model = self._advance_to_next_model()
                        continue

            except httpx.TimeoutException:
                logger.warning("request_timeout", model=target_model, attempt=attempt)
                target_model = self._advance_to_next_model()
                continue
            except Exception as e:
                last_error = str(e)
                logger.error("request_failed", error=last_error, attempt=attempt)
                target_model = self._advance_to_next_model()
                continue

        raise RuntimeError(f"All providers exhausted. Last error: {last_error}")

    async def generate_speech(
        self,
        text: str,
        voice_id: str,
        model: Optional[str] = None,
        speed: float = 1.0,
    ) -> bytes:
        """OpenRouter doesn't support TTS - use Edge TTS instead."""
        raise NotImplementedError(
            "OpenRouter doesn't support TTS. Use EdgeTTSProvider for speech generation."
        )

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics for all keys."""
        return {
            "keys": [
                {
                    "prefix": k.key[:10] + "...",
                    "requests_today": k.requests_today,
                    "total_requests": k.total_requests,
                    "is_rate_limited": k.is_rate_limited,
                }
                for k in self._keys
            ],
            "current_model": self._get_current_model(),
            "model_chain": self._model_chain,
        }
