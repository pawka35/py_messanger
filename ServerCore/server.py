"""
Функции ​​сервера:​
- принимает ​с​ообщение ​к​лиента;
- формирует ​​ответ ​к​лиенту;
- отправляет ​​ответ ​к​лиенту;
- инициализация параметров через файл ini
"""
from socket import socket, AF_INET, SOCK_STREAM
from Protocol.utils import get_message, send_message, create_message, create_work_message
import Protocol.proto_description as proto
import logging
from LOG.logger_deco import Logger
import select
from Utilitis.NonNegativeCheck import NonNegative
from Utilitis.ServerVerifier import ServerVerifier
from Utilitis.ServerBDClass import ServerBD
from Utilitis import serverGUI
import configparser
import os
import hmac
# Получаем серверный логгер по имени, из модуля LOG/server_log_config.py
logger = logging.getLogger('server')


class Server(metaclass=ServerVerifier):
    port = NonNegative()
    sercl = NonNegative()

    def __init__(self):
        """
           Конструктор объекта класса.
        """
        config = configparser.ConfigParser()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        config.read(f"{dir_path}/{'server.ini'}")

        # Загрузка параметров инициализации сервера, если нет параметров, то задаём значения по умоланию.
        self.addr = config['SETTINGS']['Listen_Address']
        port = config['SETTINGS']['Default_port']
        if port == '':
            self.port = 7777
        else:
            self.port = int(port)
        sercl = int(config['SETTINGS']['accept_clients'])
        if sercl == '':
            self.sercl = 5
        else:
            self.sercl = sercl
        # Инициализация базы данных
        database = os.path.join(config['SETTINGS']['Database_path'], config['SETTINGS']['Database_file'])
        self.serverBD = ServerBD(database)  # БД для сервера
        # список объектов клиентских сокетов
        self.clients = []
        # список объектов клиентских сокетов неавторизованных клиентов

        # словарь с никами, id и сокетами пользователей
        self.names = {}
        # определяем экземпляр сервера
        self.server = socket(AF_INET, SOCK_STREAM)
        logger.info(f"{'=' * 10}Инициализация сервера {'=' * 10}")
        print("Сервер инициализирован")

    def start(self):
        """
        Запуск сервера.
        Используем модуль select.
        """
        self.server.bind((self.addr,  self.port))  # присваиваем полученный порт и хост
        self.server.listen(self.sercl)  # начинаем ждать подключения
        # Задержка для корректной работы модуля select
        self.server.settimeout(0.2)

        # действие ниже будут выполняться циклически и во веки веков
        logger.info(f"{'=' * 10}Запуск сервера{'=' * 10}")
        print("Сервер запущен")
        while True:
            try:
                # принимаем запрос на соединение
                conn, addr = self.server.accept()
                logger.info(f"{'=' * 10}Начало соединения{'=' * 10}")
                logger.info(f'Соединение с ip:{addr[0]}, port:{addr[1]}')
                # принимает сообщение клиента
                presence = get_message(conn, addr)
                # определяем ник клиента
                self.client_name = presence['user']['account_name']
                # проверка есть ли такой клиент в нашей БД
                clientSecretPhrase = self.serverBD.getUserSekretKey(self.client_name)
                # если нет, запрашиваем у клиента пароль и добавляем в БД
                if clientSecretPhrase is None:
                    clientSecretPhrase = self.reqPassword(conn)
                    self.serverBD.addNewClient(self.client_name, clientSecretPhrase)
                # если клиент есть, отправляем ему ОК и следуем дальше
                else:
                    response = self.presence_response(presence)
                    send_message(conn, response)

                # аутифицируем клиента
                if self.server_authenticate(conn, clientSecretPhrase):
                    response = self.auth_response(True)
                    send_message(conn, response)
                else:
                    response = self.auth_response(False)
                    send_message(conn, response)
                    conn.close()

            except OSError as e:
                pass  # timeout вышел
            else:
                print(f"Получен запрос на соединение от {str(addr)}")
                self.names[self.client_name] = conn
                # Добавляем клиента в список
                self.clients.append(conn)
                # добавляем ник пользователя в таблицу подлючившихся и выбираем его id
                self.serverBD.addActiveClientToBD(self.client_name, addr, self.clients)
            finally:
                # Проверить наличие событий ввода-вывода
                wait = 0
                r = []  # список клиентов, которые готовы читать
                w = []  # список клиентов, которые готовы читать
            try:
                # получаем клиентов, которые готовы  r - читать,w - писать или отвалились с ошибками - e
                r, w, e = select.select(self.clients, self.clients, [], wait)
            except:
                pass  # Ничего не делать, если нет подключений (ждем)

            requests = self.read_requests(r, self.clients)  # Получаем сообщения от клиентов
            self.write_responses(requests)  # отправляем  сообщения

    def read_requests(self, r_clients, all_clients):
        """
        Чтение сообщений, которые будут посылать клиенты
        :param r_clients: клиенты которые могут отправлять сообщения
        :param all_clients: все клиенты
        :return:
        """
        # Список входящих сообщений
        messages = []
        for sock in r_clients:
            try:
                # Получаем входящие сообщения
                message = get_message(sock)
                # Добавляем их в список
                messages.append((message, sock))
            except:
                # если не можем ответить клиенту, значит он отключился, оповещаем остальных, убираем его из списка
                all_clients.remove(sock)
                try:
                    del self.names[self.client_name]
                except:
                    pass
                self.serverBD.remFromActive(self.client_name)
        # Возвращаем словарь сообщений
        return messages

    def reqPassword(self, conn):
        """
        Запрос пароля у клиента (для добавление в БД)
        :param conn: сокет клиента
        :return: полученный от клиента хэш пароля
        """
        response = self.password_ask()
        send_message(conn, response)
        clientPass = conn.recv(1024)
        return clientPass

    def server_authenticate(self, con, secret_key):
        ''' Запрос аутентификаии клиента.
            сonnection - сетевое соединение (сокет);
            secret_key - ключ шифрования => пароль клиента, который хранится в БД (и вводит клиент у себя)
        '''
        # 1. Создаётся случайное послание и отсылается клиенту
        message = os.urandom(32)
        con.send(message)
        # 2. Вычисляется HMAC-функция (локальный результат) от послания с использованием секретного ключа
        hash = hmac.new(secret_key, message)
        digest = hash.digest()
        # 3. Пришедший ответ от клиента сравнивается с локальным результатом HMAC
        response = con.recv(len(digest))
        return hmac.compare_digest(digest, response)

    # если пользователя нет в БД, запрашиваем у него пароль для добавления в БД
    def password_ask(self):
        """
        Формирование сообщения "такой клиент не найдет"
        :return: сформированное сообщение
        """
        return {proto.PacketType.RESPONSE.value: proto.AnswerCodes.NOT_FOUND.value}

    @Logger()
    # функция формирования ответа
    def presence_response(self, presence_message):
        """
        Формирование ответа при передаче служебных сообщений
        :param presence_message: присланное служебное сообщение
        :return:
        """
        # если сообщение соответствует протоколу
        if proto.PacketType.ACTION.value in presence_message and \
                presence_message[proto.PacketType.ACTION.value] == proto.Actions.PRESENCE.value and \
                proto.PacketType.TIME.value in presence_message and \
                isinstance(presence_message[proto.PacketType.TIME.value], float):
            # отправляем код 200 (ОК)
            return {proto.PacketType.RESPONSE.value: proto.AnswerCodes.OK.value}
        else:
            # если не соответствует, оповещаем ошибкой 400 (Не верный запрос)
            return {proto.PacketType.RESPONSE.value: proto.AnswerCodes.WRONG_REQUEST.value, \
                    proto.PacketType.ERROR.value: 'Не верный запрос'}

    def auth_response(self, auth):
        """
        Формирование ответа о прохождение аутентификации
        :param auth: флаг прохождения
        :return: положительный, либо отрицательный ответ
        """
        if auth:
            return {proto.PacketType.RESPONSE.value: proto.AnswerCodes.OK.value}
        else:
            return {proto.PacketType.RESPONSE.value: proto.AnswerCodes.WRONG_LOGIN.value}

    def write_responses(self, messages):
        """
        Отправка сообщений тем клиентам, которые их ждут
        :param messages: список сообщений
        :return:
        """
        for message, sender in messages:
            print(message)
            # если тип сообщения - сообщение и адреса есть в списке подключенных
            if message['action'] == proto.Actions.MESSAGE.value and message['to']: # in self.names:
                if message['to'] in self.names:
                    adresat = message['to']
                    sock = self.names[adresat]
                    send_message(sock, message)
                # если сообщение адресовано всем, пересылаем каждому из списка подключенных
                if message['to'] == "#all":
                    for x in self.clients:
                        send_message(x, message)
                    # если сообщение адресовано серверу, то смотрим что за команду просят и отправляем назад ответ
                elif message['to'] == 'server':
                    adresat = self.names[message['from']]
                    message['from'] = 'server'
                    sock = adresat
                    if message['message'] == 'show users':
                        message['message'] = f"Список подключенных пользователей: {self.serverBD.getActiveUserNames()}"
                    else:
                        message['message'] = f'Неизвестная команда. Доступные команды -> help'
                    send_message(sock, message)
                # если адресата нет в списке, отправляем назад оповещение об отсутствии адресата
            elif message['action'] == proto.Actions.MESSAGE.value and message['to'] not in self.names:
                adresat = self.names[message['from']]
                message['from'] = 'server'
                message['message'] = f"Адресат {message['to']} недоступен"
                sock=adresat
                send_message(sock, message)

            elif message['action'] == proto.Actions.GETCONTACT.value:
                send_message(sender, {proto.PacketType.RESPONSE.value: proto.AnswerCodes.ACCEPTED.OK.value,
                                      'alert': self.serverBD.getAllUsers()})

            elif message['action'] == proto.Actions.INCLUDECONTACT.value:
                if message['user_id'] in self.serverBD.getAllUsers():
                    message = create_work_message(proto.Actions.INCLUDECONTACT.value, message['user']['account_name'],
                    {'user_id' : message['user_id'], proto.PacketType.RESPONSE.value: \
                                            proto.AnswerCodes.ACCEPTED.OK.value},'server')
                else:
                    message = create_work_message(proto.Actions.INCLUDECONTACT.value, message['user']['account_name'],
                        {'user_id' : message['user_id'], proto.PacketType.RESPONSE.value: \
                                                        proto.AnswerCodes.ACCEPTED.NOT_FOUND.value},'server')
                send_message(sender, message)

            elif message['action'] == proto.Actions.EXCLUDECONTACT.value:
                message = create_work_message(proto.Actions.EXCLUDECONTACT.value, message['user']['account_name'],{'user_id':message['user_id'],proto.PacketType.RESPONSE.value:proto.AnswerCodes.ACCEPTED.OK.value}, 'server')
                print('+'*50)
                print(message)
                send_message(sender, message)


if __name__ == '__main__':
    serverGUI.startWind()



