import argparse
import json
import logging
import socket
import sys
import threading
import time
import logs.config_client_log
from lesson3.common.utils import send_message, get_message
from lesson3.common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, DEFAULT_IP_ADDRESS, \
    DEFAULT_PORT, MESSAGE, SENDER, MESSAGE_TEXT, EXIT, DESTINATION
from lesson3.decorators import log
from lesson3.errors import ReqFieldMissingError, ServerError, IncorrectDataReceivedError


class ChatClient:
    CLIENT_LOGGER = logging.getLogger('client')
    server_address = None
    server_port = None
    client_name = None

    def __init__(self):
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    @classmethod
    @log
    def create_exit_message(cls, account_name):
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: account_name
        }

    @classmethod
    @log
    def msg_from_server(cls, sock, my_username):
        while True:
            try:
                message = get_message(sock)
                if ACTION in message and message[ACTION] == MESSAGE and \
                        SENDER in message and DESTINATION in message \
                        and MESSAGE_TEXT in message and message[DESTINATION] == my_username:
                    print(f'\nПолучено сообщение от пользователя {message[SENDER]}:'
                          f'\n{message[MESSAGE_TEXT]}')
                    cls.CLIENT_LOGGER.info(f'Получено сообщение от пользователя {message[SENDER]}:'
                                           f'\n{message[MESSAGE_TEXT]}')
                else:
                    cls.CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')
            except IncorrectDataReceivedError:
                cls.CLIENT_LOGGER.error(f'Не удалось декодировать полученное сообщение.')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, json.JSONDecodeError):
                cls.CLIENT_LOGGER.critical(f'Потеряно соединение с сервером.')
                break

    @classmethod
    @log
    def create_msg(cls, sock, account_name='Guest'):
        to_user = input('Введите получателя сообщения: ')
        message = input('Введите сообщение для отправки: ')
        message_dict = {
            ACTION: MESSAGE,
            SENDER: account_name,
            DESTINATION: to_user,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        cls.CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
        try:
            send_message(sock, message_dict)
            cls.CLIENT_LOGGER.info(f'Отправлено сообщение для пользователя {to_user}')
        except Exception as e:
            print(e)
            cls.CLIENT_LOGGER.critical('Потеряно соединение с сервером.')
            sys.exit(1)

    @classmethod
    @log
    def user_interactive(cls, sock, username):
        cls.print_help()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                cls.create_msg(sock, username)
            elif command == 'help':
                cls.print_help()
            elif command == 'exit':
                send_message(sock, cls.create_exit_message(username))
                print('Завершение соединения.')
                cls.CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
                # Задержка неоходима, чтобы успело уйти сообщение о выходе
                time.sleep(0.5)
                break
            else:
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')

    @classmethod
    def print_help(cls):
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')

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
    def process_ans(cls, message):
        cls.CLIENT_LOGGER.debug(f'Разбор приветственного сообщения от сервера: {message}')
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return '200 : OK'
            elif message[RESPONSE] == 400:
                raise ServerError(f'400 : {message[ERROR]}')
        raise ReqFieldMissingError(RESPONSE)

    @classmethod
    @log
    def arg_parser(cls):
        parser = argparse.ArgumentParser()
        parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
        parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
        parser.add_argument('-n', '--name', default=None, nargs='?')
        namespace = parser.parse_args(sys.argv[1:])
        cls.server_address = namespace.addr
        cls.server_port = namespace.port
        cls.client_name = namespace.name

        # проверим подходящий номер порта
        if not 1023 < cls.server_port < 65536:
            cls.CLIENT_LOGGER.critical(
                f'Попытка запуска клиента с неподходящим номером порта: {cls.server_port}. '
                f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
            sys.exit(1)

    def main(self):
        self.arg_parser()

        """Сообщаем о запуске"""
        print(f'Консольный месседжер. Клиентский модуль. Имя пользователя: {self.client_name}')

        # Если имя пользователя не было задано, необходимо запросить пользователя.
        if not self.client_name:
            self.client_name = input('Введите имя пользователя: ')

        self.CLIENT_LOGGER.info(
            f'Запущен клиент с параметрами: адрес сервера: {self.server_address}, '
            f'порт: {self.server_port}, имя пользователя: {self.client_name}')

        # Инициализация сокета и сообщение серверу о нашем появлении
        try:
            self.transport.connect((self.server_address, self.server_port))
            send_message(self.transport, self.create_presence(self.client_name))
            answer = self.process_ans(get_message(self.transport))
            self.CLIENT_LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
            print(f'Установлено соединение с сервером.')
        except json.JSONDecodeError:
            self.CLIENT_LOGGER.error('Не удалось декодировать полученную Json строку.')
            sys.exit(1)
        except ServerError as error:
            self.CLIENT_LOGGER.error(f'При установке соединения сервер вернул ошибку: {error.text}')
            sys.exit(1)
        except ReqFieldMissingError as missing_error:
            self.CLIENT_LOGGER.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
            sys.exit(1)
        except (ConnectionRefusedError, ConnectionError):
            self.CLIENT_LOGGER.critical(
                f'Не удалось подключиться к серверу {self.server_address}:{self.server_port}, '
                f'конечный компьютер отверг запрос на подключение.')
            sys.exit(1)
        else:
            # Если соединение с сервером установлено корректно,
            # запускаем клиентский процесс приёма сообщений
            receiver = threading.Thread(target=self.msg_from_server, args=(self.transport, self.client_name))
            receiver.daemon = True
            receiver.start()

            # затем запускаем отправку сообщений и взаимодействие с пользователем.
            user_interface = threading.Thread(target=self.user_interactive, args=(self.transport,  self.client_name))
            user_interface.daemon = True
            user_interface.start()
            self.CLIENT_LOGGER.debug('Запущены процессы')

            # Watchdog основной цикл, если один из потоков завершён,
            # то значит или потеряно соединение или пользователь
            # ввёл exit. Поскольку все события обработываются в потоках,
            # достаточно просто завершить цикл.
            while True:
                time.sleep(1)
                if receiver.is_alive() and user_interface.is_alive():
                    continue
                break


if __name__ == '__main__':
    my_client = ChatClient()
    my_client.main()
