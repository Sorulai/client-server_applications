"""
1. Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность сетевых узлов.
Аргументом функции является список, в котором каждый сетевой узел должен быть представлен именем хоста или ip-адресом.
В функции необходимо перебирать ip-адреса и проверять их доступность с выводом соответствующего сообщения
(«Узел доступен», «Узел недоступен»).
При этом ip-адрес сетевого узла должен создаваться с помощью функции ip_address().

2. Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона.
Меняться должен только последний октет каждого адреса.
По результатам проверки должно выводиться соответствующее сообщение.

3. Написать функцию host_range_ping_tab(), возможности которой основаны на функции из примера 2.
Но в данном случае результат должен быть итоговым по всем ip-адресам,
представленным в табличном формате (использовать модуль tabulate).
Таблица должна состоять из двух колонок и выглядеть примерно так:
Reachable
10.0.0.1
10.0.0.2
Unreachable
10.0.0.3
10.0.0.4

"""
import platform
import subprocess
from ipaddress import ip_address
from tabulate import tabulate


def host_ping(hosts_list):
    ipv4 = ''
    data_reachable = []
    data_unreachable = []
    for address in hosts_list:
        try:
            ipv4 = ip_address(address)
        except ValueError:
            print('Неправильный ip адрес')

        if platform.system().lower() == 'windows':
            parametr = '-n'
        else:
            parametr = '-c'
        response = subprocess.Popen(["ping", parametr, '1', '-w', '1', str(ipv4)], stdout=subprocess.PIPE)
        if response.wait() == 0:
            res_string = f"{ipv4} - Узел доступен"
            data_reachable.append(str(ipv4))
        else:
            res_string = f"{ipv4} - Узел недоступен"
            data_unreachable.append(str(ipv4))
        print(res_string)
    res = {'Доступные': data_reachable, 'Недоступые': data_unreachable}
    return res


def host_range_ping():
    while True:
        user_api_address = input('Введите первый ip адрес: ')
        try:
            ipv4 = ip_address(user_api_address)
            break
        except Exception as e:
            print(e)
    while True:
        ipv4_end = input('Кол-во проверяемых адрессов')
        if not isinstance(int(ipv4_end), int):
            print('Введите число')
        else:
            break
    host_list = []
    for i in range(int(ipv4_end)):
        host_list.append(str(ipv4 + i))
    return host_list


def host_range_ping_tab():
    ip_dict = host_range_ping()
    res_dict = host_ping(ip_dict)
    print(tabulate([res_dict], headers='keys'))


if __name__ == '__main__':
    address_list = ['95.79.231.8', '172.217.22.14', 'google.com', 'yandex.com', '8.8.8.8', 'youtube.com', '0.0.0.0']
    host_range_ping_tab()
