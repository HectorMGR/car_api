from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleDetail, VehicleResponse, VehiclePagination
from app.services.vehicle_service import VehicleService
from app.core.security import get_current_admin

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


# ─── Public ────────────────────────────────────────────

@router.get("/", response_model=VehiclePagination)
async def list_vehicles(
    cursor: str | None = Query(None, description="Timestamp del último ítem para paginación"),
    limit: int = Query(12, ge=1, le=100, description="Ítems por página"),
    status: str = Query("available", description="Filtrar por estado"),
    brand_id: int | None = Query(None, description="Filtrar por marca"),
    min_price: float | None = Query(None, description="Precio mínimo"),
    max_price: float | None = Query(None, description="Precio máximo"),
    year: int | None = Query(None, description="Filtrar por año"),
    sort_by: str = Query("price", description="Criterio de ordenamiento"),
    order: str = Query("asc", description="Orden: asc o desc"),
    db: AsyncSession = Depends(get_db),
):
    cursor_dt = None
    if cursor:
        try:
            cursor_dt = datetime.fromisoformat(cursor)
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de cursor inválido")

    return await VehicleService.get_all(
        db,
        brand_id=brand_id,
        min_price=min_price,
        max_price=max_price,
        year=year,
        status=status,
        cursor=cursor_dt,
        limit=limit,
        sort_by=sort_by,
        order=order,
    )


@router.get("/{vehicle_id}", response_model=VehicleDetail)
async def get_vehicle(
    vehicle_id: int,
    db: AsyncSession = Depends(get_db),
):
    vehicle = await VehicleService.get_by_id(db, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return vehicle


# ─── Admin ─────────────────────────────────────────────

@router.post("/", response_model=VehicleResponse, status_code=201)
async def create_vehicle(
    data: VehicleCreate,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    return await VehicleService.create(db, data)


@router.put("/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: int,
    data: VehicleUpdate,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    vehicle = await VehicleService.update(db, vehicle_id, data)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return vehicle


@router.delete("/{vehicle_id}", status_code=204)
async def delete_vehicle(
    vehicle_id: int,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    deleted = await VehicleService.delete(db, vehicle_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")