from __future__ import annotations

import asyncio
from time import sleep
from typing import List

from pydantic import BaseModel, Field
from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import mapped_column

from db import Base, DbResult


class StationSchema(BaseModel):
    id: int = Field(exclude=False, title="id")
    fuel_type:int = Field(exclude=False, title="fuel_type")
    fuel_quantity: float = Field(exclude=False, title="fuel")
    status: bool = Field(exclude=False, title="status")


# pylint: disable=E0213,C0115,C0116,W0718
class Station(Base):
    __tablename__ = "stations"

    id = Column(Integer, autoincrement=True, primary_key=True)
    fuel_type = mapped_column(ForeignKey("fuel_types.id"))
    fuel_quantity = Column(Float)
    status = Column(Boolean)

    async def add(self, session: AsyncSession) -> DbResult:
        try:
            result = await session.execute(insert(Station).values((None,self.fuel_type,self.fuel_quantity,self.status)))
            if result.is_insert:
                await session.commit()
                return DbResult.result(self.id)
            else:
                raise "Error"
        except Exception as e:
            await session.rollback()
            return DbResult.error(str(e), False)
        


    def auto_open(session: AsyncSession, station_id: int) -> DbResult:
        sleep(10)
        try:
            asyncio.run(Station.set_active(session,station_id,True))
            return DbResult.result()
        except Exception as e:
            return DbResult.error(str(e))

    async def get_by_id(session: AsyncSession, station_id: int) -> DbResult:
        try:
            result = await session.execute(select(Station).where(Station.id == station_id))
            data = result.scalars().first()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))
        
    
    async def set_active(session: AsyncSession, station_id: int, status: bool) -> DbResult:
        try:
            result = await session.execute(update(Station).where(Station.id == station_id).values(status=status))
            await session.commit()
            return DbResult.result()
        except Exception as e:
            return DbResult.error(str(e))
        
    
    async def set_fuel_quantity(session: AsyncSession, station_id: int, quantity: float) -> DbResult:
        try:
            await session.execute(update(Station).where(Station.id == station_id).values(fuel_quantity=Station.fuel_quantity+quantity))
            await session.commit()
            return DbResult.result()
        except Exception as e:
            return DbResult.error(str(e))

    async def get_all(session: AsyncSession) -> DbResult:
        try:
            result = await session.execute(select(Station))
            data = result.scalars().all()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))
        
    async def delete(session: AsyncSession, id: int) -> DbResult:
        try:
            _ = await session.execute(delete(Station).where(Station.id == id))
            await session.commit()
            return DbResult.result(True)
        except Exception as e:
            await session.rollback()
            return DbResult.error(str(e), False)
    


    def from_one_to_schema(station: Station) -> StationSchema:
        try:
            station_schema = StationSchema(
                id=station.id,
                fuel_type=station.fuel_type,
                fuel_quantity=station.fuel_quantity,
                status=station.status
            )
            return station_schema
        except Exception:
            return None

    def from_list_to_schema(stations: List[Station]) -> list[StationSchema]:
        try:
            return [Station.from_one_to_schema(b) for b in stations]
        except Exception:
            return []


async def init_station(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
