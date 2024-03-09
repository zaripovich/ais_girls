from typing import Optional

from fastapi import Depends, FastAPI, Response
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from db import DbResult, get_session
from models.fuel_type import FuelType
from models.station import Station, StationSchema


class NewStation(BaseModel):
    fuel_type: int = Field(exclude=False, title="fuel_type")


# pylint: disable=E0213,C0115,C0116,W0718
class AddResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: Optional[str] = Field(exclude=False, title="description")
    value: Optional[int] = Field(exclude=False, title="value")

    def __init__(
        self, code: int = 200, error_desc: Optional[str] = "", value: Optional[int] = None
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


# pylint: disable=E0213,C0115,C0116,W0718
class DeleteResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: Optional[str] = Field(exclude=False, title="description")
    value: Optional[bool] = Field(exclude=False, title="value")

    def __init__(
        self,
        code: int = 200,
        error_desc: Optional[str] = None,
        value: Optional[bool] = True,
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


# pylint: disable=E0213,C0115,C0116,W0718
class StationResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: Optional[str] = Field(exclude=False, title="description")
    value: Optional[StationSchema] = Field(exclude=False, title="value")

    def __init__(
        self,
        code: int = 200,
        error_desc: Optional[str] = None,
        value: Optional[StationSchema] = None,
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


# pylint: disable=E0213,C0115,C0116,W0718
class StationsResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: Optional[str] = Field(exclude=False, title="description")
    value: Optional[list[StationSchema]] = Field(exclude=False, title="values",serialization_alias="values")

    def __init__(
        self,
        code: int = 200,
        error_desc: Optional[str] = None,
        value: Optional[list[StationSchema]] = [],
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


def init_stations_routes(app: FastAPI):

    @app.post(
        "/stations/add", response_model=AddResponse, response_model_exclude_none=True
    )
    async def add(
        response: Response,
        data: NewStation,
        session: AsyncSession = Depends(get_session),
    ):
        try:
           
            fuel_result = await FuelType.get_by_id(session,data.fuel_type)
            if fuel_result.is_error:
                response.status_code = 500
                return AddResponse(code=500, error_desc="Fuel Not Found")
            
            new_station = Station()
            new_station.fuel_type = data.fuel_type
            new_station.fuel_quantity = 1000
            new_station.status = True
            result = await new_station.add(session)
            if result.is_error is True:
                response.status_code = 500
                return AddResponse(code=500, error_desc=result.error_desc)
            return AddResponse(code=200, value=result.value)
        except Exception as e:
            response.status_code = 500
            return AddResponse(code=500, error_desc=str(e))

    @app.get("/stations/get_by_id/{id}", response_model=StationResponse)
    async def get_by_id(
        response: Response,
        id: int,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result: DbResult = await Station.get_by_id(session, id)
            if result.is_error is True:
                response.status_code = 500
                return StationResponse(code=500, error_desc=result.error_desc)
            return StationResponse(code=200, value=Station.from_one_to_schema(result.value))
        except Exception as e:
            response.status_code = 500
            return StationResponse(code=500, error_desc=str(e))
        
    

    @app.get("/stations/get_all", response_model=StationsResponse)
    async def get_all(
        response: Response,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result: DbResult = await Station.get_all(session)
            if result.is_error is True:
                response.status_code = 500
                return StationsResponse(code=500, error_desc=result.error_desc)
            return StationsResponse(code=200, value=Station.from_list_to_schema(result.value))
        except Exception as e:
            response.status_code = 500
            return StationsResponse(code=500, error_desc=str(e))


    @app.delete("/stations/{id}", response_model=DeleteResponse)
    async def delete(
        response: Response,
        id: int,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result = await Station.delete(session, id)
            if result is False:
                response.status_code = 500
                return DeleteResponse(code=500, error_desc=result.error_desc)
            return DeleteResponse(code=200, value=result.value)
        except Exception as e:
            response.status_code = 500
            return DeleteResponse(code=500, error_desc=str(e))