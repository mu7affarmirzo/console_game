from server.db.models.all import ItemMaster


class ItemManager:
    """
    Provides access to the master list of items.
    """
    def __init__(self, session_factory):
        self.SessionLocal = session_factory

    def get_items_master(self):
        session = self.SessionLocal()
        try:
            items = session.query(ItemMaster).all()
            return {item.item_key: {"name": item.name, "price": item.price} for item in items}
        finally:
            session.close()
