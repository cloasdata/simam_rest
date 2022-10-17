from pathlib import Path

from sqlalchemy import create_engine

from src.simam.config.config import config


# maintain the same connection per thread
from sqlalchemy.pool import SingletonThreadPool
echo = True if config["database"].getboolean("verbose") else False

if db_path := config['database']['path']:
    db_path = Path(db_path)
else:
    raise ImportError(f"No database path provided in config.ini")

if not db_path.parent.exists():
    db_path.parent.mkdir(parents=True)

db_string = f"sqlite:///{db_path}"

engine = create_engine(db_string,
                       connect_args={'check_same_thread': False},
                        poolclass=SingletonThreadPool, echo=echo)

