# Support Ticket Management System

Backend API for customer support operations, built with FastAPI, PostgreSQL, and Redis.

## Tech Stack

- FastAPI
- SQLAlchemy + PostgreSQL
- Redis (async client)
- JWT auth (`python-jose`) + password hashing (`bcrypt`)
- OpenAI API (`gpt-4o-mini`) for ticket description enhancement
- APScheduler for periodic reminder jobs

## Features

- Role-based access control for `customer`, `agent`, and `admin`
- Ticket lifecycle with `open`, `in_progress`, `resolved`, `cancelled`
- Category-based ticket creation (title must match an existing category)
- Redis caching for ticket reads and filtered listings
- Auto cache invalidation on ticket mutations
- Background hooks for email notifications on ticket events
- Scheduled reminder job for stale assigned tickets

## API Overview

### Auth

| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | `/register` | Register a new user | Public |
| POST | `/login` | Login with `email` + `password` and get bearer token | Public |
| POST | `/forget-password` | Send OTP to registered email | Public |
| POST | `/verify-otp-reset-password` | Verify OTP and set new password | Public |
| POST | `/change-password` | Change password using current password | Authenticated |

Login request format:
- Content-Type: `application/x-www-form-urlencoded`
- Fields: `email`, `password`

Swagger usage:
1. Call `POST /login` with `email` and `password`.
2. Copy `access_token` from response.
3. Click `Authorize` in Swagger and paste only the token value.

Password reset flow:
1. Call `POST /forget-password` with email.
2. Read OTP from email.
3. Call `POST /verify-otp-reset-password` with `email`, `otp`, `new_password`.

Change password flow:
- Call `POST /change-password` with bearer token and JSON body:
`{"current_password":"...","new_password":"..."}`

### Categories

| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | `/categories` | Create category | Admin |

### Tickets

| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | `/tickets` | Create ticket | Authenticated |
| GET | `/tickets/by-id/{id}` | Get ticket by ID | Authenticated |
| GET | `/tickets/by-priority?priority=` | Filter by priority | Agent/Admin |
| GET | `/tickets/filter?status_code=` | Filter by status | Agent/Admin |
| GET | `/tickets` | List tickets (pagination) | Agent/Admin |
| GET | `/tickets/my-tickets` | List requester/assignee tickets | Authenticated |
| PATCH | `/tickets/{id}/status` | Update ticket status | Agent/Admin |
| PATCH | `/tickets/{id}/assign?assign=` | Assign to agent user ID | Admin |
| PATCH | `/tickets/customer/{ticket_id}` | Customer self-update | Customer |

### Comments

| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | `/comments` | Create comment | Authenticated |
| GET | `/tickets/{ticket_id}/comments` | List ticket comments | Authenticated |

Notes:
- Customers can comment only on their own tickets.
- Resolved/cancelled tickets cannot be updated or reassigned.

## Local Setup

### Prerequisites

- Python 3.10+
- PostgreSQL running on `localhost:5432`
- Redis running on `localhost:6379`

### Install

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Database

Create a database named `SupportTicket`:

```sql
CREATE DATABASE "SupportTicket";
```

Tables are created on app startup using SQLAlchemy metadata.

### Runtime Configuration

Current code uses hardcoded values for some settings:
- DB URL in `app/database.py`
- JWT secret in `utils/security.py`
- Redis host/port in `utils/redis_connection.py`

Environment variables currently used:
- `OPENAI_API_KEY` (read in `services/ai_services.py`)

### Run API

```bash
uvicorn app.main:app --reload
```

- API base: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`

## Testing

Run:

```bash
PYTHONPATH=. pytest
```

Tests use:
- a PostgreSQL test DB connection from `tests/conftest.py`
- mocked Redis operations
- disabled email sender in test fixtures

## Project Structure

```
Support-Ticket-Management-System/
├── app/
│   ├── main.py              # FastAPI app entry point
│   └── database.py          # PostgreSQL connection & session
├── decorators/
│   └── ticket_decorators.py # Ticket decorators
├── models/
│   ├── cancelled_tickets.py     # Cancelled tickets table
│   ├── category.py            # Categories table
│   ├── comments.py          # Comment table
│   ├── tickets.py           # Ticket table
│   └── users.py             # User table
├── schemas/
│   ├── category_schema.py             # Category Pydantic schemas
│   ├── comment_schema.py              # Comment Pydantic schemas
│   ├── ticket_schema.py               # Ticket Pydantic schemas
│   └── user_schema.py                 # User Pydantic schemas
├── routes/
│   ├── auth_routes.py       # Register & Login APIs
│   ├── category_routes.py   # Category APIs
│   ├── ticket_routes.py     # Ticket APIs
│   └── comment_routes.py    # Comment APIs
├── services/
│   ├── ai_services.py       # AI services
│   ├── auth_service.py      # Forgot/reset/change password logic
│   ├── cron_email.py        # Cron email sender
│   ├── cache.py             # Redis get/set/delete helpers
│   └── send_email.py        # SMTP email sender
├── tests/
│   ├── conftest.py          # Test fixtures
│   ├── auth_test.py         # Auth tests
│   ├── category_test.py     # Category tests
│   ├── comment_test.py      # Comment tests
│   ├── ticket_test.py       # Ticket tests
├── utils/
│   ├── security.py          # JWT + bcrypt utilities
│   ├── role.py              # Auth guard (get_current_user)
│   └── redis_connection.py  # Redis client setup
├── requirements.txt
└── README.md
