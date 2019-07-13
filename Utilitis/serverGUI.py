# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\test.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
import threading
from sqlalchemy.orm import sessionmaker, mapper
from sqlalchemy.ext.declarative import declarative_base
import sys
import os
import configparser
sys.path.append('../')
import ServerCore.server as server


Base = declarative_base()


class User(Base):
    """Класс для взаимодействия с БД, таблица User"""
    __tablename__ = 'Clients'
    id = Column(Integer, primary_key = True)
    Login = Column(String)
    Description = Column(String)
    Password = Column(String)

    def __init__(self, login, description, password=""):
        self.Login = login
        self.Description = description
        self.Password = password

    def __repr__(self):
        return f"<User('{self.Login}','{self.Description}','{self.Password} ')>"


class History(Base):
    """Класс для взаимодействия с БД, таблица History"""
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


class Ui_Form(object):
    """Класс GUI сервера"""
    def __init__(self):
        sqlfile=os.path.join(os.path.dirname(__file__), "serverBD.db")
        engine=create_engine(f'sqlite:///{sqlfile}', echo=False, pool_recycle=7200)
        Session=sessionmaker(bind=engine)
        self.session=Session()


    def setupUi(self, Form):
        """Настройка положения окон"""
        Form.setObjectName("Form")
        Form.resize(600, 300)
        self.tableWidget = QtWidgets.QTableWidget(Form)
        self.tableWidget.setGeometry(QtCore.QRect(10, 10, 540, 201))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.btn_getUsers = QtWidgets.QPushButton(Form)
        self.btn_getUsers.setGeometry(QtCore.QRect(10, 270, 131, 23))
        self.btn_getUsers.setObjectName("btn_getUsers")
        self.btn_getHistory = QtWidgets.QPushButton(Form)
        self.btn_getHistory.setGeometry(QtCore.QRect(150, 270, 131, 23))
        self.btn_getHistory.setObjectName("btn_getHistory")
        self.optinsButton=QtWidgets.QPushButton(Form)
        self.optinsButton.setGeometry(QtCore.QRect(290, 270, 131, 23))
        self.optinsButton.setObjectName("optinsButton")
        self.startButton=QtWidgets.QToolButton(Form)
        self.startButton.setGeometry(QtCore.QRect(430, 270, 131, 23))
        self.startButton.setObjectName("startButton")


        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        """Подписи"""
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Серверный GUI"))
        self.btn_getUsers.setText(_translate("Form", "Список пользователей"))
        self.optinsButton.setText(_translate("Form", "Настройки"))
        self.btn_getHistory.setText(_translate("Form", "Статистика клиентов"))
        self.startButton.setText(_translate("Form", "Старт сервера"))
        self.btn_getUsers.clicked.connect(self.userList)
        self.btn_getHistory.clicked.connect(self.historyList)
        self.startButton.clicked.connect(self.startStopServer)
        self.optinsButton.clicked.connect(self.setOptions)

   # sys.path.append('../')
    def setOptions(self):
        """Окно изменения настроек сервера"""
        print('set options')
        self.config = configparser.ConfigParser()
        dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.config.read(f"{dir_path}/{'server.ini'}")
        global config_window
        # Создаём окно и заносим в него текущие параметры
        config_window = ConfigWindow()
        config_window.db_path.insert(self.config['SETTINGS']['Database_path'])
        config_window.db_file.insert(self.config['SETTINGS']['Database_file'])
        config_window.port.insert(self.config['SETTINGS']['Default_port'])
        config_window.ip.insert(self.config['SETTINGS']['Listen_Address'])
        config_window.save_btn.clicked.connect(self.save_server_config)
        config_window.show()

    # Функция сохранения настроек
    def save_server_config(self):
        """Окно сохранения настроек сервера"""

        global config_window
        message=QMessageBox()
        self.config['SETTINGS']['Database_path']=config_window.db_path.text()
        self.config['SETTINGS']['Database_file']=config_window.db_file.text()
        try:
            port=int(config_window.port.text())
        except ValueError:
            message.warning(config_window, 'Ошибка', 'Порт должен быть числом')
        else:
            self.config['SETTINGS']['Listen_Address']=config_window.ip.text()
            if 1023 < port < 65536:
                self.config['SETTINGS']['Default_port']=str(port)
                print(port)
                with open('server.ini', 'w') as conf:
                    self.config.write(conf)
                    message.information(config_window, 'OK', 'Настройки успешно сохранены!')
            else:
                message.warning(config_window, 'Ошибка', 'Порт должен быть от 1024 до 65536')

    def startStopServer(self):
        """Запуск/остановка сервера"""
        print(self.startButton.text())
        if self.startButton.text() == 'Старт сервера':
            self.serv = server.Server()
            t = threading.Thread(target=self.serv.start)
            t.daemon = True
            t.start()  # стартуем вторичный поток
            self.startButton.setText("Выход")
            self.startButton.setShortcut('Ctr+Q')
            self.startButton.setVisible(False)

    def exiteApp(self):
        """Выход из приложения"""
        #sys.exit(qApp.exec_())
        qApp.quit()

    def userList(self):
        """Окно списка пользователей"""
        rt=self.session.query(User.Login).all()
        self.session.commit()
        print(rt)
        self.tableWidget.clear()
        labels = ['NickName']
        self.tableWidget.setColumnCount(len(labels))
        self.tableWidget.setHorizontalHeaderLabels(labels)
        self.tableWidget.setRowCount(len(rt))
        self.tableWidget.setColumnCount(1)
        row = 0
        for x in rt:
            cellinfo=QTableWidgetItem(x[0])
            cellinfo.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.tableWidget.setItem(row, 0, cellinfo)
            row += 1


    def historyList(self):
        """Окно истории пользователей"""
        #rt = self.session.query(History.clientId, func.count(History.clientId)).group_by(History.clientId).all()
        res = self.session.query(User.Login, func.count(History.clientId), History.ConnectTime).join(History, User.id == History.clientId).group_by(User.Login).all()
        self.session.commit()
        self.tableWidget.clear()
        labels=['NickName', 'Заходов','Последний заход']
        self.tableWidget.setColumnCount(len(labels))
        self.tableWidget.setHorizontalHeaderLabels(labels)
        self.tableWidget.setRowCount(len(res))
        row = 0

        for x,y,z in res:
            cellinfo = QTableWidgetItem(x)
            cellinfo2 = QTableWidgetItem(str(y))
            cellinfo3 = QTableWidgetItem(str(z))

            for x in [cellinfo,cellinfo2,cellinfo3]:
            # делаем ячейки только для чтения
                x.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)


            self.tableWidget.setItem(row, 0, cellinfo)
            self.tableWidget.setItem(row, 1, cellinfo2)
            self.tableWidget.setItem(row, 2, cellinfo3)
            row+=1

        print(res)

# Класс окна настроек
class ConfigWindow(QDialog):
    """Класс окна настроек"""
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """Настройка окна"""
        self.setFixedSize(365, 260)
        self.setWindowTitle('Настройки сервера')

        # Надпись о файле базы данных:
        self.db_path_label = QLabel('Путь до файла базы данных: ', self)
        self.db_path_label.move(10, 10)
        self.db_path_label.setFixedSize(240, 15)

        # Строка с путём базы
        self.db_path = QLineEdit(self)
        self.db_path.setFixedSize(250, 20)
        self.db_path.move(10, 30)
        self.db_path.setReadOnly(True)

        # Кнопка выбора пути.
        self.db_path_select = QPushButton('Обзор...', self)
        self.db_path_select.move(275, 28)

        self.db_path_select.clicked.connect(self.open_file_dialog)

        # Метка с именем поля файла базы данных
        self.db_file_label = QLabel('Имя файла базы данных: ', self)
        self.db_file_label.move(10, 68)
        self.db_file_label.setFixedSize(180, 15)

        # Поле для ввода имени файла
        self.db_file = QLineEdit(self)
        self.db_file.move(200, 66)
        self.db_file.setFixedSize(150 , 20)

        # Метка с номером порта
        self.port_label = QLabel('Номер порта для соединений:', self)
        self.port_label.move(10, 108)
        self.port_label.setFixedSize(180, 15)

        # Поле для ввода номера порта
        self.port = QLineEdit(self)
        self.port.move(200, 108)
        self.port.setFixedSize(150, 20)

        # Метка с адресом для соединений
        self.ip_label = QLabel('С какого IP принимаем соединения:', self)
        self.ip_label.move(10, 148)
        self.ip_label.setFixedSize(180, 15)

        # Метка с напоминанием о пустом поле.
        self.ip_label_note = QLabel(' оставьте это поле пустым, чтобы\n принимать соединения с любых адресов.', self)
        self.ip_label_note.move(10, 168)
        self.ip_label_note.setFixedSize(500, 30)

        # Поле для ввода ip
        self.ip = QLineEdit(self)
        self.ip.move(200, 148)
        self.ip.setFixedSize(150, 20)

        # Кнопка сохранения настроек
        self.save_btn = QPushButton('Сохранить' , self)
        self.save_btn.move(190 , 220)

        # Кнапка закрытия окна
        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(275, 220)
        self.close_button.clicked.connect(self.close)

        #self.show()

    # Функция обработчик открытия окна выбора папки
    def open_file_dialog(self):
        """Функция обработчик открытия окна выбора папки"""
        global dialog
        dialog = QFileDialog(self)
        path = dialog.getExistingDirectory()
        path = path.replace('/', '\\')
        self.db_path.insert(path)


def startWind():
    """Отображение формы"""
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()

    app.exec_()
    #sys.exit(app.exec_())


if __name__ == "__main__":
    startWind()


