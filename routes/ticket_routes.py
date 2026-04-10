from decorators.ticket_decorators import (
    notify_agents,
    notify_customer_on_status_change,
    require_roles,
    validate_cancel_reason,
    validate_ticket_status,
)
from schemas.ticket_schema import TicketPriority
from schemas.ticket_schema import TicketUpdate
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from app.database import db_dependecies
from models.tickets import Ticket
from models.cancelled_tickets import CancelledTicket
from schemas.ticket_schema import (
    TicketCreate,
    TicketResponse,
    TicketStatus,
    TicketStatusUpdate,
)
from utils.role import get_current_user
from services.notification_service import notify_user
from models.users import User
from services.cache import delete_pattern, get_cache, set_cache
from services.ai_services import generate_description
from models.category import Category

router = APIRouter(tags=["Tickets"])


@router.post("/tickets", response_model=TicketResponse)
@notify_agents
async def create_ticket(
    ticket: TicketCreate,
    db: db_dependecies,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
):
    if not ticket.description.strip() or not ticket.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Description and title cannot be empty",
        )
    category = db.query(Category).filter(Category.name == ticket.title).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    user_desc = ticket.description
    ai_desc = generate_description(user_desc)
    ticket.description = ai_desc
    new_ticket = Ticket(
        title=ticket.title,
        description=ticket.description,
        priority=ticket.priority.value,
        category_id=category.id,
        created_by=current_user.id,
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    # Notify agents and admin about new ticket
    if db.refresh(new_ticket):
        agents = db.query(User).filter(User.role == "agent").all()
        for agent in agents:
            notify_user(
                user_id=agent.id,
                message=f"New ticket created: {new_ticket.title}",
                db=db,
            )
        admin = db.query(User).filter(User.role == "admin").first()
        if admin:
            notify_user(
                user_id=admin.id,
                message=f"New ticket created: {new_ticket.title}",
                db=db,
            )

    await delete_pattern("tickets:priority:*")
    await delete_pattern("tickets:list:*")
    await delete_pattern("tickets:status:*")
    await delete_pattern("tickets:user:*")

    return new_ticket


@router.get("/tickets/by-id/{id}", response_model=TicketResponse)
async def get_ticket_by_id(
    id: int, db: db_dependecies, current_user: User = Depends(get_current_user)
):
    if current_user.role == "customer":
        ticket = (
            db.query(Ticket)
            .filter(Ticket.id == id, Ticket.created_by == current_user.id)
            .first()
        )
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can't view others tickets",
            )
    cache_key = f"tickets:{id}"
    cached_ticket = await get_cache(cache_key)
    if cached_ticket:
        return cached_ticket
    ticket = db.query(Ticket).filter(Ticket.id == id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
        )
    await set_cache(cache_key, ticket, expire=120)
    return ticket


@router.get("/tickets/by-priority", response_model=list[TicketResponse])
@require_roles(["agent", "admin"])
async def get_tickets_by_priority(
    priority: TicketPriority,
    db: db_dependecies,
    current_user: User = Depends(get_current_user),
):
    cache_key = f"tickets:priority:{priority.value}"
    cached_tickets = await get_cache(cache_key)
    if cached_tickets:
        return cached_tickets
    tickets = (
        db.query(Ticket)
        .filter(
            Ticket.priority == priority.value,
            Ticket.status != TicketStatus.RESOLVED,
            Ticket.status != TicketStatus.CANCELLED,
        )
        .all()
    )
    if not tickets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tickets not found"
        )
    await set_cache(cache_key, tickets, expire=120)
    return tickets


@router.get("/tickets/filter", response_model=list[TicketResponse])
@require_roles(["agent", "admin"])
async def get_tickets_by_status(
    status_code: TicketStatus,
    db: db_dependecies,
    current_user: User = Depends(get_current_user),
):
    cache_key = f"tickets:status:{status_code.value}"
    cached_tickets = await get_cache(cache_key)
    if cached_tickets:
        return cached_tickets
    tickets = db.query(Ticket).filter(Ticket.status == status_code.value).all()
    if not tickets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tickets not found"
        )
    await set_cache(cache_key, tickets, expire=120)
    return tickets


@router.get("/tickets", response_model=list[TicketResponse])
@require_roles(["agent", "admin"])
async def get_tickets(
    db: db_dependecies,
    current_user: User = Depends(get_current_user),
    page: int = 1,
    page_size: int = 10,
):
    cache_key = f"tickets:list:{page}:{page_size}"
    cached_tickets = await get_cache(cache_key)
    if cached_tickets:
        return cached_tickets
    tickets = db.query(Ticket).offset((page - 1) * page_size).limit(page_size).all()
    if not tickets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tickets not found"
        )
    await set_cache(cache_key, tickets, expire=120)
    return tickets


@router.get("/tickets/my-tickets", response_model=list[TicketResponse])
async def get_ticket(
    db: db_dependecies, current_user: User = Depends(get_current_user)
):
    cache_key = f"tickets:user:{current_user.id}"
    cached_tickets = await get_cache(cache_key)
    if cached_tickets:
        return cached_tickets
    if current_user.role == "customer":
        ticket = db.query(Ticket).filter(Ticket.created_by == current_user.id).all()
    elif current_user.role == "agent":
        ticket = db.query(Ticket).filter(Ticket.assigned_to == current_user.id).all()
    elif current_user.role == "admin":
        ticket = db.query(Ticket).all()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
        )
    await set_cache(cache_key, ticket, expire=120)
    return ticket


@router.patch("/tickets/{id}/status", response_model=TicketResponse)
@require_roles(["agent", "admin"])
@validate_ticket_status
@validate_cancel_reason
@notify_customer_on_status_change
async def update_ticket_status(
    id: int,
    ticket_status: TicketStatusUpdate,
    background_tasks: BackgroundTasks,
    db: db_dependecies,
    current_user: User = Depends(get_current_user),
):

    ticket = db.query(Ticket).filter(Ticket.id == id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
        )
    if (
        ticket.assigned_to
        and current_user.role == "agent"
        and ticket.assigned_to != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Agents can only update tickets assigned to them",
        )

    ticket.status = ticket_status.status.value
    if ticket_status.status == TicketStatus.CANCELLED:
        cancelled_ticket = CancelledTicket(
            ticket_id=ticket.id, reason=ticket_status.reason
        )
        db.add(cancelled_ticket)
    db.commit()
    db.refresh(ticket)
    if ticket:
        customer = db.query(User).filter(User.id == ticket.created_by).first()
        if customer:
             notify_user(
                user_id=customer.id,
                message=f"Ticket status updated: {ticket.title}\nNew status: {ticket.status}",
                db=db,
            )
    await delete_pattern(f"tickets:{id}")
    await delete_pattern("tickets:priority:*")
    await delete_pattern("tickets:list:*")
    await delete_pattern("tickets:status:*")
    await delete_pattern("tickets:user:*")

    # customer = db.query(User).filter(User.id == ticket.created_by).first()
    # if customer:
    #     if ticket_status.status == TicketStatus.IN_PROGRESS:
    #         email_subject = "Ticket In Progress"
    #         email_body = f"Your ticket '{ticket.title}' is now in progress."
    #         print("Ticket In Progress", ticket_status)
    #     elif ticket_status.status == TicketStatus.RESOLVED:
    #         email_subject = "Ticket Resolved"
    #         email_body = f"Your ticket '{ticket.title}' has been resolved."
    #         print("Ticket Resolved", ticket_status)
    #     elif ticket_status.status == TicketStatus.CANCELLED:
    #         email_subject = "Ticket Cancelled"
    #         email_body = f"Your ticket '{ticket.title}' has been cancelled.\nReason: {ticket_status.reason}"
    #         print("Ticket Cancelled", ticket_status)
    #     else:
    #         email_subject = "Ticket Status Updated"
    #         email_body = f"Your ticket '{ticket.title}' status has been updated to {ticket_status.status.value}."
    #         print("Ticket Status Updated", ticket_status)
    #     background_tasks.add_task(send_email, customer.email, email_subject, email_body)
    return ticket


@router.patch("/tickets/{id}/assign", response_model=TicketResponse)
@require_roles(["admin"])
async def update_ticket_assign(
    id: int,
    assign: int,
    db: db_dependecies,
    current_user: User = Depends(get_current_user),
):
    ticket = db.query(Ticket).filter(Ticket.id == id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
        )
    if (
        ticket.status == TicketStatus.RESOLVED
        or ticket.status == TicketStatus.CANCELLED
    ):
        raise HTTPException(
            status_code=400, detail="Cannot assign resolved or cancelled ticket"
        )
    assign_user = db.query(User).filter(User.id == assign).first()
    if not assign_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if assign_user.role != "agent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only agents can be assigned tickets",
        )
    ticket.assigned_to = assign
    db.commit()
    db.refresh(ticket)
    if ticket:
        assigned_agent = db.query(User).filter(User.id == assign).first()
        if assigned_agent:
            notify_user(
                user_id=assigned_agent.id,
                message=f"You have been assigned a new ticket: {ticket.title}",
                db=db,
            )
    await delete_pattern(f"tickets:{id}")
    await delete_pattern("tickets:list:*")
    await delete_pattern("tickets:status:*")
    await delete_pattern("tickets:user:*")

    return ticket


@router.patch("/tickets/customer/{ticket_id}", response_model=TicketResponse)
@require_roles(["customer"])
async def update_ticket_customer(
    ticket_id: int,
    ticket_data: TicketUpdate,
    db: db_dependecies,
    current_user: User = Depends(get_current_user),
):
    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id, Ticket.created_by == current_user.id)
        .first()
    )
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
        )
    if (
        ticket.status == TicketStatus.RESOLVED
        or ticket.status == TicketStatus.CANCELLED
    ):
        raise HTTPException(
            status_code=400, detail="Cannot update resolved or cancelled ticket"
        )
    if ticket_data.title:
        ticket.title = ticket_data.title
    if ticket_data.description:
        ticket.description = ticket_data.description
    db.commit()
    db.refresh(ticket)
    if ticket:
        customer = db.query(User).filter(User.id == ticket.created_by).first()
        if customer:
             notify_user(
                user_id=customer.id,
                message=f"Your ticket has been updated: {ticket.title}",
                db=db,
            )
    await delete_pattern(f"tickets:{ticket_id}")
    await delete_pattern("tickets:list:*")
    await delete_pattern("tickets:user:*")

    return ticket
