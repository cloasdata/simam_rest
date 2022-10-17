import json

from starlette.status import HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_200_OK

from conftest import API_BASE_PATH
from simam.model.model import Message, MessageDTO


class TestMessageDTO:
    def test_init(self):
        text = "hello this is a post from the programmer"
        msg = MessageDTO(message_text=text)
        assert json.loads(msg.json())["message_text"] == text


class TestMessageController:
    def test_new_message(self, test_client, auth_header):
        with test_client as client:
            text = "hello this is a post from the programmer"
            message = {
                "sender_id": "1", # admin
                "message_text": text,
            }
            project_id = 1
            response = client.post(url=API_BASE_PATH + f"/messages/{project_id}/sendall", data=json.dumps(message), headers=auth_header)
            assert response.status_code == HTTP_201_CREATED

    def test_new_message_wrong_project(self, test_client, auth_header):
        with test_client as client:
            text = "hello this is a post from the programmer"
            message = {
                "message_text": text,
            }
            project_id = 2
            response = client.post(url=API_BASE_PATH + f"/messages/{project_id}", data=json.dumps(message), headers=auth_header)
            assert response.status_code == HTTP_401_UNAUTHORIZED

    def test_get_messages(self, test_client, auth_header):
        project_id = 1
        with test_client as client:
            response = client.get(url=API_BASE_PATH + f"/messages/{project_id}", headers=auth_header)
        assert response.status_code == HTTP_200_OK

    def test_filter_messages(self, test_client, auth_header):
        project_id = 1
        query = {"index":str(project_id)}
        with test_client as client:
            response = client.get(
                url=API_BASE_PATH + f"/messages/{project_id}",
                params=query,
                headers=auth_header
            )
        assert response.status_code == 200