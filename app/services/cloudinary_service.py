import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException

from app.core.config import get_settings

settings = get_settings()

cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True,
)

ALLOWED_FORMATS = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 🔥 2MB


class CloudinaryService:

    @staticmethod
    async def upload_image(file: UploadFile, folder: str = "vehicles") -> str:
        if file.content_type not in ALLOWED_FORMATS:
            raise HTTPException(
                status_code=400,
                detail="Formato no permitido. Usar: JPEG, PNG o WebP",
            )

        contents = await file.read()

        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Imagen muy pesada. Máximo {MAX_FILE_SIZE // 1024} KB",
            )

        try:
            result = cloudinary.uploader.upload(
                contents,
                folder=folder,
                transformation=[
                    {"quality": "auto:good", "fetch_format": "auto"},
                ],
                resource_type="image",
            )
            return result["secure_url"]

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail="Error subiendo imagen a Cloudinary",
            ) from e

    @staticmethod
    async def delete_image(url: str) -> bool:
        try:
            public_id = CloudinaryService._extract_public_id(url)
            result = cloudinary.uploader.destroy(public_id)
            return result.get("result") == "ok"
        except Exception:
            return False

    @staticmethod
    def _extract_public_id(url: str) -> str:
        parts = url.split("/upload/")
        if len(parts) != 2:
            raise ValueError("URL de Cloudinary inválida")

        path = parts[1]

        # Remover versión si existe (v123456/)
        if path.startswith("v") and "/" in path:
            path = path.split("/", 1)[1]

        # Remover extensión
        return path.rsplit(".", 1)[0]