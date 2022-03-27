from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from .main import app, get_influx_client


client = TestClient(app)


async def override_dependency():
    influx_client = MagicMock()
    return influx_client


app.dependency_overrides[get_influx_client] = override_dependency


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {}


def test_measurement():
    data = {"wifi": -43,
            "chip_id": "25e8ae",
            "pm02": 28,
            "rco2": 720,
            "atmp": 21.60,
            "rhum": 9
            }
    response = client.post("/measurements", json=data)
    assert response.status_code == 201
    assert response.json()['rco2'] == data['rco2']
