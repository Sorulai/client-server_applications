"""
Выполнить пинг веб-ресурсов yandex.ru, youtube.com и
преобразовать результаты из байтовового в строковый (предварительно определив кодировку выводимых сообщений).
"""
import platform
import subprocess
import chardet


def ping_func(site):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    args = ['ping', param, '2', site]
    result = subprocess.Popen(args, stdout=subprocess.PIPE)
    for line in result.stdout:
        result = chardet.detect(line)
        line = line.decode(result['encoding']).encode('utf-8')
        print(line.decode('utf-8'))


ping_func('yandex.ru')
ping_func('youtube')
