from fastapi.testclient import TestClient
from routes.comment_routes import router



customer_email = "raj0707@gmail.com"
agent_email = "mayur0707@gmail.com"
admin_email = "mukundpatil0707@gmail.com"


# valid customer comment test
def test_customer_comment(client):
    admin_login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    admin_token = admin_login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test", "description": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    login_response = client.post(
        "/login", data={"username": customer_email, "password": "Raj@07"}
    )
    token = login_response.json()["access_token"]
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    print("ticket response:", ticket_response.json())
    ticket_id = ticket_response.json()["id"]
    response = client.post(
        "/comments",
        json={
            "ticket_id": ticket_id,
            "message": "This is a comment",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "This is a comment"
    assert response.json()["ticket_id"] == ticket_id


# invalid customer comment test
def test_customer_comment_invalid_ticket(client):
    login_response = client.post(
        "/login", data={"username": customer_email, "password": "Raj@07"}
    )
    token = login_response.json()["access_token"]
    response = client.post(
        "/comments",
        json={
            "ticket_id": 999,
            "message": "This is a comment",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


# invalid customer comment test
def test_customer_comment_invalid_message(client):
    login_response = client.post(
        "/login", data={"username": customer_email, "password": "Raj@07"}
    )
    token = login_response.json()["access_token"]
    response = client.post(
        "/comments",
        json={
            "ticket_id": 1,
            "message": "",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Comment message cannot be empty"


# customer can't comment on others tickets
def test_customer_comment_others_ticket(client):
    admin_login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    admin_token = admin_login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test", "description": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    login_response = client.post(
        "/login", data={"username": customer_email, "password": "Raj@07"}
    )
    token = login_response.json()["access_token"]
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    print("ticket response:", ticket_response.json())
    ticket_id = ticket_response.json()["id"]
    response = client.post(
        "/comments",
        json={
            "ticket_id": ticket_id,
            "message": "This is a comment",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "You can't comment on others tickets"


# valid agent comment test
def test_agent_comment(client):
    admin_login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    admin_token = admin_login_response.json()["access_token"]
    login_response = client.post(
        "/login", data={"username": agent_email, "password": "Mayur@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test", "description": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_id = ticket_response.json()["id"]
    response = client.post(
        "/comments",
        json={
            "ticket_id": ticket_id,
            "message": "This is a comment",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "This is a comment"
    assert response.json()["ticket_id"] == ticket_id


# valid admin comment test
def test_admin_comment(client):
    login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test", "description": "Test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_id = ticket_response.json()["id"]
    response = client.post(
        "/comments",
        json={
            "ticket_id": ticket_id,
            "message": "This is a comment",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "This is a comment"
    assert response.json()["ticket_id"] == ticket_id
