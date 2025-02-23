from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from server.api.schemas.auth import LoginSchema
from server.api.services.auth_service import LoginService
from server.config.db import get_db

auth_routers = APIRouter()


@auth_routers.post("/login")
async def login_router(request: Request, username: LoginSchema, db: Session = Depends(get_db)) -> JSONResponse:
    login_service = LoginService(db)
    response = login_service.authenticate(username)
    return response_handler(request, response)

