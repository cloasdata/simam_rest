import json
from typing import List, NoReturn, Any
import os
from uuid import uuid4

from pydantic import UUID4
from starlite import Controller, Partial, get, post, put, patch, delete, Response, MediaType, Request, NotAuthorizedException
from starlite_jwt import JWTAuth, Token

from simam.model.model import User, UserDTO, get_user_by_name, get_user_by_id, get_users, Project, ProjectDTO, \
    get_project
from src.simam.util.hashing import verify_password
from src.simam.guards.guards import guard_user_post_message


class ProjectController(Controller):
    path = "/projects"

    # @post()
    # async def create_user(self, data: User) -> User:
    #     ...

    @get(guards=[guard_user_post_message])
    async def list_users(self, request: Request[User, Token]) -> List[UserDTO]:
        return await get_users()

    # @patch(path="/{user_id:uuid}")
    # async def partial_update_user(self, user_id: UUID4, data: Any) -> User:
    #     ...
    #
    # @put(path="/{user_id:uuid}")
    # async def update_user(self, user_id: UUID4, data: User) -> User:
    #     ...
    #
    @get(path="/{project_id:str}")
    async def get_project(self, project_id: str) -> ProjectDTO:
        project = get_project(project_id)
        return await ProjectDTO.from_model_instance_async(project)
    #     ...
    #
    # @delete(path="/{user_id:uuid}")
    # async def delete_user(self, user_id: UUID4) -> NoReturn:
    #     ...