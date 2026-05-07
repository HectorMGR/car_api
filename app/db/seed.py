import asyncio
from sqlalchemy import select
from app.db.session import async_session
from app.models import Currency, VehicleStatus


CURRENCIES = [
    {"code": "USD", "symbol": "$"},
    {"code": "CRC", "symbol": "₡"},
    {"code": "EUR", "symbol": "€"},
]

STATUSES = [
    {"name": "available"},
    {"name": "sold"},
    {"name": "reserved"},
]


async def seed():
    async with async_session() as session:
        # Currencies
        for c in CURRENCIES:
            exists = await session.execute(
                select(Currency).where(Currency.code == c["code"])
            )
            if not exists.scalar_one_or_none():
                session.add(Currency(**c))
                print(f"  + Currency: {c['code']}")
                await session.commit()
        print("Seed completado!")


if __name__ == "__main__":
    asyncio.run(seed())