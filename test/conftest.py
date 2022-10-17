import pytest
import json

from starlite.testing import TestClient

from server import app
from src.simam.util.string import stringify

API_BASE_PATH = "/api/v1"

@pytest.fixture(scope="function")
def test_client() -> TestClient:
    return TestClient(app=app, base_url="http://127.0.0.1:8000")


@pytest.fixture()
def auth_header(test_client) -> dict:
    # log ins a user and provide token at headers dict
    with test_client as client:
        credentials = {"name":"admin", "password": "admin"}
        response = client.post(API_BASE_PATH + "/login", json.dumps(credentials))
        user = json.loads(response.text, parse_int=str)
        token = response.headers['authorization']
        headers = {}
        #headers.update(user)
        headers.setdefault("Authorization", f'{token}')
        return stringify(headers)

