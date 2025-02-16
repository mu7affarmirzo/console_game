# item_manager.py
# account_manager.py
import random
from server.config.settings import MIN_CREDITS, MAX_CREDITS
from server.db.models.all import Account, ItemMaster, AccountItem


class AccountManager:
    """
    Handles account operations: retrieval, creation, and login bonus updates.
    """
    def __init__(self, session_factory):
        self.SessionLocal = session_factory

    def get_account(self, nickname):
        session = self.SessionLocal()
        try:
            account = session.query(Account).filter(Account.nickname == nickname).first()
            if account:
                items = [ai.item_key for ai in account.items]
                return {"nickname": account.nickname, "credits": account.credits, "items": items}
            return None
        finally:
            session.close()

    def create_account(self, nickname):
        session = self.SessionLocal()
        try:
            bonus = random.randint(MIN_CREDITS, MAX_CREDITS)
            account = Account(nickname=nickname, credits=bonus)
            session.add(account)
            session.commit()
            return self.get_account(nickname)
        finally:
            session.close()

    def update_account_on_login(self, nickname):
        session = self.SessionLocal()
        try:
            bonus = random.randint(MIN_CREDITS, MAX_CREDITS)
            account = session.query(Account).filter(Account.nickname == nickname).first()
            if account:
                account.credits += bonus
                session.commit()
            return self.get_account(nickname)
        finally:
            session.close()


class AccountItemManager:
    """
    Manages the purchase and sale logic that connects accounts with items.
    """

    def __init__(self, session_factory):
        self.SessionLocal = session_factory

    def process_purchase(self, nickname, item_key):
        session = self.SessionLocal()
        try:
            account = session.query(Account).filter(Account.nickname == nickname).first()
            if not account:
                return {"status": "error", "message": "Account not found."}

            item = session.query(ItemMaster).filter(ItemMaster.item_key == item_key).first()
            if not item:
                return {"status": "error", "message": "Invalid item."}

            if any(ai.item_key == item_key for ai in account.items):
                return {"status": "error", "message": "Item already owned."}

            if account.credits < item.price:
                return {"status": "error", "message": "Not enough credits."}

            account.credits -= item.price
            account_item = AccountItem(nickname=nickname, item_key=item_key)
            session.add(account_item)
            session.commit()
            return {"status": "success"}
        finally:
            session.close()

    def process_sale(self, nickname, item_key):
        session = self.SessionLocal()
        try:
            account = session.query(Account).filter(Account.nickname == nickname).first()
            if not account:
                return {"status": "error", "message": "Account not found."}

            account_item = session.query(AccountItem).filter(
                AccountItem.nickname == nickname,
                AccountItem.item_key == item_key
            ).first()
            if not account_item:
                return {"status": "error", "message": "Item not owned."}

            item = session.query(ItemMaster).filter(ItemMaster.item_key == item_key).first()
            if not item:
                return {"status": "error", "message": "Invalid item."}

            refund = item.price // 2
            account.credits += refund
            session.delete(account_item)
            session.commit()
            return {"status": "success"}
        finally:
            session.close()
