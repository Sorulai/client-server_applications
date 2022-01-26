import argparse
import json
import logging
import socket
import sys
import time
import logs.config_client_log
from lesson3.common.utils import send_message, get_message
from lesson3.common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, DEFAULT_IP_ADDRESS, \
    DEFAULT_PORT, MESSAGE, SENDER, MESSAGE_TEXT
from lesson3.decorators import log
from lesson3.errors import ReqFieldMissingError, ServerError


class ChatClient:
    CLIENT_LOGGER = logging.getLogger('client')
    server_address = None
    server_port = None
    client_mode = None

    def __init__(self):
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    @classmethod
    @log
    def msg_from_server(cls, msg):
        if ACTION in msg and msg[ACTION] == MESSAGE and SENDER in msg and MESSAGE_TEXT in msg:
            print(f'Получено сообщение от пользователя '
                  f'{msg[SENDER]}:\n{msg[MESSAGE_TEXT]}')
            cls.CLIENT_LOGGER.info(f'Получено сообщение от пользователя '
                                   f'{msg[SENDER]}:\n{msg[MESSAGE_TEXT]}')
        else:
            cls.CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {msg}')

    @classmethod
    @log
    def create_msg(cls, sock, account_name='Guest'):
        message = input('Введите сообщение для отправки или \'!!!\' для завершения работы: ')
        if message == '!!!':
            sock.close()
            cls.CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
            print('Спасибо за использование нашего сервиса!')
            sys.exit(0)
        message_dict = {
            ACTION: MESSAGE,
            TIME: time.time(),
            ACCOUNT_NAME: account_name,
            MESSAGE_TEXT: message
        }
        cls.CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
        return message_dict

    @classmethod
    @log
    def create_presence(cls, account_name='Guest'):
        out = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: account_name
            }
        }
        cls.CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
        return out

    @classmethod
    @log
    def process_ans(cls, msg):
        cls.CLIENT_LOGGER.debug(f'Разбор сообщения от сервера: {msg}')
        if RESPONSE in msg:
            if msg[RESPONSE] == 200:
                return '200: ok'
            elif msg[RESPONSE] == 400:
                raise ServerError(f'400 : {msg[ERROR]}')
        raise ReqFieldMissingError(RESPONSE)

    @classmethod
    @log
    def arg_parser(cls):
        parser = argparse.ArgumentParser()
        parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
        parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
        parser.add_argument('-m', '--mode', default='listen', nargs='?')
        namespace = parser.parse_args(sys.argv[1:])
        cls.server_address = namespace.addr
        cls.server_port = namespace.port
        cls.client_mode = namespace.mode

        if not 1023 < cls.server_port < 65536:
            cls.CLIENT_LOGGER.critical(f'Попытка запуска клиента с неподходящим номером порта: {cls.server_port}. '
                                       f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
            sys.exit(1)

        if cls.client_mode not in ('listen', 'send'):
            cls.CLIENT_LOGGER.critical(f'Указан недопустимый режим работы {cls.client_mode}, '
                                       f'допустимые режимы: listen , send')
            sys.exit(1)

    def main(self):
        self.arg_parser()
        self.CLIENT_LOGGER.info(f'Запущен клиент с парамертами: адрес сервера: {self.server_address}, '
                                f'порт: {self.server_port}, режим работы: {self.client_mode}')
        try:
            self.transport.connect((self.server_address, self.server_port))
            send_message(self.transport, self.create_presence())
            answer = self.process_ans(get_message(self.transport))
            self.CLIENT_LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
            print(f'Установлено соединение с сервером.')
        except json.JSONDecodeError:
            self.CLIENT_LOGGER.error(f'Не удалось декодировать Json строку.'
                                     f'Соединение закрывается. ')
            sys.exit(1)
        except ServerError as error:
            self.CLIENT_LOGGER.error(f'При установке соединения сервер вернул ошибку: {error.text}')
            sys.exit(1)
        except ConnectionRefusedError:
            self.CLIENT_LOGGER.critical(
                f'Не удалось подключится к серверу {self.server_address}:{self.server_port}, '
                f'конечный компьютер отверг запрос на подключение.')
            sys.exit(1)
        except ReqFieldMissingError as missing_err:
            self.CLIENT_LOGGER.error(f'В ответе сервера отсутствует необходимое поле '
                                     f'{missing_err.missing_field}')
            sys.exit(1)
        else:
            if self.client_mode == 'send':
                print('Режим работы - отправка сообщений.')
            else:
                print('Режим работы - приём сообщений.')
            while True:
                if self.client_mode == 'send':
                    try:
                        send_message(self.transport, self.create_msg(self.transport))
                    except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                        self.CLIENT_LOGGER.error(f'Соединение с сервером {self.server_address} было потеряно.')
                        sys.exit(1)
                if self.client_mode == 'listen':
                    try:
                        self.msg_from_server(get_message(self.transport))
                    except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                        self.CLIENT_LOGGER.error(f'Соединение с сервером {self.server_address} было потеряно.')
                        sys.exit(1)


if __name__ == '__main__':
    my_client = ChatClient()
    my_client.main()
