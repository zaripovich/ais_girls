import datetime
import threading
from typing import Optional

from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from db import DbResult, get_session
from models.fuel_type import FuelType
from models.station import Station
from models.transaction import Transaction, TransactionSchema


class NewTransaction(BaseModel):
    number: str = Field(exclude=False, title="number")
    fuel_quantity: int = Field(exclude=False, title="fuel_quantity")
    fuel_type: int = Field(exclude=False, title="fuel_type")
    date: str = Field(exclude=False, title="date")
    station_id: int = Field(exclude=False, title="station_id")

# pylint: disable=E0213,C0115,C0116,W0718
class AddResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: Optional[str] = Field(exclude=False, title="description")
    value: Optional[int] = Field(exclude=False, title="value")

    def __init__(
        self, code: int = 200, error_desc: Optional[str] = "", value: Optional[int] = 1
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


# pylint: disable=E0213,C0115,C0116,W0718
class TransactionResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: Optional[str] = Field(exclude=False, title="description")
    value: Optional[TransactionSchema] = Field(exclude=False, title="value")

    def __init__(
        self,
        code: int = 200,
        error_desc: Optional[str] = None,
        value: Optional[TransactionSchema] = None,
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


# pylint: disable=E0213,C0115,C0116,W0718
class TransactionsResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: Optional[str] = Field(exclude=False, title="description")
    value: Optional[list[TransactionSchema]] = Field(exclude=False, title="values",serialization_alias="values")

    def __init__(
        self,
        code: int = 200,
        error_desc: Optional[str] = None,
        value: Optional[list[TransactionSchema]] = [],
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


def init_transactions_routes(app: FastAPI):
    @app.post(
        "/transactions/add", response_model=AddResponse, response_model_exclude_none=True
    )
    async def add(
        data: NewTransaction,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            station_result = await Station.get_by_id(session,data.station_id)
            if not station_result.is_error:
                if station_result.value.fuel_type != data.fuel_type:
                    return AddResponse(code=500, error_desc="Incorrect fuel type")
                if station_result.value.fuel_quantity < data.fuel_quantity:
                    return AddResponse(code=500, error_desc="Fuel quantity")

                if station_result.value.status is False:
                    return AddResponse(code=500, error_desc="Station status is false")
            fuel_result = await FuelType.get_by_id(session,data.fuel_type)
            if fuel_result.is_error:
                return AddResponse(code=500, error_desc="Fuel Not Found")
            
            new_transaction = Transaction()
            new_transaction.number = data.number
            new_transaction.fuel_quantity = data.fuel_quantity
            new_transaction.fuel_type = data.fuel_type
            new_transaction.price = fuel_result.value.price * new_transaction.fuel_quantity
            new_transaction.date = datetime.datetime.fromisoformat(data.date)
            new_transaction.station_id = data.station_id
            result = await new_transaction.add(session)
            if result.is_error is True:
                return AddResponse(code=500, error_desc=result.error_desc)

            await Station.set_active(session,new_transaction.station_id,False)
            await Station.set_fuel_quantity(session,new_transaction.station_id,-new_transaction.fuel_quantity)

            thread = threading.Thread(target=Station.auto_open,args=(session,data.station_id,))
            thread.start()
            return AddResponse(code=200, value=result.value)
        except Exception as e:
            return AddResponse(code=500, error_desc=str(e))

    @app.get("/transactions/get_by_id/{id}", response_model=TransactionResponse)
    async def get_by_id(
        id: int,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result: DbResult = await Transaction.get_by_id(session, id)
            if result.is_error is True:
                return TransactionResponse(code=500, error_desc=result.error_desc)
            return TransactionResponse(code=200, value=Transaction.from_one_to_schema(result.value))
        except Exception as e:
            return TransactionResponse(code=500, error_desc=str(e))

    @app.get("/transactions/get_by_fuel/{id}", response_model=TransactionResponse)
    async def get_by_fuel_type(
        id: int,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result: DbResult = await Transaction.get_by_id(session, id)
            if result.is_error is True:
                return TransactionResponse(code=500, error_desc=result.error_desc)
            return TransactionResponse(code=200, value=Transaction.from_one_to_schema(result.value))
        except Exception as e:
            return TransactionResponse(code=500, error_desc=str(e))


    @app.get("/transactions/get_all", response_model=TransactionsResponse)
    async def get_all(
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result: DbResult = await Transaction.get_all(session)
            if result.is_error is True:
                return TransactionsResponse(code=500, error_desc=result.error_desc)
            return TransactionsResponse(code=200, value=Transaction.from_list_to_schema(result.value))
        except Exception as e:
            return TransactionsResponse(code=500, error_desc=str(e))
