import argparse
import logging
import select
import socket
import sys
import time

import logs.config_server_log
from lesson3.common.utils import get_message, send_message
from lesson3.common.variables import DEFAULT_PORT, MAX_CONNECTIONS, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, RESPONDEFAULT_IP_ADDRESS, ERROR, MESSAGE, MESSAGE_TEXT, SENDER, RESPONSE_200, RESPONSE_400, DESTINATION, \
    EXIT
from lesson3.decorators import log


class ChatServer:
    SERVER_LOGGER = logging.getLogger('server')
    listen_address = None
    listen_port = None

    def __init__(self):
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    @classmethod
    @log
    def arg_parser(cls):
        parser = argparse.ArgumentParser()
        parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
        parser.add_argument('-a', default='', nargs='?')
        namespace = parser.parse_args(sys.argv[1:])
        cls.listen_address = namespace.a
        cls.listen_port = namespace.p

        if not 1023 < cls.listen_port < 65536:
            cls.SERVER_LOGGER.critical(
                f'Попытка запуска сервера с указанием неподходящего порта {cls.listen_port}. '
                f'Допустимы адреса с 1024 до 65535.')
            sys.exit(1)

    @classmethod
    @log
    def process_client_message(cls, message, messages_list, client, clients, names):
        cls.SERVER_LOGGER.debug(f'Разбор сообщения от клиента : {message}')
        if ACTION in message and message[ACTION] == PRESENCE and \
                TIME in message and USER in message:
            if message[USER][ACCOUNT_NAME] not in names.keys():
                names[message[USER][ACCOUNT_NAME]] = client
                send_message(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя уже занято.'
                send_message(client, response)
                clients.remove(client)
                client.close()
            return

        elif ACTION in message and message[ACTION] == MESSAGE and \
                DESTINATION in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message:
            messages_list.append(message)
            return
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            clients.remove(names[message[ACCOUNT_NAME]])
            names[message[ACCOUNT_NAME]].close()
            del names[message[ACCOUNT_NAME]]
            return
        else:
            response = RESPONSE_400
            response[ERROR] = 'Запрос некорректен.'
            send_message(client, response)
            return

    @classmethod
    @log
    def process_message(cls, message, names, listen_socks):
        if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
            send_message(names[message[DESTINATION]], message)
            cls.SERVER_LOGGER.info(f'Отправлено сообщение пользователю {message[DESTINATION]} '
                                   f'от пользователя {message[SENDER]}.')
        elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            cls.SERVER_LOGGER.error(
                f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
                f'отправка сообщения невозможна.')

    def main(self):
        self.arg_parser()
        self.SERVER_LOGGER.info(
            f'Запущен сервер, порт для подключений: {self.listen_port}, '
            f'адрес с которого принимаются подключения: {self.listen_address}. '
            f'Если адрес не указан, принимаются соединения с любых адресов.')
        # Готовим сокет

        self.transport.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.transport.bind((self.listen_address, self.listen_port))
        self.transport.settimeout(0.5)

        # список клиентов , очередь сообщений
        clients = []
        messages = []

        # Словарь, содержащий имена пользователей и соответствующие им сокеты.
        names = dict()  # {client_name: client_socket}

        # Слушаем порт
        self.transport.listen(MAX_CONNECTIONS)
        # Основной цикл программы сервера
        while True:
            # Ждём подключения, если таймаут вышел, ловим исключение.
            try:
                client, client_address = self.transport.accept()
            except OSError:
                pass
            else:
                self.SERVER_LOGGER.info(f'Установлено соедение с ПК {client_address}')
                clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []
            # Проверяем на наличие ждущих клиентов
            try:
                if clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
            except OSError:
                pass

            # принимаем сообщения и если ошибка, исключаем клиента.
            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.process_client_message(get_message(client_with_message),
                                               messages, client_with_message, clients, names)
                    except Exception:
                        self.SERVER_LOGGER.info(f'Клиент {client_with_message.getpeername()} '
                                    f'отключился от сервера.')
                        clients.remove(client_with_message)

            # Если есть сообщения, обрабатываем каждое.
            for i in messages:
                try:
                    self.process_message(i, names, send_data_lst)
                except Exception:
                    self.SERVER_LOGGER.info(f'Связь с клиентом с именем {i[DESTINATION]} была потеряна')
                    clients.remove(names[i[DESTINATION]])
                    del names[i[DESTINATION]]
            messages.clear()


if __name__ == '__main__':
    my_server = ChatServer()
    my_server.main()
