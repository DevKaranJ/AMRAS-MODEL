from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class AnimationProfileBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    is_default: bool = False
    config: Dict[str, Any] = Field(default_factory=dict)

class AnimationProfileCreate(AnimationProfileBase):
    pass

class AnimationProfileResponse(AnimationProfileBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TransitionBase(BaseModel):
    type: str = Field(..., max_length=100)
    duration_ms: int = 0
    config: Dict[str, Any] = Field(default_factory=dict)

class TransitionCreate(TransitionBase):
    pass

class TransitionResponse(TransitionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CameraPathBase(BaseModel):
    type: str = Field(..., max_length=100)
    start_zoom: float = 1.0
    end_zoom: float = 1.0
    start_x: float = 0.0
    start_y: float = 0.0
    end_x: float = 0.0
    end_y: float = 0.0
    duration_ms: int
    config: Dict[str, Any] = Field(default_factory=dict)

class CameraPathCreate(CameraPathBase):
    pass

class CameraPathResponse(CameraPathBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class SceneMetadataBase(BaseModel):
    emotion: Optional[str] = Field(None, max_length=100)
    intensity: float = 0.0
    visual_complexity: float = 0.0
    dialogue_density: float = 0.0
    is_battle: bool = False
    is_flashback: bool = False
    config: Dict[str, Any] = Field(default_factory=dict)

class SceneMetadataCreate(SceneMetadataBase):
    pass

class SceneMetadataResponse(SceneMetadataBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TimelinePanelBase(BaseModel):
    scene_id: int
    panel_id: Optional[int] = None
    sequence_number: int
    start_time_ms: int
    end_time_ms: int
    duration_ms: int
    importance_score: float = 0.0
    camera_path_id: Optional[int] = None

class TimelinePanelCreate(TimelinePanelBase):
    pass

class TimelinePanelResponse(TimelinePanelBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class SynchronizationBase(BaseModel):
    scene_id: int
    audio_segment_id: Optional[int] = None
    narration_id: Optional[int] = None
    start_time_ms: int
    end_time_ms: int
    sync_accuracy: float = 1.0

class SynchronizationCreate(SynchronizationBase):
    pass

class SynchronizationResponse(SynchronizationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TimelineSceneBase(BaseModel):
    timeline_id: int
    sequence_number: int
    start_time_ms: int
    end_time_ms: int
    duration_ms: int
    page_id: Optional[int] = None
    transition_id: Optional[int] = None
    metadata_id: Optional[int] = None

class TimelineSceneCreate(TimelineSceneBase):
    pass

class TimelineSceneResponse(TimelineSceneBase):
    id: int
    created_at: datetime
    updated_at: datetime
    panels: List[TimelinePanelResponse] = Field(default_factory=list)
    synchronizations: List[SynchronizationResponse] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)

class TimelineBase(BaseModel):
    project_id: int
    status: str = Field(default="draft", max_length=50)
    duration_ms: int = 0
    settings: Dict[str, Any] = Field(default_factory=dict)

class TimelineCreate(TimelineBase):
    pass

class TimelineResponse(TimelineBase):
    id: int
    created_at: datetime
    updated_at: datetime
    scenes: List[TimelineSceneResponse] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)

class TimelineGenerateRequest(BaseModel):
    project_id: int
    part_id: Optional[int] = None
    chapter_id: Optional[int] = None
    settings: Optional[Dict[str, Any]] = None

class TimelineRebuildRequest(BaseModel):
    timeline_id: int
    rebuild_scenes: Optional[List[int]] = None
    settings: Optional[Dict[str, Any]] = None
