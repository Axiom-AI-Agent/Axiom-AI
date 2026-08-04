from sqlalchemy import (
    Column,
    String,
    DateTime,
    Boolean,
    Enum,
    Float,
    ForeignKey,
    Index,
    UniqueConstraint,
    JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from app.database.session import Base
from app.models.enums import MessageRole


class MemProcedure(Base):
    """
    Institution-level procedural memory.

    Stores onboarding workflows, payment processes, registration steps,
    and other institutional procedures. Each procedure has an embedding
    vector for semantic similarity search.
    """

    __tablename__ = "mem_procedures"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "name",
            name="uq_mem_procedures_tenant_name",
        ),
    )

    # Primary Key
    id = Column(String, primary_key=True)

    # Foreign Key
    tenant_id = Column(
        String,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Procedure Details
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    steps = Column(JSON, nullable=False, server_default="[]")

    # Vector Embedding (pgvector)
    embedding = Column(Vector(1536), nullable=True)

    # Status
    active = Column(Boolean, nullable=False, server_default="true")

    # Timestamp
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    tenant = relationship("Tenant", back_populates="mem_procedures")

    def __repr__(self):
        return (
            f"<MemProcedure("
            f"id='{self.id}', "
            f"name='{self.name}', "
            f"tenant='{self.tenant_id}')>"
        )


class MemFact(Base):
    """
    Long-term semantic memory for a specific student.

    Stores distilled facts extracted from conversations, such as
    language preferences, parent preferences, study goals, and
    other persistent student attributes. Each fact has an embedding
    vector for semantic similarity search.
    """

    __tablename__ = "mem_facts"

    __table_args__ = (
        Index("idx_mem_facts_tenant_user", "tenant_id", "user_id"),
    )

    # Primary Key
    id = Column(String, primary_key=True)

    # Foreign Keys
    tenant_id = Column(
        String,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )

    user_id = Column(
        String,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Fact Details
    text = Column(String, nullable=False)

    # Vector Embedding (pgvector)
    embedding = Column(Vector(1536), nullable=True)

    # Relevance Score
    score = Column(Float, nullable=False, server_default="0")

    # Tags for categorization
    tags = Column(JSON, nullable=False, server_default="[]")

    # Timestamp
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    tenant = relationship("Tenant", back_populates="mem_facts")
    student = relationship("Student", back_populates="mem_facts")

    def __repr__(self):
        return (
            f"<MemFact("
            f"id='{self.id}', "
            f"user='{self.user_id}', "
            f"text='{self.text[:30]}...')>"
        )


class MemEpisode(Base):
    """
    Conversation summaries (episodic memory).

    Each episode represents one summarized conversation session.
    Stores the summary text, summary embedding for semantic search,
    and the full turn history as JSONB.
    """

    __tablename__ = "mem_episodes"

    __table_args__ = (
        Index("idx_mem_episodes_session", "tenant_id", "session_id"),
    )

    # Primary Key
    id = Column(String, primary_key=True)

    # Foreign Keys
    tenant_id = Column(
        String,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )

    user_id = Column(
        String,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Episode Details
    session_id = Column(String, nullable=False)
    summary = Column(String, nullable=True)

    # Summary Embedding (pgvector)
    summary_embedding = Column(Vector(1536), nullable=True)

    # Full turn history
    turns = Column(JSON, nullable=False, server_default="[]")

    # Timestamp
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    tenant = relationship("Tenant", back_populates="mem_episodes")
    student = relationship("Student", back_populates="mem_episodes")

    def __repr__(self):
        return (
            f"<MemEpisode("
            f"id='{self.id}', "
            f"session='{self.session_id}', "
            f"user='{self.user_id}')>"
        )


class STTurn(Base):
    """
    Short-term conversational memory.

    Stores every conversation turn as a ring buffer with TTL-based cleanup.
    This table does NOT use embeddings — it is for recent context only.
    """

    __tablename__ = "st_turns"

    __table_args__ = (
        Index("idx_st_turns_session", "tenant_id", "session_id", "created_at"),
        Index("idx_st_turns_user", "tenant_id", "user_id", "created_at"),
    )

    # Primary Key
    id = Column(String, primary_key=True)

    # Foreign Keys
    tenant_id = Column(
        String,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )

    user_id = Column(
        String,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Turn Details
    session_id = Column(String, nullable=False)
    role = Column(
        Enum(MessageRole, name="message_role"),
        nullable=False,
    )
    content = Column(String, nullable=False)

    # Timestamp
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    tenant = relationship("Tenant", back_populates="st_turns")
    student = relationship("Student", back_populates="st_turns")

    def __repr__(self):
        return (
            f"<STTurn("
            f"id='{self.id}', "
            f"session='{self.session_id}', "
            f"role='{self.role}')>"
        )
