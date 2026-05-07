from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import vehicles, brands, models, auth, vehicle_images


app = FastAPI(
    title="Vehicle Marketplace API",
    description="API para marketplace de vehículos",
    version="0.1.0",
)

# CORS - ajustar origins en producción
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Vehicle Marketplace API is running"}


# Routes
app.include_router(vehicles.router, prefix="/api")
app.include_router(brands.router, prefix="/api")
app.include_router(models.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(vehicle_images.router, prefix="/api")