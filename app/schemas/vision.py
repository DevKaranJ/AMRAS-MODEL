from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict


class BaseVisionEntity(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = None


class ConfidenceScoreSchema(BaseVisionEntity):
    entity_type: str
    entity_id: int
    score: float


class SpeechBubbleSchema(BaseVisionEntity):
    speaker: Optional[str] = None
    text: str
    confidence: float
    language: Optional[str] = None
    bubble_type: str
    bounding_box: Optional[Any] = None


class NarrationSchema(BaseVisionEntity):
    text: str
    type: str = "narration"


class CharacterDetectedSchema(BaseVisionEntity):
    identity_estimate: Optional[str] = None
    gender: Optional[str] = None
    age_group: Optional[str] = None
    clothing: Optional[str] = None
    expression: Optional[str] = None
    pose: Optional[str] = None
    confidence: float
    bounding_box: Optional[Any] = None


class ObjectDetectedSchema(BaseVisionEntity):
    label: str
    confidence: float
    bounding_box: Optional[Any] = None


class ActionDetectedSchema(BaseVisionEntity):
    label: str
    confidence: float


class SoundEffectSchema(BaseVisionEntity):
    text: str
    category: str = "sound_effect"
    ignore_for_summary: bool = True


class PanelSchema(BaseVisionEntity):
    panel_number: int
    reading_order: int
    bounding_box: Any
    scene_type: Optional[str] = None
    emotion: Optional[str] = None

    speech_bubbles: List[SpeechBubbleSchema] = []
    narrations: List[NarrationSchema] = []
    characters: List[CharacterDetectedSchema] = []
    objects: List[ObjectDetectedSchema] = []
    actions: List[ActionDetectedSchema] = []
    sound_effects: List[SoundEffectSchema] = []


class VisionJobSchema(BaseVisionEntity):
    page_id: int
    status: str
    error: Optional[str] = None


class PageVisionResult(BaseModel):
    page: int
    width: int
    height: int
    panels: List[PanelSchema] = []


class OCRExtractionResult(BaseModel):
    dialogue: List[SpeechBubbleSchema] = []
    narration: List[NarrationSchema] = []
    sound_effects: List[SoundEffectSchema] = []
