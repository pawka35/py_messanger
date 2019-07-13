'''
В качестве СУБД используем sqlite.
Опорная схема базы данных:
На стороне сервера БД содержит следующие таблицы:
1) клиент:
a) логин;
b) информация.
2) история клиента:
a) время входа;
b) ip-адрес.
3) список контактов (составляется на основании выборки всех записей с id владельца):
a) id владельца;
b) id клиента.
'''

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime, MetaData, Table, ForeignKey
from sqlalchemy.orm import sessionmaker, mapper
import os
from datetime import datetime as currentTime
from LOG.logger_deco import server_login_required


Base = declarative_base()


# На основании базового класса можно создавать необходимые классы
class User(Base):
    """Класс для взаимодействия с БД. Таблица Clients"""
    __tablename__ = 'Clients'
    id = Column(Integer, primary_key = True)
    Login = Column(String)
    Description = Column(String)
    Password = Column(String)

    def __init__(self, login, description="", password=""):
        self.Login = login
        self.Description = description
        self.Password = password

    def __repr__(self):
        return f"<User('{self.Login}','{self.Description}','{self.Password} ')>"


class History(Base):
    """Класс для взаимодействия с БД. Таблица History"""
    __tablename__ = 'History'
    id = Column(Integer, primary_key = True)
    clientId = Column(Integer)
    ConnectTime = Column(DateTime)
    Ip = Column(String)

    def __init__(self, clientId, connectTime, ipaddress):
        self.clientId = clientId[0]
        self.ConnectTime = connectTime
        self.Ip = ipaddress

    def __repr__(self):
        return f"<User('{self.clientId}','{self.ConnectTime}', '{self.Ip}')>"



class ActiveUser(Base):
    """Класс для взаимодействия с БД. Таблица ActiveUser"""
    __tablename__ = 'ActiveUser'
    id = Column(Integer, primary_key = True)
    clientId = Column(Integer)
    ConnectTime = Column(DateTime)
    Ip = Column(String)
    Port = Column(Integer)

    def __init__(self, clientId, connectTime, conn):
        self.clientId = clientId[0]
        self.ConnectTime = connectTime
        self.Ip = conn[0]
        self.Port = conn[1]

    def __repr__(self):
        return f"<User('{self.clientId}','{self.ConnectTime}', '{self.Ip}', '{self.Port}')>"


class ServerBD:
    """Класс для взаимодействия с БД"""
    def __init__(self, bdFile):
        # Создаём объект MetaData
        self.metadata = MetaData()
        sqlfile = os.path.join(os.path.dirname(__file__), bdFile)
        self.engine = create_engine(f'sqlite:///{sqlfile}', echo=False, pool_recycle=7200)

        # Создаём таблицы
        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        # Если в таблице активных пользователей есть записи, то их необходимо удалить
        self.session.query(ActiveUser).delete()
        self.session.commit()

    def addNewClient(self, login, password):
        """Добавление нового клиента в БД
        :param login - имя пользователя
        :param password - пароль
        """
        client = User(login, password=password)
        self.session.add(client)
        self.session.commit()

    @server_login_required
    def addActiveClientToBD(self, login, connInfo, clients):
        """Добавление активного клиента в БД
        :param login - имя пользователя
        :param connInfo - ip, port
        :return id пользователя
        """
        # ищем есть ли такой ник в БД
        userid = self.session.query(User.id).filter_by(Login=login).first()
        activeUser = ActiveUser(userid, currentTime.now(), connInfo)  # добавляем клиента в активные
        history = History(userid, currentTime.now(), connInfo[0])  # добавляем историю входа в БД
        self.session.add(activeUser)
        self.session.add(history)
        self.session.commit()
        return userid[0]

    # исключаем пользователя из активных
    def remFromActive(self, login):
        """Исключение пользователя из таблицы активных
        :param login - имя пользователя
        """
        userID = self.session.query(User.id).filter_by(Login=login).first()[0]
        print(userID)
        self.session.query(ActiveUser).filter_by(clientId=userID).delete()
        self.session.commit()

    # список активных пользователей
    def getActiveUserNames(self):
        """Получение списка активных пользователей
        :return список активных пользователей
        """
        resList =[]
        logins = self.session.query(User.Login).\
            join(ActiveUser, ActiveUser.id == User.id).all()
        [resList.append(x[0]) for x in logins]
        return resList

    def getAllUsers(self):
        """Получение списка  пользователей
        :return список  пользователей
        """
        resList = []
        logins = self.session.query(User.Login).all()
        [resList.append(x[0]) for x in logins]
        return resList

    def getaCon(self, withTime=False):
        """Получение истории заходов пользователей
        :return список истории заходов пользователей
        """
        resList = []
        logins = self.session.query(User.Login, ActiveUser.ConnectTime). \
            join(ActiveUser, ActiveUser.id == User.id).all()
        if not withTime:
            [resList.append(x[0]) for x in logins]
        else:
            resList = logins
        return resList

    def getUserSekretKey(self, login):
        """Получение хэша пароля пользователя
        :return хэш пароля пользователя
        """
        result = self.session.query(User.Password).filter_by(Login=login).first()
        if result is not None:
            return result[0]
        else:
            return None


if __name__ == '__main__':
    se = ServerBD()
    se.getaCon(True)



'''
# Простой запрос
    q_user = session.query(User).filter_by(Login="vasia").first()
    print('Simple query:', q_user)

# Добавить сразу несколько записей
session.add_all([User("kolia", "Cool Kolian[S.A.]","kolia$$$"),
                 User("zina", "Zina Korzina", "zk18")])

# Сессия "знает" об изменениях пользователя
admin_user.password = "-=VP2001=-"
print('Session. Changed objects:', session.dirty)

# Атрибут `new` хранит объекты, ожидающие сохранения в базу данных
print('Session. New objects:', session.new)

# Метод commit() фиксирует транзакцию, сохраняя оставшиеся изменения в базу
session.commit()

print('User ID after commit:', admin_user.id)
'''