import subprocess
from subprocess import Popen

P_LIST = []
CLIENTS_COUNT = 2

while True:
    USER = input('Выберите действие: q - выход, '
                 's - запустить сервер и клиенты, x - закрыть все окна: ')

    if USER == 'q':
        break

    elif USER == 's':
        P_LIST.append(subprocess.Popen('python server.py',
                                       creationflags=subprocess.CREATE_NEW_CONSOLE))
        for _ in range(CLIENTS_COUNT):
            P_LIST.append(Popen('python client.py -m send',
                                creationflags=subprocess.CREATE_NEW_CONSOLE))
        for _ in range(CLIENTS_COUNT):
            P_LIST.append(Popen('python client.py -m listen',
                                creationflags=subprocess.CREATE_NEW_CONSOLE))

    elif USER == 'x':
        while P_LIST:
            KILL_PROCESS = P_LIST.pop()
            KILL_PROCESS.kill()
