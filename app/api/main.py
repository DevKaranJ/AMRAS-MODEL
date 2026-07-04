from app.core.config import get_settings
from app.core.logger import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)

def main() -> None:
    settings = get_settings()
    logger.info(f"Starting {settings.project_name} in {settings.environment} mode.")

if __name__ == "__main__":
    main()
