# app\schemas\vehicle_image.py

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class VehicleImageBase(BaseModel):
    url: str
    is_primary: bool = False
    sort_order: int = 0


class VehicleImageCreate(VehicleImageBase):
    pass


class VehicleImageResponse(VehicleImageBase):
    id: int
    vehicle_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)