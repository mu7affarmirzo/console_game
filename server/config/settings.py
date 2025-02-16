from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import MetaData

HOST = '127.0.0.1'
PORT = 65432

MIN_CREDITS = 10
MAX_CREDITS = 100

DB_TYPE = 'sqlite'
DB_FILE = 'game.db'
DATABASE_URL = f'sqlite:///{DB_FILE}'

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


metadata = MetaData()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
