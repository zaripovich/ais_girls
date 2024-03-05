from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field
from sqlalchemy import Column, Float, Integer, String, insert, select, update
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from db import Base, DbResult


class FuelTypeSchema(BaseModel):
    id: int = Field(exclude=False, title="id")
    fuel_name: str = Field(exclude=False, title="fuel_name")
    price: float = Field(exclude=False, title="price")


# pylint: disable=E0213,C0115,C0116,W0718
class FuelType(Base):
    __tablename__ = "fuel_types"

    id = Column(Integer, autoincrement=True, primary_key=True)
    fuel_name = Column(String, unique=True)
    price = Column(Float)

    async def add(self, session: AsyncSession) -> DbResult:
        try:
            result = await session.execute(insert(FuelType).values((None,self.fuel_name,self.price,)))
            if result.is_insert:
                await session.commit()
                return DbResult.result(self.id)
            else:
                raise "Error"
        except Exception as e:
            await session.rollback()
            return DbResult.error(str(e), False)
        
    async def set_price(session: AsyncSession, fuel_type: int, new_price: float) -> DbResult:
        try:
            await session.execute(update(FuelType).where(FuelType.id == fuel_type).values(price=new_price))
            await session.commit()
            return DbResult.result(True)
        except Exception as e:
            return DbResult.error(str(e),False)

    async def get_by_id(session: AsyncSession, fueltype_id: int) -> DbResult:
        try:
            result = await session.execute(select(FuelType).where(FuelType.id == fueltype_id))
            data = result.scalars().first()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))

    async def get_all(session: AsyncSession) -> DbResult:
        try:
            result = await session.execute(select(FuelType))
            data = result.scalars().all()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))

    def from_one_to_schema(fueltype: FuelType) -> FuelTypeSchema:
        try:
            fueltype_schema = FuelTypeSchema(
                id=fueltype.id,
                fuel_name=fueltype.fuel_name,
                price=fueltype.price,
            )
            return fueltype_schema
        except Exception:
            return None

    def from_list_to_schema(fueltypes: List[FuelType]) -> list[FuelTypeSchema]:
        try:
            return [FuelType.from_one_to_schema(b) for b in fueltypes]
        except Exception:
            return []


async def init_fuel_type(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
