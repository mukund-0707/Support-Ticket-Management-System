from models.users import User
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from datetime import datetime, timedelta
from app.database import SessionLocal
from models.tickets import Ticket
from fastapi import BackgroundTasks

from services.send_email import send_email

logging.basicConfig(level=logging.INFO)

scheduler = BackgroundScheduler()


def check_inactive_tickets():
    db = SessionLocal()

    twelve_hours_ago = datetime.utcnow() - timedelta(hours=30)

    tickets = (
        db.query(Ticket)
        .filter(
            Ticket.assigned_to != None,
            Ticket.status == "open",
            Ticket.updated_at <= twelve_hours_ago,
        )
        .all()
    )

    for ticket in tickets:
        agent = db.query(User).filter(User.id == ticket.assigned_to).first()
        print("agent", agent)
        if agent:
            send_email(
                to_email=agent.email,
                subject="Ticket Reminder",
                body=f"Please update ticket ID {ticket.id}. No activity in last 12 hours.",
            )
        else:
            print("No tickets found")
    db.close()


def start():
    scheduler.add_job(check_inactive_tickets, "interval", hours=10)
    scheduler.start()
    logging.info("Scheduler started...")
