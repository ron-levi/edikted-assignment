from pydantic import BaseModel, ConfigDict, Field


class MaterialCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class MaterialResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class GarmentMaterialCreate(BaseModel):
    material_id: int
    percentage: float = Field(..., gt=0, le=100)


class GarmentMaterialResponse(BaseModel):
    id: int
    material_id: int
    material_name: str
    percentage: float

    model_config = ConfigDict(from_attributes=True)
