from typing import Annotated
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from fastapi import Depends

DB_URL = "postgresql://postgres:1234@localhost:5432/SupportTicket"

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


def db_conn():
    db = SessionLocal()
    print("db: ", db)
    try:
        yield db
        # print("here in db connn")
    finally:
        db.close()


db_dependecies = Annotated[Session, Depends(db_conn)]
