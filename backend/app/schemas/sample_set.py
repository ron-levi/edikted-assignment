from pydantic import BaseModel, ConfigDict
from datetime import datetime


class SampleSetBase(BaseModel):
    notes: str | None = None


class SampleSetCreate(SampleSetBase):
    pass


class SampleSetUpdate(SampleSetBase):
    status: str


class SampleSetResponse(BaseModel):
    id: int
    garment_supplier_id: int
    status: str
    notes: str | None
    submitted_date: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
