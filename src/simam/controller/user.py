import json
from typing import List, NoReturn, Any
import os
from uuid import uuid4

from pydantic import UUID4
from starlite import Controller, Partial, get, post, put, patch, delete, Response, MediaType, Request, NotAuthorizedException
from starlite_jwt import JWTAuth, Token

from simam.model.model import User, UserDTO, get_user_by_name, get_user_by_id, get_users
from src.simam.util.hashing import verify_password
from src.simam.guards.guards import guard_user_post_message


async def retrieve_user_handler(unique_identifier: str) -> None | User:
    return get_user_by_id(unique_identifier)


jwt_auth = JWTAuth(
    retrieve_user_handler=retrieve_user_handler,
    token_secret=os.environ.get("JWT_SECRET", "abcd123"),
    exclude=["/schema", "/manual_login", "/login"],
)


@get("/manual_login")
def manual_login() -> Response:
    response = Response(
        """<html><body><form action="http://127.0.0.1:8000/login" method="post" enctype='text/plain'>
  <input name='{"name": "eins", "password": "11passwort", "trash": "' value='"}'/>
  <input type="submit" />
</form></body></html>""",
        media_type=MediaType.HTML,
        status_code=200)
    return response


@post("/login")
async def login_handler(request: Request) -> Response:
    data = await request.json()
    login_user = get_user_by_name(data["name"])
    if login_user and verify_password(login_user.password, data["password"]):
        response = jwt_auth.login(identifier=str(login_user.id), response_body=await UserDTO.from_model_instance_async(login_user))
        return response
    else:
        raise NotAuthorizedException


class UserController(Controller):
    path = "/users"

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
    @get(path="/{user_id:str}")
    async def get_user(self, user_id: str) -> UserDTO:
        user = get_user_by_id(user_id)
        return await UserDTO.from_model_instance_async(user)
    #     ...
    #
    # @delete(path="/{user_id:uuid}")
    # async def delete_user(self, user_id: UUID4) -> NoReturn:
    #     ...
