from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Vehicle, VehicleImage, Brand, Model, Currency, VehicleStatus
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleDetail
from app.schemas.vehicle_image import VehicleImageResponse


class VehicleService:

    @staticmethod
    async def get_all(
        db: AsyncSession,
        brand_id: int | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        year: int | None = None,
    ) -> list[VehicleDetail]:
        query = (
            select(Vehicle)
            .join(Model)
            .join(Brand)
            .join(Currency)
            .join(VehicleStatus)
            .options(selectinload(Vehicle.images))
            .options(selectinload(Vehicle.model).selectinload(Model.brand))
            .options(selectinload(Vehicle.currency))
            .options(selectinload(Vehicle.status))
            .order_by(Vehicle.created_at.desc())
        )

        if brand_id:
            query = query.where(Brand.id == brand_id)
        if min_price:
            query = query.where(Vehicle.price >= min_price)
        if max_price:
            query = query.where(Vehicle.price <= max_price)
        if year:
            query = query.where(Vehicle.year == year)

        result = await db.execute(query)
        vehicles = result.scalars().unique().all()

        return [VehicleService._to_detail(v) for v in vehicles]

    @staticmethod
    async def get_by_id(db: AsyncSession, vehicle_id: int) -> VehicleDetail | None:
        query = (
            select(Vehicle)
            .where(Vehicle.id == vehicle_id)
            .options(selectinload(Vehicle.images))
            .options(selectinload(Vehicle.model).selectinload(Model.brand))
            .options(selectinload(Vehicle.currency))
            .options(selectinload(Vehicle.status))
        )
        result = await db.execute(query)
        vehicle = result.scalar_one_or_none()

        if not vehicle:
            return None

        return VehicleService._to_detail(vehicle)

    @staticmethod
    async def create(db: AsyncSession, data: VehicleCreate) -> Vehicle:
        vehicle = Vehicle(**data.model_dump())
        db.add(vehicle)
        await db.flush()
        await db.refresh(vehicle)
        return vehicle

    @staticmethod
    async def update(
        db: AsyncSession, vehicle_id: int, data: VehicleUpdate
    ) -> Vehicle | None:
        result = await db.execute(
            select(Vehicle).where(Vehicle.id == vehicle_id)
        )
        vehicle = result.scalar_one_or_none()

        if not vehicle:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(vehicle, field, value)

        await db.flush()
        await db.refresh(vehicle)
        return vehicle

    @staticmethod
    async def delete(db: AsyncSession, vehicle_id: int) -> bool:
        result = await db.execute(
            select(Vehicle).where(Vehicle.id == vehicle_id)
        )
        vehicle = result.scalar_one_or_none()

        if not vehicle:
            return False

        await db.delete(vehicle)
        await db.flush()
        return True

    @staticmethod
    def _to_detail(vehicle: Vehicle) -> VehicleDetail:
        return VehicleDetail(
            id=vehicle.id,
            brand=vehicle.model.brand.name,
            model=vehicle.model.name,
            year=vehicle.year,
            price=float(vehicle.price),
            currency_code=vehicle.currency.code,
            currency_symbol=vehicle.currency.symbol,
            status=vehicle.status.name,
            description=vehicle.description,
            images=[
                VehicleImageResponse.model_validate(img)
                for img in sorted(vehicle.images, key=lambda i: i.sort_order)
            ],
            created_at=vehicle.created_at,
        )