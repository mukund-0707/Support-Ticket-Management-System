from dotenv import load_dotenv
import os
from middleware.middleware import common_middleware, ActiveUserMiddleware
from services.cron_email import *

load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from routes import auth_routes, ticket_routes, comment_routes, category_routes
from models import users, tickets, comments, category, cancelled_tickets
from app.database import engine

users.Base.metadata.create_all(bind=engine)
tickets.Base.metadata.create_all(bind=engine)
comments.Base.metadata.create_all(bind=engine)
category.Base.metadata.create_all(bind=engine)
cancelled_tickets.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.middleware("http")(common_middleware)
app.add_middleware(ActiveUserMiddleware)


@app.on_event("startup")
def start_scheduler():
    start()


app.include_router(auth_routes.router)
app.include_router(ticket_routes.router)
app.include_router(comment_routes.router)
app.include_router(category_routes.router)
