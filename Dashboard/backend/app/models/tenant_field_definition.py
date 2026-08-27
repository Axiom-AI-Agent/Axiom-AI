from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.session import Base


class TenantFieldDefinition(Base):
    """Per-tenant custom onboarding field (beyond name/phone/class/consent)."""

    __tablename__ = "tenant_field_definition"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "field_key",
            name="uq_tenant_field_definition_tenant_key",
        ),
        CheckConstraint(
            "field_type IN ('text', 'number', 'select', 'boolean', 'date')",
            name="tenant_field_definition_type_check",
        ),
        Index(
            "idx_tenant_field_definition_tenant_sort",
            "tenant_id",
            "active",
            "sort_order",
        ),
    )

    id = Column(
        String,
        primary_key=True,
    )

    tenant_id = Column(
        String,
        ForeignKey(
            "tenants.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    field_key = Column(
        String,
        nullable=False,
    )

    label = Column(
        String,
        nullable=False,
    )

    field_type = Column(
        String,
        nullable=False,
    )

    options = Column(
        JSONB,
        nullable=True,
    )

    required = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    sort_order = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    tenant = relationship(
        "Tenant",
        back_populates="field_definitions",
    )

    def __repr__(self):
        return (
            f"<TenantFieldDefinition("
            f"id='{self.id}', "
            f"tenant='{self.tenant_id}', "
            f"field_key='{self.field_key}')>"
        )
