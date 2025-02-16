# datastore.py
from server.db.managers.account_manager import AccountManager, AccountItemManager
from server.db.managers.items_manager import ItemManager


class DataStore:
    """
    Composed DataStore that delegates operations to specialized managers.
    This serves as the unified interface to the underlying data layer.
    """
    def __init__(self, session_factory):
        # Dependency injection for testability and modularity.
        self.account_manager = AccountManager(session_factory)
        self.item_manager = ItemManager(session_factory)
        self.account_item_manager = AccountItemManager(session_factory)

    def get_items_master(self):
        return self.item_manager.get_items_master()

    def get_account(self, nickname):
        return self.account_manager.get_account(nickname)

    def create_account(self, nickname):
        return self.account_manager.create_account(nickname)

    def update_account_on_login(self, nickname):
        return self.account_manager.update_account_on_login(nickname)

    def process_purchase(self, nickname, item_key):
        purchase_result = self.account_item_manager.process_purchase(nickname, item_key)
        if purchase_result.get("status") == "success":
            return {"status": "success", "account": self.account_manager.get_account(nickname)}
        return purchase_result

    def process_sale(self, nickname, item_key):
        sale_result = self.account_item_manager.process_sale(nickname, item_key)
        if sale_result.get("status") == "success":
            return {"status": "success", "account": self.account_manager.get_account(nickname)}
        return sale_result
