import json
import socket
import sys

from lesson3.common.utils import get_message, send_message
from lesson3.common.variables import DEFAULT_PORT, MAX_CONNECTIONS, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, RESPONDEFAULT_IP_ADDRESS, ERROR


class ChatServer:

    def __init__(self):
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    @staticmethod
    def get_listen_port():
        try:
            if '-p' in sys.argv:
                listen_port = int(sys.argv[sys.argv.index('-p') + 1])
            else:
                listen_port = DEFAULT_PORT

            if listen_port < 1024 or listen_port > 65535:
                raise ValueError
            else:
                return listen_port
        except IndexError:
            print('После параметра -\'p\' необходимо указать номер порта.')
            sys.exit(1)
        except ValueError:
            print('В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
            sys.exit(1)

    @staticmethod
    def get_listen_address():
        try:
            if '-a' in sys.argv:
                listen_address = sys.argv[sys.argv.index('-a') + 1]
            else:
                listen_address = ''
            return listen_address
        except IndexError:
            print('После параметра -\'a\' необходимо указать адрес,который будет слушать сокет.')
            sys.exit(1)

    @staticmethod
    def process_client_message(msg):
        if ACTION in msg and msg[ACTION] == PRESENCE and TIME in msg and USER in msg and msg[USER][ACCOUNT_NAME] == 'Guest':
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
            try:
                message_from_client = get_message(client)
                print(message_from_client)
                response = self.process_client_message(message_from_client)
                send_message(client, response)
                client.close()
            except (ValueError, json.JSONDecodeError):
                print('Принято неккоректное сообщение от клиента.')
                client.close()


if __name__ == '__main__':
    my_server = ChatServer()
    my_server.main()
