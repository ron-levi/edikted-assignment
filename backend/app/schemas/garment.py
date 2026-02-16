from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class GarmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None


class GarmentCreate(GarmentBase):
    pass


class GarmentUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None


class GarmentTransition(BaseModel):
    target_stage: Literal["CONCEPT", "DESIGN", "DEVELOPMENT", "SAMPLING", "PRODUCTION"]


class GarmentVariationCreate(GarmentBase):
    pass


class GarmentResponse(BaseModel):
    id: int
    name: str
    description: str | None
    lifecycle_stage: str
    parent_garment_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GarmentMaterialResponse(BaseModel):
    id: int
    name: str
    percentage: float

    model_config = ConfigDict(from_attributes=True)


class GarmentAttributeResponse(BaseModel):
    id: int
    name: str
    category: str

    model_config = ConfigDict(from_attributes=True)


class GarmentSupplierSummary(BaseModel):
    supplier_id: int
    supplier_name: str
    status: str
    offer_price: float | None

    model_config = ConfigDict(from_attributes=True)


class GarmentVariationSummary(BaseModel):
    id: int
    name: str
    lifecycle_stage: str

    model_config = ConfigDict(from_attributes=True)


class GarmentDetailResponse(GarmentResponse):
    materials: list[GarmentMaterialResponse] = []
    attributes: list[GarmentAttributeResponse] = []
    suppliers: list[GarmentSupplierSummary] = []
    variations: list[GarmentVariationSummary] = []
