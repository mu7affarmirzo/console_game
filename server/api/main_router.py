from fastapi import APIRouter
from server.api.routers.auth import auth_routers

v1_router = APIRouter()

v1_router.include_router(auth_routers, prefix="/auth")
