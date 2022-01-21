import json
import logging
import socket
import sys
import time
import logs.config_client_log
from lesson3.common.utils import send_message, get_message
from lesson3.common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, DEFAULT_IP_ADDRESS, \
    DEFAULT_PORT
from lesson3.errors import ReqFieldMissingError


class ChatClient:
    CLIENT_LOGGER = logging.getLogger('client')

    def __init__(self):
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.message_to_server = self.create_presence()

    @classmethod
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
    def process_ans(cls, msg):
        cls.CLIENT_LOGGER.debug(f'Разбор сообщения от сервераp: {msg}')
        if RESPONSE in msg:
            if msg[RESPONSE] == 200:
                return '200: ok'
            return f'400: {msg[ERROR]}'
        raise ReqFieldMissingError

    @classmethod
    def get_server_address(cls):
        try:
            server_address = sys.argv[1]
            cls.CLIENT_LOGGER.info(f'Запущен сервер, адрес  для подключений: {server_address}.')
            return server_address
        except IndexError:
            server_address = DEFAULT_IP_ADDRESS
            cls.CLIENT_LOGGER.info(f'Запущен сервер, адрес  для подключений: {server_address}.')
            return server_address
        except ValueError:
            cls.CLIENT_LOGGER.error('В качестве порта может быть указано число больше 1024 и меньше 65535.')
            sys.exit(1)

    @classmethod
    def get_server_port(cls):
        try:
            server_port = int(sys.argv[2])
            if server_port < 1024 or server_port > 65535:
                cls.CLIENT_LOGGER.critical(f'Попытка  запуска сервера с указанием неподходящего порта {server_port}.'
                                           f'Допустимые адресса с 1024 до 65535.')
                sys.exit(1)
            cls.CLIENT_LOGGER.info(f'Запущен сервер, порт для подключений: {server_port}.')
            return server_port
        except IndexError:
            server_port = DEFAULT_PORT
            cls.CLIENT_LOGGER.info(f'Запущен сервер, порт для подключений: {server_port}.')
            return server_port
        except ValueError:
            cls.CLIENT_LOGGER.error('В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
            sys.exit(1)

    def main(self):
        self.transport.connect((self.get_server_address(), self.get_server_port()))
        send_message(self.transport, self.message_to_server)
        try:
            answer = self.process_ans(get_message(self.transport))
            self.CLIENT_LOGGER.info(f'Принят ответ от сервера {answer}')
            self.transport.close()
        except json.JSONDecodeError:
            self.CLIENT_LOGGER.error(f'Не удалось декодировать Json строку.'
                                     f'Соединение закрывается. ')
            self.transport.close()
        except ConnectionRefusedError:
            self.CLIENT_LOGGER.critical(
                f'Не удалось подключится к серверу {self.get_server_address()}:{self.get_server_port()}, '
                f'конечный компьютер отверг запрос на подключение.')
        except ReqFieldMissingError as missing_err:
            self.CLIENT_LOGGER.error(f'В ответе сервера отсутствует необходимое поле '
                                     f'{missing_err.missing_field}')


if __name__ == '__main__':
    my_client = ChatClient()
    my_client.main()
