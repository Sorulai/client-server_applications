import json
import socket
import sys
import time

from lesson3.common.utils import send_message, get_message
from lesson3.common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, DEFAULT_IP_ADDRESS, \
    DEFAULT_PORT


class ChatClient:
    def __init__(self):
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.message_to_server = self.create_presence()

    @staticmethod
    def create_presence(account_name='Guest'):
        out = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: account_name
            }
        }
        return out

    @staticmethod
    def process_ans(msg):
        if RESPONSE in msg:
            if msg[RESPONSE] == 200:
                return '200: ok'
            return f'400: {msg[ERROR]}'
        raise ValueError

    @staticmethod
    def get_server_address():
        try:
            server_address = sys.argv[1]
            return server_address
        except IndexError:
            server_address = DEFAULT_IP_ADDRESS
            return server_address
        except ValueError:
            print('В качестве порта может быть указано число больше 1024 и меньше 65535.')
            sys.exit(1)

    @staticmethod
    def get_server_port():
        try:
            server_port = int(sys.argv[2])
            if server_port < 1024 or server_port > 65535:
                raise ValueError
            return server_port
        except IndexError:
            server_port = DEFAULT_PORT
            return server_port
        except ValueError:
            print('В качестве порта может быть указано число больше 1024 и меньше 65535.')
            sys.exit(1)

    def main(self):
        self.transport.connect((self.get_server_address(), self.get_server_port()))
        send_message(self.transport, self.message_to_server)
        try:
            answer = self.process_ans(get_message(self.transport))
            print(answer)
            self.transport.close()
        except (ValueError, json.JSONDecodeError):
            print('Не удалось декодировать сообщение сервера.')
            self.transport.close()


if __name__ == '__main__':
    my_client = ChatClient()
    my_client.main()
