from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class SupplierBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    contact_info: str | None = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    contact_info: str | None = None


class SupplierResponse(BaseModel):
    id: int
    name: str
    contact_info: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GarmentSupplierCreate(BaseModel):
    supplier_id: int
    offer_price: float | None = None
    lead_time_days: int | None = None
    notes: str | None = None


class GarmentSupplierTransition(BaseModel):
    target_status: str


class GarmentSupplierResponse(BaseModel):
    id: int
    garment_id: int
    supplier_id: int
    supplier_name: str | None = None
    status: str
    offer_price: float | None
    lead_time_days: int | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
