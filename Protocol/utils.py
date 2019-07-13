'''
Функции, которые используют как клиент, так и сервер
'''
import json
import sys
import time
from Protocol.proto_description import PacketType as pctType
from Protocol.proto_description import Actions as action
from Protocol.proto_description import Helpers as verb
import logging
import LOG.client_log_config
import LOG.server_log_config
from LOG.logger_deco import Logger
import inspect
import datetime
from functools import wraps

# Кодировка
ENCODING = 'utf-8'


def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

@Logger()
def dict_to_bytes(message_dict):
    """
    Преобразование словаря в байты
    :param message_dict: словарь
    :return: bytes
    """
    # Проверям, что пришел словарь
    if isinstance(message_dict, dict):
        # Преобразуем словарь в json
        jmessage = json.dumps(message_dict, default = myconverter)
        # Переводим json в байты
        bmessage = jmessage.encode(ENCODING)
        # Возвращаем байты
        return bmessage
    else:
        raise TypeError


@Logger()
def bytes_to_dict(message_bytes):
    """
    Преобразование байт в словарь
    :param message_bytes: байты
    :return: message - словарь
    """
    # Если переданы байты
    if isinstance(message_bytes, bytes):
        # Декодируем
        jmessage = message_bytes.decode(ENCODING)
        # Из json делаем словарь
        message = json.loads(jmessage)
        # Если там был словарь
        if isinstance(message, dict):
            # Возвращаем сообщение
            return message
        else:
            # Нам прислали неверный тип
            raise TypeError
    else:
        # Передан неверный тип
        raise TypeError


@Logger()
def get_message(sock, *address):
    """Получение информации из сокета и перевод её в словарь
     :param sock: сокет
     :param *address
     :return: response - словарь"""
    # Получаем байты
    bresponse = sock.recv(1024)
    # переводим байты в словарь
    if len(bresponse)!= 0:
        response = bytes_to_dict(bresponse)
    # если в сокете пусто, то генериуем сообщение об отключении
    else:
        message = {
            pctType.ACTION.value: action.LEAVE.value,
            pctType.TIME.value: time.time(),
            pctType.USER.value: {pctType.ACCOUNT_NAME.value: address[0]}
            }
        response = message
    # возвращаем словарь
    return response

'''
def get_auth_message(sock, *address):
    bresponse = sock.recv(1024)
    if len(bresponse) != 0:
        response = bytes_to_dict(bresponse)
        # если в сокете пусто, то генериуем сообщение об отключении
    else:
        message={
            pctType.ACTION.value: action.LEAVE.value,
            pctType.TIME.value: time.time(),
            pctType.USER.value: {pctType.ACCOUNT_NAME.value: address[0]}
        }
        response = message
        # возвращаем словарь
    return response
'''


def create_message(message_to, text, account_name='Guest'):
    """
     Формирование сообщения, согласно протоколу
     :param message_to: адресат
     :param text: текст сообщения
     :param account_name: отправитель
     :return: сообщение в формате протокола обмена
     """
    return {pctType.ACTION.value: action.MESSAGE.value, pctType.TIME.value: time.time(), verb.TO.value: message_to,
            verb.FROM.value: account_name, action.MESSAGE.value: text}


def create_work_message(userAction, message_to, text, account_name='Guest'):
    """
     Создание служебного сообщения
     :param userAction: действие
     :param message_to: адресат
     :param text: текст сообщения
     :param account_name: отправитель
     :return: response - словарь
     """
    message = {pctType.ACTION.value: userAction, pctType.TIME.value: time.time(), verb.TO.value: message_to,
               verb.FROM.value: account_name, action.MESSAGE.value: text}
    print(message)
    return message

@Logger()
def send_message(sock, message):
    """
     Отправка сообщения через сокет
     :param sock: сокет
     :param message: сообщение в формате протокола обмена
     :return:
     """
    # Словарь переводим в байты
    bprescence = dict_to_bytes(message)
    # Отправляем
    sock.send(bprescence)


def checkValue(value):
    """
    Проверка значения
    :param value: значение
    :return:
    """
    global logger
    try:
        int(value)
    except ValueError:
        logger.error(f'Неверное значение параметра {sys.argv[sys.argv.index(value)-1]}')
        sys.exit(0)


@Logger()
def paramForServer(startOptions):
    """
    Получение параметров запуска из командной строки для сервера
    :param startOptions: пустой список параметров
    :return: startOptions: сформированный список параметров
    """
    try:
        startOptions['addr'] = sys.argv[sys.argv.index('-a')+1]
    except:
        pass
    try:
        startOptions['port'] = sys.argv[sys.argv.index('-p') + 1]
    except:
        pass
    try:
        startOptions['clients'] = sys.argv[sys.argv.index('-c') + 1]
    except:
        pass

    try:
        checkValue(startOptions['port'])
        checkValue(startOptions['clients'])
    except:
        sys.exit(0)
    return startOptions


@Logger()
def paramForClient(startOptions):
    """
    Получение параметров запуска из командной строки для клиента
    :param startOptions: пустой список параметров
    :return: startOptions: сформированный список параметров
    """
    try:
        startOptions['addr'] = sys.argv[1]
    except IndexError:
        startOptions['addr'] = 'localhost'
    try:
        port = sys.argv[2]
        startOptions['port'] = int(str(port).replace("[", "").replace("]", ""))
        if not port.startswith("[") and not port.endswith("]"):
            raise ZeroDivisionError
    except ZeroDivisionError:
        print("Неверно указан порт, должен быть [порт]")
        sys.exit(0)
    except IndexError:
        startOptions['port'] = 7777
        # если порт - не целое число
    except ValueError:
        logger.error(f'Порт должен быть целым числом')
        sys.exit(0)
    try:
        startOptions['mode'] = sys.argv[3]
    except IndexError:
        startOptions['mode'] = 'undefinded'
    return startOptions


def getStartParametrs():
    """
    Получение параметров запуска из командной строки для сервера и клиента (точка входа)
    :param
    :return: startOptions: сформированный список параметров
    """
    global logger
    startOptions = {
        'addr': '',
        'port': 7777,
        'clients': 5
    }
    # если запрос пришел от сервера
    if str(inspect.stack()[1][1]).endswith('server.py'):
        logger = logging.getLogger('server')
        startOptions = paramForServer(startOptions)

    # если запрос пришел от клиента
    elif str(inspect.stack()[1][1]).endswith('client.py'):
        logger = logging.getLogger('client')
        startOptions = paramForClient(startOptions)
    return startOptions
