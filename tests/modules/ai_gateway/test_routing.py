from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_gateway import AIGatewayProvider, AIModel, RoutingPolicy
from modules.ai_gateway.routing.manager import AIGatewayRoutingError, RoutingManager


@pytest.fixture
async def gateway_seed(db_session: AsyncSession) -> dict[str, Any]:
    # Setup test data
    p = AIGatewayProvider(name="test_provider", provider_type="local")
    db_session.add(p)
    await db_session.commit()
    await db_session.refresh(p)

    m1 = AIModel(
        name="fast_model",
        provider_id=p.id,
        version="1",
        capabilities=["text"],
        priority=10,
        average_latency=50.0,
        is_active=True,
        health_status="healthy",
    )
    m2 = AIModel(
        name="good_model",
        provider_id=p.id,
        version="1",
        capabilities=["text"],
        priority=20,
        average_latency=100.0,
        is_active=True,
        health_status="healthy",
    )
    m3 = AIModel(
        name="offline_model",
        provider_id=p.id,
        version="1",
        capabilities=["text"],
        priority=100,
        average_latency=10.0,
        is_active=True,
        health_status="unhealthy",
    )

    pol = RoutingPolicy(task_type="text", routing_mode="balanced", preferred_providers=["good_model"])

    db_session.add_all([m1, m2, m3, pol])
    await db_session.commit()
    return {"provider": p, "m1": m1, "m2": m2, "m3": m3, "policy": pol}


@pytest.mark.asyncio
async def test_get_available_models(db_session: AsyncSession, gateway_seed: dict[str, Any]) -> None:
    rm = RoutingManager(db_session)
    models = await rm.get_available_models("text")

    assert len(models) == 2
    names = [m.name for m in models]
    assert "fast_model" in names
    assert "good_model" in names
    assert "offline_model" not in names


@pytest.mark.asyncio
async def test_route_request_preferred(db_session: AsyncSession, gateway_seed: dict[str, Any]) -> None:
    rm = RoutingManager(db_session)
    model = await rm.route_request("text")

    assert model.name == "good_model"


@pytest.mark.asyncio
async def test_route_request_fallback(db_session: AsyncSession, gateway_seed: dict[str, Any]) -> None:
    rm = RoutingManager(db_session)
    # Modify policy to remove preferred models
    gateway_seed["policy"].preferred_providers = []
    db_session.add(gateway_seed["policy"])
    await db_session.commit()

    model = await rm.route_request("text")
    # should fallback to highest priority
    assert model.name == "good_model"


@pytest.mark.asyncio
async def test_route_request_no_models(db_session: AsyncSession) -> None:
    rm = RoutingManager(db_session)
    with pytest.raises(AIGatewayRoutingError):
        await rm.route_request("unknown_task")
