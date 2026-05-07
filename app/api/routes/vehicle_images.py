from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import get_current_admin
from app.schemas.vehicle_image import VehicleImageResponse
from app.services.vehicle_image_service import VehicleImageService

router = APIRouter(prefix="/vehicles/{vehicle_id}/images", tags=["vehicle images"])


@router.post("/", response_model=VehicleImageResponse, status_code=201)
async def upload_image(
    vehicle_id: int,
    file: UploadFile = File(...),
    is_primary: bool = Query(False),
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    return await VehicleImageService.add_image(db, vehicle_id, file, is_primary)


@router.delete("/{image_id}", status_code=204)
async def delete_image(
    vehicle_id: int,
    image_id: int,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    deleted = await VehicleImageService.delete_image(db, vehicle_id, image_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")


@router.patch("/{image_id}/primary", response_model=VehicleImageResponse)
async def set_primary_image(
    vehicle_id: int,
    image_id: int,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    image = await VehicleImageService.set_primary(db, vehicle_id, image_id)

    if not image:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    return image