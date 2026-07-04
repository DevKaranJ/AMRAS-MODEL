from typing import Any, Dict

import pytest

from app.agents.base import BaseAgent


class DummyAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "dummy_agent"

    @property
    def description(self) -> str:
        return "Dummy description"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success"}

    async def validate(self, payload: Dict[str, Any]) -> bool:
        return True

    async def health_check(self) -> bool:
        return True

    async def rollback(self, context_id: str) -> bool:
        return True


@pytest.mark.asyncio
async def test_base_agent_implementation() -> None:
    agent = DummyAgent()
    assert agent.name == "dummy_agent"
    assert agent.description == "Dummy description"
    assert agent.version == "1.0.0"

    assert await agent.validate({}) is True
    assert await agent.health_check() is True
    assert await agent.rollback("ctx_1") is True

    res = await agent.execute({})
    assert res == {"status": "success"}
