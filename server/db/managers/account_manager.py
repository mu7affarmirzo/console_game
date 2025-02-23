import random
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from server.config.settings import MIN_CREDITS, MAX_CREDITS
from server.db.models.all import Account, ItemMaster, AccountItem, Token


class AccountManager:
    """
    Handles account operations: retrieval, creation, and login bonus updates.
    """
    def __init__(self, db: Session):
        self.db = db

    def get_account_by_nickname(self, nickname: str) -> Optional[Account]:
        return self.db.query(Account).filter(Account.nickname == nickname).first()

    def create_account(self, nickname: str) -> Account:
        bonus = random.randint(MIN_CREDITS, MAX_CREDITS)
        db_account = Account(nickname=nickname, credits=bonus)
        self.db.add(db_account)
        try:
            self.db.commit()
            self.db.refresh(db_account)
            return db_account
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Nickname already exists")

    def update_account_on_login(self, nickname):
        account = self.get_account_by_nickname(nickname)
        if account:
            bonus = random.randint(MIN_CREDITS, MAX_CREDITS)
            account.credits += bonus
            try:
                self.db.commit()
                self.db.refresh(account)
                return account
            except Exception as e:
                self.db.rollback()
                raise HTTPException(status_code=400, detail="Problem occurred while updating account!")
        return None


class TokenManager:
    def __init__(self, db: Session):
        self.db = db

    def get_token(self, token: str) -> Optional[Token]:
        return self.db.query(Token).filter(Token.token == token).first()

    def create_account(self, token: str, expires_at) -> Token:
        db_token = Token(token=token, expires_at=expires_at)
        self.db.add(db_token)
        try:
            self.db.commit()
            self.db.refresh(db_token)
            return db_token
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Unexpected error occurred")

    def update_token(self, token, expires_at) -> [Token, None]:
        token = self.get_token(token)
        if token:
            token.token = token
            token.expires_at = expires_at
            try:
                self.db.commit()
                self.db.refresh(token)
                return token
            except Exception as e:
                self.db.rollback()
                raise HTTPException(status_code=400, detail="Problem occurred while updating token!")
        return None

