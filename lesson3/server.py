import json
import logging
import socket
import sys
import logs.config_server_log
from lesson3.common.utils import get_message, send_message
from lesson3.common.variables import DEFAULT_PORT, MAX_CONNECTIONS, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, RESPONDEFAULT_IP_ADDRESS, ERROR
from lesson3.errors import IncorrectDataReceivedError


class ChatServer:
    SERVER_LOGGER = logging.getLogger('server')

    def __init__(self):
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    @classmethod
    def get_listen_port(cls):
        try:
            if '-p' in sys.argv:
                listen_port = int(sys.argv[sys.argv.index('-p') + 1])
            else:
                listen_port = DEFAULT_PORT

            if listen_port < 1024 or listen_port > 65535:
                cls.SERVER_LOGGER.critical(f'Попытка  запуска сервера с указанием неподходящего порта {listen_port}.'
                                           f'Допустимые адресса с 1024 до 65535.')
                sys.exit(1)
            else:
                cls.SERVER_LOGGER.info(f'Запущен сервер, порт для подключений: {listen_port}.')
                return listen_port
        except IndexError:
            cls.SERVER_LOGGER.error('После параметра -\'p\' необходимо указать номер порта.')
            sys.exit(1)
        except ValueError:
            cls.SERVER_LOGGER.error('В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
            sys.exit(1)

    @classmethod
    def get_listen_address(cls):
        try:
            if '-a' in sys.argv:
                listen_address = sys.argv[sys.argv.index('-a') + 1]
            else:
                listen_address = ''
            return listen_address
        except IndexError:
            cls.SERVER_LOGGER.error('После параметра -\'a\' необходимо указать адрес,который будет слушать сокет.')
            sys.exit(1)

    @classmethod
    def process_client_message(cls, msg):
        cls.SERVER_LOGGER.debug(f'Разбор сообщения от клиента {msg}')
        if ACTION in msg and msg[ACTION] == PRESENCE and TIME in msg and USER in msg and msg[USER][
            ACCOUNT_NAME] == 'Guest':
            return {RESPONSE: 200}
        return {
            RESPONDEFAULT_IP_ADDRESS: 400,
            ERROR: 'Bad Request'
        }

    def main(self):
        self.transport.bind((self.get_listen_address(), self.get_listen_port()))
        self.transport.listen(MAX_CONNECTIONS)
        while True:
            client, client_address = self.transport.accept()
            self.SERVER_LOGGER.info(f'Установлено соединение с ПК {client_address}')
            try:
                message_from_client = get_message(client)
                self.SERVER_LOGGER.debug(f'Получено сообщение {message_from_client}')
                response = self.process_client_message(message_from_client)
                self.SERVER_LOGGER.info(f'Сформирован ответ клиенту {response}')
                send_message(client, response)
                client.close()
            except json.JSONDecodeError:
                self.SERVER_LOGGER.error(f'Не удалось декодировать Json строку, полученную от клиента {client_address}.'
                                         f'Соединение закрывается. ')
                client.close()
            except IncorrectDataReceivedError:
                self.SERVER_LOGGER.error(f'От клиента {client_address} приняты некорректные данные.'
                                         f'Соединение закрывается. ')
                client.close()


if __name__ == '__main__':
    my_server = ChatServer()
    my_server.main()
