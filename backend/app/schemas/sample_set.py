from pydantic import BaseModel, ConfigDict
from datetime import datetime


class SampleSetCreate(BaseModel):
    notes: str | None = None


class SampleSetUpdate(BaseModel):
    status: str
    notes: str | None = None


class SampleSetResponse(BaseModel):
    id: int
    garment_supplier_id: int
    status: str
    notes: str | None
    submitted_date: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
