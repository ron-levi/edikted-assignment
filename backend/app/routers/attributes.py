from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.attribute import (
    AttributeCreate,
    AttributeResponse,
    IncompatibilityCreate,
    IncompatibilityResponse,
)
from app.services import attribute_service

router = APIRouter(
    prefix="/attributes",
    tags=["attributes"],
)


@router.get("", response_model=list[AttributeResponse])
async def list_attributes(
    category: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await attribute_service.get_attributes(db, category=category)


@router.post("", response_model=AttributeResponse, status_code=status.HTTP_201_CREATED)
async def create_attribute(
    data: AttributeCreate, db: AsyncSession = Depends(get_db)
):
    return await attribute_service.create_attribute(db, data)


@router.get("/incompatibilities", response_model=list[IncompatibilityResponse])
async def list_incompatibilities(db: AsyncSession = Depends(get_db)):
    rules = await attribute_service.get_incompatibilities(db)
    return [
        IncompatibilityResponse(
            id=r.id,
            attribute_id_1=r.attribute_id_1,
            attribute_id_2=r.attribute_id_2,
            attribute_1_name=r.attribute_1.name if r.attribute_1 else None,
            attribute_2_name=r.attribute_2.name if r.attribute_2 else None,
        )
        for r in rules
    ]


@router.post(
    "/incompatibilities",
    response_model=IncompatibilityResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_incompatibility(
    data: IncompatibilityCreate, db: AsyncSession = Depends(get_db)
):
    rule = await attribute_service.create_incompatibility(db, data)
    await db.refresh(rule, ["attribute_1", "attribute_2"])
    return IncompatibilityResponse(
        id=rule.id,
        attribute_id_1=rule.attribute_id_1,
        attribute_id_2=rule.attribute_id_2,
        attribute_1_name=rule.attribute_1.name if rule.attribute_1 else None,
        attribute_2_name=rule.attribute_2.name if rule.attribute_2 else None,
    )
