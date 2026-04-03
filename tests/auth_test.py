import pytest
from fastapi.testclient import TestClient
from routes.auth_routes import router
from app.database import db_conn
from conftest import TestingSessionLocal, engine

customer_email = "raj0707@gmail.com"
agent_email = "mayur0707@gmail.com"
admin_email = "mukundpatil0707@gmail.com"


# valid customer register test
def test_customer_register(client):
    response = client.post(
        "/register",
        json={
            "name": "John Customer",
            "email": "johncustomer0707@gmail.com",
            "password": "John@07",
            "role": "customer",
        },
    )
    assert response.status_code == 200
    assert response.json()["name"] == "John Customer"
    assert response.json()["email"] == "johncustomer0707@gmail.com"
    assert response.json()["role"] == "customer"


# invalid customer register with already existing email test
def test_invalid_customer_register(client):
    response = client.post(
        "/register",
        json={
            "name": "Raj",
            "email": "raj0707@gmail.com",
            "password": "Raj@07",
            "role": "customer",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "User already exists"


# invalid customer register with invalid email and password test
def test_invalid_customer_register_with_invalid_email_and_password(client):
    response = client.post(
        "/register",
        json={
            "name": "John Customer",
            "email": "invalid-email",
            "password": "invalid-password",
            "role": "customer",
        },
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"].startswith("value is not a valid email address")
    print(response.json())


# valid agent register test
def test_agent_register(client):
    response = client.post(
        "/register",
        json={
            "name": "John Agent",
            "email": "johnagent0707@gmail.com",
            "password": "John@07",
            "role": "agent",
        },
    )
    assert response.status_code == 200
    assert response.json()["name"] == "John Agent"
    assert response.json()["email"] == "johnagent0707@gmail.com"
    assert response.json()["role"] == "agent"

    # invalid agent register with already existing email test


def test_invalid_agent_register(client):
    response = client.post(
        "/register",
        json={
            "name": "Mayur",
            "email": "mayur0707@gmail.com",
            "password": "Mayur@07",
            "role": "agent",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "User already exists"


# invalid agent register with invalid email and password test
def test_invalid_agent_register_with_invalid_email_and_password(client):
    response = client.post(
        "/register",
        json={
            "name": "John Agent",
            "email": "invalid-email",
            "password": "invalid-password",
            "role": "agent",
        },
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"].startswith("value is not a valid email address")
    print(response.json())

# valid admin register test
def test_admin_register(client):
    response = client.post(
        "/register",
        json={
            "name": "John Admin",
            "email": "johnadmin0707@gmail.com",
            "password": "John@07",
            "role": "admin",
        },
    )
    assert response.status_code == 200
    assert response.json()["name"] == "John Admin"
    assert response.json()["email"] == "johnadmin0707@gmail.com"
    assert response.json()["role"] == "admin"


# invalid admin register with already existing email test
def test_invalid_admin_register(client):
    response = client.post(
        "/register",
        json={
            "name": "Mukund",
            "email": "mukundpatil0707@gmail.com",
            "password": "Mukund@07",
            "role": "admin",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "User already exists"


# invalid admin register with invalid email and password test
def test_invalid_admin_register_with_invalid_email_and_password(client):
    response = client.post(
        "/register",
        json={
            "name": "John Admin",
            "email": "invalid-email",
            "password": "invalid-password",
            "role": "admin",
        },
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"].startswith("value is not a valid email address")
    print(response.json())


# valid customer login test
def test_customer_login(client):
    response = client.post(
        "/login", data={"username": customer_email, "password": "Raj@07"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


# invalid customer login with invalid email and password test
def test_invalid_customer_login(client):
    response = client.post(
        "/login", data={"username": customer_email, "password": "invalid-password"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


# valid agent login test
def test_agent_login(client):
    response = client.post(
        "/login", data={"username": agent_email, "password": "Mayur@07"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


# invalid agent login with invalid email and password test
def test_invalid_agent_login(client):
    response = client.post(
        "/login", data={"username": agent_email, "password": "invalid-password"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


# valid admin login test
def test_admin_login(client):
    response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


# invalid admin login with invalid email and password test
def test_invalid_admin_login(client):
    response = client.post(
        "/login", data={"username": admin_email, "password": "invalid-password"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
