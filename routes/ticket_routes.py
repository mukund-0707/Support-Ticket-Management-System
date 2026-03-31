from fastapi import APIRouter, Depends,HTTPException,status
from app.database import db_dependecies
from models.tickets import Ticket
from schemas.ticket_schema import TicketCreate,TicketResponse,TicketStatus
from utils.role import get_current_user
from models.users import User

router = APIRouter()

@router.post("/tickets",response_model=TicketResponse)
def create_ticket(ticket:TicketCreate,db:db_dependecies,current_user:User = Depends(get_current_user)):
    if not ticket.description.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Description cannot be empty")
    new_ticket = Ticket(
        title = ticket.title,
        description = ticket.description,
        priority = ticket.priority.value,
        created_by = current_user.id
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return new_ticket

@router.get("/tickets/filter",response_model=list[TicketResponse])
def get_tickets_by_status(status_code:TicketStatus,db:db_dependecies,current_user:User = Depends(get_current_user)):
    if not (current_user.role == "agent" or current_user.role == "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only agents and admins can view tickets")
    tickets = db.query(Ticket).filter(Ticket.status == status_code.value).all()
    return tickets

@router.get("/tickets",response_model=list[TicketResponse])
def get_tickets(db:db_dependecies,current_user:User = Depends(get_current_user)):
    if not (current_user.role == "agent" or current_user.role == "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only agents and admins can view tickets")
    tickets = db.query(Ticket).all()
    return tickets

@router.get("/tickets/my-tickets",response_model=list[TicketResponse])
def get_ticket(db:db_dependecies,current_user:User = Depends(get_current_user)):
    ticket = db.query(Ticket).filter(Ticket.created_by == current_user.id).all()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Ticket not found")
    return ticket

@router.patch("/tickets/{id}/status",response_model=TicketResponse)
def update_ticket_status(id:int,ticket_status:TicketStatus,db:db_dependecies,current_user:User = Depends(get_current_user)):
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
    return ticket

@router.patch("/tickets/{id}/assign",response_model=TicketResponse)
def update_ticket_assign(id:int,assign:int,db:db_dependecies,current_user:User = Depends(get_current_user)):
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
    return ticket

