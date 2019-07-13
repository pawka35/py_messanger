"""
Функции клиента:​
- подключается к серверу
- принимает ​с​ообщение ​от сервера;
- формирует ​​ответ серверу;
- имеет ​​параметры ​к​омандной ​с​троки:
- <addr> [port]
​-​ ​I​P-адрес ​​сервер ​(​по ​у​молчанию ​localhost).
- [port] ​-​ ​​TCP-порт ​​для ​​работы ​(​по ​у​молчанию ​​использует ​​порт ​​7777);
- Реализован функционал работы со списком контактов по протоколу JIM:
"""
from socket import socket, AF_INET, SOCK_STREAM
from Protocol.utils import get_message, send_message, getStartParametrs, create_message
from Protocol.proto_description import PacketType as pctType
from Protocol.proto_description import Actions as action
from Protocol.proto_description import AnswerCodes as answer
from Protocol.proto_description import Helpers as verb
import datetime
from Protocol.proto_description import RESPONSE_CODES
import Utilitis.errors as errors
import sys
import time
import logging
import LOG.client_log_config
from LOG.logger_deco import Logger
import threading
from Utilitis.ClientVerifier import ClientVerifier
from Utilitis.ClientBDClass import ClientBD
import hmac
import hashlib

logger = logging.getLogger('client')
RECONNECT_TIME = 1  # константа для задержки между неудачными попытками подключения к серверу


class Client(metaclass=ClientVerifier):
    def __init__(self, login, password, res_queue=None):
        """
           Конструктор эклземпляра класса:
           :param login: имя пользователя
           :param password: пароль из GUI
           :param res_queue: очередь для приема сообщений
           :return:
        """
        # получаем параметры для запуска соединения (хост, порт сервера)
        self.startOption = getStartParametrs()
        # предлагаем пользователю ввести свой ник
        self.username = login  # создаем пользователя для текущего сеанса
        self.password = self.criptPassword(password)  # шифруем пароль для дальнейшего использования
        logger.info(f"{'=' * 10}Начало сеанса{'=' * 10}")
        self.clientDB = ClientBD()  # инициализация БД клиента
        self.res_queue = res_queue
        self.auth = False  # флаг аутентификации

    def connectToServer(self, client, countTry):
        """
        Соединенеие с сервером
        :param client: сокет
        :param startOption: хост и порт сервера
        :param countTry: кол-во попыток подключения
        :return:
        """
        try:
            if self.startOption['addr'] == '':
                self.startOption['addr']='localhost'
            client.connect((self.startOption['addr'], self.startOption['port']))
            logger.info('Успешно подключились к серверу')
        except Exception as e:
            print(e)
            # если подключение не удалось, увеличиваем счетчик, пробуем еще, пока счетчик не зашкалит
            logger.info(f'Сервер не запущен...переподключение через {RECONNECT_TIME} сек (попытка{countTry})')
            print(f'Сервер не запущен...переподключение через {RECONNECT_TIME} сек (попытка{countTry})')
            countTry += 1
            if countTry > 5:
                print('Сервер не отвечает. Проверьте правильность указания сервера.')
                logger.error('Сервер не отвечает. Проверьте правильность указания сервера.')
                sys.exit(0)
            else:
                time.sleep(RECONNECT_TIME)
                self.connectToServer(client, self.startOption, countTry)  # да-да! это рекурсия :)

    def start(self, password=None):
        """
         Запуск клиента:
         :param password: пароль в текстовом виде, из поля для ввода пароля GUI-клиента
         :return:
         """
        client = socket(AF_INET, SOCK_STREAM)  # Создать сокет TCP
        self.ourSocket = client
        # подключаемся к серверу
        self.connectToServer(client,  0)
        # Формируем сообщение серверу
        presence = self.create_presence(account_name=self.username, password=password)
        # Отправляем сообщение серверу
        send_message(client, presence)
        # получаем ответ, авторизованы ли мы
        response = get_message(client)
        # разбираем ответ
        response = self.translate_message(response)
        # если сервер ответил, что нас нет, отправляем ему данные для регистрации
        if response['response'] == answer.NOT_FOUND.value:
            self.ourSocket.send(self.password)
        print('Сервер знает про нас')
        # проходим аутентификация на сервере
        self.client_authenticate()
        # получаем результат аутентификации
        response = get_message(client)
        # Разобрать ответ сервера
        response = self.translate_message(response)
        # если ответ с кодом 200 (ОК)
        if response['response'] == answer.OK.value:
            print("Прошли аутентификацию")
            self.auth = True # ставим признак того, что пользователь аутентифицирован
            logger.info(f"{'=' * 10}Успешное подключение{'=' * 10}")
            self.getAllUsers(client)
            # запускам вторичный поток, в котором будем ожидать и работать с входящими сообщениями
            t = threading.Thread(target=self.read_messages, args=(client,))
            t.start()  # стартуем вторичный поток
            # в первичном потоке переходим в функцию с бесконечным циклом ввода и отправки сообщений
            self.write_messages(self.username)
        else:
            print("Не прошли аутентификацию")
            client.close()

    # шифруем пароль для передачи на сервер
    def criptPassword(self, password):
        """
         Шифрование пароля:
         :param password: пароль в текстовом виде, из поля для ввода пароля GUI-клиента
         :return: хэш пароля с солью
         """
        # Генерируем хэш пароля, в качестве соли будем использовать логин в нижнем регистре.
        salt = self.username.lower().encode('utf-8')
        passwd_hash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 10000)
        return passwd_hash

    def client_authenticate(self):
        """
           Аутентификация клиента на сервере.
           :return:
        """
        # принимаем случайное послание от сервера
        message = self.ourSocket.recv(32)
        # вычисляем HMAC-функцию
        hash = hmac.new(self.password, message)
        digest = hash.digest()
        # отправляем ответ серверу
        self.ourSocket.send(digest)

    def read_messages(self, client):
        """
        Клиент читает входящие сообщения в бесконечном цикле
        :param client: сокет клиента
        :return
        """
        # бесконечный цикл, к котором мы постоянно пытаемся принять сообщение

        while True:
            # принимаем сообщение
            message = get_message(client, '')
            self.res_queue.put((message, ''))
            self.res_queue.join()

    # функция разбора ответа сервера
    @Logger()
    def translate_message(self, response):
        """
        Разбор сообщения от сервера
        :param response: Словарь ответа от сервера
        :return: корректный словарь ответа
        """
        # Передали не словарь
        if not isinstance(response, dict):
            raise TypeError
        # Нету ключа response
        if pctType.RESPONSE.value not in response:
            # Ошибка нужен обязательный ключ
            raise errors.MandatoryKeyError(pctType.RESPONSE.value)
        # если все хорошо, то
        # получаем код ответа
        code = response[pctType.RESPONSE.value]
        # длина кода не 3 символа
        if len(str(code)) != 3:
            # Ошибка неверная длина кода ошибки
            raise errors.ResponseCodeLenError(code)
        # неправильные коды символов
        if code not in RESPONSE_CODES:
            # ошибка неверный код ответа
            raise errors.ResponseCodeError(code)
        # возвращаем ответ
        return response

    @Logger()
    def create_presence(self, account_name="Guest", password=None):
        """
        Формируем запрос на подключение к серверу
        :param account_name: имя пользователя, по=умолчанию Guest
        :param password: пароль, передается только в случае регистрации, в остальных - пустая строка
        :return message - сообщение для сервера о попытки подключения по протоколу
        """
        # если имя пользователя состоит только из цифр, то выкидывам ошибку
        if str(account_name).isnumeric():
            raise errors.DigitName(account_name)

        # если имя пользователя передан тип None, то выкидывам ошибку
        if account_name is None:
            raise errors.OutOfUserName

        # Если длина имени пользователя больше 25 символов,то выкидывам ошибку
        if isinstance(account_name, str) and len(account_name) > 25:
            raise errors.UsernameToLongError(account_name)
        # если все хорошо, то
        # формируем словарь сообщения
        message = {
            pctType.ACTION.value: action.PRESENCE.value,
            pctType.TIME.value: time.time(),
            pctType.USER.value: {
                pctType.ACCOUNT_NAME.value: account_name,
                pctType.PASSWORD.value: password
            }
        }
        # возвращаем сообщение в виде словаря
        return message


    def write_messages(self, message_str):
        """
                Клиент ждет ввода сообщения в бесконечном цикле и отправляет их на сервер
                :param client: сокет клиента
                :param currClient: класс клиента, содержащий ник
                :return
                """
        if message_str.startswith('message'.lower()):
            # если со слова message, то делим на части
            params = message_str.split()
            try:
                # первое слово - это адресат
                to = params[1]
                # все последующие - это сообщение
                text = ' '.join(params[2:])
            # если разобрать не удалось, показываем сообщение
            except IndexError:
                print('Не задан получатель или текст сообщения')
            else:
                # если все ок, формируем сообщение и оправляем его на сервер
                message = create_message(to, text, self.username)
                send_message(self.ourSocket, message)

        elif message_str.startswith('add'.lower()):
            params = message_str.split()
            send_message(self.ourSocket, self.InContact(params[1]))
        elif message_str.startswith('rem'.lower()):
            params=message_str.split()
            send_message(self.ourSocket, self.DellContact(params[1]))

    def getAllUsers(self, client):
        """
            Запрос и получения списка контактов из БД сервера
            :param client: сокет клиента дял отправки сообщения с запросом списка пользователей
            :return
        """
        # формируем сообщение с запросом списка
        message = {
            pctType.ACTION.value: action.GETCONTACT.value,
            pctType.TIME.value: time.time(),
            pctType.USER.value: {pctType.ACCOUNT_NAME.value: self.username}}
        # отправляем сообщение на сервер
        send_message(client, message)
        # принимает ответ
        response = get_message(client, '')
        # заносим принятые контакты в локальную БД
        self.clientDB.addContactList(response['alert'], self.username)

    def InContact(self, contactName, stage=0):
        """
           Добавление контакта в локальную БД пользователя
           :param contactName: имя контакта
           :param stage - на каком этапе добавления (запрос, или уже добавляем)
        """
        if stage == 0:
            # формируем сообщение серверу о желании добавить в друзья данный контакт
            message = {
                pctType.ACTION.value: action.INCLUDECONTACT.value,
                'user_id': contactName,
                pctType.USER.value: {pctType.ACCOUNT_NAME.value: self.username},
                pctType.TIME.value: time.time(),
            }
            return message
        else:
            print('Сервер разрешил, добавляем')
            self.clientDB.IncludeInLocalContactList(contactName)

    def DellContact(self, contactName, stage=0):
        """Удаление контакта из локальной БД пользователя
          :param contactName: имя контакта
          :param stage - на каком этапе добавления (запрос, или уже добавляем)"""

        if stage == 0:
            message = {
                pctType.ACTION.value: action.EXCLUDECONTACT.value,
                'user_id': contactName,
                pctType.USER.value: {pctType.ACCOUNT_NAME.value: self.username},
                pctType.TIME.value: time.time(),
            }
            return message
        else:
            print('Сервер разрешил, добавляем')
            self.clientDB.ExcludeInLocalContactList(contactName)


