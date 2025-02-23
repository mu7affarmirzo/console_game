import random
from datetime import timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from server.config.security import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, generate_access_token
from server.config.settings import MIN_CREDITS, MAX_CREDITS
from server.db.crud.account import get_user_by_nickname, create_user_with_nickname, get_token_by_account, update_token, \
    create_access_token
from server.db.models.all import Token
from server.utils.exception_handlers import handle_exceptions

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@handle_exceptions
async def authenticate_user(db: Session, nickname: str) -> JSONResponse:
    user = await get_or_create_user(db, nickname)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Some Error occurred!",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    generated_access_token = generate_access_token(
        data={"user": user.nickname}, expires_delta=access_token_expires
    )
    token = get_token_by_account(db, user.nickname)

    if not token:
        token = create_access_token(db, generated_access_token, access_token_expires)
    else:
        token = update_token(db, token, generated_access_token, access_token_expires)
    return JSONResponse(content={"token": token.token, "token_type": "bearer"}, status_code=status.HTTP_200_OK)


async def get_or_create_user(db: Session, nickname: str):
    user = get_user_by_nickname(db, nickname)
    if not user:
        bonus = random.randint(MIN_CREDITS, MAX_CREDITS)
        user = create_user_with_nickname(db, nickname, bonus)
        return user
    return user


# async def get_current_user(db: Session, token: Annotated[str, Depends(oauth2_scheme)]):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = TokenData(username=username)
#     except InvalidTokenError:
#         raise credentials_exception
#     user = get_user_by_nickname(db, nickname=token_data.username)
#     if user is None:
#         raise credentials_exception
#     return user


# class SecurityService:
#     def __init__(self):
#         self.account_manager: Optional[AccountManager] = None
#
#     def get_db(self):
#         db = SessionLocal()
#         try:
#             yield db
#         finally:
#             db.close()
#
#     async def get_account_manager(self, db: Session = Depends(get_db)) -> AccountManager:
#         if not self.account_manager:
#             self.account_manager = AccountManager(db)
#         return self.account_manager
#
#     async def authenticate_account(
#             self, nickname: str,
#             account_manager: AccountManager = Depends(get_account_manager)
#     ) -> bool:
#         account = account_manager.get_account_by_nickname(nickname)
#         if not account:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Invalid credentials",
#                 headers={"WWW-Authenticate": "Bearer"},
#             )
#
#         return True
#
#     async def get_current_account(
#             self, token: str = Depends(oauth2_scheme),
#             account_manager: AccountManager = Depends(get_account_manager)
#     ):
#         account = account_manager.get_account_by_nickname(token)
#         if not account:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Invalid authentication credentials",
#                 headers={"WWW-Authenticate": "Bearer"},
#             )
#         return account
#
#     async def _generate_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
#         expire = datetime.utcnow() + timedelta(minutes=expires_delta)
#         data.update({"exp": expire})
#         return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
#
#
#     async def _verify_token(self, token: str) -> Optional[str]:
#         try:
#             payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#             nickname: str = payload.get("sub")
#             if nickname is None:
#                 return None
#             return nickname
#         except JWTError:
#             return None




