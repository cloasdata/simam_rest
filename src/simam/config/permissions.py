from sqlalchemy import select

from src.simam.database.session import new_session
from simam.model.model import Permission


def get(session=None):
    session = session or new_session()
    return {permission.name: permission for permission in session.execute(select(Permission)).scalars().all()}
