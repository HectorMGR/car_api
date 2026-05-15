from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Vehicle, VehicleImage, Brand, Model, Currency, VehicleStatus
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleDetail, VehiclePagination
from app.schemas.vehicle_image import VehicleImageResponse


class VehicleService:

    @staticmethod
    async def get_all(
        db: AsyncSession,
        brand_id: int | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        year: int | None = None,
        status: str = "available",
        cursor: datetime | None = None,
        limit: int = 12,
        sort_by: str = "price",
        order: str = "asc",
    ) -> VehiclePagination:
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
        )

        if brand_id:
            query = query.where(Brand.id == brand_id)
        if min_price:
            query = query.where(Vehicle.price >= min_price)
        if max_price:
            query = query.where(Vehicle.price <= max_price)
        if year:
            query = query.where(Vehicle.year == year)
        if status:
            query = query.where(VehicleStatus.name == status)
        if cursor:
            query = query.where(Vehicle.created_at > cursor)

        if sort_by == "price":
            query = query.order_by(
                Vehicle.price.asc() if order == "asc" else Vehicle.price.desc()
            )
        else:
            query = query.order_by(
                Vehicle.created_at.desc()
            )

        query = query.limit(limit + 1)

        result = await db.execute(query)
        vehicles = result.scalars().unique().all()

        has_more = len(vehicles) > limit
        if has_more:
            vehicles = vehicles[:limit]

        items = [VehicleService._to_detail(v) for v in vehicles]

        next_cursor = None
        if has_more and items:
            next_cursor = items[-1].created_at.isoformat()

        return VehiclePagination(
            items=items,
            next_cursor=next_cursor,
            has_more=has_more,
        )

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