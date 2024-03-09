import datetime
import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.testclient import TestClient
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware

from routes.fuel_type import init_fuel_type_routes
from routes.station import init_stations_routes
from routes.stats import init_stats_routes
from routes.transaction import init_transactions_routes

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
app.add_middleware(SQLAlchemyMiddleware, db_url=os.environ["DATABASE_URL"])

init_fuel_type_routes(app)
init_stations_routes(app)
init_transactions_routes(app)
init_stats_routes(app)


client = TestClient(app)
auth = ""


def test_add_station():
    test_data = {"fuel_type": 2}
    post_data = json.dumps(test_data)
    response = client.post("/stations/add", data=post_data)
    print(response.json())
    assert response.json()["code"] == 200
    assert response.json()["value"] is not None

def test_get_all_stations():
    response = client.get("/stations/get_all")
    print(response.json())
    assert response.json()["code"] == 200
    assert response.json()["values"] is not None


def test_get_station_by_id():
    response = client.get("/stations/get_by_id/1")
    print(response.json())
    assert response.json()["code"] == 200
    assert response.json()["value"] is not None



def test_get_all_fuel_types():
    response = client.get("/fuel_types/get_all")
    print(response.json())
    assert response.json()["code"] == 200
    assert response.json()["values"] is not None


def test_get_fuel_type_by_id():
    response = client.get("/fuel_types/get_by_id/1")
    print(response.json())
    assert response.json()["code"] == 200
    assert response.json()["value"] is not None


def test_update_fuel_price():
    response = client.get("/fuel_types/get_by_id/1")
    print(response.json())
    assert response.json()["code"] == 200
    assert response.json()["value"] is not None
    price = response.json()["value"]["price"]
    test_data = {"fuel_type": 1, "new_price": price+10}
    post_data = json.dumps(test_data)
    response_2 = client.put("/fuel_types/update_price", data=post_data)
    assert response_2.json()["code"] == 200
    assert response_2.json()["value"] == 1
    response_3 = client.get("/fuel_types/get_by_id/1")
    print(response_3.json())
    assert response_3.json()["code"] == 200
    assert response_3.json()["value"] is not None
    new_price = response_3.json()["value"]["price"]
    assert new_price == (price+10)




def test_transactions_add():
    test_data = {"number": "125XFS", "fuel_quantity": 30, "station_id": 1}
    post_data = json.dumps(test_data)
    response = client.post(
        "/transactions/add", data=post_data
    )
    assert response.json()["code"] == 200
    assert response.json()["value"] is not None


def test_transaction_get_by_id():
    response = client.get(
        "/transactions/get_by_id/1"
    )
    assert response.json()["code"] == 200
    assert response.json()["value"] is not None


def test_get_all_transactions():
    response = client.get(
        "/transactions/get_all"
    )
    assert response.json()["code"] == 200
    assert response.json()["values"] is not None


def test_get_median_price():
    response = client.get(
        "/stats/get_median_price/1"
    )
    print(response.json())
    assert response.json()["code"] == 200
    assert response.json()["value"] is not None


def test_get_all_fuel():
    test_data = {"station_id": 1, "date_from": datetime.datetime(day=8,month=3,year=2024).isoformat(), "date_to": datetime.datetime.now().isoformat()}
    post_data = json.dumps(test_data)
    response = client.post(
        "/stats/get_all_fuel", data= post_data
    )
    print(response.json())
    assert response.json()["code"] == 200
    assert response.json()["value"] is not None


