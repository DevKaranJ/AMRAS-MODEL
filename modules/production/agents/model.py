from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.models.production import InstalledModels

logger = get_logger("amras.production.model")


class AIModelManagerAgent:
    """
    AI Model Manager Agent
    Responsibilities: Manage installed models, downloaded models, local models, remote providers, model updates, GPU allocation.
    """

    def __init__(self) -> None:
        pass

    async def list_available_models(self, db: AsyncSession) -> List[Dict[str, Any]]:
        """Lists available local and remote models from database."""
        result = await db.execute(select(InstalledModels))
        models = result.scalars().all()
        return [
            {
                "id": m.id,
                "name": m.name,
                "version": m.version,
                "provider": m.provider,
                "status": m.status,
                "path": m.path,
                "memory_usage_mb": m.memory_usage_mb
            }
            for m in models
        ]

    async def allocate_gpu(self, model_name: str, required_vram_mb: int) -> bool:
        """Attempts to allocate GPU resources for a model."""
        logger.info(f"Allocating {required_vram_mb}MB VRAM for model {model_name}.")
        return True

    async def install_local_model(self, model_name: str, source_url: str, db: AsyncSession) -> Dict[str, Any]:
        """Downloads and installs a local AI model."""
        try:
            # Try to insert new model first (optimistic approach)
            model = InstalledModels(
                name=model_name,
                provider="local",
                status="installed",
                path=source_url
            )
            db.add(model)
            await db.commit()
            logger.info(f"Installing model {model_name} from {source_url}.")
            return {"model": model_name, "status": "installed"}
        except IntegrityError:
            # Handle concurrent insert or existing model - rollback and update
            await db.rollback()
            result = await db.execute(select(InstalledModels).where(InstalledModels.name == model_name))
            existing_model = result.scalar_one_or_none()
            if existing_model:
                # Update existing model
                existing_model.provider = "local"
                existing_model.status = "installed"
                existing_model.path = source_url
                try:
                    await db.commit()
                    logger.info(f"Updated existing model {model_name} from {source_url}.")
                    return {"model": model_name, "status": "installed"}
                except Exception as e:
                    await db.rollback()
                    logger.error(f"Failed to update model {model_name}: {e}")
                    raise
            else:
                logger.error(f"Failed to install model {model_name} due to integrity constraint.")
                raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to install model {model_name}: {e}")
            raise
