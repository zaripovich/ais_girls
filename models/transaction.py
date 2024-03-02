from __future__ import annotations

import datetime
from typing import List

from pydantic import BaseModel, Field
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    select,
)
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import mapped_column

from db import Base, DbResult


class TransactionSchema(BaseModel):
    id: int = Field(exclude=False, title="id")
    number: str = Field(exclude=False, title="name")
    fuel_quantity: float = Field(exclude=False, title="fuel_quantity")
    fuel_type: int = Field(exclude=False, title="fuel_type")
    price: float = Field(exclude=False, title="price")
    date: datetime.datetime = Field(exclude=False, title="date")
    station_id: int = Field(exclude=False, title="station_id")


# pylint: disable=E0213,C0115,C0116,W0718
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, autoincrement=True, primary_key=True)
    number = Column(String)
    fuel_quantity = Column(Float)
    fuel_type = mapped_column(ForeignKey("fuel_types.id"))
    price = Column(Float)
    date = Column(DateTime)
    station_id = mapped_column(ForeignKey("stations.id"))
   

    async def add(self, session: AsyncSession) -> DbResult:
        try:
            session.add(self)
            await session.commit()
            return DbResult.result(self.id)
        except Exception as e:
            await session.rollback()
            return DbResult.error(str(e), False)

    async def get_by_id(session: AsyncSession, transaction_id: int) -> DbResult:
        try:
            result = await session.execute(select(Transaction).where(Transaction.id == transaction_id))
            data = result.scalars().first()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))
        
    async def get_by_station_and_time(session: AsyncSession, station_id: int,date_from: datetime.datetime, date_to: datetime.datetime) -> DbResult:
        try:
            result = await session.execute(select(Transaction).where(Transaction.station_id == station_id).where(Transaction.date >= date_from).where(Transaction.date <= date_to))
            data = result.scalars().all()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))
        
    
    async def get_by_station(session: AsyncSession, station_id: int) -> DbResult:
        try:
            result = await session.execute(select(Transaction).where(Transaction.station_id == station_id))
            data = result.scalars().all()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))
        
    async def get_all(session: AsyncSession) -> DbResult:
        try:
            result = await session.execute(select(Transaction))
            data = result.scalars().all()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))

    async def get_by_date(session: AsyncSession,date_from: datetime.datetime, date_to: datetime.datetime) -> DbResult:
        try:
            result = await session.execute(select(Transaction).where(Transaction.date >= date_from).where(Transaction.date <= date_to))
            data = result.scalars().all()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))
        

    async def get_by_fuel_type(session: AsyncSession, fuel_type: int) -> DbResult:
        try:
            result = await session.execute(select(Transaction).where(Transaction.fuel_type == fuel_type))
            data = result.scalars().all()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))

    def from_one_to_schema(transaction: Transaction) -> TransactionSchema:
        try:
            transaction_schema = TransactionSchema(
                id=transaction.id,
                number=transaction.number,
                fuel_quantity = transaction.fuel_quantity,
                fuel_type = transaction.fuel_type,
                price = transaction.price,
                date=transaction.date,
                station_id=transaction.station_id
            )
            return transaction_schema
        except Exception:
            return None

    def from_list_to_schema(transactions: List[Transaction]) -> list[TransactionSchema]:
        try:
            return [Transaction.from_one_to_schema(b) for b in transactions]
        except Exception:
            return []


async def init_transaction(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)