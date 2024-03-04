
import datetime
from typing import Optional

from fastapi import Depends, FastAPI, Response
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from db import DbResult, get_session
from models.transaction import Transaction


# pylint: disable=E0213,C0115,C0116,W0718
class StatsResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: Optional[str] = Field(exclude=False, title="description")
    value: Optional[float] = Field(exclude=False, title="value")

    def __init__(
        self,
        code: int = 200,
        error_desc: Optional[str] = None,
        value: Optional[float] = None,
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


class StationDateFilter(BaseModel):
    station_id: int = Field(exclude=False, title="station_id"),
    date_from: datetime.datetime = Field(exclude=False, title="date_from"),
    date_to: datetime.datetime = Field(exclude=False, title="date_to"),



def init_stats_routes(app: FastAPI):


    @app.get("/stats/get_all_fuel", response_model=StatsResponse)
    async def get_fuel_by_date(
        response: Response,
        data: StationDateFilter,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result_trans: DbResult = await Transaction.get_by_station_and_time(session,data.station_id,data.date_from,data.date_to)
            if result_trans.is_error is True:
                response.status_code = 500
                return StatsResponse(code=500, error_desc=result_trans.error_desc)
            transactions: list[Transaction] = result_trans.value
            fuel = 0.0
            for transaction in transactions:
                fuel += transaction.fuel_quantity
            return StatsResponse(code=200, value=fuel)
        except Exception as e:
            response.status_code = 500
            return StatsResponse(code=500, error_desc=str(e))
        
    
    @app.get("/stats/get_median_price/{id}", response_model=StatsResponse)
    async def get_median_price(
        response: Response,
        id: int,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result_trans: DbResult = await Transaction.get_by_station(session,id)
            if result_trans.is_error is True:
                response.status_code = 500
                return StatsResponse(code=500, error_desc=result_trans.error_desc)
            transactions: list[Transaction] = result_trans.value
            price = 0.0
            for transaction in transactions:
                price += transaction.fuel_quantity
            if len(transactions):
                price /= len(transactions)
            return StatsResponse(code=200, value=price)
        except Exception as e:
            response.status_code = 500
            return StatsResponse(code=500, error_desc=str(e))
        
        
    
