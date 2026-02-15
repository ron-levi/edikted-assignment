from pydantic import BaseModel, ConfigDict, Field


class AttributeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: str


class AttributeResponse(BaseModel):
    id: int
    name: str
    category: str

    model_config = ConfigDict(from_attributes=True)


class GarmentAttributeCreate(BaseModel):
    attribute_id: int


class IncompatibilityCreate(BaseModel):
    attribute_id_1: int
    attribute_id_2: int


class IncompatibilityResponse(BaseModel):
    id: int
    attribute_id_1: int
    attribute_id_2: int
    attribute_1_name: str | None = None
    attribute_2_name: str | None = None

    model_config = ConfigDict(from_attributes=True)
