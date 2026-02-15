from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import String, Text, ForeignKey, DateTime, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SupplierStatus(str, enum.Enum):
    OFFERED = "OFFERED"
    SAMPLING = "SAMPLING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    IN_PRODUCTION = "IN_PRODUCTION"
    IN_STORE = "IN_STORE"


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    contact_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    garment_suppliers: Mapped[list["GarmentSupplier"]] = relationship(
        back_populates="supplier",
    )


class GarmentSupplier(Base):
    __tablename__ = "garment_suppliers"

    id: Mapped[int] = mapped_column(primary_key=True)
    garment_id: Mapped[int] = mapped_column(
        ForeignKey("garments.id", ondelete="CASCADE"), nullable=False
    )
    supplier_id: Mapped[int] = mapped_column(
        ForeignKey("suppliers.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=SupplierStatus.OFFERED.value
    )
    offer_price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    lead_time_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    garment: Mapped["Garment"] = relationship(back_populates="garment_suppliers")
    supplier: Mapped["Supplier"] = relationship(back_populates="garment_suppliers")
    sample_sets: Mapped[list["SampleSet"]] = relationship(
        back_populates="garment_supplier",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("garment_id", "supplier_id", name="uq_garment_supplier"),
    )
