from sqlalchemy.orm import sessionmaker
from src.simam.database.engine import engine
from sqlalchemy.orm.session import Session as Session_type

Session = sessionmaker(bind=engine)

def new_session() -> Session_type:
    return Session()


session = new_session()

