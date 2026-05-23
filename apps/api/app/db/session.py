import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo = False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db()->Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    
def init_db():
    from app.db.base import Base
    from app.db.models import Repository, CodeChunk

    Base.metadata.create_all(bind=engine)
    print("tables created")
    