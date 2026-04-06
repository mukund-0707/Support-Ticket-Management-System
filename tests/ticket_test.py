from fastapi.testclient import TestClient
from routes.ticket_routes import router

customer_email = "raj0707@gmail.com"
agent_email = "mayur0707@gmail.com"
admin_email = "mukundpatil0707@gmail.com"


# invalid customer ticket test
def test_invalid_customer_ticket(client):
    admin_login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    admin_token = admin_login_response.json()["access_token"]
    login_response = client.post(
        "/login", data={"username": customer_email, "password": "Raj@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Description and title cannot be empty"


# category not found
def test_customer_ticket_category_not_found(client):
    login_response = client.post(
        "/login", data={"username": customer_email, "password": "Raj@07"}
    )
    token = login_response.json()["access_token"]
    response = client.post(
        "/tickets",
        json={
            "title": "NonExistent Category",
            "description": "Test",
            "priority": "high",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


# not authorized
def test_customer_ticket_not_authorized(client):
    login_response = client.post(
        "/login", data={"username": customer_email, "password": "Raj@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


# valid customer ticket test
def test_customer_ticket(client):
    admin_login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    admin_token = admin_login_response.json()["access_token"]

    login_response = client.post(
        "/login", data={"username": customer_email, "password": "Raj@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test Category"
    assert isinstance(response.json()["description"], str)
    assert response.json()["priority"] == "high"
    assert response.json()["created_by"] == login_response.json()["id"]


# invalid agent ticket test
def test_invalid_agent_ticket(client):
    login_response = client.post(
        "/login", data={"username": agent_email, "password": "Mayur@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Description and title cannot be empty"


# category not found
def test_agent_ticket_category_not_found(client):
    login_response = client.post(
        "/login", data={"username": agent_email, "password": "Mayur@07"}
    )
    token = login_response.json()["access_token"]
    response = client.post(
        "/tickets",
        json={
            "title": "NonExistent Category",
            "description": "Test",
            "priority": "high",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


# not authorized
def test_agent_ticket_not_authorized(client):
    login_response = client.post(
        "/login", data={"username": agent_email, "password": "Mayur@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


# valid agent ticket test
def test_agent_ticket(client):
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
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test Category"
    assert isinstance(response.json()["description"], str)
    assert response.json()["priority"] == "high"
    assert response.json()["created_by"] == login_response.json()["id"]


# invalid admin ticket test
def test_invalid_admin_ticket(client):
    login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Description and title cannot be empty"


# category not found
def test_admin_ticket_category_not_found(client):
    login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    token = login_response.json()["access_token"]
    response = client.post(
        "/tickets",
        json={
            "title": "NonExistent Category",
            "description": "Test",
            "priority": "high",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


# not authorized
def test_admin_ticket_not_authorized(client):
    login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
    )
    response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


# valid admin ticket test
def test_admin_ticket(client):
    login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test Category"
    assert isinstance(response.json()["description"], str)
    assert response.json()["priority"] == "high"
    assert response.json()["created_by"] == login_response.json()["id"]


# /tickets/by-id/{id}
# customer get ticket by id
def test_customer_get_ticket_by_id(client):
    admin_login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    admin_token = admin_login_response.json()["access_token"]
    login_response = client.post(
        "/login", data={"username": customer_email, "password": "Raj@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_id = ticket_response.json()["id"]
    response = client.get(
        f"/tickets/by-id/{ticket_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["id"] == ticket_id
    assert response.json()["created_by"] == login_response.json()["id"]


# customer get ticket by id not found
def test_customer_get_ticket_by_id_not_found(client):
    login_response = client.post(
        "/login", data={"username": customer_email, "password": "Raj@07"}
    )
    token = login_response.json()["access_token"]
    response = client.get(
        "/tickets/by-id/394",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "You can't view others tickets"


# customer get ticket by id not authorized
def test_customer_get_ticket_by_id_not_authorized(client):
    admin_login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    admin_token = admin_login_response.json()["access_token"]
    login_response = client.post(
        "/login", data={"username": customer_email, "password": "Raj@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_id = ticket_response.json()["id"]
    response = client.get(f"/tickets/by-id/{ticket_id}")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


# customer you can't view others tickets
def test_customer_get_ticket_by_id_not_authorized_customer(client):
    # admin login
    admin_login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    admin_token = admin_login_response.json()["access_token"]
    # admin create ticket
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    ticket_id = ticket_response.json()["id"]
    # customer login
    login_response = client.post(
        "/login", data={"username": customer_email, "password": "Raj@07"}
    )
    token = login_response.json()["access_token"]
    response = client.get(
        f"/tickets/by-id/{ticket_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "You can't view others tickets"


# agent get ticket by id
def test_agent_get_ticket_by_id(client):
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
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_id = ticket_response.json()["id"]
    response = client.get(
        f"/tickets/by-id/{ticket_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["id"] == ticket_id
    assert response.json()["created_by"] == login_response.json()["id"]


# agent get ticket by id not found
def test_agent_get_ticket_by_id_not_found(client):
    login_response = client.post(
        "/login", data={"username": agent_email, "password": "Mayur@07"}
    )
    token = login_response.json()["access_token"]
    response = client.get(
        "/tickets/by-id/999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


# agent get ticket by id not authorized
def test_agent_get_ticket_by_id_not_authorized(client):
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
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_id = ticket_response.json()["id"]
    response = client.get(f"/tickets/by-id/{ticket_id}")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


# admin get ticket by id
def test_admin_get_ticket_by_id(client):
    login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_id = ticket_response.json()["id"]
    response = client.get(
        f"/tickets/by-id/{ticket_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["id"] == ticket_id
    assert response.json()["created_by"] == login_response.json()["id"]


# admin get ticket by id not found
def test_admin_get_ticket_by_id_not_found(client):
    login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    token = login_response.json()["access_token"]
    response = client.get(
        "/tickets/by-id/999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


# admin get ticket by id not authorized
def test_admin_get_ticket_by_id_not_authorized(client):
    login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_id = ticket_response.json()["id"]
    response = client.get(
        f"/tickets/by-id/{ticket_id}",
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


# /tickets/by-priority
# customer get ticket by priority and get error of Only agent and admin can view tickets
def test_customer_get_ticket_by_priority(client):
    login_response = client.post(
        "/login", data={"username": customer_email, "password": "Raj@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = client.get(
        "/tickets/by-priority?priority=high",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Only agents and admins can view tickets"


# agent get ticket by priority
def test_agent_get_ticket_by_priority(client):
    admin_login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    print("admin_login_response", admin_login_response)
    admin_token = admin_login_response.json()["access_token"]
    login_response = client.post(
        "/login", data={"username": agent_email, "password": "Mayur@07"}
    )
    print("login_response", login_response)
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    print("category_response", category_response)
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    print("ticket_response", ticket_response)
    ticket_id = ticket_response.json()["id"]
    response = client.get(
        "/tickets/by-priority?priority=high",
        headers={"Authorization": f"Bearer {token}"},
    )
    print("response", response)
    assert response.status_code == 200
    assert response.json()[0]["priority"] == "high"


# admin get ticket by priority
def test_admin_get_ticket_by_priority(client):
    login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_id = ticket_response.json()["id"]
    response = client.get(
        "/tickets/by-priority?priority=high",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()[0]["priority"] == "high"


# /tickets/filter
# customer get ticket by filter and get error of Only agent and admin can view tickets
def test_customer_get_ticket_by_filter(client):
    admin_login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    admin_token = admin_login_response.json()["access_token"]
    login_response = client.post(
        "/login", data={"username": customer_email, "password": "Raj@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_id = ticket_response.json()["id"]
    response = client.get(
        "/tickets/filter?status_code=open",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Only agents and admins can view tickets"


# agent get ticket by filter
def test_agent_get_ticket_by_filter(client):
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
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_id = ticket_response.json()["id"]
    response = client.get(
        "/tickets/filter?status_code=open",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()[0]["status"] == "open"


# admin get ticket by filter
def test_admin_get_ticket_by_filter(client):
    login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_id = ticket_response.json()["id"]
    response = client.get(
        "/tickets/filter?status_code=open",
        headers={"Authorization": f"Bearer {token}"},
    )
    print("RESPONSE:", response.json())
    assert response.status_code == 200
    assert response.json()[0]["status"] == "open"


# /tickets #get all tickets
# customer get all tickets
def test_customer_get_all_tickets(client):
    login_response = client.post(
        "/login", data={"username": customer_email, "password": "Raj@07"}
    )
    token = login_response.json()["access_token"]
    response = client.get(
        "/tickets",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Only agents and admins can view tickets"


# agent get all tickets
def test_agent_get_all_tickets(client):
    login_response = client.post(
        "/login", data={"username": agent_email, "password": "Mayur@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = client.get(
        "/tickets",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


# agent get all tickets not found
# def test_agent_get_all_tickets_not_found(client):
#     login_response = client.post(
#         "/login", data={"username": agent_email, "password": "Mayur@07"}
#     )
#     token = login_response.json()["access_token"]
#     response = client.get(
#         "/tickets",
#         headers={"Authorization": f"Bearer {token}"},
#     )
#     assert response.status_code == 404
#     assert response.json()["detail"] == "Ticket not found"


# admin get all tickets
def test_admin_get_all_tickets(client):
    login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = client.get(
        "/tickets",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


# /tickets/my-tickets
def test_get_all_ticket_by_customer(client):
    login_response = client.post(
        "/login", data={"username": customer_email, "password": "Raj@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = client.get(
        "/tickets/my-tickets",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


# /tickets/{id}/status
# customer update ticket status and get error only agents and admins can update ticket status
def test_customer_update_ticket_status_error(client):
    admin_login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    admin_token = admin_login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    login_response = client.post(
        "/login", data={"username": customer_email, "password": "Raj@07"}
    )
    token = login_response.json()["access_token"]
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_id = ticket_response.json()["id"]
    response = client.patch(
        f"/tickets/{ticket_id}/status?ticket_status=resolved",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Only agents and admins can update tickets"


# agent update ticket status and get success
def test_agent_update_ticket_status(client):
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
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_id = ticket_response.json()["id"]
    response = client.patch(
        f"/tickets/{ticket_id}/status?ticket_status=resolved",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "resolved"


# agent cancel ticket and get success
def test_agent_cancel_ticket(client):
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
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_id = ticket_response.json()["id"]
    response = client.patch(
        f"/tickets/{ticket_id}/status?ticket_status=cancelled",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


# agent update ticket status and get error if ticket not found
def test_agent_update_ticket_status_not_found(client):
    login_response = client.post(
        "/login", data={"username": agent_email, "password": "Mayur@07"}
    )
    token = login_response.json()["access_token"]
    response = client.patch(
        "/tickets/999/status?ticket_status=resolved",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


# agent update resolved ticket and get error
def test_agent_update_resolved_ticket(client):
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
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_id = ticket_response.json()["id"]
    print("ticket_id", ticket_id)
    print("ticket_response.status_code", ticket_response.status_code)
    print("ticket_response.json()", ticket_response.json())
    response = client.patch(
        f"/tickets/{ticket_id}/status?ticket_status=resolved",
        headers={"Authorization": f"Bearer {token}"},
    )
    print("response.status_code", response.status_code)
    print("response.json()", response.json())
    assert response.status_code == 200
    assert response.json()["status"] == "resolved"
    response = client.patch(
        f"/tickets/{ticket_id}/status?ticket_status=resolved",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot update resolved or cancelled ticket"


# agent update cancelled ticket and get error
def test_agent_update_cancelled_ticket(client):
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
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_id = ticket_response.json()["id"]
    response = client.patch(
        f"/tickets/{ticket_id}/status?ticket_status=cancelled",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
    response = client.patch(
        f"/tickets/{ticket_id}/status?ticket_status=resolved",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot update resolved or cancelled ticket"


# admin update ticket status and get success
def test_admin_update_ticket_status(client):
    login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_id = ticket_response.json()["id"]
    response = client.patch(
        f"/tickets/{ticket_id}/status?ticket_status=resolved",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "resolved"


# admin update ticket to cancelled and get success  in this test we cover cancel the ticket and trying to cancel again
def test_admin_update_ticket_to_cancelled(client):
    login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_id = ticket_response.json()["id"]
    response = client.patch(
        f"/tickets/{ticket_id}/status?ticket_status=cancelled",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
    response = client.patch(
        f"/tickets/{ticket_id}/status?ticket_status=resolved",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot update resolved or cancelled ticket"


# admin update ticket status and get error if ticket not found
def test_admin_update_ticket_status_not_found(client):
    login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    token = login_response.json()["access_token"]
    response = client.patch(
        "/tickets/999/status?ticket_status=resolved",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


# admin update resolved ticket and get error
def test_admin_update_resolved_ticket(client):
    login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_id = ticket_response.json()["id"]
    response = client.patch(
        f"/tickets/{ticket_id}/status?ticket_status=resolved",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "resolved"
    response = client.patch(
        f"/tickets/{ticket_id}/status?ticket_status=resolved",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot update resolved or cancelled ticket"


# customer update ticket status and get error
def test_customer_update_ticket_status(client):
    admin_reponse = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    admin_token = admin_reponse.json()["access_token"]
    login_response = client.post(
        "/login", data={"username": customer_email, "password": "Raj@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_id = ticket_response.json()["id"]
    response = client.patch(
        f"/tickets/{ticket_id}/status?ticket_status=resolved",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Only agents and admins can update tickets"


# customer update ticket status and get error if ticket not found
def test_customer_update_ticket_status_not_found(client):
    login_response = client.post(
        "/login", data={"username": customer_email, "password": "Raj@07"}
    )
    token = login_response.json()["access_token"]
    response = client.patch(
        "/tickets/999/status?ticket_status=resolved",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Only agents and admins can update tickets"


# /tickets/{id}/assign
# customer assign ticket and get error
def test_customer_assign_ticket(client):
    agent_register = client.post(
        "/register",
        json={
            "name": "testagent",
            "email": "testaget07@gmail.com",
            "password": "John@07",
            "role": "agent",
        },
    )
    agent_id = agent_register.json()["id"]
    admin_reponse = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    admin_token = admin_reponse.json()["access_token"]
    login_response = client.post(
        "/login", data={"username": customer_email, "password": "Raj@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_id = ticket_response.json()["id"]
    response = client.patch(
        f"/tickets/{ticket_id}/assign?assign={agent_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Only admin can assign tickets"


# agent assign ticket and get error
def test_agent_assign_ticket(client):
    admin_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    admin_token = admin_response.json()["access_token"]
    agent_register = client.post(
        "/register",
        json={
            "name": "testagent",
            "email": "testaget07@gmail.com",
            "password": "John@07",
            "role": "agent",
        },
    )
    agent_id = agent_register.json()["id"]
    login_response = client.post(
        "/login", data={"username": agent_email, "password": "Mayur@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_id = ticket_response.json()["id"]
    response = client.patch(
        f"/tickets/{ticket_id}/assign?assign={agent_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Only admin can assign tickets"


# admin assign ticket and get success
def test_admin_assign_ticket(client):
    admin_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    print("admin_response", admin_response)
    admin_token = admin_response.json()["access_token"]
    agent_register = client.post(
        "/register",
        json={
            "name": "testagent",
            "email": "testaget07@gmail.com",
            "password": "John@07",
            "role": "agent",
        },
    )
    print("agent_register", agent_register)
    agent_id = agent_register.json()["id"]
    login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    print("login_response", login_response)
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    print("ticket_response", ticket_response)
    ticket_id = ticket_response.json()["id"]
    response = client.patch(
        f"/tickets/{ticket_id}/assign?assign={agent_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    print("response.status_code", response.status_code)
    print("response.json():", response.json())
    assert response.status_code == 200


# admin assign ticket and get error if ticket not found
def test_admin_assign_ticket_not_found(client):
    login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    token = login_response.json()["access_token"]
    response = client.patch(
        "/tickets/999/assign?assign=999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


# admin assign ticket and get error if agent not found
def test_admin_assign_ticket_agent_not_found(client):
    login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_id = ticket_response.json()["id"]
    response = client.patch(
        f"/tickets/{ticket_id}/assign?assign=999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


# not assign resolved ticket
def test_not_assign_resolved_ticket(client):
    agent_register = client.post(
        "/register",
        json={
            "name": "testagent",
            "email": "testaget07@gmail.com",
            "password": "John@07",
            "role": "agent",
        },
    )
    agent_id = agent_register.json()["id"]
    admin_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    admin_token = admin_response.json()["access_token"]
    login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_id = ticket_response.json()["id"]
    response = client.patch(
        f"/tickets/{ticket_id}/status?ticket_status=resolved",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    response = client.patch(
        f"/tickets/{ticket_id}/assign?assign={agent_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot assign resolved or cancelled ticket"


# cannot assign cancel ticket
def test_cannot_assign_cancel_ticket(client):
    agent_register = client.post(
        "/register",
        json={
            "name": "testagent",
            "email": "testaget07@gmail.com",
            "password": "John@07",
            "role": "agent",
        },
    )
    agent_id = agent_register.json()["id"]
    admin_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    admin_token = admin_response.json()["access_token"]
    login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_id = ticket_response.json()["id"]
    response = client.patch(
        f"/tickets/{ticket_id}/status?ticket_status=cancelled",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    response = client.patch(
        f"/tickets/{ticket_id}/assign?assign={agent_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot assign resolved or cancelled ticket"


# cannot assign to customer
def test_cannot_assign_to_customer(client):
    customer_register = client.post(
        "/register",
        json={
            "name": "testcustomer",
            "email": "testcustomer07@gmail.com",
            "password": "John@07",
            "role": "customer",
        },
    )
    customer_id = customer_register.json()["id"]
    admin_reponse = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    admin_token = admin_reponse.json()["access_token"]
    login_response = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_id = ticket_response.json()["id"]
    response = client.patch(
        f"/tickets/{ticket_id}/assign?assign={customer_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Only agents can be assigned tickets"


# patch("/tickets/customer/{ticket_id}"


# customer update ticket and get success
def test_customer_update_ticket(client):
    admin_reponse = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    admin_token = admin_reponse.json()["access_token"]
    login_response = client.post(
        "/login", data={"username": customer_email, "password": "Raj@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_id = ticket_response.json()["id"]
    response = client.patch(
        f"/tickets/customer/{ticket_id}",
        json={"title": "Test Category", "description": "there is silly mistake"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test Category"
    assert response.json()["description"] == "there is silly mistake"


# customer update ticket and get error if ticket is not found
def test_customer_update_ticket_not_found(client):
    login_response = client.post(
        "/login", data={"username": customer_email, "password": "Raj@07"}
    )
    token = login_response.json()["access_token"]
    response = client.patch(
        "/tickets/customer/999",
        json={"title": "Test Category", "description": "there is silly mistake"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


# cannot update resolved ticket
def test_cannot_update_resolved_ticket(client):
    admin_respomse = client.post(
        "/login", data={"username": admin_email, "password": "Mukund@07"}
    )
    admin_token = admin_respomse.json()["access_token"]

    agent_login = client.post(
        "/login", data={"username": agent_email, "password": "Mayur@07"}
    )
    agent_token = agent_login.json()["access_token"]

    login_response = client.post(
        "/login", data={"username": customer_email, "password": "Raj@07"}
    )
    token = login_response.json()["access_token"]
    category_response = client.post(
        "/categories",
        json={"name": "Test Category", "description": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    ticket_response = client.post(
        "/tickets",
        json={"title": "Test Category", "description": "Test", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ticket_id = ticket_response.json()["id"]
    response = client.patch(
        f"/tickets/{ticket_id}/status?ticket_status=resolved",
        headers={"Authorization": f"Bearer {agent_token}"},
    )
    assert response.status_code == 200
    response = client.patch(
        f"/tickets/customer/{ticket_id}",
        json={"title": "Test Category", "description": "there is silly mistake"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot update resolved or cancelled ticket"
