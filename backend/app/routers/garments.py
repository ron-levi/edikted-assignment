from fastapi import APIRouter, Depends, Response, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.garment import (
    GarmentCreate,
    GarmentUpdate,
    GarmentResponse,
    GarmentDetailResponse,
    GarmentTransition,
    GarmentVariationCreate,
    GarmentMaterialResponse,
    GarmentAttributeResponse,
    GarmentSupplierSummary,
    GarmentVariationSummary,
)
from app.schemas.material import GarmentMaterialCreate
from app.schemas.attribute import GarmentAttributeCreate
from app.schemas.supplier import GarmentSupplierCreate, GarmentSupplierTransition, GarmentSupplierResponse
from app.schemas.sample_set import SampleSetCreate, SampleSetUpdate, SampleSetResponse
from app.services import garment_service, supplier_service

router = APIRouter(
    prefix="/garments",
    tags=["garments"],
)


@router.get("", response_model=list[GarmentResponse])
async def list_garments(
    stage: str | None = Query(None),
    search: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await garment_service.get_garments(db, stage=stage, search=search)


@router.post("", response_model=GarmentResponse, status_code=status.HTTP_201_CREATED)
async def create_garment(data: GarmentCreate, db: AsyncSession = Depends(get_db)):
    return await garment_service.create_garment(db, data)


@router.get("/{garment_id}", response_model=GarmentDetailResponse)
async def get_garment_detail(garment_id: int, db: AsyncSession = Depends(get_db)):
    garment = await garment_service.get_garment(db, garment_id)
    return GarmentDetailResponse(
        id=garment.id,
        name=garment.name,
        description=garment.description,
        lifecycle_stage=garment.lifecycle_stage,
        parent_garment_id=garment.parent_garment_id,
        created_at=garment.created_at,
        updated_at=garment.updated_at,
        materials=[
            GarmentMaterialResponse(
                id=gm.material.id,
                name=gm.material.name,
                percentage=float(gm.percentage),
            )
            for gm in garment.garment_materials
        ],
        attributes=[
            GarmentAttributeResponse(
                id=ga.attribute.id,
                name=ga.attribute.name,
                category=ga.attribute.category,
            )
            for ga in garment.garment_attributes
        ],
        suppliers=[
            GarmentSupplierSummary(
                supplier_id=gs.supplier.id,
                supplier_name=gs.supplier.name,
                status=gs.status,
                offer_price=float(gs.offer_price) if gs.offer_price else None,
            )
            for gs in garment.garment_suppliers
        ],
        variations=[
            GarmentVariationSummary(
                id=v.id, name=v.name, lifecycle_stage=v.lifecycle_stage
            )
            for v in garment.variations
        ],
    )


@router.put("/{garment_id}", response_model=GarmentResponse)
async def update_garment(
    garment_id: int, data: GarmentUpdate, db: AsyncSession = Depends(get_db)
):
    return await garment_service.update_garment(db, garment_id, data)


@router.delete("/{garment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_garment(garment_id: int, db: AsyncSession = Depends(get_db)):
    await garment_service.delete_garment(db, garment_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{garment_id}/transition", response_model=GarmentResponse)
async def transition_garment(
    garment_id: int, data: GarmentTransition, db: AsyncSession = Depends(get_db)
):
    return await garment_service.transition_garment(db, garment_id, data.target_stage)


@router.post(
    "/{garment_id}/variations",
    response_model=GarmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_variation(
    garment_id: int,
    data: GarmentVariationCreate,
    db: AsyncSession = Depends(get_db),
):
    return await garment_service.create_variation(db, garment_id, data)


@router.post(
    "/{garment_id}/materials",
    status_code=status.HTTP_201_CREATED,
)
async def add_material(
    garment_id: int,
    data: GarmentMaterialCreate,
    db: AsyncSession = Depends(get_db),
):
    gm = await garment_service.add_material(db, garment_id, data)
    await db.refresh(gm, ["material"])
    return {
        "id": gm.material.id,
        "name": gm.material.name,
        "percentage": float(gm.percentage),
    }


@router.delete(
    "/{garment_id}/materials/{material_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_material(
    garment_id: int, material_id: int, db: AsyncSession = Depends(get_db)
):
    await garment_service.remove_material(db, garment_id, material_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{garment_id}/attributes",
    status_code=status.HTTP_201_CREATED,
)
async def add_attribute(
    garment_id: int,
    data: GarmentAttributeCreate,
    db: AsyncSession = Depends(get_db),
):
    ga = await garment_service.add_attribute(db, garment_id, data)
    await db.refresh(ga, ["attribute"])
    return {
        "id": ga.attribute.id,
        "name": ga.attribute.name,
        "category": ga.attribute.category,
    }


@router.delete(
    "/{garment_id}/attributes/{attribute_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_attribute(
    garment_id: int, attribute_id: int, db: AsyncSession = Depends(get_db)
):
    await garment_service.remove_attribute(db, garment_id, attribute_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Supplier endpoints (nested under garment) ---


@router.post(
    "/{garment_id}/suppliers",
    response_model=GarmentSupplierResponse,
    status_code=status.HTTP_201_CREATED,
)
async def associate_supplier(
    garment_id: int,
    data: GarmentSupplierCreate,
    db: AsyncSession = Depends(get_db),
):
    gs = await supplier_service.associate_supplier(db, garment_id, data)
    # Load supplier name for response
    await db.refresh(gs, ["supplier"])
    return GarmentSupplierResponse(
        id=gs.id,
        garment_id=gs.garment_id,
        supplier_id=gs.supplier_id,
        supplier_name=gs.supplier.name,
        status=gs.status,
        offer_price=float(gs.offer_price) if gs.offer_price else None,
        lead_time_days=gs.lead_time_days,
        notes=gs.notes,
        created_at=gs.created_at,
        updated_at=gs.updated_at,
    )


@router.post(
    "/{garment_id}/suppliers/{supplier_id}/transition",
    response_model=GarmentSupplierResponse,
)
async def transition_supplier(
    garment_id: int,
    supplier_id: int,
    data: GarmentSupplierTransition,
    db: AsyncSession = Depends(get_db),
):
    gs = await supplier_service.transition_supplier(
        db, garment_id, supplier_id, data.target_status
    )
    await db.refresh(gs, ["supplier"])
    return GarmentSupplierResponse(
        id=gs.id,
        garment_id=gs.garment_id,
        supplier_id=gs.supplier_id,
        supplier_name=gs.supplier.name,
        status=gs.status,
        offer_price=float(gs.offer_price) if gs.offer_price else None,
        lead_time_days=gs.lead_time_days,
        notes=gs.notes,
        created_at=gs.created_at,
        updated_at=gs.updated_at,
    )


@router.get(
    "/{garment_id}/suppliers/{supplier_id}/samples",
    response_model=list[SampleSetResponse],
)
async def list_sample_sets(
    garment_id: int, supplier_id: int, db: AsyncSession = Depends(get_db)
):
    return await supplier_service.get_sample_sets(db, garment_id, supplier_id)


@router.post(
    "/{garment_id}/suppliers/{supplier_id}/samples",
    response_model=SampleSetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_sample_set(
    garment_id: int,
    supplier_id: int,
    data: SampleSetCreate,
    db: AsyncSession = Depends(get_db),
):
    return await supplier_service.create_sample_set(db, garment_id, supplier_id, data)


@router.put(
    "/{garment_id}/suppliers/{supplier_id}/samples/{sample_id}",
    response_model=SampleSetResponse,
)
async def update_sample_set(
    garment_id: int,
    supplier_id: int,
    sample_id: int,
    data: SampleSetUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await supplier_service.update_sample_set(
        db, garment_id, supplier_id, sample_id, data
    )
