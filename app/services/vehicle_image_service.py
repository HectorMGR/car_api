from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, HTTPException

from app.models import VehicleImage, Vehicle
from app.services.cloudinary_service import CloudinaryService

MAX_IMAGES_PER_VEHICLE = 8


class VehicleImageService:

    @staticmethod
    async def add_image(
        db: AsyncSession,
        vehicle_id: int,
        file: UploadFile,
        is_primary: bool = False,
    ) -> VehicleImage:

        # 🔍 Validar vehículo
        vehicle = await db.execute(
            select(Vehicle).where(Vehicle.id == vehicle_id)
        )
        if not vehicle.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Vehículo no encontrado")

        # 🔢 Contar imágenes
        count_result = await db.execute(
            select(func.count()).where(VehicleImage.vehicle_id == vehicle_id)
        )
        count = count_result.scalar() or 0

        if count >= MAX_IMAGES_PER_VEHICLE:
            raise HTTPException(
                status_code=400,
                detail=f"Máximo {MAX_IMAGES_PER_VEHICLE} imágenes por vehículo",
            )

        # ☁️ Subir imagen
        url = await CloudinaryService.upload_image(
            file,
            folder=f"vehicles/{vehicle_id}"
        )

        # ⭐ Manejo de primary
        if count == 0:
            is_primary = True
        elif is_primary:
            await VehicleImageService._clear_primary(db, vehicle_id)

        image = VehicleImage(
            vehicle_id=vehicle_id,
            url=url,
            is_primary=is_primary,
            sort_order=count,
        )

        db.add(image)
        await db.flush()
        await db.refresh(image)

        return image

    @staticmethod
    async def delete_image(
        db: AsyncSession,
        vehicle_id: int,
        image_id: int
    ) -> bool:

        result = await db.execute(
            select(VehicleImage).where(
                VehicleImage.id == image_id,
                VehicleImage.vehicle_id == vehicle_id
            )
        )
        image = result.scalar_one_or_none()

        if not image:
            return False

        # ☁️ Eliminar en Cloudinary
        deleted_cloudinary = await CloudinaryService.delete_image(image.url)

        if not deleted_cloudinary:
            raise HTTPException(
                status_code=500,
                detail="Error eliminando imagen en Cloudinary"
            )

        was_primary = image.is_primary

        # 🗑️ Eliminar DB
        await db.delete(image)
        await db.flush()

        # 🔄 Reordenar imágenes
        await VehicleImageService._reorder_images(db, vehicle_id)

        # ⭐ Reasignar primary si es necesario
        if was_primary:
            await VehicleImageService._assign_new_primary(db, vehicle_id)

        return True

    @staticmethod
    async def set_primary(
        db: AsyncSession,
        vehicle_id: int,
        image_id: int
    ) -> VehicleImage | None:

        result = await db.execute(
            select(VehicleImage).where(
                VehicleImage.id == image_id,
                VehicleImage.vehicle_id == vehicle_id
            )
        )
        image = result.scalar_one_or_none()

        if not image:
            return None

        await VehicleImageService._clear_primary(db, vehicle_id)

        image.is_primary = True

        await db.flush()
        await db.refresh(image)

        return image

    @staticmethod
    async def _clear_primary(db: AsyncSession, vehicle_id: int):
        result = await db.execute(
            select(VehicleImage).where(
                VehicleImage.vehicle_id == vehicle_id,
                VehicleImage.is_primary == True,
            )
        )

        for img in result.scalars().all():
            img.is_primary = False

    @staticmethod
    async def _reorder_images(db: AsyncSession, vehicle_id: int):
        result = await db.execute(
            select(VehicleImage)
            .where(VehicleImage.vehicle_id == vehicle_id)
            .order_by(VehicleImage.sort_order)
        )

        images = result.scalars().all()

        for index, img in enumerate(images):
            img.sort_order = index

    @staticmethod
    async def _assign_new_primary(db: AsyncSession, vehicle_id: int):
        result = await db.execute(
            select(VehicleImage)
            .where(VehicleImage.vehicle_id == vehicle_id)
            .order_by(VehicleImage.sort_order)
        )

        first_image = result.scalars().first()

        if first_image:
            first_image.is_primary = True