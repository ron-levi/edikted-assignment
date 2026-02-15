from __future__ import annotations

import enum

from sqlalchemy import String, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AttributeCategory(str, enum.Enum):
    SLEEVE_TYPE = "SLEEVE_TYPE"
    NECKLINE = "NECKLINE"
    GARMENT_CATEGORY = "GARMENT_CATEGORY"
    FIT = "FIT"
    FEATURE = "FEATURE"


class Attribute(Base):
    __tablename__ = "attributes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False)

    garment_attributes: Mapped[list["GarmentAttribute"]] = relationship(
        back_populates="attribute",
    )

    __table_args__ = (
        UniqueConstraint("name", "category", name="uq_attribute_name_category"),
    )


class GarmentAttribute(Base):
    __tablename__ = "garment_attributes"

    id: Mapped[int] = mapped_column(primary_key=True)
    garment_id: Mapped[int] = mapped_column(
        ForeignKey("garments.id", ondelete="CASCADE"), nullable=False
    )
    attribute_id: Mapped[int] = mapped_column(
        ForeignKey("attributes.id"), nullable=False
    )

    garment: Mapped["Garment"] = relationship(back_populates="garment_attributes")
    attribute: Mapped["Attribute"] = relationship(back_populates="garment_attributes")

    __table_args__ = (
        UniqueConstraint("garment_id", "attribute_id", name="uq_garment_attribute"),
    )


class AttributeIncompatibility(Base):
    __tablename__ = "attribute_incompatibilities"

    id: Mapped[int] = mapped_column(primary_key=True)
    attribute_id_1: Mapped[int] = mapped_column(
        ForeignKey("attributes.id"), nullable=False
    )
    attribute_id_2: Mapped[int] = mapped_column(
        ForeignKey("attributes.id"), nullable=False
    )

    attribute_1: Mapped["Attribute"] = relationship(
        foreign_keys=[attribute_id_1],
    )
    attribute_2: Mapped["Attribute"] = relationship(
        foreign_keys=[attribute_id_2],
    )

    __table_args__ = (
        CheckConstraint(
            "attribute_id_1 < attribute_id_2",
            name="ck_incompatibility_ordered_pair",
        ),
        UniqueConstraint(
            "attribute_id_1", "attribute_id_2", name="uq_incompatibility_pair"
        ),
    )
