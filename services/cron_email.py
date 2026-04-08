from models.users import User
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from datetime import datetime, timedelta
from app.database import SessionLocal
from models.tickets import Ticket
from sqlalchemy import or_
from services.send_email import send_email

logging.basicConfig(level=logging.INFO)

scheduler = BackgroundScheduler()


def check_inactive_tickets():
    db = SessionLocal()

    twelve_hours_ago = datetime.utcnow() - timedelta(hours=12)
    print("TWELVE HOURS AGO:", twelve_hours_ago)

    tickets = (
        db.query(Ticket)
        .filter(
            Ticket.assigned_to != None,
            Ticket.status == "open",
            Ticket.updated_at <= twelve_hours_ago,
            or_(
                Ticket.last_reminder_sent_at == None,
                Ticket.last_reminder_sent_at <= twelve_hours_ago,
            ),
        )
        .all()
    )
    print("NOW:", datetime.utcnow())
    print("12 sec ago:", twelve_hours_ago)
    print("TICKETS:", tickets)
    for ticket in tickets:
        agent = db.query(User).filter(User.id == ticket.assigned_to).first()
        print("agent", agent)
        if agent:
            send_email(
                to_email=agent.email,
                subject="Ticket Reminder",
                body=f"Please update ticket ID {ticket.id}. No activity in last 12 hours.",
            )

            ticket.last_reminder_sent_at = datetime.utcnow()
            db.commit()
        else:
            print("No tickets found")
    db.close()


def start():
    scheduler.add_job(check_inactive_tickets, "interval", seconds=10)
    scheduler.start()
    logging.info("Scheduler started...")
