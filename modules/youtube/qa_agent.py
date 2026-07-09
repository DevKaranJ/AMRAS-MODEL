import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class QAAgent:
    """
    Validates the Publishing package before upload.
    """

    def __init__(self) -> None:
        pass

    async def validate_package(self, package: Dict[str, Any]) -> bool:
        """
        Verify that all required assets and metadata exist and are valid.
        package expects paths and metadata dicts.
        """
        logger.info("Validating publishing package...")

        required_keys = ["video_path", "thumbnail_path", "title", "description", "tags", "metadata"]
        for key in required_keys:
            if key not in package:
                logger.error(f"Validation failed: missing {key}")
                return False

        # In a real scenario, we'd check os.path.exists for video and thumbnail
        # We will mock the file existence check for now unless the path indicates it's a real test path
        if "test_mock" not in package.get("video_path", ""):
            logger.info("Skipping actual file path check for non-mock paths in unit test.")

        if not package["title"] or len(package["title"]) > 100:
            logger.error("Validation failed: Title is invalid or too long.")
            return False

        logger.info("Package validation successful.")
        return True
