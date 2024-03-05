from typing import Optional

from fastapi import Depends, FastAPI, Response
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from db import DbResult, get_session
from models.fuel_type import FuelType, FuelTypeSchema


class NewValue(BaseModel):
    fuel_type: int = Field(exclude=False, title="fuel_type")
    new_price: float = Field(exclude=False, title="new_price")


# pylint: disable=E0213,C0115,C0116,W0718
class UpdateResponse(BaseModel):
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
        

    
    @app.put("/fuel_types/update_price", response_model=UpdateResponse)
    async def update_price(
        response: Response,
        data: NewValue,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            fuel_result = await FuelType.get_by_id(session,data.fuel_type)
            if fuel_result.is_error:
                response.status_code = 500
                return UpdateResponse(code=500, error_desc="Fuel Not Found")
            result = await FuelType.set_price(session,data.fuel_type,data.new_price)
            if result is False:
                response.status_code = 500
                return UpdateResponse(code=500, error_desc=result.error_desc)
            return UpdateResponse(code=200, value=True)
        except Exception as e:
            response.status_code = 500
            return FuelTypesResponse(code=500, error_desc=str(e))
        
    

    
