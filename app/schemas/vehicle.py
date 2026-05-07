from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.schemas.vehicle_image import VehicleImageResponse


class VehicleBase(BaseModel):
    model_id: int
    year: int
    price: float
    currency_id: int
    status_id: int
    description: str | None = None


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    model_id: int | None = None
    year: int | None = None
    price: float | None = None
    currency_id: int | None = None
    status_id: int | None = None
    description: str | None = None


class VehicleResponse(VehicleBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VehicleDetail(BaseModel):
    """Flattened response for public API"""
    id: int
    brand: str
    model: str
    year: int
    price: float
    currency_code: str
    currency_symbol: str
    status: str
    description: str | None
    images: list[VehicleImageResponse]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)