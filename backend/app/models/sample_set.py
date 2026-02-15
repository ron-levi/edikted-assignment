from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SampleStatus(str, enum.Enum):
    PENDING = "PENDING"
    RECEIVED = "RECEIVED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class SampleSet(Base):
    __tablename__ = "sample_sets"

    id: Mapped[int] = mapped_column(primary_key=True)
    garment_supplier_id: Mapped[int] = mapped_column(
        ForeignKey("garment_suppliers.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=SampleStatus.PENDING.value
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    garment_supplier: Mapped["GarmentSupplier"] = relationship(
        back_populates="sample_sets",
    )
