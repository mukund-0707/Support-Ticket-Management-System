from schemas.ticket_schema import TicketPriority
from schemas.ticket_schema import TicketUpdate
from fastapi import APIRouter, Depends,HTTPException,status,BackgroundTasks
from app.database import db_dependecies
from models.tickets import Ticket
from schemas.ticket_schema import TicketCreate,TicketResponse,TicketStatus
from utils.role import get_current_user
from models.users import User
from services.cache import delete_pattern, get_cache, set_cache
from services.send_email import send_email


router = APIRouter(tags=["Tickets"])


@router.post("/tickets",response_model=TicketResponse)
async def create_ticket(ticket:TicketCreate,db:db_dependecies,background_tasks: BackgroundTasks,current_user:User = Depends(get_current_user)):
    if not ticket.description.strip() or not ticket.title.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Description and title cannot be empty")
    new_ticket = Ticket(
        title = ticket.title,
        description = ticket.description,
        priority = ticket.priority.value,
        created_by = current_user.id
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    await delete_pattern("tickets:list:*")
    await delete_pattern("tickets:status:*")

    agents = db.query(User).filter(User.role == "agent").all()

    for agent in agents:
        background_tasks.add_task(
            send_email,
            agent.email,
            "New Ticket Created",
            f"New ticket created:\n\nTitle: {new_ticket.title}\nPriority: {new_ticket.priority}"
        )
    return new_ticket

@router.get("/tickets/by-id/{id}",response_model=TicketResponse)
async def get_ticket_by_id(id:int,db:db_dependecies,current_user:User = Depends(get_current_user)):
    if current_user.role == "customer":
        ticket = db.query(Ticket).filter(Ticket.id == id, Ticket.created_by == current_user.id).first()
        if not ticket:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't view others tickets")
    cache_key = f"tickets:{id}"
    cached_ticket = await get_cache(cache_key)
    if cached_ticket:
        return cached_ticket
    ticket = db.query(Ticket).filter(Ticket.id == id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Ticket not found")
    await set_cache(cache_key, ticket,expire=120)
    return ticket

@router.get("/tickets/by-priority",response_model=list[TicketResponse])
async def get_tickets_by_priority(priority:TicketPriority,db:db_dependecies,current_user:User = Depends(get_current_user)):
    if not (current_user.role == "agent" or current_user.role == "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only agents and admins can view tickets")
    cache_key = f"tickets:priority:{priority.value}"
    cached_tickets = await get_cache(cache_key)
    if cached_tickets:
        return cached_tickets
    tickets = db.query(Ticket).filter(Ticket.priority == priority.value,Ticket.status != "resolved").all()
    if not tickets:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Tickets not found")
    await set_cache(cache_key, tickets,expire=120)
    return tickets

@router.get("/tickets/filter",response_model=list[TicketResponse])
async def get_tickets_by_status(status_code:TicketStatus,db:db_dependecies,current_user:User = Depends(get_current_user)):
    if not (current_user.role == "agent" or current_user.role == "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only agents and admins can view tickets")
    cache_key = f"tickets:status:{status_code.value}"
    cached_tickets = await get_cache(cache_key)
    if cached_tickets:
        return cached_tickets
    tickets = db.query(Ticket).filter(Ticket.status == status_code.value).all()
    if not tickets:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Tickets not found")
    await set_cache(cache_key, tickets,expire=120)
    return tickets

@router.get("/tickets",response_model=list[TicketResponse])
async def get_tickets(db:db_dependecies,current_user:User = Depends(get_current_user),page:int = 1, page_size:int = 10):
    if not (current_user.role == "agent" or current_user.role == "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only agents and admins can view tickets")
    cache_key = f"tickets:list:{page}:{page_size}"
    cached_tickets = await get_cache(cache_key)
    if cached_tickets:
        return cached_tickets
    tickets = db.query(Ticket).offset((page - 1) * page_size).limit(page_size).all()
    if not tickets:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Tickets not found")
    await set_cache(cache_key, tickets,expire=120)
    return tickets

@router.get("/tickets/my-tickets",response_model=list[TicketResponse])
async def get_ticket(db:db_dependecies,current_user:User = Depends(get_current_user)):
    cache_key = f"tickets:user:{current_user.id}"
    cached_tickets = await get_cache(cache_key)
    if cached_tickets:
        return cached_tickets
    ticket = db.query(Ticket).filter(Ticket.created_by == current_user.id).all()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Ticket not found")
    await set_cache(cache_key, ticket,expire=120)
    return ticket

@router.patch("/tickets/{id}/status",response_model=TicketResponse)
async def update_ticket_status(id:int,ticket_status:TicketStatus,background_tasks: BackgroundTasks,db:db_dependecies,current_user:User = Depends(get_current_user)):
    if not (current_user.role == "agent" or current_user.role == "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only agents and admins can update tickets")
    ticket = db.query(Ticket).filter(Ticket.id == id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Ticket not found")
    if ticket.status == "resolved":
        raise HTTPException(status_code=400, detail="Cannot update resolved ticket")
    ticket.status = ticket_status.value
    db.commit()
    db.refresh(ticket)
    await delete_pattern("tickets:list:*")
    await delete_pattern("tickets:status:*")
    await delete_pattern("tickets:user:*")
    
    customer = db.query(User).filter(User.id == ticket.created_by).first()
    if customer:
        if ticket_status == TicketStatus.IN_PROGRESS:
            email_subject = "Ticket In Progress"
            email_body = f"Your ticket '{ticket.title}' is now in progress."
        elif ticket_status == TicketStatus.RESOLVED:
            email_subject = "Ticket Resolved"
            email_body = f"Your ticket '{ticket.title}' has been resolved."
        else:
            email_subject = "Ticket Status Updated"
            email_body = f"Your ticket '{ticket.title}' status has been updated to {ticket_status.value}."
        background_tasks.add_task(
            send_email,
            customer.email,
            email_subject,
            email_body
        )
    return ticket

@router.patch("/tickets/{id}/assign",response_model=TicketResponse)
async def update_ticket_assign(id:int,assign:int,db:db_dependecies,current_user:User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only admin can assign tickets")
    ticket = db.query(Ticket).filter(Ticket.id == id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Ticket not found")
    if ticket.status == "resolved":
        raise HTTPException(status_code=400, detail="Cannot assign resolved ticket")
    assign_user = db.query(User).filter(User.id == assign).first()
    if not assign_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    if assign_user.role != "agent":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only agents can be assigned tickets")
    ticket.assigned_to = assign
    db.commit()
    db.refresh(ticket)
    await delete_pattern("tickets:list:*")
    await delete_pattern("tickets:status:*")

    return ticket

@router.patch("/tickets/customer/{ticket_id}",response_model=TicketResponse)
async def update_ticket_customer(ticket_id:int,ticket_data:TicketUpdate,db:db_dependecies,current_user:User = Depends(get_current_user)):
    if current_user.role != "customer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only customers can update tickets")
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id,Ticket.created_by == current_user.id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Ticket not found")
    if ticket.status == "resolved":
        raise HTTPException(status_code=400, detail="Cannot update resolved ticket")
    if ticket_data.title:
        ticket.title = ticket_data.title
    if ticket_data.description:
        ticket.description = ticket_data.description
    db.commit()
    db.refresh(ticket)
    await delete_pattern("tickets:list:*")
    await delete_pattern("tickets:user:*")

    return ticket
