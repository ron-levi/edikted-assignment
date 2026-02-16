from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierResponse
from app.services import supplier_service

router = APIRouter(
    prefix="/suppliers",
    tags=["suppliers"],
)


@router.get("", response_model=list[SupplierResponse])
async def list_suppliers(db: AsyncSession = Depends(get_db)):
    return await supplier_service.get_suppliers(db)


@router.post("", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(data: SupplierCreate, db: AsyncSession = Depends(get_db)):
    return await supplier_service.create_supplier(db, data)


@router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(supplier_id: int, db: AsyncSession = Depends(get_db)):
    return await supplier_service.get_supplier(db, supplier_id)


@router.put("/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: int, data: SupplierUpdate, db: AsyncSession = Depends(get_db)
):
    return await supplier_service.update_supplier(db, supplier_id, data)


@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(supplier_id: int, db: AsyncSession = Depends(get_db)):
    await supplier_service.delete_supplier(db, supplier_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
