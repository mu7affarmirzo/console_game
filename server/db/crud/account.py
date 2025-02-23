from datetime import datetime

from sqlalchemy.orm import Session

from server.db.models.all import Account, Token


def get_user_by_nickname(db: Session, nickname: str):
    return db.query(Account).filter(Account.nickname == nickname).first()


def create_user_with_nickname(db: Session, nickname: str, bonus: int):
    user = Account(nickname=nickname, credits=bonus)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_credit(db: Session, user: Account, credit: int):
    user.credits += credit
    db.commit()
    db.refresh(user)
    return user


def get_token_by_key(db: Session, key: str):
    return db.query(Token).filter(Token.token == key).first()


def get_token_by_account(db: Session, nickname: str):
    return db.query(Token).filter(Token.account_nickname == nickname).first()


def create_access_token(db: Session, token: str, expires_at):
    expires_at = datetime.utcnow() + expires_at
    token = Token(token=token, expires_at=expires_at)
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


def update_token(db: Session, token: Token, key: str, expires_at):
    token.expires_at = datetime.utcnow() + expires_at

    token.token = key
    db.commit()
    db.refresh(token)
    return token