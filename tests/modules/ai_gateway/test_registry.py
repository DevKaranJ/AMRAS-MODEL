import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.ai_gateway import AIGatewayProviderCreate, AIModelCreate
from modules.ai_gateway.registry.service import ModelRegistryService


@pytest.mark.asyncio
async def test_register_provider(db_session: AsyncSession) -> None:
    registry = ModelRegistryService(db_session)
    provider_in = AIGatewayProviderCreate(
        name="test_local_ollama", provider_type="local", is_active=True, config={"base_url": "http://localhost:11434"}
    )
    provider = await registry.register_provider(provider_in)

    assert provider.id is not None
    assert provider.name == "test_local_ollama"
    assert provider.provider_type == "local"


@pytest.mark.asyncio
async def test_register_model(db_session: AsyncSession) -> None:
    registry = ModelRegistryService(db_session)
    # create provider
    provider_in = AIGatewayProviderCreate(name="test_local_vllm", provider_type="local")
    provider = await registry.register_provider(provider_in)

    # create model
    model_in = AIModelCreate(
        name="llama3_test", provider_id=provider.id, version="v1", capabilities=["text", "translation"]
    )
    model = await registry.register_model(model_in)

    assert model.id is not None
    assert model.name == "llama3_test"
    assert "translation" in model.capabilities

    # retrieve by capability
    models = await registry.get_models_by_capability("text")
    assert any(m.name == "llama3_test" for m in models)
