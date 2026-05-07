import asyncio
from app.db.session import async_session
from app.models import VehicleStatus

async def add():
    async with async_session() as s:
        for name in ['available', 'sold', 'reserved']:
            s.add(VehicleStatus(name=name))
        await s.commit()
        print('Statuses creados')

asyncio.run(add())