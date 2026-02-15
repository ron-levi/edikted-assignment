from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class LifecycleStage(str, enum.Enum):
    CONCEPT = "CONCEPT"
    DESIGN = "DESIGN"
    DEVELOPMENT = "DEVELOPMENT"
    SAMPLING = "SAMPLING"
    PRODUCTION = "PRODUCTION"


class Garment(Base):
    __tablename__ = "garments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    lifecycle_stage: Mapped[str] = mapped_column(
        String(20), nullable=False, default=LifecycleStage.CONCEPT.value
    )
    parent_garment_id: Mapped[int | None] = mapped_column(
        ForeignKey("garments.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Self-referential relationship for design variations
    parent: Mapped[Garment | None] = relationship(
        "Garment",
        back_populates="variations",
        remote_side="Garment.id",
    )
    variations: Mapped[list[Garment]] = relationship(
        "Garment",
        back_populates="parent",
    )

    # Related collections
    garment_materials: Mapped[list["GarmentMaterial"]] = relationship(
        back_populates="garment",
        cascade="all, delete-orphan",
    )
    garment_attributes: Mapped[list["GarmentAttribute"]] = relationship(
        back_populates="garment",
        cascade="all, delete-orphan",
    )
    garment_suppliers: Mapped[list["GarmentSupplier"]] = relationship(
        back_populates="garment",
        cascade="all, delete-orphan",
    )
