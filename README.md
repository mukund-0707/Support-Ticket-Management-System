# 🎫 Support Ticket Management System

A backend API system for managing customer support tickets, built with **FastAPI**, **PostgreSQL**, and **Redis**.

## Tech Stack

- **FastAPI** — REST API framework
- **PostgreSQL** — Database (SQLAlchemy ORM)
- **Redis** — Caching layer
- **JWT** — Authentication (python-jose + bcrypt)
- **SMTP** — Email notifications (Gmail)

---

## ⚙️ Setup & Run

### Prerequisites

- Python 3.10+
- PostgreSQL running on `localhost:5432`
- Redis running on `localhost:6379`

### 1. Clone & Install

```bash
git clone https://github.com/mukund-0707/Support-Ticket-Management-System.git
cd Support-Ticket-Management-System
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Create PostgreSQL Database

```sql
CREATE DATABASE "SupportTicket";
```

> Tables are auto-created on startup via SQLAlchemy `create_all()`.

### 3. Environment Configuration

Update the following values in the source files (or move to `.env`):

| Config | File | Current Value |
|--------|------|---------------|
| Database URL | `app/database.py` | `postgresql://postgres:1234@localhost:5432/SupportTicket` |
| JWT Secret | `utils/security.py` | `SECRET_KEY` |
| Email credentials | `services/send_email.py` | Gmail app password |

### 4. Run the Server

```bash
uvicorn app.main:app --reload
```

Server starts at: **http://localhost:8000**
Swagger docs at: **http://localhost:8000/docs**

---

## 📡 API Endpoints

### Auth

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/register` | Create new user account | Public |
| POST | `/login` | Login & get JWT token | Public |

### Tickets

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/tickets` | Create a new ticket | Any logged-in user |
| GET | `/tickets/{id}` | View a single ticket | Any logged-in user |
| GET | `/tickets` | List all tickets (paginated) | Agent / Admin |
| GET | `/tickets/my-tickets` | View own tickets | Any logged-in user |
| GET | `/tickets/filter?status_code=` | Filter by status | Agent / Admin |
| GET | `/tickets/priority?priority=` | Filter by priority | Agent / Admin |
| PATCH | `/tickets/{id}/status` | Update ticket status | Agent / Admin |
| PATCH | `/tickets/{id}/assign` | Assign ticket to agent | Admin |
| PATCH | `/tickets/customer/{ticket_id}` | Edit own ticket | Customer only |

### Comments

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/comments` | Add comment to ticket | Any logged-in user* |
| GET | `/tickets/{ticket_id}/comments` | View ticket comments | Any logged-in user |

> \*Customers can only comment on their own tickets.

---

## 🔐 Roles

| Role | Permissions |
|------|-------------|
| **Customer** | Create tickets, view/edit own tickets, comment on own tickets |
| **Agent** | View all tickets, update status, filter & assign tickets, comment on any ticket |
| **Admin** | All agent permissions + assign tickets to agents |

---

## 🚀 Key Features

- **JWT Authentication** — Secure token-based auth with 30-min expiry
- **Role-Based Access Control** — Customer / Agent / Admin permissions
- **Redis Caching** — Ticket lists cached (120s TTL) with auto-invalidation on writes
- **Background Email Notifications** — Non-blocking SMTP emails via FastAPI BackgroundTasks
  - New ticket → all agents notified
  - Status change → customer notified
  - Resolved → customer gets confirmation
- **Pagination** — `page` & `page_size` query params on ticket list
- **Input Validation** — Empty title/description/comments rejected
- **Resolved Ticket Protection** — Resolved tickets cannot be edited or reassigned

---

## 📁 Project Structure

```
Support-Ticket-Management-System/
├── app/
│   ├── main.py              # FastAPI app entry point
│   └── database.py          # PostgreSQL connection & session
├── models/
│   ├── users.py             # User table
│   ├── tickets.py           # Ticket table
│   └── comments.py          # Comment table
├── schemas/
│   ├── user_schema.py       # User Pydantic schemas
│   ├── ticket_schema.py     # Ticket Pydantic schemas
│   └── comment_schema.py    # Comment Pydantic schemas
├── routes/
│   ├── auth_routes.py       # Register & Login APIs
│   ├── ticket_routes.py     # All ticket CRUD APIs
│   └── comment_routes.py    # Comment APIs
├── services/
│   ├── cache.py             # Redis get/set/delete helpers
│   └── send_email.py        # SMTP email sender
├── utils/
│   ├── security.py          # JWT + bcrypt utilities
│   ├── role.py              # Auth guard (get_current_user)
│   └── redis_connection.py  # Redis client setup
├── requirements.txt
└── README.md
```

---

## 🗄️ Database Schema

```
users
├── id (PK)
├── name
├── email
├── password (hashed)
├── role (customer/agent/admin)
└── created_at

tickets
├── id (PK)
├── title
├── description
├── priority (low/medium/high)
├── status (open/in_progress/resolved)
├── created_by (FK → users.id)
├── assigned_to (FK → users.id, nullable)
├── created_at
└── updated_at

comments
├── id (PK)
├── ticket_id (FK → tickets.id)
├── user_id (FK → users.id)
├── message
├── created_at
└── updated_at
```