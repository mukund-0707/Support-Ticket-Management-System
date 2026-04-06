from functools import wraps
from fastapi import HTTPException, status
from models.tickets import Ticket
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

            return await func(*args, **kwargs)

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
