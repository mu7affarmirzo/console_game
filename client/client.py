# client.py

import socket
import json

HOST = "127.0.0.1"
PORT = 50007

class GameClient:
    def __init__(self):
        self.nickname = None
        self.all_items = {}    # кэш списка предметов, полученный с сервера
        self.credits = 0
        self.items_owned = []

    def send_request(self, sock, request_data):
        """
        Отправляет JSON-запрос и читает ответ (одну строку JSON).
        Возвращает словарь-ответ от сервера.
        """
        request_str = json.dumps(request_data)
        sock.sendall((request_str + "\n").encode("utf-8"))
        response_str = sock.recv(4096).decode("utf-8").strip()
        if not response_str:
            return {"status": "error", "error": "Пустой ответ от сервера"}
        try:
            return json.loads(response_str)
        except json.JSONDecodeError:
            return {"status": "error", "error": f"Ошибка парсинга ответа: {response_str}"}

    def login(self, sock):
        """
        Запрашивает у пользователя nickname и вызывает серверный login.
        """
        nickname_input = input("Введите ваш nickname: ").strip()
        if not nickname_input:
            print("Nickname не может быть пустым.")
            return

        request = {
            "action": "login",
            "nickname": nickname_input
        }
        response = self.send_request(sock, request)
        if response.get("status") == "ok":
            self.nickname = response.get("nickname")
            self.credits = response.get("credits", 0)
            self.items_owned = response.get("items_owned", [])
            self.all_items = response.get("all_items", {})
            print(f"Успешный вход. Ваш ник: {self.nickname}, кредиты: {self.credits}")
        else:
            print("Ошибка при входе:", response.get("error", "Неизвестная ошибка"))

    def logout(self, sock):
        """
        Вызывает серверный logout.
        """
        if not self.nickname:
            print("Сначала войдите в игру (команда login).")
            return

        request = {
            "action": "logout",
            "nickname": self.nickname
        }
        response = self.send_request(sock, request)
        if response.get("status") == "ok":
            print(response.get("message", "Logout выполнен."))
            self.nickname = None
            self.credits = 0
            self.items_owned = []
        else:
            print("Ошибка при логауте:", response.get("error", "Неизвестная ошибка"))

    def buy_item(self, sock):
        """
        Запрашивает у пользователя, какой предмет купить, и формирует запрос buy на сервер.
        """
        if not self.nickname:
            print("Сначала войдите (login).")
            return
        if not self.all_items:
            print("Нет списка товаров. Попробуйте перелогиниться.")
            return

        print("Доступные предметы (name -> price):")
        for name, price in self.all_items.items():
            # Показать только те предметы, которых у игрока ещё нет
            if name not in self.items_owned:
                print(f"  {name} -> {price}")

        item_name = input("Введите название предмета для покупки: ").strip()
        if not item_name:
            print("Пустой ввод.")
            return

        request = {
            "action": "buy",
            "nickname": self.nickname,
            "item": item_name
        }
        response = self.send_request(sock, request)
        if response.get("status") == "ok":
            self.credits = response.get("credits", self.credits)
            self.items_owned = response.get("items_owned", self.items_owned)
            print(f"Куплен предмет {item_name}. Баланс: {self.credits}")
        else:
            print("Ошибка при покупке:", response.get("error", "Неизвестная ошибка"))

    def sell_item(self, sock):
        """
        Запрашивает у пользователя, какой предмет продать, и формирует запрос sell на сервер.
        """
        if not self.nickname:
            print("Сначала войдите (login).")
            return

        print("Ваши предметы:", self.items_owned)
        item_name = input("Введите название предмета для продажи: ").strip()
        if not item_name:
            print("Пустой ввод.")
            return

        request = {
            "action": "sell",
            "nickname": self.nickname,
            "item": item_name
        }
        response = self.send_request(sock, request)
        if response.get("status") == "ok":
            self.credits = response.get("credits", self.credits)
            self.items_owned = response.get("items_owned", self.items_owned)
            print(f"Продан предмет {item_name}. Баланс: {self.credits}")
        else:
            print("Ошибка при продаже:", response.get("error", "Неизвестная ошибка"))

    def show_balance(self):
        """Показывает баланс."""
        if not self.nickname:
            print("Сначала войдите (login).")
            return
        print(f"Ваш баланс: {self.credits}")

    def show_owned_items(self):
        """Показывает список купленных предметов."""
        if not self.nickname:
            print("Сначала войдите (login).")
            return
        print("У вас есть следующие предметы:", self.items_owned)

    def show_all_items(self):
        """Показывает все возможные предметы с их ценами."""
        if not self.nickname:
            print("Сначала войдите (login).")
            return
        for item_name, price in self.all_items.items():
            print(f"{item_name} -> {price}")

    def main_loop(self):
        """
        Основной цикл ввода команд с консоли.
        """
        print("Добро пожаловать в Game Client!")
        print("Подключение к серверу...")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORT))
            print("Подключение установлено.")

            while True:
                print("\nСписок команд:")
                print(" 1) login  - войти или создать аккаунт")
                print(" 2) logout - выйти из аккаунта")
                print(" 3) balance - показать баланс")
                print(" 4) list_all - список всех возможных предметов")
                print(" 5) list_owned - список купленных предметов")
                print(" 6) buy  - купить предмет")
                print(" 7) sell - продать предмет")
                print(" 8) quit - выход из клиента (завершить соединение)\n")

                cmd = input("Введите команду: ").strip().lower()

                if cmd == "1" or cmd == "login":
                    self.login(sock)
                elif cmd == "2" or cmd == "logout":
                    self.logout(sock)
                elif cmd == "3" or cmd == "balance":
                    self.show_balance()
                elif cmd == "4" or cmd == "list_all":
                    self.show_all_items()
                elif cmd == "5" or cmd == "list_owned":
                    self.show_owned_items()
                elif cmd == "6" or cmd == "buy":
                    self.buy_item(sock)
                elif cmd == "7" or cmd == "sell":
                    self.sell_item(sock)
                elif cmd == "8" or cmd == "quit":
                    # Посылаем серверу action=quit, чтобы закрыть соединение
                    quit_request = {"action": "quit"}
                    self.send_request(sock, quit_request)
                    print("Выход из клиента.")
                    break
                else:
                    print("Неизвестная команда. Повторите ввод.")


if __name__ == "__main__":
    client = GameClient()
    client.main_loop()
