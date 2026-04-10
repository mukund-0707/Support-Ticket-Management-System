from models.tickets import Ticket
from fastapi import APIRouter, Depends, HTTPException, status
from app.database import db_dependecies
from models.comments import Comment
from models.users import User
from schemas.comment_schema import CommentCreate, CommentResponse
from utils.role import get_current_user
from services.notification_service import notify_user

router = APIRouter(tags=["Comments"])


@router.post("/comments", response_model=CommentResponse)
def create_comment(
    comment: CommentCreate,
    db: db_dependecies,
    current_user: User = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to comment on tickets",
        )
    ticket = db.query(Ticket).filter(Ticket.id == comment.ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
        )
    if current_user.role == "customer":
        ticket = (
            db.query(Ticket)
            .filter(
                Ticket.id == comment.ticket_id, Ticket.created_by == current_user.id
            )
            .first()
        )
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can't comment on others tickets",
            )
    new_comment = Comment(
        ticket_id=comment.ticket_id, user_id=current_user.id, message=comment.message
    )
    if not new_comment.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment message cannot be empty",
        )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

# Notify ticket owner, assigned agent and admins about new comment
    ticket = db.query(Ticket).filter(Ticket.id == comment.ticket_id).first()
    if ticket:
        ticket_owner = db.query(User).filter(User.id == ticket.created_by).first()
        if ticket_owner:
            notify_user(
                user_id=ticket_owner.id,
                message=f"New comment on your ticket: {ticket.title}\nComment: {new_comment.message}",
                db=db,
            )
        assigned_agent = db.query(User).filter(User.id == ticket.assigned_to).first()
        if assigned_agent:
            notify_user(
                user_id=assigned_agent.id,
                message=f"New comment on assigned ticket: {ticket.title}\nComment: {new_comment.message}",
                db=db,
            )
        admin_users = db.query(User).filter(User.role == "admin").first()
        if admin_users:
            notify_user(
                user_id=admin_users.id,
                message=f"New comment on ticket: {ticket.title}\nComment: {new_comment.message}",
                db=db,
            )
    return new_comment


@router.get("/tickets/{ticket_id}/comments", response_model=list[CommentResponse])
def get_comments(
    ticket_id: int, db: db_dependecies, current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to view comments on tickets",
        )
    comments = db.query(Comment).filter(Comment.ticket_id == ticket_id).all()
    if not comments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comments not found"
        )
    return comments
