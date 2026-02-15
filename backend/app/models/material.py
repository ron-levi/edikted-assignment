from __future__ import annotations

from sqlalchemy import String, ForeignKey, Numeric, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Material(Base):
    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    garment_materials: Mapped[list["GarmentMaterial"]] = relationship(
        back_populates="material",
    )


class GarmentMaterial(Base):
    __tablename__ = "garment_materials"

    id: Mapped[int] = mapped_column(primary_key=True)
    garment_id: Mapped[int] = mapped_column(
        ForeignKey("garments.id", ondelete="CASCADE"), nullable=False
    )
    material_id: Mapped[int] = mapped_column(
        ForeignKey("materials.id"), nullable=False
    )
    percentage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)

    garment: Mapped["Garment"] = relationship(back_populates="garment_materials")
    material: Mapped["Material"] = relationship(back_populates="garment_materials")

    __table_args__ = (
        UniqueConstraint("garment_id", "material_id", name="uq_garment_material"),
        CheckConstraint(
            "percentage > 0 AND percentage <= 100",
            name="ck_garment_material_percentage",
        ),
    )
