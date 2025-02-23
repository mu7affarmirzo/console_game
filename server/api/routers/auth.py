from typing import Annotated

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from server.api.schemas.auth import Token, LoginForm
from server.api.services.auth_service import authenticate_user
from server.api.services import account
from server.config.settings import get_db
from server.db.models.all import Account

auth_routers = APIRouter()


@auth_routers.post("/login")
async def login_for_access_token(
        form_data: Annotated[LoginForm, Depends()],
        db: Session = Depends(get_db),
) -> Token:
    response = await authenticate_user(db, form_data.nickname)
    return response


# @auth_routers.get("/users/me")
# async def my_account_router(
#         current_user: Annotated[Account, Depends(get_current_user)],
#         db: Session = Depends(get_db),
# ):
#     # response = authenticate_user(db, form_data.nickname)
#     return "response"
