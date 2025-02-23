from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from server.api.schemas.auth import LoginSchema
from server.db.models.all import Account
from server.utils.exception_handlers import handle_exceptions


class LoginService:
    def __init__(self, db: Session):
        self.db = db

    @handle_exceptions
    async def authenticate(self, nickname: LoginSchema) -> JSONResponse:

        user = self.db.query(Account).filter(Account.nickname == nickname.nickname).first()
        if not user:
            # Create a new user if it doesn't exist
            user = Account(nickname=nickname, credits=100)  # Default credits
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        return JSONResponse(content={"message": "Authentication Success", "token": "SOME_GENERATED_TOKEN"}, status_code=200)


