from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# Base Models
class MemoryBase(BaseModel):
    entity_id: str
    entity_type: str
    memory_type: str
    data: Dict[str, Any]
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class MemoryStoreCreate(MemoryBase):
    pass


class MemoryStoreRead(MemoryBase):
    id: int
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Character Memory
class CharacterMemoryBase(BaseModel):
    name: str
    aliases: Optional[List[str]] = None
    current_status: Optional[str] = None
    first_appearance_chapter: Optional[int] = None
    last_appearance_chapter: Optional[int] = None


class CharacterMemoryCreate(CharacterMemoryBase):
    pass


class CharacterMemoryRead(CharacterMemoryBase):
    id: int
    memory_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Relationship Memory
class RelationshipMemoryBase(BaseModel):
    source_entity_id: str
    target_entity_id: str
    relationship_type: str
    trust_score: Optional[float] = None
    conflict_score: Optional[float] = None


class RelationshipMemoryCreate(RelationshipMemoryBase):
    pass


class RelationshipMemoryRead(RelationshipMemoryBase):
    id: int
    memory_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Event Memory
class EventMemoryBase(BaseModel):
    name: str
    event_type: str
    importance: int = Field(default=1, ge=1, le=10)
    chapter_id: Optional[int] = None
    outcome: Optional[str] = None


class EventMemoryCreate(EventMemoryBase):
    pass


class EventMemoryRead(EventMemoryBase):
    id: int
    memory_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# World Memory
class WorldMemoryBase(BaseModel):
    name: str
    location_type: str
    description: Optional[str] = None


class WorldMemoryCreate(WorldMemoryBase):
    pass


class WorldMemoryRead(WorldMemoryBase):
    id: int
    memory_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Object Memory
class ObjectMemoryBase(BaseModel):
    name: str
    object_type: str
    owner_id: Optional[str] = None


class ObjectMemoryCreate(ObjectMemoryBase):
    pass


class ObjectMemoryRead(ObjectMemoryBase):
    id: int
    memory_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Ability Memory
class AbilityMemoryBase(BaseModel):
    name: str
    ability_type: str
    owner_id: Optional[str] = None


class AbilityMemoryCreate(AbilityMemoryBase):
    pass


class AbilityMemoryRead(AbilityMemoryBase):
    id: int
    memory_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Conflict Report
class ConflictReportBase(BaseModel):
    entity_id: str
    conflict_type: str
    description: str


class ConflictReportCreate(ConflictReportBase):
    pass


class ConflictReportRead(ConflictReportBase):
    id: int
    resolved: bool
    resolution_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Memory Search Request
class MemorySearchRequest(BaseModel):
    query: str
    entity_type: Optional[str] = None
    memory_type: Optional[str] = None
    limit: int = 10
