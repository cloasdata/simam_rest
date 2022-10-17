import datetime
import json
from typing import List, NoReturn, Any
import os
from uuid import uuid4

from pydantic import UUID4
from starlite import Controller, Partial, get, post, put, patch, delete, Response, MediaType, Request, Provide
from starlite_jwt import JWTAuth, Token
from starlette.status import HTTP_201_CREATED

from ..model.model import User, UserDTO, Project, Message, get_message_by_project, MessageDTO, transmit, filter_message
from ..guards.guards import guard_user_post_message, guard_project_message
from ..database.session import session


def get_final_id(project_id: int) -> int:
    return project_id


class MessageController(Controller):
    path = "/messages/{project_id:int}"
    guards = [guard_project_message]

    @get("/")
    async def get_messages(self, project_id: int, request: Request[User, Token], index:int = None) -> list[Message]:
        if not index:
            messages = get_message_by_project(project_id)
        else:
            messages = filter_message(project_id=project_id, from_=index)
        return await transmit(messages, request.user)


    @post(path="/sendall", guards=[guard_user_post_message])
    async def new_message(self, data: MessageDTO, project_id: int, request: Request[User, Token]) -> Message:
        msg = data.to_model_instance()
        # msg.sender = request.user
        msg.issue_date = datetime.datetime.now()
        msg.edit_date = datetime.datetime.now()
        session.add(msg)
        session.commit()
        msg.send_to_project_members(project_id)
        return await MessageDTO.from_model_instance_async(msg)
