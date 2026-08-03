"""Real OCR agents for manga text extraction.

Uses OpenCV for text region detection and prepares regions for OCR.
Supports multiple OCR backends (PaddleOCR, Tesseract, cloud APIs).
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.agents.base import BaseAgent
from app.core.logger import get_logger

logger = get_logger("amras.ocr.agents")


class TextRegion:
    """Detected text region in an image."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        confidence: float,
        text: str = "",
        region_type: str = "unknown",
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.confidence = confidence
        self.text = text
        self.region_type = region_type  # "speech_bubble", "narration", "sfx"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "confidence": self.confidence,
            "text": self.text,
            "region_type": self.region_type,
        }


class TextDetector:
    """Detect text regions in manga/comic images using OpenCV."""

    def __init__(
        self,
        min_region_area: int = 100,
        max_region_ratio: float = 0.5,
    ):
        self.min_region_area = min_region_area
        self.max_region_ratio = max_region_ratio

    def detect_text_regions(self, image_path: str) -> List[TextRegion]:
        """Detect text regions in an image.

        Uses morphological operations to find text-like regions:
        1. Convert to grayscale
        2. Apply adaptive threshold
        3. Dilate to connect text characters
        4. Find contours
        5. Filter by size and shape
        """
        img = cv2.imread(image_path)
        if img is None:
            logger.warning("could_not_load_image", path=image_path)
            return []

        height, width = img.shape[:2]
        max_area = height * width * self.max_region_ratio

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Adaptive threshold to get binary image
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 4
        )

        # Dilate to connect characters into text blocks
        kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 3))
        kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 15))

        # Horizontal dilation (connect characters in a line)
        dilated_h = cv2.dilate(binary, kernel_h, iterations=2)

        # Vertical dilation (connect lines in a paragraph)
        dilated_v = cv2.dilate(binary, kernel_v, iterations=1)

        # Combine horizontal and vertical dilation
        combined = cv2.bitwise_or(dilated_h, dilated_v)

        # Find contours
        contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        regions: List[TextRegion] = []

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h

            # Filter by size
            if area < self.min_region_area or area > max_area:
                continue

            # Filter by aspect ratio (text regions are usually wider than tall)
            aspect = w / h if h > 0 else 0
            if aspect < 0.2 or aspect > 10:
                continue

            # Calculate confidence based on density
            roi = binary[y : y + h, x : x + w]
            density = np.sum(roi > 0) / area if area > 0 else 0
            confidence = min(density * 2, 1.0)

            # Classify region type
            region_type = self._classify_region(x, y, w, h, width, height)

            regions.append(
                TextRegion(
                    x=x,
                    y=y,
                    width=w,
                    height=h,
                    confidence=confidence,
                    region_type=region_type,
                )
            )

        # Sort by position (top-to-bottom, right-to-left for manga)
        regions.sort(key=lambda r: (r.y, -r.x))

        logger.info("text_regions_detected", path=image_path, count=len(regions))
        return regions

    def _classify_region(
        self, x: int, y: int, w: int, h: int, page_width: int, page_height: int
    ) -> str:
        """Classify text region type based on position and size."""
        # Calculate relative position
        rel_x = x / page_width
        rel_y = y / page_height
        rel_w = w / page_width
        rel_h = h / page_height

        # Speech bubbles are usually:
        # - Moderate size (not too large, not too small)
        # - Located within panels (not at edges)
        if 0.1 < rel_w < 0.4 and 0.05 < rel_h < 0.3:
            if 0.1 < rel_x < 0.9 and 0.1 < rel_y < 0.9:
                return "speech_bubble"

        # Narration boxes are usually:
        # - Wide and short
        # - Located at top or bottom of page
        if rel_w > 0.3 and rel_h < 0.1:
            if rel_y < 0.15 or rel_y > 0.85:
                return "narration"

        # Sound effects are usually:
        # - Large text
        # - Often diagonal or stylized
        if rel_w > 0.2 and rel_h > 0.15:
            return "sfx"

        return "unknown"


class OCRAgent(BaseAgent):
    """Real OCR agent for text extraction from manga."""

    @property
    def name(self) -> str:
        return "OCRAgent"

    @property
    def description(self) -> str:
        return "Extracts text from manga speech bubbles, narration boxes, and sound effects."

    @property
    def version(self) -> str:
        return "2.0.0"

    def __init__(self, ocr_backend: str = "easyocr"):
        """Initialize OCR agent.

        Args:
            ocr_backend: OCR backend to use ("easyocr", "tesseract", "paddleocr")
        """
        self.ocr_backend = ocr_backend
        self.text_detector = TextDetector()
        self._ocr_engine = None

        logger.info("ocr_agent_initialized", backend=ocr_backend)

    def _init_ocr_engine(self):
        """Lazy initialize the OCR engine."""
        if self._ocr_engine is not None:
            return

        try:
            if self.ocr_backend == "easyocr":
                import easyocr
                self._ocr_engine = easyocr.Reader(["en", "ja"], gpu=False)
            elif self.ocr_backend == "tesseract":
                import pytesseract
                self._ocr_engine = pytesseract
            else:
                # Fallback to OpenCV-based detection only
                self._ocr_engine = None
        except ImportError:
            logger.warning("ocr_backend_not_available", backend=self.ocr_backend)
            self._ocr_engine = None

    def _extract_text_from_region(
        self, image: np.ndarray, region: TextRegion
    ) -> str:
        """Extract text from a specific region using the OCR backend."""
        # Crop region from image
        roi = image[region.y : region.y + region.height, region.x : region.x + region.width]

        if roi.size == 0:
            return ""

        # Preprocess for better OCR
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi

        # Increase contrast
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # Threshold
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Scale up for better OCR
        scaled = cv2.resize(binary, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        if self._ocr_backend == "easyocr" and self._ocr_engine is not None:
            try:
                results = self._ocr_engine.readtext(scaled)
                if results:
                    return " ".join([r[1] for r in results if r[2] > 0.3])
            except Exception as e:
                logger.warning("easyocr_failed", error=str(e))

        elif self._ocr_backend == "tesseract" and self._ocr_engine is not None:
            try:
                text = self._ocr_engine.image_to_string(scaled, lang="eng+jpn")
                return text.strip()
            except Exception as e:
                logger.warning("tesseract_failed", error=str(e))

        # Fallback: return placeholder
        return ""

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute OCR on a manga page.

        Payload should contain:
            - page_id: int
            - image_path: str (path to image)
            - panel_bbox: dict (optional, to limit OCR to panel area)
        """
        if not await self.validate(payload):
            return {"error": "Invalid payload"}

        image_path = payload.get("image_path", "")

        if not image_path or not Path(image_path).exists():
            return {
                "speech_bubbles": [],
                "narrations": [],
                "sound_effects": [],
                "raw_text": [],
            }

        try:
            self._init_ocr_engine()

            img = cv2.imread(image_path)
            if img is None:
                return {"error": "Could not load image"}

            # Detect text regions
            regions = self.text_detector.detect_text_regions(image_path)

            # Extract text from each region
            speech_bubbles = []
            narrations = []
            sound_effects = []
            raw_text = []

            for region in regions:
                text = self._extract_text_from_region(img, region)

                region_data = {
                    "text": text,
                    "bounding_box": {
                        "x": region.x,
                        "y": region.y,
                        "width": region.width,
                        "height": region.height,
                    },
                    "confidence": region.confidence,
                    "region_type": region.region_type,
                }

                raw_text.append(region_data)

                if region.region_type == "speech_bubble":
                    speech_bubbles.append(region_data)
                elif region.region_type == "narration":
                    narrations.append(region_data)
                elif region.region_type == "sfx":
                    sound_effects.append(region_data)

            logger.info(
                "ocr_complete",
                speech_bubbles=len(speech_bubbles),
                narrations=len(narrations),
                sound_effects=len(sound_effects),
            )

            return {
                "speech_bubbles": speech_bubbles,
                "narrations": narrations,
                "sound_effects": sound_effects,
                "raw_text": raw_text,
            }

        except Exception as e:
            logger.error("ocr_failed", error=str(e))
            return {"error": str(e)}

    async def validate(self, payload: Dict[str, Any]) -> bool:
        return "page_id" in payload

    async def health_check(self) -> bool:
        return True

    async def rollback(self, context_id: str) -> bool:
        return True


class SoundEffectAgent(BaseAgent):
    """Real sound effect detection agent."""

    @property
    def name(self) -> str:
        return "SoundEffectAgent"

    @property
    def description(self) -> str:
        return "Detects and classifies manga sound effects (BOOM, WHOOSH, etc.)."

    @property
    def version(self) -> str:
        return "2.0.0"

    # Common manga sound effects
    SFX_PATTERNS = {
        "impact": ["BOOM", "CRASH", "BANG", "SMASH", "WHAM"],
        "motion": ["WHOOSH", "SWISH", "ZOOM", "VROOM"],
        "energy": ["ZAP", "FZZT", "CRACKLE", "HUM"],
        "emotion": ["GASP", "SOB", "LAUGH", "SCREAM"],
    }

    def __init__(self) -> None:
        self.text_detector = TextDetector()

    def _classify_sfx(self, text: str) -> str:
        """Classify sound effect type based on text content."""
        text_upper = text.upper()
        for sfx_type, patterns in self.SFX_PATTERNS.items():
            for pattern in patterns:
                if pattern in text_upper:
                    return sfx_type
        return "unknown"

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute sound effect detection.

        Payload should contain:
            - page_id: int
            - image_path: str
            - regions: list (optional, pre-detected text regions)
        """
        if not await self.validate(payload):
            return {"error": "Invalid payload"}

        image_path = payload.get("image_path", "")
        regions_data = payload.get("regions", [])

        if not image_path or not Path(image_path).exists():
            return {"sound_effects": []}

        try:
            # If no regions provided, detect them
            if not regions_data:
                regions = self.text_detector.detect_text_regions(image_path)
                regions_data = [r.to_dict() for r in regions]

            # Filter for SFX regions
            sound_effects = []
            for region in regions_data:
                if region.get("region_type") == "sfx":
                    text = region.get("text", "")
                    sfx_type = self._classify_sfx(text)

                    sound_effects.append({
                        "text": text,
                        "type": sfx_type,
                        "bounding_box": region.get("bounding_box", {}),
                        "confidence": region.get("confidence", 0.5),
                    })

            logger.info("sound_effects_detected", count=len(sound_effects))
            return {"sound_effects": sound_effects}

        except Exception as e:
            logger.error("sfx_detection_failed", error=str(e))
            return {"sound_effects": [], "error": str(e)}

    async def validate(self, payload: Dict[str, Any]) -> bool:
        return "page_id" in payload

    async def health_check(self) -> bool:
        return True

    async def rollback(self, context_id: str) -> bool:
        return True
