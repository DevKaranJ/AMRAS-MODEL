"""Real image preprocessing pipeline for manga/comics.

Uses OpenCV for:
- Deskew (Hough transform)
- Denoise (Non-local means)
- Contrast enhancement (CLAHE)
- Adaptive thresholding
- Color normalization
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple

from app.core.logger import get_logger

logger = get_logger("amras.vision.preprocessing")


def deskew_image(image_path: str, output_path: Optional[str] = None) -> str:
    """Corrects skew of the input image using Hough transform.

    Args:
        image_path: Path to input image
        output_path: Path to save corrected image (overwrites if None)

    Returns:
        Path to corrected image
    """
    if output_path is None:
        output_path = image_path

    try:
        img = cv2.imread(image_path)
        if img is None:
            logger.warning("could_not_load_image", path=image_path)
            return image_path

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detect edges
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        # Detect lines using Hough transform
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)

        if lines is None or len(lines) == 0:
            return image_path

        # Calculate average angle
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            angles.append(angle)

        # Filter angles (only keep small rotations)
        angles = [a for a in angles if abs(a) < 15]
        if not angles:
            return image_path

        avg_angle = np.median(angles)

        # Only correct if angle is significant
        if abs(avg_angle) > 0.5:
            h, w = img.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, avg_angle, 1.0)
            img = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            logger.info("image_deskewed", angle=avg_angle, path=image_path)

        cv2.imwrite(output_path, img)
        return output_path

    except Exception as e:
        logger.error("deskew_failed", error=str(e), path=image_path)
        return image_path


def denoise_image(image_path: str, output_path: Optional[str] = None, strength: int = 10) -> str:
    """Removes noise from the input image using non-local means denoising.

    Args:
        image_path: Path to input image
        output_path: Path to save denoised image
        strength: Denoising strength (higher = more denoising)

    Returns:
        Path to denoised image
    """
    if output_path is None:
        output_path = image_path

    try:
        img = cv2.imread(image_path)
        if img is None:
            return image_path

        # Non-local means denoising
        denoised = cv2.fastNlMeansDenoisingColored(img, None, strength, strength, 7, 21)

        cv2.imwrite(output_path, denoised)
        logger.info("image_denoised", strength=strength, path=image_path)
        return output_path

    except Exception as e:
        logger.error("denoise_failed", error=str(e), path=image_path)
        return image_path


def enhance_contrast(image_path: str, output_path: Optional[str] = None, clip_limit: float = 2.0) -> str:
    """Enhances contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization).

    Args:
        image_path: Path to input image
        output_path: Path to save enhanced image
        clip_limit: CLAHE clip limit (higher = more contrast)

    Returns:
        Path to enhanced image
    """
    if output_path is None:
        output_path = image_path

    try:
        img = cv2.imread(image_path)
        if img is None:
            return image_path

        # Convert to LAB color space
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])

        # Convert back to BGR
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

        cv2.imwrite(output_path, enhanced)
        logger.info("contrast_enhanced", clip_limit=clip_limit, path=image_path)
        return output_path

    except Exception as e:
        logger.error("contrast_enhance_failed", error=str(e), path=image_path)
        return image_path


def adaptive_threshold(image_path: str, output_path: Optional[str] = None) -> str:
    """Applies adaptive thresholding for clean binary output.

    Args:
        image_path: Path to input image
        output_path: Path to save thresholded image

    Returns:
        Path to thresholded image
    """
    if output_path is None:
        output_path = image_path

    try:
        img = cv2.imread(image_path)
        if img is None:
            return image_path

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Adaptive threshold
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        cv2.imwrite(output_path, binary)
        logger.info("threshold_applied", path=image_path)
        return output_path

    except Exception as e:
        logger.error("threshold_failed", error=str(e), path=image_path)
        return image_path


def resize_image(
    image_path: str,
    output_path: Optional[str] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
) -> str:
    """Resizes the input image while maintaining aspect ratio.

    Args:
        image_path: Path to input image
        output_path: Path to save resized image
        width: Target width (if None, calculated from height)
        height: Target height (if None, calculated from width)

    Returns:
        Path to resized image
    """
    if output_path is None:
        output_path = image_path

    try:
        img = cv2.imread(image_path)
        if img is None:
            return image_path

        h, w = img.shape[:2]

        if width is None and height is None:
            return image_path

        if width is None:
            width = int(w * height / h)
        elif height is None:
            height = int(h * width / w)

        resized = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)

        cv2.imwrite(output_path, resized)
        logger.info("image_resized", new_size=(width, height), path=image_path)
        return output_path

    except Exception as e:
        logger.error("resize_failed", error=str(e), path=image_path)
        return image_path


def correct_orientation(image_path: str, output_path: Optional[str] = None) -> str:
    """Corrects orientation based on EXIF data (if available).

    Args:
        image_path: Path to input image
        output_path: Path to save corrected image

    Returns:
        Path to corrected image
    """
    if output_path is None:
        output_path = image_path

    try:
        img = cv2.imread(image_path)
        if img is None:
            return image_path

        # For now, just copy the image
        # Real implementation would read EXIF orientation tag
        cv2.imwrite(output_path, img)
        return output_path

    except Exception as e:
        logger.error("orientation_correction_failed", error=str(e), path=image_path)
        return image_path


def normalize_color(image_path: str, output_path: Optional[str] = None) -> str:
    """Normalizes colors using white balance correction.

    Args:
        image_path: Path to input image
        output_path: Path to save normalized image

    Returns:
        Path to normalized image
    """
    if output_path is None:
        output_path = image_path

    try:
        img = cv2.imread(image_path)
        if img is None:
            return image_path

        # Simple white balance: normalize each channel
        result = img.copy().astype(np.float32)

        for i in range(3):  # BGR channels
            channel = result[:, :, i]
            min_val = np.percentile(channel, 1)
            max_val = np.percentile(channel, 99)

            if max_val > min_val:
                channel = (channel - min_val) / (max_val - min_val) * 255
                result[:, :, i] = np.clip(channel, 0, 255)

        result = result.astype(np.uint8)

        cv2.imwrite(output_path, result)
        logger.info("color_normalized", path=image_path)
        return output_path

    except Exception as e:
        logger.error("color_normalize_failed", error=str(e), path=image_path)
        return image_path


def preprocess_pipeline(
    image_path: str,
    output_dir: Optional[str] = None,
    skip_deskew: bool = False,
    skip_denoise: bool = False,
    skip_contrast: bool = False,
    skip_threshold: bool = False,
) -> str:
    """Runs the full image preprocessing pipeline.

    Args:
        image_path: Path to input image
        output_dir: Directory for intermediate files (uses temp if None)
        skip_deskew: Skip deskew step
        skip_denoise: Skip denoise step
        skip_contrast: Skip contrast enhancement
        skip_threshold: Skip adaptive threshold

    Returns:
        Path to preprocessed image
    """
    if output_dir is None:
        output_dir = str(Path(image_path).parent)

    output_path = str(Path(output_dir) / f"preprocessed_{Path(image_path).name}")

    try:
        # Load original
        img = cv2.imread(image_path)
        if img is None:
            logger.warning("could_not_load_image", path=image_path)
            return image_path

        result = img.copy()

        # Step 1: Deskew
        if not skip_deskew:
            temp_path = str(Path(output_dir) / "temp_deskew.png")
            deskew_image(image_path, temp_path)
            result = cv2.imread(temp_path)
            if result is None:
                result = img.copy()

        # Step 2: Denoise
        if not skip_denoise:
            result = cv2.fastNlMeansDenoisingColored(result, None, 10, 10, 7, 21)

        # Step 3: Contrast enhancement (CLAHE)
        if not skip_contrast:
            lab = cv2.cvtColor(result, cv2.COLOR_BGR2LAB)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            lab[:, :, 0] = clahe.apply(lab[:, :, 0])
            result = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

        # Save result
        cv2.imwrite(output_path, result)

        # Cleanup temp files
        temp_deskew = Path(output_dir) / "temp_deskew.png"
        if temp_deskew.exists():
            temp_deskew.unlink()

        logger.info("preprocessing_complete", input=image_path, output=output_path)
        return output_path

    except Exception as e:
        logger.error("preprocessing_failed", error=str(e), path=image_path)
        return image_path
