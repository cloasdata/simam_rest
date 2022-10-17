from starlite import Request, BaseRouteHandler, NotAuthorizedException
from starlite_jwt import Token

from ..model.model import User
import src.simam.config.permissions as permission


def guard_user_post_message(request: Request[User, Token], _: BaseRouteHandler) -> None:
    permissions = permission.get()
    if not request.user.has_permission(permissions["post_message"]):
        raise NotAuthorizedException


async def guard_project_message(request: Request[User, Token], _: BaseRouteHandler) -> None:
    project_id = request.path_params.get("project_id")
    if not request.user.has_project(project_id):
        raise NotAuthorizedException
