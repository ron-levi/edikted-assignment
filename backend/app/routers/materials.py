from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.material import MaterialCreate, MaterialResponse
from app.services import material_service

router = APIRouter(
    prefix="/materials",
    tags=["materials"],
)


@router.get("", response_model=list[MaterialResponse])
async def list_materials(db: AsyncSession = Depends(get_db)):
    return await material_service.get_materials(db)


@router.post("", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
async def create_material(data: MaterialCreate, db: AsyncSession = Depends(get_db)):
    return await material_service.create_material(db, data)
