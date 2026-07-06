from typing import Optional

from sqlalchemy import JSON, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class StoryCharacter(Base, TimestampMixin):
    __tablename__ = "story_characters"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    aliases: Mapped[Optional[list[str]]] = mapped_column(JSON, default=list)
    nicknames: Mapped[Optional[list[str]]] = mapped_column(JSON, default=list)
    age: Mapped[Optional[str]] = mapped_column(String(50))
    gender: Mapped[Optional[str]] = mapped_column(String(50))
    role: Mapped[Optional[str]] = mapped_column(String(100))
    occupation: Mapped[Optional[str]] = mapped_column(String(100))
    species: Mapped[Optional[str]] = mapped_column(String(100))
    affiliation: Mapped[Optional[str]] = mapped_column(String(255))
    current_status: Mapped[str] = mapped_column(String(50), default="Alive")  # Alive, Dead, Unknown, Missing
    personality: Mapped[Optional[str]] = mapped_column(Text)
    appearance: Mapped[Optional[str]] = mapped_column(Text)
    strength: Mapped[Optional[str]] = mapped_column(Text)
    weakness: Mapped[Optional[str]] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    memory_history: Mapped[Optional[list[dict]]] = mapped_column(
        JSON, default=list
    )  # To track character development across chapters


class StoryEvent(Base, TimestampMixin):
    __tablename__ = "story_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    chapter_id: Mapped[int] = mapped_column(Integer, index=True)  # Linking to chapter, page, panel logically
    page_id: Mapped[Optional[int]] = mapped_column(Integer)
    panel_id: Mapped[Optional[int]] = mapped_column(Integer)
    event_type: Mapped[str] = mapped_column(String(100), index=True)  # Battle, Introduction, Discovery, etc.
    importance: Mapped[int] = mapped_column(Integer, default=50)  # 0-100
    description: Mapped[Optional[str]] = mapped_column(Text)
    timestamp_val: Mapped[Optional[str]] = mapped_column(String(50))
    confidence: Mapped[float] = mapped_column(Float, default=1.0)


class StoryRelationship(Base, TimestampMixin):
    __tablename__ = "story_relationships"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_character_id: Mapped[int] = mapped_column(ForeignKey("story_characters.id", ondelete="CASCADE"), index=True)
    target_character_id: Mapped[int] = mapped_column(ForeignKey("story_characters.id", ondelete="CASCADE"), index=True)
    relationship_type: Mapped[str] = mapped_column(String(100))  # Friend, Enemy, Family, etc.
    trust: Mapped[int] = mapped_column(Integer, default=50)  # 0-100
    hostility: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    history: Mapped[Optional[str]] = mapped_column(Text)
    recent_events: Mapped[Optional[str]] = mapped_column(Text)
    strength: Mapped[int] = mapped_column(Integer, default=50)  # 0-100


class StoryLocation(Base, TimestampMixin):
    __tablename__ = "story_locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    location_type: Mapped[str] = mapped_column(String(100))  # Country, City, Building, etc.
    coordinates: Mapped[Optional[str]] = mapped_column(String(100))
    first_appearance_id: Mapped[Optional[int]] = mapped_column(Integer)
    last_appearance_id: Mapped[Optional[int]] = mapped_column(Integer)
    importance: Mapped[int] = mapped_column(Integer, default=50)  # 0-100


class StoryOrganization(Base, TimestampMixin):
    __tablename__ = "story_organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    org_type: Mapped[str] = mapped_column(String(100))  # Guild, School, Government, etc.
    description: Mapped[Optional[str]] = mapped_column(Text)


class StoryAbility(Base, TimestampMixin):
    __tablename__ = "story_abilities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    power_system: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    restrictions: Mapped[Optional[str]] = mapped_column(Text)
    weaknesses: Mapped[Optional[str]] = mapped_column(Text)


class StoryItem(Base, TimestampMixin):
    __tablename__ = "story_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    item_type: Mapped[str] = mapped_column(String(100))  # Weapon, Artifact, Treasure, etc.
    description: Mapped[Optional[str]] = mapped_column(Text)
    ownership_history: Mapped[Optional[list[dict]]] = mapped_column(JSON, default=list)


class StoryGoal(Base, TimestampMixin):
    __tablename__ = "story_goals"

    id: Mapped[int] = mapped_column(primary_key=True)
    character_id: Mapped[int] = mapped_column(ForeignKey("story_characters.id", ondelete="CASCADE"), index=True)
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50))  # Current, Completed, Failed, Future, Hidden


class StoryConflict(Base, TimestampMixin):
    __tablename__ = "story_conflicts"

    id: Mapped[int] = mapped_column(primary_key=True)
    conflict_type: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    entities_involved: Mapped[Optional[list[str]]] = mapped_column(JSON, default=list)


class StoryTimeline(Base, TimestampMixin):
    __tablename__ = "story_timelines"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("story_events.id", ondelete="CASCADE"), index=True)
    chronological_order: Mapped[int] = mapped_column(Integer)
    timeline_type: Mapped[str] = mapped_column(String(50), default="main")  # main, flashback, dream, future, parallel


class StoryGraphEdge(Base, TimestampMixin):
    __tablename__ = "story_graph_edges"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_type: Mapped[str] = mapped_column(String(50))  # character, location, item, event
    source_id: Mapped[int] = mapped_column(Integer, index=True)
    target_type: Mapped[str] = mapped_column(String(50))
    target_id: Mapped[int] = mapped_column(Integer, index=True)
    relation_type: Mapped[str] = mapped_column(String(100))  # visited, fought, used, etc.


class KnowledgeBaseEntry(Base, TimestampMixin):
    __tablename__ = "knowledge_base"

    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(String(100), index=True)  # world, magic, rules
    key: Mapped[str] = mapped_column(String(255), index=True)
    value: Mapped[str] = mapped_column(Text)
    version: Mapped[int] = mapped_column(Integer, default=1)
