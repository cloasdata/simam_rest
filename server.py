from starlite import Starlite, OpenAPIConfig, Router
from starlite.plugins.sql_alchemy import SQLAlchemyPlugin

from src.simam.controller.user import UserController, jwt_auth, login_handler, manual_login
from src.simam.controller.message import MessageController
from src.simam.controller.project import ProjectController

openapi_config = OpenAPIConfig(
    components=[jwt_auth.openapi_components],
    security=[jwt_auth.security_requirement],
    title="hans",
    version="1",
    # exclude any URLs that should not have authentication.  We exclude the documentation URLs here.
)

version_router = Router(path="/v1", route_handlers=[UserController, MessageController, login_handler, manual_login, ProjectController] )
base_router = Router(path="/api", route_handlers=[version_router])

app = Starlite(
    route_handlers= [base_router],
    middleware=[jwt_auth.middleware,],
    openapi_config=openapi_config,
    plugins=[SQLAlchemyPlugin()]
    )