import orjson
import json

from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED

from simam.model.dto import UserDTO
from src.simam.util.string import stringify

def test_login(test_client):
    with test_client as client:
        response = client.post("/login", orjson.dumps({"name":"admin", "password": "admin"}))
        user = orjson.loads(response.text)
        token = response.headers['authorization']
        assert response.status_code == HTTP_201_CREATED
        headers = {}
        headers.update(user)
        headers.setdefault("Authorization", f'{token}')
        stringify(headers)
        response = client.get("/users", headers=headers)
        assert response.status_code == HTTP_200_OK

def test_bad_login(test_client):
    # wrong user
    with test_client as client:
        response = client.post("/login", json.dumps({"name": "ein", "password": "11passwort"}))
        assert response.status_code == HTTP_401_UNAUTHORIZED


def test_bad_login_pass(test_client):
    # wrong user
    with test_client as client:
        response = client.post("/login", json.dumps({"name": "ein", "password": "1passwort"}))
        assert response.status_code == HTTP_401_UNAUTHORIZED