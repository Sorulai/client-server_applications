import argparse
import logging
import select
import socket
import sys
import time

import logs.config_server_log
from lesson3.common.utils import get_message, send_message
from lesson3.common.variables import DEFAULT_PORT, MAX_CONNECTIONS, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, RESPONDEFAULT_IP_ADDRESS, ERROR, MESSAGE, MESSAGE_TEXT, SENDER
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
                f'Попытка запуска сервера с указанием неподходящего порта '
                f'{cls.listen_port}. Допустимы адреса с 1024 до 65535.')
            sys.exit(1)

    @classmethod
    @log
    def process_client_message(cls, msg, msg_list, client):
        cls.SERVER_LOGGER.debug(f'Разбор сообщения от клиента {msg}')
        if ACTION in msg and msg[ACTION] == PRESENCE and TIME in msg and USER in msg and msg[USER][
            ACCOUNT_NAME] == 'Guest':
            send_message(client, {RESPONSE: 200})
            return
        elif ACTION in msg and msg[ACTION] == MESSAGE and TIME in msg and MESSAGE_TEXT in msg:
            msg_list.append((msg[ACCOUNT_NAME], msg[MESSAGE_TEXT]))
            return
        else:
            send_message(client, {
                RESPONDEFAULT_IP_ADDRESS: 400,
                ERROR: 'Bad Request'
            })
            return

    def main(self):
        self.arg_parser()
        self.SERVER_LOGGER.info(
            f'Запущен сервер, порт для подключений: {self.listen_port}, '
            f'адрес с которого принимаются подключения: {self.listen_address}. '
            f'Если адрес не указан, принимаются соединения с любых адресов.'
        )

        self.transport.bind((self.listen_address, self.listen_port))
        self.transport.settimeout(0.5)

        clients = []
        messages = []
        self.transport.listen(MAX_CONNECTIONS)
        while True:
            try:
                client, client_address = self.transport.accept()
            except OSError:
                pass
            else:
                self.SERVER_LOGGER.info(f'Установлено соединение с ПК {client_address}')
                clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []

            try:
                if clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
            except OSError:
                pass

            if recv_data_lst:
                for cl_in_msg in recv_data_lst:
                    try:
                        self.process_client_message(get_message(cl_in_msg), messages, cl_in_msg)
                    except:
                        self.SERVER_LOGGER.info(f'Клиент {cl_in_msg.getpeername()} '
                                                f'отключился от сервера.')
                        clients.remove(cl_in_msg)

            if messages and send_data_lst:
                message = {
                    ACTION: MESSAGE,
                    SENDER: messages[0][0],
                    TIME: time.time(),
                    MESSAGE_TEXT: messages[0][1]
                }
                del messages[0]
                for waiting_client in send_data_lst:
                    try:
                        send_message(waiting_client, message)
                    except:
                        self.SERVER_LOGGER.info(f'Клиент {waiting_client.getpeername()} отключился от сервера.')
                        waiting_client.close()
                        clients.remove(waiting_client)


if __name__ == '__main__':
    my_server = ChatServer()
    my_server.main()
