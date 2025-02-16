# server.py
import json
import socket
import threading
import logging
from server.config import HOST, PORT, SessionLocal
from server.db.master import DataStore
from server.db.models.all import init_db


# Configure logging.
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(levelname)s] %(message)s')

init_db()


class RequestHandler:
    """
    Routes client requests to the DataStore.
    """

    def __init__(self, datastore):
        self.datastore = datastore

    def process(self, request):
        action = request.get("action")
        logging.debug(f"Processing action: {action} with request: {request}")

        if action == "login":
            nickname = request.get("nickname")
            account = self.datastore.get_account(nickname)
            if account:
                account = self.datastore.update_account_on_login(nickname)
            else:
                account = self.datastore.create_account(nickname)
            return {"status": "success",
                    "account": account,
                    "items_master": self.datastore.get_items_master()}
        elif action == "buy":
            nickname = request.get("nickname")
            item_key = request.get("item_key")
            return self.datastore.process_purchase(nickname, item_key)
        elif action == "sell":
            nickname = request.get("nickname")
            item_key = request.get("item_key")
            return self.datastore.process_sale(nickname, item_key)
        elif action == "logout":
            return {"status": "success", "message": "Logged out."}
        else:
            logging.warning(f"Unknown action: {action}")
            return {"status": "error", "message": "Unknown action."}


class GameServer:
    """
    Manages network communication. Listens on a TCP socket and spawns a new thread
    for each client connection.
    """

    def __init__(self, host, port, datastore):
        self.host = host
        self.port = port
        self.datastore = datastore
        self.handler = RequestHandler(self.datastore)

    def client_thread(self, conn, addr):
        logging.info(f"Client connected from {addr}")
        try:
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    try:
                        request = json.loads(data.decode())
                        response = self.handler.process(request)
                    except Exception as e:
                        logging.exception("Error processing request.")
                        response = {"status": "error", "message": str(e)}
                    conn.sendall(json.dumps(response).encode())
        except Exception as e:
            logging.exception(f"Connection error with {addr}")
        finally:
            logging.info(f"Connection with {addr} closed.")

    def start(self):
        logging.info(f"Starting Game Server on {self.host}:{self.port}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            while True:
                conn, addr = s.accept()
                threading.Thread(target=self.client_thread, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    datastore = DataStore(SessionLocal)
    server = GameServer(HOST, PORT, datastore)
    server.start()
