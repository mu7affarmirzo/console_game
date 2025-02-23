# server_main.py
from fastapi import FastAPI

from server.api.main_router import v1_router

app = FastAPI()

app.include_router(v1_router, prefix="/api/v1")

