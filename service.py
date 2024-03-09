import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware
from sqlalchemy.ext.asyncio import AsyncEngine

from db import engine
from models.fuel_type import FuelType, init_fuel_type
from models.station import Station, init_station
from models.transaction import init_transaction

# pylint: disable=E0401
from routes.fuel_type import init_fuel_type_routes
from routes.station import init_stations_routes
from routes.stats import init_stats_routes
from routes.transaction import init_transactions_routes

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)




app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(SQLAlchemyMiddleware, db_url=os.environ["DATABASE_URL"])


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Custom title",
        version="2.5.0",
        summary="This is a very custom OpenAPI schema",
        description="Here's a longer description of the custom **OpenAPI** schema",
        routes=app.routes,
    )
    return openapi_schema


async def init_models():
    try:
        if os.environ.get("REINIT_DB") == "1":
            await init_fuel_type(engine)
            await init_station(engine)
            await init_transaction(engine)
            await init_base_vars(engine)
        print("Done\n")
    except Exception as e:
        print(e)

async def init_base_vars(engine: AsyncEngine):
    try:
        fuels = [
            [43,"АИ-92"],
            [45,"АИ-95"],
            [47,"АИ-100"],
            [55,"Дизель"],
        ]
        for fuel in fuels:
            fuel_temp = FuelType()
            fuel_temp.price = fuel[0]
            fuel_temp.fuel_name = fuel[1]
            async with engine.connect() as conn:
                result = await fuel_temp.add(conn)
                if result.is_error:
                    print("Error create fuel_types\n")
        
        for station in range(4):
            station_temp = Station()
            station_temp.fuel_type = station+1
            station_temp.fuel_quantity = (10000 - 123*station)
            station_temp.status = True
            async with engine.connect() as conn:
                result = await station_temp.add_first(conn)
                if result.is_error:
                    print("Error create stations\n")

        print("Done\n")

    except Exception as e:
        print(e)


def run():
    init_fuel_type_routes(app)
    init_stations_routes(app)
    init_transactions_routes(app)
    init_stats_routes(app)
    app.openapi_schema = custom_openapi()
    uvicorn.run(app, host=os.environ.get("HOST"), port=int(os.environ.get("PORT")))
