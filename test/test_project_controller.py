import pytest

from src.simam.controller.project import ProjectController

from conftest import API_BASE_PATH


class TestProjectController():
    def test_get_project(self,test_client, auth_header):
        with test_client as client:
            project_id = 1
            response = client.get(API_BASE_PATH+f"/projects/{project_id}", headers=auth_header)

        assert response.status_code == 200