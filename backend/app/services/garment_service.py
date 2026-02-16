from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload

from app.models import (
    Garment,
    Material,
    GarmentMaterial,
    Attribute,
    GarmentAttribute,
    GarmentSupplier,
)
from app.schemas.garment import GarmentCreate, GarmentUpdate, GarmentVariationCreate
from app.schemas.material import GarmentMaterialCreate
from app.schemas.attribute import GarmentAttributeCreate
from app.exceptions import NotFoundError, DeletionProtectedError, ProductionProtectedError, ValidationError
from app.services.lifecycle import validate_garment_transition
from app.services.attribute_service import check_attribute_compatibility


def _ensure_not_production(garment: Garment, operation: str) -> None:
    if garment.lifecycle_stage == "PRODUCTION":
        raise ProductionProtectedError(garment.name, operation)


async def get_garments(
    db: AsyncSession, stage: str | None = None, search: str | None = None
) -> list[Garment]:
    stmt = select(Garment)
    if stage:
        stmt = stmt.where(Garment.lifecycle_stage == stage)
    if search:
        stmt = stmt.where(Garment.name.ilike(f"%{search}%"))
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_garment(db: AsyncSession, garment_id: int) -> Garment:
    result = await db.execute(
        select(Garment)
        .options(
            selectinload(Garment.garment_materials).joinedload(GarmentMaterial.material),
            selectinload(Garment.garment_attributes).joinedload(GarmentAttribute.attribute),
            selectinload(Garment.garment_suppliers).joinedload(GarmentSupplier.supplier),
            selectinload(Garment.variations),
        )
        .where(Garment.id == garment_id)
    )
    garment = result.scalar_one_or_none()
    if not garment:
        raise NotFoundError("Garment", garment_id)
    return garment


async def create_garment(db: AsyncSession, data: GarmentCreate) -> Garment:
    garment = Garment(name=data.name, description=data.description)
    db.add(garment)
    await db.commit()
    await db.refresh(garment)
    return garment


async def update_garment(
    db: AsyncSession, garment_id: int, data: GarmentUpdate
) -> Garment:
    result = await db.execute(select(Garment).where(Garment.id == garment_id))
    garment = result.scalar_one_or_none()
    if not garment:
        raise NotFoundError("Garment", garment_id)

    _ensure_not_production(garment, "update")

    if data.name is not None:
        garment.name = data.name
    if data.description is not None:
        garment.description = data.description

    await db.commit()
    await db.refresh(garment)
    return garment


async def delete_garment(db: AsyncSession, garment_id: int) -> None:
    result = await db.execute(select(Garment).where(Garment.id == garment_id))
    garment = result.scalar_one_or_none()
    if not garment:
        raise NotFoundError("Garment", garment_id)

    if garment.lifecycle_stage == "PRODUCTION":
        raise DeletionProtectedError(garment.name)

    await db.delete(garment)
    await db.commit()


async def transition_garment(
    db: AsyncSession, garment_id: int, target_stage: str
) -> Garment:
    result = await db.execute(select(Garment).where(Garment.id == garment_id))
    garment = result.scalar_one_or_none()
    if not garment:
        raise NotFoundError("Garment", garment_id)

    validate_garment_transition(garment.lifecycle_stage, target_stage)
    garment.lifecycle_stage = target_stage
    await db.commit()
    await db.refresh(garment)
    return garment


async def create_variation(
    db: AsyncSession, parent_id: int, data: GarmentVariationCreate
) -> Garment:
    result = await db.execute(select(Garment).where(Garment.id == parent_id))
    parent = result.scalar_one_or_none()
    if not parent:
        raise NotFoundError("Garment", parent_id)

    variation = Garment(
        name=data.name,
        description=data.description,
        parent_garment_id=parent_id,
    )
    db.add(variation)
    await db.commit()
    await db.refresh(variation)
    return variation


async def add_material(
    db: AsyncSession, garment_id: int, data: GarmentMaterialCreate
) -> GarmentMaterial:
    # Verify garment exists
    result = await db.execute(select(Garment).where(Garment.id == garment_id))
    garment = result.scalar_one_or_none()
    if not garment:
        raise NotFoundError("Garment", garment_id)
    _ensure_not_production(garment, "add material")

    # Verify material exists
    result = await db.execute(select(Material).where(Material.id == data.material_id))
    if not result.scalar_one_or_none():
        raise NotFoundError("Material", data.material_id)

    # Check total percentage
    result = await db.execute(
        select(func.coalesce(func.sum(GarmentMaterial.percentage), 0)).where(
            GarmentMaterial.garment_id == garment_id
        )
    )
    current_total = float(result.scalar_one())
    if current_total + data.percentage > 100:
        raise ValidationError(
            f"Total material percentage would exceed 100% "
            f"(current: {current_total}%, adding: {data.percentage}%)"
        )

    gm = GarmentMaterial(
        garment_id=garment_id,
        material_id=data.material_id,
        percentage=data.percentage,
    )
    db.add(gm)
    await db.commit()
    await db.refresh(gm)
    return gm


async def remove_material(
    db: AsyncSession, garment_id: int, material_id: int
) -> None:
    # Verify garment exists and not in production
    result = await db.execute(select(Garment).where(Garment.id == garment_id))
    garment = result.scalar_one_or_none()
    if not garment:
        raise NotFoundError("Garment", garment_id)
    _ensure_not_production(garment, "remove material")

    result = await db.execute(
        select(GarmentMaterial).where(
            GarmentMaterial.garment_id == garment_id,
            GarmentMaterial.material_id == material_id,
        )
    )
    gm = result.scalar_one_or_none()
    if not gm:
        raise NotFoundError("GarmentMaterial", 0)

    await db.delete(gm)
    await db.commit()


async def add_attribute(
    db: AsyncSession, garment_id: int, data: GarmentAttributeCreate
) -> GarmentAttribute:
    # Verify garment exists
    result = await db.execute(select(Garment).where(Garment.id == garment_id))
    garment = result.scalar_one_or_none()
    if not garment:
        raise NotFoundError("Garment", garment_id)
    _ensure_not_production(garment, "add attribute")

    # Verify attribute exists
    result = await db.execute(
        select(Attribute).where(Attribute.id == data.attribute_id)
    )
    if not result.scalar_one_or_none():
        raise NotFoundError("Attribute", data.attribute_id)

    # Check compatibility
    await check_attribute_compatibility(db, garment_id, data.attribute_id)

    ga = GarmentAttribute(garment_id=garment_id, attribute_id=data.attribute_id)
    db.add(ga)
    await db.commit()
    await db.refresh(ga)
    return ga


async def remove_attribute(
    db: AsyncSession, garment_id: int, attribute_id: int
) -> None:
    # Verify garment exists and not in production
    result = await db.execute(select(Garment).where(Garment.id == garment_id))
    garment = result.scalar_one_or_none()
    if not garment:
        raise NotFoundError("Garment", garment_id)
    _ensure_not_production(garment, "remove attribute")

    result = await db.execute(
        select(GarmentAttribute).where(
            GarmentAttribute.garment_id == garment_id,
            GarmentAttribute.attribute_id == attribute_id,
        )
    )
    ga = result.scalar_one_or_none()
    if not ga:
        raise NotFoundError("GarmentAttribute", 0)

    await db.delete(ga)
    await db.commit()
