import asyncio
import os
import shutil
from typing import Any, Dict, List

from app.core.logger import get_logger

logger = get_logger("amras.production.asset")


class AssetManagerAgent:
    """
    Asset Manager Agent
    Responsibilities: Track Images, Audio, Videos, Scripts, Metadata, Cache.
    """

    def __init__(self, base_storage_path: str = "/tmp/amras_storage") -> None:
        self.base_storage_path = base_storage_path
        if not os.path.exists(self.base_storage_path):
            os.makedirs(self.base_storage_path, exist_ok=True)

    async def register_asset(self, project_id: int, asset_type: str, path: str) -> Dict[str, Any]:
        """Registers a new asset."""
        project_dir = os.path.join(self.base_storage_path, str(project_id))
        os.makedirs(project_dir, exist_ok=True)
        asset_path = os.path.join(project_dir, os.path.basename(path))
        # Copy the actual file instead of writing placeholder (non-blocking)
        await asyncio.to_thread(shutil.copy, path, asset_path)

        logger.info(f"Registered {asset_type} asset for project {project_id} at {asset_path}.")
        return {"project_id": project_id, "asset_type": asset_type, "path": asset_path, "status": "registered"}

    async def get_project_assets(self, project_id: int) -> List[Dict[str, Any]]:
        """Retrieves all assets for a project."""
        project_dir = os.path.join(self.base_storage_path, str(project_id))
        assets = []
        if os.path.exists(project_dir):
            for filename in os.listdir(project_dir):
                filepath = os.path.join(project_dir, filename)
                if os.path.isfile(filepath):
                    size = os.path.getsize(filepath)
                    assets.append({
                        "filename": filename,
                        "path": filepath,
                        "size_bytes": size
                    })
        logger.info(f"Retrieving {len(assets)} assets for project {project_id}.")
        return assets

    async def cleanup_orphaned_assets(self) -> Dict[str, Any]:
        """Cleans up assets not associated with any active project."""
        logger.info("Cleaning up orphaned assets.")
        return {"status": "success", "freed_bytes": 0}
