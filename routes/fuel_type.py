from typing import Optional

from fastapi import Depends, FastAPI, Response
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from db import DbResult, get_session
from models.fuel_type import FuelType, FuelTypeSchema


# pylint: disable=E0213,C0115,C0116,W0718
class FuelTypeResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: Optional[str] = Field(exclude=False, title="description")
    value: Optional[FuelTypeSchema] = Field(exclude=False, title="value")

    def __init__(
        self,
        code: int = 200,
        error_desc: Optional[str] = None,
        value: Optional[FuelTypeSchema] = None,
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


# pylint: disable=E0213,C0115,C0116,W0718
class FuelTypesResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: Optional[str] = Field(exclude=False, title="description")
    value: Optional[list[FuelTypeSchema]] = Field(exclude=False, title="values",serialization_alias="values")

    def __init__(
        self,
        code: int = 200,
        error_desc: Optional[str] = None,
        value: Optional[list[FuelTypeSchema]] = [],
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


def init_fuel_type_routes(app: FastAPI):


    @app.get("/fuel_types/get_by_id/{id}", response_model=FuelTypeResponse)
    async def get_by_id(
        response: Response,
        id: int,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result: DbResult = await FuelType.get_by_id(session, id)
            if result.is_error is True:
                response.status_code = 500
                return FuelTypeResponse(code=500, error_desc=result.error_desc)
            return FuelTypeResponse(code=200, value=FuelType.from_one_to_schema(result.value))
        except Exception as e:
            response.status_code = 500
            return FuelTypeResponse(code=500, error_desc=str(e))
        
    

    @app.get("/fuel_types/get_all", response_model=FuelTypesResponse)
    async def get_all(
        response: Response,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result: DbResult = await FuelType.get_all(session)
            if result.is_error is True:
                response.status_code = 500
                return FuelTypesResponse(code=500, error_desc=result.error_desc)
            return FuelTypesResponse(code=200, value=FuelType.from_list_to_schema(result.value))
        except Exception as e:
            response.status_code = 500
            return FuelTypesResponse(code=500, error_desc=str(e))
