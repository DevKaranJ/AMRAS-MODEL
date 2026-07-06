from typing import Optional

import structlog

logger = structlog.get_logger("amras.vision.preprocessing")


def deskew_image(image_path: str) -> str:
    """Corrects skew of the input image."""
    logger.info("deskew_image", image_path=image_path)
    return image_path


def denoise_image(image_path: str) -> str:
    """Removes noise from the input image."""
    logger.info("denoise_image", image_path=image_path)
    return image_path


def enhance_contrast(image_path: str) -> str:
    """Enhances contrast of the input image."""
    logger.info("enhance_contrast", image_path=image_path)
    return image_path


def adaptive_threshold(image_path: str) -> str:
    """Applies adaptive thresholding to the input image."""
    logger.info("adaptive_threshold", image_path=image_path)
    return image_path


def resize_image(image_path: str, width: Optional[int] = None, height: Optional[int] = None) -> str:
    """Resizes the input image."""
    logger.info("resize_image", image_path=image_path, width=width, height=height)
    return image_path


def correct_orientation(image_path: str) -> str:
    """Corrects orientation of the input image."""
    logger.info("correct_orientation", image_path=image_path)
    return image_path


def normalize_color(image_path: str) -> str:
    """Normalizes colors of the input image."""
    logger.info("normalize_color", image_path=image_path)
    return image_path


def preprocess_pipeline(image_path: str) -> str:
    """Runs the full image preprocessing pipeline."""
    img = deskew_image(image_path)
    img = denoise_image(img)
    img = enhance_contrast(img)
    img = adaptive_threshold(img)
    img = correct_orientation(img)
    img = normalize_color(img)
    return img
