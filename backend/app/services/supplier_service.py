from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.models import Supplier, GarmentSupplier, Garment, SampleSet
from app.schemas.supplier import SupplierCreate, SupplierUpdate, GarmentSupplierCreate
from app.schemas.sample_set import SampleSetCreate, SampleSetUpdate
from app.exceptions import NotFoundError, ProductionProtectedError
from app.services.lifecycle import validate_supplier_transition, validate_sample_transition


async def get_suppliers(db: AsyncSession) -> list[Supplier]:
    result = await db.execute(select(Supplier))
    return list(result.scalars().all())


async def get_supplier(db: AsyncSession, supplier_id: int) -> Supplier:
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise NotFoundError("Supplier", supplier_id)
    return supplier


async def create_supplier(db: AsyncSession, data: SupplierCreate) -> Supplier:
    supplier = Supplier(name=data.name, contact_info=data.contact_info)
    db.add(supplier)
    await db.commit()
    await db.refresh(supplier)
    return supplier


async def update_supplier(
    db: AsyncSession, supplier_id: int, data: SupplierUpdate
) -> Supplier:
    supplier = await get_supplier(db, supplier_id)

    if data.name is not None:
        supplier.name = data.name
    if data.contact_info is not None:
        supplier.contact_info = data.contact_info

    await db.commit()
    await db.refresh(supplier)
    return supplier


async def delete_supplier(db: AsyncSession, supplier_id: int) -> None:
    supplier = await get_supplier(db, supplier_id)
    await db.delete(supplier)
    await db.commit()


async def _get_garment_supplier(
    db: AsyncSession, garment_id: int, supplier_id: int
) -> GarmentSupplier:
    result = await db.execute(
        select(GarmentSupplier).where(
            GarmentSupplier.garment_id == garment_id,
            GarmentSupplier.supplier_id == supplier_id,
        )
    )
    gs = result.scalar_one_or_none()
    if not gs:
        raise NotFoundError("GarmentSupplier", 0)
    return gs


async def associate_supplier(
    db: AsyncSession, garment_id: int, data: GarmentSupplierCreate
) -> GarmentSupplier:
    # Verify garment exists and not in production
    result = await db.execute(select(Garment).where(Garment.id == garment_id))
    garment = result.scalar_one_or_none()
    if not garment:
        raise NotFoundError("Garment", garment_id)
    if garment.lifecycle_stage == "PRODUCTION":
        raise ProductionProtectedError(garment.name, "associate supplier")

    # Verify supplier exists
    result = await db.execute(
        select(Supplier).where(Supplier.id == data.supplier_id)
    )
    if not result.scalar_one_or_none():
        raise NotFoundError("Supplier", data.supplier_id)

    gs = GarmentSupplier(
        garment_id=garment_id,
        supplier_id=data.supplier_id,
        offer_price=data.offer_price,
        lead_time_days=data.lead_time_days,
        notes=data.notes,
    )
    db.add(gs)
    await db.commit()
    await db.refresh(gs)
    return gs


async def transition_supplier(
    db: AsyncSession, garment_id: int, supplier_id: int, target_status: str
) -> GarmentSupplier:
    gs = await _get_garment_supplier(db, garment_id, supplier_id)
    validate_supplier_transition(gs.status, target_status)
    gs.status = target_status
    await db.commit()
    await db.refresh(gs)
    return gs


async def get_sample_sets(
    db: AsyncSession, garment_id: int, supplier_id: int
) -> list[SampleSet]:
    gs = await _get_garment_supplier(db, garment_id, supplier_id)
    result = await db.execute(
        select(SampleSet).where(SampleSet.garment_supplier_id == gs.id)
    )
    return list(result.scalars().all())


async def create_sample_set(
    db: AsyncSession, garment_id: int, supplier_id: int, data: SampleSetCreate
) -> SampleSet:
    gs = await _get_garment_supplier(db, garment_id, supplier_id)
    sample = SampleSet(garment_supplier_id=gs.id, notes=data.notes)
    db.add(sample)
    await db.commit()
    await db.refresh(sample)
    return sample


async def update_sample_set(
    db: AsyncSession,
    garment_id: int,
    supplier_id: int,
    sample_id: int,
    data: SampleSetUpdate,
) -> SampleSet:
    gs = await _get_garment_supplier(db, garment_id, supplier_id)
    result = await db.execute(
        select(SampleSet).where(
            SampleSet.id == sample_id,
            SampleSet.garment_supplier_id == gs.id,
        )
    )
    sample = result.scalar_one_or_none()
    if not sample:
        raise NotFoundError("SampleSet", sample_id)

    validate_sample_transition(sample.status, data.status)
    sample.status = data.status
    if data.notes is not None:
        sample.notes = data.notes

    await db.commit()
    await db.refresh(sample)
    return sample
