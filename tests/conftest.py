# tests/conftest.py

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.database import db_conn   
from app.main import app

TEST_DB_URL = "postgresql://postgres:1234@localhost:5432/SupportTicket"

engine = create_engine(TEST_DB_URL)
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()

    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()  
    connection.close()

@pytest.fixture
def client(db):
    def override_db_conn():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[db_conn] = override_db_conn

    with TestClient(app) as test_client:
        yield test_client

from unittest.mock import AsyncMock
from utils.redis_connection import redis_client

@pytest.fixture(autouse=True)
def override_redis():
    redis_client.get = AsyncMock(return_value=None)
    redis_client.set = AsyncMock(return_value=None)
    redis_client.keys = AsyncMock(return_value=[])
    redis_client.delete = AsyncMock(return_value=None)

from services import send_email

@pytest.fixture(autouse=True)
def disable_email():
    def fake_send_email(*args, **kwargs):
        return

    send_email.send_email = fake_send_email