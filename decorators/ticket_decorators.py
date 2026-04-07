from services.send_email import send_email
from functools import wraps
import inspect
from fastapi import HTTPException, status
from models.tickets import Ticket
from models.users import User
from schemas.ticket_schema import TicketStatus


def require_roles(allowed_roles: list):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(status_code=500, detail="User not found in request")

            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have required permissions to perform this action",
                )

            result = func(*args, **kwargs)
            if inspect.isawaitable(result):
                return await result
            return result

        return wrapper

    return decorator


def validate_cancel_reason(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        ticket_status = kwargs.get("ticket_status")
        if not ticket_status:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ticket status not found in request",
            )

        if ticket_status.status == TicketStatus.CANCELLED and not ticket_status.reason:
            raise HTTPException(
                status_code=400, detail="Reason required for cancellation"
            )
        elif ticket_status.status != TicketStatus.CANCELLED and ticket_status.reason:
            raise HTTPException(
                status_code=400, detail="Reason only allowed for cancelled ticket"
            )

        return await func(*args, **kwargs)

    return wrapper


# could not update same status of ticket, for example if ticket is already cancelled, it cannot be cancelled again, or if it is already resolved, it cannot be resolved again
def validate_ticket_status(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        db = kwargs.get("db")
        print("DB in decorator:", db)
        ticket_id = kwargs.get("id")
        print("Ticket ID in decorator:", ticket_id)
        ticket_status = kwargs.get("ticket_status")
        print("Ticket status in decorator:", ticket_status)

        if not ticket_id or not ticket_status:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ticket ID or status not found in request",
            )
        if not db:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session not found in request",
            )
        existing_ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not existing_ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        if (
            existing_ticket.status == TicketStatus.RESOLVED
            or existing_ticket.status == TicketStatus.CANCELLED
        ):
            raise HTTPException(
                status_code=400, detail="Cannot update resolved or cancelled ticket"
            )
        if existing_ticket.status == ticket_status.status:
            raise HTTPException(
                status_code=400,
                detail=f"Ticket is already in '{ticket_status.status.value}' status",
            )

        return await func(*args, **kwargs)

    return wrapper


def notify_agents(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)

        db = kwargs.get("db")
        background_tasks = kwargs.get("background_tasks")
        if not db or not background_tasks:
            return result
        agents = db.query(User).filter(User.role == "agent").all()
        if not agents:
            return result
        for agent in agents:
            background_tasks.add_task(
                send_email,
                agent.email,
                "New Ticket Created",
                f"New ticket created:\n\nTitle: {result.title}\nPriority: {result.priority}",
            )

        return result

    return wrapper


def notify_customer_on_status_change(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)

        db = kwargs.get("db")
        background_tasks = kwargs.get("background_tasks")
        ticket_status = kwargs.get("ticket_status")
        if not db or not background_tasks or not ticket_status:
            return result
        customer = db.query(User).filter(User.id == result.created_by).first()

        if customer:
            if ticket_status.status == TicketStatus.IN_PROGRESS:
                subject = "Ticket In Progress"
                body = f"Your ticket '{result.title}' is now in progress."

            elif ticket_status.status == TicketStatus.RESOLVED:
                subject = "Ticket Resolved"
                body = f"Your ticket '{result.title}' has been resolved."

            elif ticket_status.status == TicketStatus.CANCELLED:
                subject = "Ticket Cancelled"
                body = f"Your ticket '{result.title}' has been cancelled.\nReason: {ticket_status.reason}"

            else:
                subject = "Ticket Status Updated"
                body = f"Your ticket '{result.title}' status updated to {ticket_status.status.value}"

            background_tasks.add_task(send_email, customer.email, subject, body)

        return result

    return wrapper
