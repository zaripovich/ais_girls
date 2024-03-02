from typing import Optional

from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from db import DbResult, get_session
from models.station import Station, StationSchema


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


    @app.get("/stations/get/id/{id}", response_model=StationResponse)
    async def get_by_id(
        id: int,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result: DbResult = await Station.get_by_id(session, id)
            if result.is_error is True:
                return StationResponse(code=500, error_desc=result.error_desc)
            return StationResponse(code=200, value=Station.from_one_to_schema(result.value))
        except Exception as e:
            return StationResponse(code=500, error_desc=str(e))
        
    

    @app.get("/stations/get_all", response_model=StationsResponse)
    async def get_all(
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result: DbResult = await Station.get_all(session)
            if result.is_error is True:
                return StationsResponse(code=500, error_desc=result.error_desc)
            return StationsResponse(code=200, value=Station.from_list_to_schema(result.value))
        except Exception as e:
            return StationsResponse(code=500, error_desc=str(e))
