from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AmrasException
from app.models.ai_gateway import AIModel, RoutingPolicy


class AIGatewayRoutingError(AmrasException):
    def __init__(self, message: str):
        super().__init__(error_code="ROUTING_ERROR", message=message, retryable=False)


class RoutingManager:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_policy(self, task_type: str) -> Optional[RoutingPolicy]:
        result = await self.db.execute(
            select(RoutingPolicy).where(RoutingPolicy.task_type == task_type, RoutingPolicy.is_active)
        )
        val = result.scalars().first()
        return val if isinstance(val, RoutingPolicy) else None

    async def get_available_models(self, task_type: str) -> List[AIModel]:
        result = await self.db.execute(select(AIModel).where(AIModel.is_active, AIModel.health_status == "healthy"))
        all_models = result.scalars().all()
        return [m for m in all_models if task_type in m.capabilities]

    async def route_request(self, task_type: str) -> AIModel:
        policy = await self.get_policy(task_type)
        available_models = await self.get_available_models(task_type)

        if not available_models:
            raise AIGatewayRoutingError(f"No healthy models available for task: {task_type}")

        if policy and policy.preferred_providers:
            for preferred in policy.preferred_providers:
                for model in available_models:
                    if model.name == preferred:
                        return model

        available_models.sort(key=lambda x: (x.priority, -(x.average_latency if x.average_latency is not None else float("inf"))), reverse=True)

        return available_models[0]
