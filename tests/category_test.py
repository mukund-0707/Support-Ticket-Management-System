from fastapi.testclient import TestClient
from routes.category_routes import router

customer_email = "johncustomer0707@gmail.com"
agent_email = "johnagent0707@gmail.com"
admin_email = "johnadmin0707@gmail.com"


def test_create_category_cusotmer(client):
    register_response = client.post(
        "/register",
        json={
            "name": "John Customer",
            "email": customer_email,
            "password": "John@07",
            "role": "customer",
        }
    )
    login_response = client.post(
        "/login", data={"username": customer_email, "password": "John@07"}
    )
    print(register_response.json())
    print("login response:",login_response.json())

    token = login_response.json()["access_token"]
    response = client.post(
        "/categories",
        json={
            "name": "Demo Category",
            "description": "Demo Description",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_create_category_agent(client):
    register_response = client.post(
        "/register",
        json={
            "name": "John Agent",
            "email": agent_email,
            "password": "John@07",
            "role": "agent",
        }
    )
    login_response = client.post(
        "/login", data={"username": agent_email, "password": "John@07"}
    )
    token = login_response.json()["access_token"]
    response = client.post(
        "/categories",
        json={
            "name": "Demo Category",
            "description": "Demo Description",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_create_category_admin(client):
    register_response = client.post(
        "/register",
        json={
            "name": "John Admin",
            "email": admin_email,
            "password": "John@07",
            "role": "admin",
        }
    )
    login_response = client.post(
        "/login", data={"username": admin_email, "password": "John@07"}
    )
    token = login_response.json()["access_token"]
    response = client.post(
        "/categories",
        json={
            "name": "Demo Category",
            "description": "Demo Description",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
