from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import Model
from app.schemas.model import ModelCreate, ModelResponse

router = APIRouter(prefix="/models", tags=["models"])


@router.get("/", response_model=list[ModelResponse])
async def list_models(
    brand_id: int | None = Query(None, description="Filtrar por marca"),
    db: AsyncSession = Depends(get_db),
):
    query = select(Model).order_by(Model.name)
    if brand_id:
        query = query.where(Model.brand_id == brand_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=ModelResponse, status_code=201)
async def create_model(data: ModelCreate, db: AsyncSession = Depends(get_db)):
    model = Model(**data.model_dump())
    db.add(model)
    await db.flush()
    await db.refresh(model)
    return model