from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Date, func

from server.config.settings import Base, engine, SessionLocal


class Account(Base):
    __tablename__ = "accounts"

    nickname = Column(String, primary_key=True, index=True)
    credits = Column(Integer, default=0)
    items = relationship("AccountItem", back_populates="account", cascade="all, delete-orphan")


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    account_nickname = Column(String, ForeignKey("accounts.nickname"))
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime)
    is_revoked = Column(Boolean, default=False)

    account = relationship("Account")


class ItemMaster(Base):
    __tablename__ = "items_master"

    item_key = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)


class AccountItem(Base):
    __tablename__ = "account_items"

    nickname = Column(String, ForeignKey("accounts.nickname"), primary_key=True)
    item_key = Column(String, ForeignKey("items_master.item_key"), primary_key=True)

    account = relationship("Account", back_populates="items")
    item = relationship("ItemMaster")


def init_db():
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        if session.query(ItemMaster).count() == 0:
            items = [
                {"item_key": "sword", "name": "Sword", "price": 50},
                {"item_key": "shield", "name": "Shield", "price": 40},
                {"item_key": "potion", "name": "Potion", "price": 10}
            ]
            for item_data in items:
                session.add(ItemMaster(**item_data))
            session.commit()
    finally:
        session.close()
