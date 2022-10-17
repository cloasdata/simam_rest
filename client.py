import argparse
import json
import time

import requests

from simam.model.model import get_user_by_name, MessageDTO, UserDTO, ProjectDTO


class Client:
    def __init__(self, server: str):
        self.auth_header = ""
        self.base_url = f"{server}/api/v1"
        self._user_cache = {int: UserDTO}
        self._project_cache = {int: ProjectDTO}
        self._message_cache = {int: MessageDTO}
        self.user = None

    def do_auth(self, login: str, password: str):
        credentials = {"name": login, "password": password}
        response = requests.post(f"{self.base_url}/login", json.dumps(credentials))
        token = response.headers['authorization']
        self.auth_header = {"Authorization": str(token)}
        self.user = get_user_by_name(login)

    def fetch_all_messages(self, project_id) -> list[MessageDTO]:
        response = requests.get(f"{self.base_url}/messages/{project_id}", headers=self.auth_header)
        if not response.status_code == 200:
            raise requests.HTTPError(response.status_code, response.json)
        messages = response.json()
        res = []
        for message in messages:
            msg = MessageDTO(**message)
            self._message_cache.setdefault(message['id'], msg)
            res.append(msg)
        return res

    def send_message(self, project_id: str, msg: str):
        message = {
            "id": None,
            "sender_id": str(self.user.id),  # admin
            "message_text": msg,
        }
        response = requests.post(f"{self.base_url}/messages/{project_id}/sendall", json.dumps(message),
                                 headers=self.auth_header)
        if not response.status_code == 201:
            raise requests.HTTPError(response.status_code, str(response.json()))

    def get_message(self, project_id: str) -> MessageDTO:
        query = {"index": "-1"}
        response = requests.get(
            f"{self.base_url}/messages/{project_id}",
            params=query,
            headers=self.auth_header
        )
        if not response.status_code == 200:
            raise requests.HTTPError(response.status_code, response.json)
        last_message = response.json()[0]
        if not last_message['id'] in self._message_cache:
            msg_dto = MessageDTO(**last_message)
            self._message_cache.setdefault(last_message['id'], msg_dto)
            return msg_dto

    def get_user(self, id_: str) -> UserDTO:
        user = self._user_cache.get(id_, None)
        if not user:
            response = requests.get(f"{self.base_url}/users/{id_}", headers=self.auth_header)
            if not response.status_code == 200:
                raise requests.HTTPError(response.status_code)
            user = response.json()
            user = self._user_cache.setdefault(user['id'], UserDTO(**user))
        return user

    def get_project(self, id_: str) -> ProjectDTO:
        project = self._project_cache.get(id_, None)
        if not project:
            response = requests.get(f"{self.base_url}/projects/{id_}", headers=self.auth_header)
            if not response.status_code == 200:
                raise requests.HTTPError(response.status_code, response.json())
            project = response.json()
            project = self._project_cache.setdefault(project['id'], ProjectDTO(**project))
        return project
