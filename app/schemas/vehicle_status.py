from pydantic import BaseModel, ConfigDict


class VehicleStatusBase(BaseModel):
    name: str


class VehicleStatusCreate(VehicleStatusBase):
    pass


class VehicleStatusResponse(VehicleStatusBase):
    id: int

    model_config = ConfigDict(from_attributes=True)