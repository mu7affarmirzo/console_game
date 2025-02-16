import sys
from client.client import GameClient
from server.server import GameServer


def main():
    """
    Пример использования:
      python game.py server   # запустить сервер
      python game.py client   # запустить клиент

    Сервер и клиент лучше запускать в разных терминалах.
    """
    if len(sys.argv) < 2:
        print("Использование: python game.py [server|client]")
        sys.exit(1)

    mode = sys.argv[1].lower()
    if mode == "server":
        server = GameServer()
        server.run()
    elif mode == "client":
        client = GameClient()
        client.main_loop()
    else:
        print(f"Неизвестный режим: {mode}")
        print("Использование: python game.py [server|client]")
        sys.exit(1)


if __name__ == "__main__":
    main()
