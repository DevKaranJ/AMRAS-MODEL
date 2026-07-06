from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class MemoryStore(Base, TimestampMixin):
    __tablename__ = "memory_store"
    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(50), index=True)  # character, event, location, etc.
    entity_id: Mapped[str] = mapped_column(String(100), index=True, unique=True)
    memory_type: Mapped[str] = mapped_column(String(50), index=True)  # semantic, episodic, character, etc.
    data: Mapped[Dict[str, Any]] = mapped_column(JSON)
    version: Mapped[int] = mapped_column(Integer, default=1)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)

    versions: Mapped[list["MemoryVersion"]] = relationship(
        "MemoryVersion", back_populates="memory_store", cascade="all, delete-orphan"
    )


class MemoryVersion(Base, TimestampMixin):
    __tablename__ = "memory_versions"
    id: Mapped[int] = mapped_column(primary_key=True)
    memory_id: Mapped[int] = mapped_column(ForeignKey("memory_store.id", ondelete="CASCADE"), index=True)
    version: Mapped[int] = mapped_column(Integer)
    data: Mapped[Dict[str, Any]] = mapped_column(JSON)
    change_reason: Mapped[Optional[str]] = mapped_column(Text)

    memory_store: Mapped["MemoryStore"] = relationship("MemoryStore", back_populates="versions")


class CharacterMemory(Base, TimestampMixin):
    __tablename__ = "character_memories"
    id: Mapped[int] = mapped_column(primary_key=True)
    memory_id: Mapped[int] = mapped_column(ForeignKey("memory_store.id", ondelete="CASCADE"), index=True, unique=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    aliases: Mapped[Optional[List[str]]] = mapped_column(JSON)
    current_status: Mapped[Optional[str]] = mapped_column(String(100))
    first_appearance_chapter: Mapped[Optional[int]] = mapped_column(Integer)
    last_appearance_chapter: Mapped[Optional[int]] = mapped_column(Integer)


class RelationshipMemory(Base, TimestampMixin):
    __tablename__ = "relationship_memories"
    id: Mapped[int] = mapped_column(primary_key=True)
    memory_id: Mapped[int] = mapped_column(ForeignKey("memory_store.id", ondelete="CASCADE"), index=True, unique=True)
    source_entity_id: Mapped[str] = mapped_column(String(100), index=True)
    target_entity_id: Mapped[str] = mapped_column(String(100), index=True)
    relationship_type: Mapped[str] = mapped_column(String(100))  # e.g. friend, enemy, master
    trust_score: Mapped[Optional[float]] = mapped_column(Float)
    conflict_score: Mapped[Optional[float]] = mapped_column(Float)


class EventMemory(Base, TimestampMixin):
    __tablename__ = "event_memories"
    id: Mapped[int] = mapped_column(primary_key=True)
    memory_id: Mapped[int] = mapped_column(ForeignKey("memory_store.id", ondelete="CASCADE"), index=True, unique=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    event_type: Mapped[str] = mapped_column(String(100))
    importance: Mapped[int] = mapped_column(Integer, default=1)
    chapter_id: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    outcome: Mapped[Optional[str]] = mapped_column(Text)


class WorldMemory(Base, TimestampMixin):
    __tablename__ = "world_memories"
    id: Mapped[int] = mapped_column(primary_key=True)
    memory_id: Mapped[int] = mapped_column(ForeignKey("memory_store.id", ondelete="CASCADE"), index=True, unique=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    location_type: Mapped[str] = mapped_column(String(100))  # country, city, organization, etc.
    description: Mapped[Optional[str]] = mapped_column(Text)


class ObjectMemory(Base, TimestampMixin):
    __tablename__ = "object_memories"
    id: Mapped[int] = mapped_column(primary_key=True)
    memory_id: Mapped[int] = mapped_column(ForeignKey("memory_store.id", ondelete="CASCADE"), index=True, unique=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    object_type: Mapped[str] = mapped_column(String(100))  # weapon, artifact, etc.
    owner_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)


class AbilityMemory(Base, TimestampMixin):
    __tablename__ = "ability_memories"
    id: Mapped[int] = mapped_column(primary_key=True)
    memory_id: Mapped[int] = mapped_column(ForeignKey("memory_store.id", ondelete="CASCADE"), index=True, unique=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    ability_type: Mapped[str] = mapped_column(String(100))  # skill, magic, etc.
    owner_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)


class Embedding(Base, TimestampMixin):
    __tablename__ = "embeddings"
    id: Mapped[int] = mapped_column(primary_key=True)
    entity_id: Mapped[str] = mapped_column(String(100), index=True)
    entity_type: Mapped[str] = mapped_column(String(50))
    # We use a JSON column to store embeddings for simplicity in SQLite/Postgres without pgvector for now
    # In a real production environment, this would likely be pgvector's VECTOR type
    vector: Mapped[List[float]] = mapped_column(JSON)


class KnowledgeGraphNode(Base, TimestampMixin):
    __tablename__ = "knowledge_graph_nodes"
    id: Mapped[int] = mapped_column(primary_key=True)
    node_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    label: Mapped[str] = mapped_column(String(100))  # Character, Location, Event
    properties: Mapped[Dict[str, Any]] = mapped_column(JSON)


class KnowledgeGraphEdge(Base, TimestampMixin):
    __tablename__ = "knowledge_graph_edges"
    id: Mapped[int] = mapped_column(primary_key=True)
    source_node_id: Mapped[str] = mapped_column(String(100), index=True)
    target_node_id: Mapped[str] = mapped_column(String(100), index=True)
    relationship: Mapped[str] = mapped_column(String(100))  # Knows, Visited, Defeated
    properties: Mapped[Dict[str, Any]] = mapped_column(JSON)


class MemoryAudit(Base, TimestampMixin):
    __tablename__ = "memory_audits"
    id: Mapped[int] = mapped_column(primary_key=True)
    action: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[str] = mapped_column(String(100), index=True)
    details: Mapped[Dict[str, Any]] = mapped_column(JSON)


class ConflictReport(Base, TimestampMixin):
    __tablename__ = "conflict_reports"
    id: Mapped[int] = mapped_column(primary_key=True)
    entity_id: Mapped[str] = mapped_column(String(100), index=True)
    conflict_type: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text)


class RetrievalIndex(Base, TimestampMixin):
    __tablename__ = "retrieval_indices"
    id: Mapped[int] = mapped_column(primary_key=True)
    keyword: Mapped[str] = mapped_column(String(255), index=True)
    entity_id: Mapped[str] = mapped_column(String(100), index=True)
    score: Mapped[float] = mapped_column(Float, default=1.0)
