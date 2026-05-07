from pydantic import BaseModel, ConfigDict


class ModelBase(BaseModel):
    name: str
    brand_id: int


class ModelCreate(ModelBase):
    pass


class ModelResponse(ModelBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ModelWithBrand(BaseModel):
    id: int
    name: str
    brand: str

    model_config = ConfigDict(from_attributes=True)