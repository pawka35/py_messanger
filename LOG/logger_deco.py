'''
модуль декотраторов для логирования
'''
import logging
import LOG.server_log_config
from Protocol.proto_description import PacketType as pctType
import inspect
from functools import wraps


class Logger:
    def __call__(self, func):
        @wraps(func)
        def decorated(*args, **kwargs):
            # смотрим из какого модуля пришел запрос
            initStr = str(inspect.stack()[len(inspect.stack())-1][1])

            #  определяемся какой из логеров использовать (для клиента или для сервера)
            if initStr.endswith('server.py'):
                logger = logging.getLogger('server')
            elif initStr.endswith('client.py'):
                logger = logging.getLogger('client')
            else:
            # костыль №1 (если вызывается из потока, то какая-то другая  последовательность...
            # но сейчас вечер субботы и поток только в клиенте...
                logger = logging.getLogger('client')
            # получаем результат декорируемой функции
            res = func(*args, **kwargs)
            # в зависимости от названия функции пишем в логи определенные сообщения
            if func.__name__ == "get_message":
                logger.info(f'Принято сообщение:{res}')
            elif func.__name__ == "send_message":
                logger.info(f'Сообщение отправлено')
            elif func.__name__ == "getStartParametrs":
                logger.info(f"Корректые параметры запуска:{res}")
            elif func.__name__ == "dict_to_bytes":
                if isinstance(res, bytes):
                    logger.debug(f"Успешно преобразовали словарь в массив байт")
                else:
                    logger.error(f'Ощибка преобразования словаря: {res}')
            elif func.__name__ == "bytes_to_dict":
                if isinstance(res, dict):
                    logger.debug(f"Успешно преобразовали полученные байты в словарь")
                else:
                    logger.error(f'Ощибка преобразования байт в словарь: {res}')
            elif func.__name__ == "presence_response":
                logger.info(f'Клиенту подготовлен ответ: {res}')

            elif func.__name__ == "paramForServer":
                if isinstance(res, dict):  # если результат словарь, то ок
                    logger.info(f'Получены параметры запуска: {res}')
                else:
                    logger.error('Некорректное указание параметров для запуска')

            elif func.__name__ == "create_presence":
                if isinstance(res, dict): # если результат словарь, то ок
                    logger.info(f'Сформировали серверу сообщение от имени {res[pctType.USER.value][pctType.ACCOUNT_NAME.value]}'
                               f':{res}')
                else:  # если пришло сообщение об ощибках (тип не словарь), то передаем в логер, как ошибку
                    logger.error(res)

            elif func.__name__ == 'translate_message':
                if isinstance(res, dict):
                    logger.info(f'Ответ сервера разобран корректно: {res}')
                else:
                    logger.error(f'Ошибка разбора ответа: {res}')

            elif func.__name__ == "paramForClient":
                if isinstance(res, dict):  # если результат словарь, то ок
                    logger.info(f'Получены параметры запуска: {res}')
                else:
                    logger.error('Некорректное указание параметров для запуска')
            return res
        return decorated


# Функция проверки, что клиент авторизован на сервере
# Проверяет, что передаваемый объект сокета находится в списке клиентских сокетов. Если его там нет закрывает сокет
def server_login_required(func):
    @wraps(func)
    def checker(*args, **kwargs):
        found = False
        for x in args[3]:
            print(type(x))
            if x.getpeername() == args[2]:
                found = True
                # Если не не авторизован, то вызываем исключение.
        if not found:
            raise TypeError
        return func(*args, **kwargs)
    return checker


# Проверяет, что у клиента есть объект подключения к серверу
def client_login_required(func):
    @wraps(func)
    def checker(*args, **kwargs):
        client = args[0]
        if client.monitor is None:
            raise TypeError
        return func(*args, **kwargs)
    return checker

