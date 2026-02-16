from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import joinedload

from app.models import Attribute, GarmentAttribute, AttributeIncompatibility
from app.schemas.attribute import AttributeCreate, IncompatibilityCreate
from app.exceptions import NotFoundError, IncompatibleAttributeError


async def get_attributes(db: AsyncSession, category: str | None = None) -> list[Attribute]:
    stmt = select(Attribute)
    if category:
        stmt = stmt.where(Attribute.category == category)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_attribute(db: AsyncSession, data: AttributeCreate) -> Attribute:
    attribute = Attribute(name=data.name, category=data.category)
    db.add(attribute)
    await db.commit()
    await db.refresh(attribute)
    return attribute


async def get_incompatibilities(db: AsyncSession) -> list[AttributeIncompatibility]:
    result = await db.execute(
        select(AttributeIncompatibility).options(
            joinedload(AttributeIncompatibility.attribute_1),
            joinedload(AttributeIncompatibility.attribute_2),
        )
    )
    return list(result.scalars().unique().all())


async def create_incompatibility(
    db: AsyncSession, data: IncompatibilityCreate
) -> AttributeIncompatibility:
    # Validate both attributes exist
    for attr_id in (data.attribute_id_1, data.attribute_id_2):
        result = await db.execute(select(Attribute).where(Attribute.id == attr_id))
        if not result.scalar_one_or_none():
            raise NotFoundError("Attribute", attr_id)

    # Enforce ordered pair
    low, high = min(data.attribute_id_1, data.attribute_id_2), max(
        data.attribute_id_1, data.attribute_id_2
    )
    rule = AttributeIncompatibility(attribute_id_1=low, attribute_id_2=high)
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


async def check_attribute_compatibility(
    db: AsyncSession, garment_id: int, attribute_id: int
) -> None:
    # Get existing attribute IDs on the garment
    result = await db.execute(
        select(GarmentAttribute.attribute_id).where(
            GarmentAttribute.garment_id == garment_id
        )
    )
    existing_ids = list(result.scalars().all())

    if not existing_ids:
        return

    # Build conditions for incompatibility check
    conditions = []
    for existing_id in existing_ids:
        low, high = min(attribute_id, existing_id), max(attribute_id, existing_id)
        if low == high:
            continue
        conditions.append(
            and_(
                AttributeIncompatibility.attribute_id_1 == low,
                AttributeIncompatibility.attribute_id_2 == high,
            )
        )

    if not conditions:
        return

    result = await db.execute(
        select(AttributeIncompatibility)
        .options(
            joinedload(AttributeIncompatibility.attribute_1),
            joinedload(AttributeIncompatibility.attribute_2),
        )
        .where(or_(*conditions))
    )
    conflicts = list(result.scalars().unique().all())

    if conflicts:
        new_attr_result = await db.execute(
            select(Attribute).where(Attribute.id == attribute_id)
        )
        new_attr = new_attr_result.scalar_one()
        conflicting_names = []
        for c in conflicts:
            if c.attribute_id_1 == attribute_id:
                conflicting_names.append(c.attribute_2.name)
            else:
                conflicting_names.append(c.attribute_1.name)
        raise IncompatibleAttributeError(new_attr.name, conflicting_names)
