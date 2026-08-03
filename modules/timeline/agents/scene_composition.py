"""Real scene composition agent for timeline.

Analyzes scenes and determines:
- Scene duration based on content
- Safe crop zones for Ken Burns effects
- Visual complexity for pacing
- Camera movement selection
"""

from typing import Any, Dict, List, Optional

from app.core.logger import get_logger
from app.schemas.timeline import SceneMetadataCreate

logger = get_logger("amras.timeline.scene_composition")


class SceneCompositionAgent:
    """Real scene composition agent."""

    # Duration ranges based on scene type
    DURATION_RANGES = {
        "action": (2.0, 4.0),      # Fast cuts for action
        "dialogue": (3.0, 5.0),    # Moderate for dialogue
        "emotion": (4.0, 6.0),     # Longer for emotional
        "establishing": (3.0, 4.0),  # Medium for establishing shots
        "transition": (1.5, 2.5),  # Short for transitions
    }

    # Camera effects based on emotion
    CAMERA_EFFECTS = {
        "excited": "zoom_in",
        "tense": "zoom_in",
        "sad": "zoom_out",
        "peaceful": "pan_left",
        "dramatic": "pan_right",
        "neutral": "zoom_in",
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.default_duration = config.get("default_duration", 4.0)

    def analyze_scene(
        self, scene_data: Dict[str, Any], pages_data: List[Dict[str, Any]]
    ) -> SceneMetadataCreate:
        """Analyze scene data to determine composition parameters."""
        # Analyze emotion from scene data
        emotion = scene_data.get("emotion", "neutral")
        intensity = self._calculate_intensity(scene_data)
        visual_complexity = self._calculate_visual_complexity(pages_data)
        dialogue_density = self._calculate_dialogue_density(scene_data)

        # Determine scene type
        is_battle = self._is_battle_scene(scene_data)
        is_flashback = scene_data.get("is_flashback", False)

        # Calculate optimal camera effect
        camera_effect = self._select_camera_effect(emotion, intensity)

        return SceneMetadataCreate(
            emotion=emotion,
            intensity=intensity,
            visual_complexity=visual_complexity,
            dialogue_density=dialogue_density,
            is_battle=is_battle,
            is_flashback=is_flashback,
            config={
                "camera_effect": camera_effect,
                "focus": self._determine_focus(pages_data),
            },
        )

    def calculate_safe_crop(self, panel_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate safe crop zone for Ken Burns effect.

        Returns crop coordinates as fractions (0.0-1.0):
        - x, y: top-left corner
        - w, h: width and height
        """
        bbox = panel_data.get("bounding_box", {})
        panel_type = panel_data.get("panel_type", "standard")

        # Base safe zone (90% center crop)
        crop = {"x": 0.05, "y": 0.05, "w": 0.9, "h": 0.9}

        # Adjust based on panel type
        if panel_type == "wide":
            # For wide panels, crop more vertically
            crop["y"] = 0.15
            crop["h"] = 0.7
        elif panel_type == "tall":
            # For tall panels, crop more horizontally
            crop["x"] = 0.1
            crop["w"] = 0.8

        # Ensure characters' faces are not cropped
        characters = panel_data.get("characters", [])
        if characters:
            # Find highest character (face likely at top)
            min_y = min(c.get("bounding_box", {}).get("y", 0) for c in characters)
            if min_y < 0.2:  # Character near top
                crop["y"] = max(0.0, crop["y"] - 0.1)
                crop["h"] = min(1.0, crop["h"] + 0.1)

        return crop

    def estimate_duration(
        self,
        scene_data: Dict[str, Any],
        narration_text: str = "",
        panel_count: int = 1,
    ) -> float:
        """Estimate optimal scene duration based on content."""
        # Get base duration from scene type
        scene_type = scene_data.get("scene_type", "dialogue")
        min_dur, max_dur = self.DURATION_RANGES.get(scene_type, (3.0, 5.0))

        # Adjust based on narration length
        if narration_text:
            word_count = len(narration_text.split())
            # Average speaking rate: 2.5 words/second
            narration_duration = word_count / 2.5
            # Add 0.5s buffer
            base_duration = narration_duration + 0.5
        else:
            base_duration = self.default_duration

        # Adjust based on panel count
        panel_factor = max(1.0, panel_count * 0.5)
        base_duration = max(base_duration, panel_factor)

        # Clamp to range
        duration = max(min_dur, min(max_dur, base_duration))

        return round(duration, 2)

    def _calculate_intensity(self, scene_data: Dict[str, Any]) -> float:
        """Calculate scene intensity (0.0-1.0)."""
        intensity = 0.5

        # Increase for battles
        if scene_data.get("is_battle"):
            intensity += 0.3

        # Increase based on emotion
        emotion = scene_data.get("emotion", "neutral")
        if emotion in ["excited", "tense", "angry"]:
            intensity += 0.2
        elif emotion in ["sad", "peaceful"]:
            intensity -= 0.2

        return max(0.0, min(1.0, intensity))

    def _calculate_visual_complexity(self, pages_data: List[Dict[str, Any]]) -> float:
        """Calculate visual complexity based on panel/character count."""
        if not pages_data:
            return 0.5

        total_panels = sum(len(p.get("panels", [])) for p in pages_data)
        total_chars = sum(len(p.get("characters", [])) for p in pages_data)

        # Normalize
        panel_score = min(1.0, total_panels / 10)
        char_score = min(1.0, total_chars / 5)

        return (panel_score + char_score) / 2

    def _calculate_dialogue_density(self, scene_data: Dict[str, Any]) -> float:
        """Calculate dialogue density."""
        ocr_text = scene_data.get("ocr_text", "")
        if not ocr_text:
            return 0.3

        word_count = len(ocr_text.split())
        # Normalize to 0-1 range (100+ words = full density)
        return min(1.0, word_count / 100)

    def _is_battle_scene(self, scene_data: Dict[str, Any]) -> bool:
        """Determine if scene is a battle."""
        keywords = ["battle", "fight", "attack", "punch", "kick", "sword", "weapon"]
        text = str(scene_data).lower()
        return any(kw in text for kw in keywords)

    def _select_camera_effect(self, emotion: str, intensity: float) -> str:
        """Select camera effect based on emotion and intensity."""
        if intensity > 0.7:
            return "zoom_in"  # High intensity = zoom in
        return self.CAMERA_EFFECTS.get(emotion, "zoom_in")

    def _determine_focus(self, pages_data: List[Dict[str, Any]]) -> str:
        """Determine camera focus point."""
        if not pages_data:
            return "center"

        # Check for character positions
        for page in pages_data:
            chars = page.get("characters", [])
            if chars:
                # Use first character's position
                bbox = chars[0].get("bounding_box", {})
                x = bbox.get("x", 0)
                w = bbox.get("w", 1920)

                # Determine focus based on horizontal position
                center_x = x + w / 2
                if center_x < 640:
                    return "left"
                elif center_x > 1280:
                    return "right"

        return "center"
