from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AttributeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: Literal["SLEEVE_TYPE", "NECKLINE", "GARMENT_CATEGORY", "FIT", "FEATURE"]


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

    @model_validator(mode="after")
    def check_different_ids(self):
        if self.attribute_id_1 == self.attribute_id_2:
            raise ValueError("attribute_id_1 and attribute_id_2 must be different")
        return self


class IncompatibilityResponse(BaseModel):
    id: int
    attribute_id_1: int
    attribute_id_2: int
    attribute_1_name: str | None = None
    attribute_2_name: str | None = None

    model_config = ConfigDict(from_attributes=True)
