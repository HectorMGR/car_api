from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import Brand
from app.schemas.brand import BrandCreate, BrandResponse

router = APIRouter(prefix="/brands", tags=["brands"])


@router.get("/", response_model=list[BrandResponse])
async def list_brands(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Brand).order_by(Brand.name))
    return result.scalars().all()


@router.post("/", response_model=BrandResponse, status_code=201)
async def create_brand(data: BrandCreate, db: AsyncSession = Depends(get_db)):
    brand = Brand(**data.model_dump())
    db.add(brand)
    await db.flush()
    await db.refresh(brand)
    return brand