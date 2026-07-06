from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class TimestampSchema(BaseModel):
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StoryCharacterBase(BaseModel):
    name: str
    aliases: Optional[List[str]] = Field(default_factory=list)
    nicknames: Optional[List[str]] = Field(default_factory=list)
    age: Optional[str] = None
    gender: Optional[str] = None
    role: Optional[str] = None
    occupation: Optional[str] = None
    species: Optional[str] = None
    affiliation: Optional[str] = None
    current_status: str = "Alive"
    personality: Optional[str] = None
    appearance: Optional[str] = None
    strength: Optional[str] = None
    weakness: Optional[str] = None
    confidence: float = 1.0


class StoryCharacterCreate(StoryCharacterBase):
    pass


class StoryCharacterRead(StoryCharacterBase, TimestampSchema):
    id: int
    memory_history: Optional[List[Dict[str, Any]]] = None


class StoryEventBase(BaseModel):
    chapter_id: int
    page_id: Optional[int] = None
    panel_id: Optional[int] = None
    event_type: str
    importance: int = 50
    description: Optional[str] = None
    timestamp_val: Optional[str] = None
    confidence: float = 1.0


class StoryEventCreate(StoryEventBase):
    pass


class StoryEventRead(StoryEventBase, TimestampSchema):
    id: int


class StoryRelationshipBase(BaseModel):
    source_character_id: int
    target_character_id: int
    relationship_type: str
    trust: int = 50
    hostility: int = 0
    history: Optional[str] = None
    recent_events: Optional[str] = None
    strength: int = 50


class StoryRelationshipCreate(StoryRelationshipBase):
    pass


class StoryRelationshipRead(StoryRelationshipBase, TimestampSchema):
    id: int


class StoryLocationBase(BaseModel):
    name: str
    location_type: str
    coordinates: Optional[str] = None
    first_appearance_id: Optional[int] = None
    last_appearance_id: Optional[int] = None
    importance: int = 50


class StoryLocationCreate(StoryLocationBase):
    pass


class StoryLocationRead(StoryLocationBase, TimestampSchema):
    id: int


class StoryOrganizationBase(BaseModel):
    name: str
    org_type: str
    description: Optional[str] = None


class StoryOrganizationCreate(StoryOrganizationBase):
    pass


class StoryOrganizationRead(StoryOrganizationBase, TimestampSchema):
    id: int


class StoryAbilityBase(BaseModel):
    name: str
    power_system: Optional[str] = None
    description: Optional[str] = None
    restrictions: Optional[str] = None
    weaknesses: Optional[str] = None


class StoryAbilityCreate(StoryAbilityBase):
    pass


class StoryAbilityRead(StoryAbilityBase, TimestampSchema):
    id: int


class StoryItemBase(BaseModel):
    name: str
    item_type: str
    description: Optional[str] = None


class StoryItemCreate(StoryItemBase):
    pass


class StoryItemRead(StoryItemBase, TimestampSchema):
    id: int
    ownership_history: Optional[List[Dict[str, Any]]] = None


class StoryGoalBase(BaseModel):
    character_id: int
    description: str
    status: str


class StoryGoalCreate(StoryGoalBase):
    pass


class StoryGoalRead(StoryGoalBase, TimestampSchema):
    id: int


class StoryConflictBase(BaseModel):
    conflict_type: str
    description: str
    entities_involved: Optional[List[str]] = Field(default_factory=list)


class StoryConflictCreate(StoryConflictBase):
    pass


class StoryConflictRead(StoryConflictBase, TimestampSchema):
    id: int


class StoryTimelineBase(BaseModel):
    event_id: int
    chronological_order: int
    timeline_type: str = "main"


class StoryTimelineCreate(StoryTimelineBase):
    pass


class StoryTimelineRead(StoryTimelineBase, TimestampSchema):
    id: int


class StoryGraphEdgeBase(BaseModel):
    source_type: str
    source_id: int
    target_type: str
    target_id: int
    relation_type: str


class StoryGraphEdgeCreate(StoryGraphEdgeBase):
    pass


class StoryGraphEdgeRead(StoryGraphEdgeBase, TimestampSchema):
    id: int


class KnowledgeBaseEntryBase(BaseModel):
    category: str
    key: str
    value: str
    version: int = 1


class KnowledgeBaseEntryCreate(KnowledgeBaseEntryBase):
    pass


class KnowledgeBaseEntryRead(KnowledgeBaseEntryBase, TimestampSchema):
    id: int
