import logging
import sys
import traceback

if sys.argv[0].find('client') == -1:
    LOGGER = logging.getLogger('server')
else:
    LOGGER = logging.getLogger('client')


def log(func):
    def log_saver(*args, **kwargs):
        ret = func(*args, **kwargs)
        LOGGER.debug(f'Была вызвана функция {func.__name__}, c параметрами {args}, {kwargs}.'
                     f'Вызов из модуля {func.__module__}.'
                     f'Вызов из функции {traceback.format_stack()[0].strip().split()[-1]}')
        return ret
    return log_saver
