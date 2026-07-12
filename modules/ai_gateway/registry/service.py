from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_gateway import AIGatewayProvider, AIModel
from app.schemas.ai_gateway import AIGatewayProviderCreate, AIModelCreate


class ModelRegistryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_provider_by_name(self, name: str) -> Optional[AIGatewayProvider]:
        result = await self.db.execute(select(AIGatewayProvider).where(AIGatewayProvider.name == name))
        val = result.scalars().first()
        if val is None: return None
        return val

    async def register_provider(self, provider_in: AIGatewayProviderCreate) -> AIGatewayProvider:
        existing = await self.get_provider_by_name(provider_in.name)
        if existing:
            return existing

        provider = AIGatewayProvider(**provider_in.model_dump())
        self.db.add(provider)
        await self.db.commit()
        await self.db.refresh(provider)
        return provider

    async def get_model_by_name(self, name: str) -> Optional[AIModel]:
        result = await self.db.execute(select(AIModel).where(AIModel.name == name))
        val = result.scalars().first()
        if val is None: return None
        return val

    async def register_model(self, model_in: AIModelCreate) -> AIModel:
        existing = await self.get_model_by_name(model_in.name)
        if existing:
            for key, value in model_in.model_dump().items():
                setattr(existing, key, value)
            await self.db.commit()
            await self.db.refresh(existing)
            return existing

        model = AIModel(**model_in.model_dump())
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        return model

    async def get_models_by_capability(self, capability: str) -> List[AIModel]:
        result = await self.db.execute(select(AIModel).where(AIModel.is_active))
        all_models = result.scalars().all()
        return [m for m in all_models if capability in m.capabilities]
