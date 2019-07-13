'''
Хранение информации в БД на стороне клиента:
a) список контактов;
b) история сообщений
'''

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime, MetaData, Table, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, mapper
from datetime import datetime as currentTime
import os

Base = declarative_base()


class Contacts(Base):
    """Класс для взаимодействия с БД. Таблица Contacts"""
    __tablename__ = 'Contacts'
    id = Column(Integer, primary_key = True)
    Login = Column(String)
    Description = Column(String)

    def __init__(self, login, description='', password=""):
        self.Login = login
        self.Description = description

    def __repr__(self):
        return f"<User('{self.Login}','{self.Description}' ')>"


class LocalContacts(Base):
    """Класс для взаимодействия с БД. Таблица LocalContacts"""
    __tablename__='LocalContacts'
    id = Column(Integer, primary_key=True)
    Login = Column(String)
    Description = Column(String)

    def __init__(self, login, description='', password=""):
        self.Login=login
        self.Description=description

    def __repr__(self):
        return f"<User('{self.Login}','{self.Description}','{self.Password} ')>"

class MessageHistory(Base):
    """Класс для взаимодействия с БД. Таблица MessageHistory"""
    __tablename__='MessageHistory'
    id = Column(Integer, primary_key=True)
    adrLogin = Column(String)
    Message = Column(String)
    MesTime = Column(DateTime)
    InOut = Column(Boolean)

    def __init__(self, login, message, time, inOut):
        self.adrLogin = login
        self.Message = message
        self.MesTime = time
        self.InOut = inOut

    def __repr__(self):
        return f"<User('{self.adrLogin}','{self.Message}','{self.MesTime}','{self.InOut}')>"


class ActiveContacts(Base):
    """Класс для взаимодействия с БД. Таблица ActiveContacts"""
    __tablename__ = 'ActiveContacts'
    id = Column(Integer, primary_key=True)
    Login = Column(String)
    Description = Column(String)
    Date = Column(DateTime)

    def __init__(self, login, date, description='', password=""):
        self.Login = login
        self.Description = description
        self.Date = date

    def __repr__(self):
        return f"<User('{self.Login}','{self.Description}','{self.Password} ', {self.Date})>"


class ClientBD:
    """Класс взаимодействия с БД клиента"""
    def __init__(self):
        # Создаём объект MetaData
        self.metadata = MetaData()
        sqlfile = os.path.join(os.path.dirname(__file__), "clientBD.db")
        self.engine = create_engine(f'sqlite:///{sqlfile}', echo=False, pool_recycle=7200)

        # Создаём таблицу всех пользователей, полученных с сервера
        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.session.query(Contacts).delete()  # очищаем список контактов, т.к. его запросим с сервера
        self.session.query(ActiveContacts).delete()  # очищаем список активных контаков
        self.session.commit()

    def addContactList(self, contlist, myusername):  # заполняем локальную таблицу контактов
        """Добавление контактов а в БД
        :param contlist - список пользователей
        :param myusername - имя пользоателя клиента(чтобы исключить из списка)
       """
        for contact in contlist:
            if contact != myusername:  # свой ник в список контактов не заносим!
                self.session.add(Contacts(contact))
        try:
            self.session.commit()
        except:
            pass

    def IncludeInLocalContactList(self, contactName):
        """Добавление контакта в "друзъя"
            :param contactName - имя контакта
        """
        userID = self.session.query(LocalContacts.id).filter_by(Login=contactName).first()
        if userID is None:
            self.session.add(LocalContacts(contactName))
            self.session.commit()
        else:
            print('Такой контакт уже есть в локальной БД')

    def ExcludeInLocalContactList(self, contactName):
        """Удаление контакта из "друзей"
            :param contactName - имя контакта
        """
        userID = self.session.query(LocalContacts.id).filter_by(Login=contactName).first()
        if userID is None:
            print('Такого контакта нет в локальной БД')
        else:
            self.session.query(LocalContacts).filter_by(id=userID[0]).delete()
            self.session.commit()

    def addMessageToHistory(self, abLogin, message, inOut):
        """Добавление сообщения в историю
            :param abLogin - имя контакта
            :param message - сообщение
            :param inOut - флаг входящее или исходящее
        """
        self.session.add(MessageHistory(abLogin, message, currentTime.now(), inOut))
        self.session.commit()

    def retLocalAllUsersList(self):
        """Запрос списка всех пользователей
        :return - список всех пользователей"""
        try:
            res = self.session.query(Contacts.Login).all()
        except Exception as e:
            print(e)
        print(res)
        # self.session.commit()
        return res

    def retUserContactList(self):
        """Запрос списка друзей
        :return - список друзей"""
        return self.session.query(LocalContacts.Login).all()

    def getHistoryWithUser(self, abLogin):
        """История сообщений с пользователем
        :param - abLogin - имя пользователя
        :return - список сообщений"""
        hist = self.session.query(MessageHistory.InOut, MessageHistory.MesTime, MessageHistory.Message).filter_by(
            adrLogin=abLogin).all()
        return hist


