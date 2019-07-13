import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from queue import Queue
import threading
from ClientCore.client import Client as Finder
from Utilitis.clientGUI import Ui_Form as Ui_FinderForm
from Protocol.proto_description import Helpers as verb
from Protocol.proto_description import Actions as action
from datetime import datetime as currentTime
from LOG.logger_deco import client_login_required


class ClientCliMonitor(QObject):
    ''' Класс-монитор, принимающий входящие сообщения из очереди результатов
        Данный класс будет помещён в отдельный поток QThread
    '''
    gotData = pyqtSignal(tuple)

    def __init__(self, parent, login, password):
        super().__init__()
        self.parent = parent
        self.login = login
        self.password = password
        self.res_queue = Queue()
        # cоздаем экземпляр нашего клиента из модуля client.py
        self.clientCli = Finder(self.login, self.password, self.res_queue)
        self.t = threading.Thread()
        # запускаем нашего клиента в отдельном от GUI потоке
        t = threading.Thread(target=self.clientCli.start)
        t.daemon = True
        t.start()

    def getResultFromQueny(self):
        """
           функция постоянно читает очередь, при результате, передает сообщение в GUI
           :return:
        """
        while True:
            data = self.res_queue.get()
            if data is None:
                break
            self.gotData.emit(data)
            self.res_queue.task_done()


# класс GUI клиента
class ClientGui(QtWidgets.QDialog):
    """Класс GUI клиента"""
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        # создаем объект класса нашего модуля со сгенерированным GUI
        self.ui = Ui_FinderForm()
        self.ui.setupUi(self)
        # навешиваем событие на кнопку "Войти"
        self.ui.loginBtn.clicked.connect(self.start)
        # навешиваем событие на кнопку "Отправить всем"
        self.ui.sendAllButton.clicked.connect(self.sendToAll)
        # параметры для форматированного отображения текста
        self.blue = "<span style=\"  color:#0000e6;\" >"
        self.red = "<span style=\"  color:#ff0000;\" >"
        self.localConList = []  # локальный список избранных пользователей
        self.monitor = None

    # функция принимает сигналы и отображает принятые сообщения в нужной вкладке
    @pyqtSlot(tuple)
    def update_results(self, data):
        """функция принимает сигналы и отображает принятые сообщения в нужной вкладке"""
        message = data[0]
        # если личное сообщение, то отображаем во вкладке пользователя-адресата
        if message['to'] != '#all':
            self.createUserTab(data[0]['from'], message)
        else:  # если сообщение для всех, то отображаем его во вкладке "для всех"
            self.createUserTab('#all', message)

    # функция запуска алгоритма
    def start(self):
        """функция запуска алгоритма"""
        self.ui.loginBtn.setEnabled(False)  # когда вошли на сервер, убираем кнопку логин
        self.loginName = self.ui.loginEdit.toPlainText()
        password = self.ui.passwordEdit.toPlainText()
        self.monitor = ClientCliMonitor(self, self.loginName, password)
        self.monitor.gotData.connect(self.update_results)

        # Создание потока и помещение объекта-монитора в этот поток
        self.thread = QThread()
        self.monitor.moveToThread(self.thread)
        # При запуске потока будет вызван метод getResultFromQueny
        self.thread.started.connect(self.monitor.getResultFromQueny)
        # Запуск потока, который запустит self.monitor.getResultFromQueny
        self.thread.start()
        self.thread.sleep(1)

        # получаем от сервера список всех зарегестрированных пользовталей
        contList = self.monitor.clientCli.clientDB.retLocalAllUsersList()
        self.ui.sendAllButton.setEnabled(True)

        # получаем из локальной БД список друзей
        [self.localConList.append(x[0]) for x in self.monitor.clientCli.clientDB.retUserContactList()]

        # выводим всех полученных пользователей на одну вкладку контакт-листа
        for x in contList:
            self.ui.listView.addItem(x[0])
        # навешиваем событие по двойному клику - открыть вкладку для общения с данным пользователем
        self.ui.listView.itemDoubleClicked.connect(self.createUserTab)

        # выводим всех наших друзей  на другую вкладку контакт-листа
        for x in self.localConList:
            self.ui.listView_2.addItem(x)
        # также навшиваем событие по двойному клику
        self.ui.listView_2.itemDoubleClicked.connect(self.createUserTab)

    # cоздаем вкладку для пользователя от которого пришло сообщение (или по которому 2 раза кликнули в списке)
    def createUserTab(self, item, message = None):
        """cоздаем вкладку для пользователя от которого пришло сообщение (или по которому 2 раза кликнули в списке)"""
        # вкладка может быть вызвана при приеме сообщения(тогда приходит имя), либо по двойному клику(приходит элемент)
        if isinstance(item, QtWidgets.QListWidgetItem):
            userName = item.text()
        else:
            userName = item

        # ищем вкладку на нашей панели
        tab_2 = self.ui.tabWidget.findChild(type(QtWidgets.QWidget()), userName)

        if tab_2 is None:  # если такой вкладки еще не существует, то создаем ее
            tab_2 = QtWidgets.QWidget()
            tab_2.setObjectName(f"{userName}")

            self.ui.tabWidget.addTab(tab_2, "")
            self.ui.tabWidget.setTabText(self.ui.tabWidget.indexOf(tab_2), userName)

            textBrowser = QtWidgets.QTextBrowser(tab_2)
            textBrowser.setGeometry(QtCore.QRect(10, 10, 381, 211))
            textBrowser.setObjectName(userName)

            # получаем и выводим историю общения с данным абонентом
            self.getHistoryWithUser(userName, textBrowser)

            textEdit = QtWidgets.QTextEdit(tab_2)
            textEdit.setGeometry(QtCore.QRect(10, 230, 381, 91))
            textEdit.setObjectName(userName)

            # кнопка отправки сообщения
            sendMessageButton = QtWidgets.QPushButton(tab_2)
            sendMessageButton.setGeometry(QtCore.QRect(320, 340, 75, 23))
            sendMessageButton.setObjectName(userName)
            sendMessageButton.setText("Отправить")
            # навешиваем на кнопку функцию отправки сообщения пользователю
            sendMessageButton.clicked.connect(
                lambda: self.sendMessgaFor(userName, textEdit.toPlainText(), textEdit, textBrowser))

            # кнопка добавления в друзья
            toLocalList = QtWidgets.QPushButton(tab_2)
            toLocalList.setGeometry(QtCore.QRect(200, 340, 75, 23))
            toLocalList.setObjectName(userName)

            # если пользователь не в списке наших друзей, то надпись вешаем функцию "добавить в друзья"
            if userName not in self.localConList:
                toLocalList.setText("В друзья")
                toLocalList.clicked.connect(lambda: self.addToFriends(userName,toLocalList))
            # если пользователь уже в списке наших друзей, то надпись вешаем функцию "убрать из друзей"
            else:
                toLocalList.setText("Убрать")
                toLocalList.clicked.connect(lambda: self.remFromFriends(userName,toLocalList))

        # если получили сообщение и это сообщение не от нас (в случае рассылки всем)
        if message is not None and message['from'] != self.loginName:
            # ищем элемент отображения сообщений и добавляем в него текст
            tb = tab_2.findChild(type(QtWidgets.QTextBrowser()), userName)
            if message['to'] != "#all":
                tb.append(f"{self.dateForm(currentTime.now())} ◄◄ {self.red}{message[action.MESSAGE.value]}</span> ")
                self.monitor.clientCli.clientDB.addMessageToHistory(message[verb.FROM.value], message[action.MESSAGE.value], False)
            else:
                tb.append(f"{self.dateForm(currentTime.now())} || {message[verb.FROM.value]} говорит ◄◄ {self.red}"
                          f"{message[action.MESSAGE.value]}</span> ")
        # делаем данную вкладку активной
        self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.indexOf(tab_2))  # делаем активной вкладку выбранного пользователя

    # функция "убрать из друзей"
    def remFromFriends(self, userName,toLocalList):
        """функция - убрать из друзей"""
        # добавляем в локальную БД в список друзей
        self.monitor.clientCli.clientDB.ExcludeInLocalContactList(userName)
        # убираем имя данного пользователя из списка друзей (чтоб не переопрашивать БД)
        curItem = self.ui.listView_2.findItems(userName, QtCore.Qt.MatchExactly)
        re = self.ui.listView_2.row(curItem[0])
        self.ui.listView_2.takeItem(re)
        # меняем надпись на кнопке во вкладке данного друга
        toLocalList.setText('В друзья')
        # отвязываем событие
        toLocalList.clicked.disconnect()
        # вешаем новое событие (т.к. мы его удалили, теперь снова можем добавить в друзья)
        toLocalList.clicked.connect(lambda: self.addToFriends(userName, toLocalList))

    # функция "добавить в друзья", алгоритм аналогичем remFromFriends
    def addToFriends(self, userName,toLocalList):
        """функция "добавить в друзья", алгоритм аналогичем remFromFriends"""
        self.monitor.clientCli.clientDB.IncludeInLocalContactList(userName)
        self.ui.listView_2.addItem(userName)
        toLocalList.setText('Убрать')
        toLocalList.clicked.disconnect()
        toLocalList.clicked.connect(lambda: self.remFromFriends(userName, toLocalList))

    # функция отправки сообщения все пользователям
    def sendToAll(self):
        """функция отправки сообщения все пользователям"""
        self.sendMessgaFor("#all", self.ui.textEdit.toPlainText(), self.ui.textEdit, self.ui.textBrowser, toall=True)

    @client_login_required
    # функция отправки сообщения конкретному пользователю
    def sendMessgaFor(self, adresat, text, textEdit, textBrowser, toall=False):
        """функция отправки сообщения конкретному пользователю"""
        if text == '':
            return
        self.monitor.clientCli.write_messages(f"message {adresat} {text}")
        textEdit.clear()
        textBrowser.append(f"{self.dateForm(currentTime.now())} ►► {self.blue}{text}</span> ")
        if not toall:
            self.monitor.clientCli.clientDB.addMessageToHistory(adresat, text, True)

    # получение истории сообщений с данным пользователем, для отображения в его вкладке
    def getHistoryWithUser(self, login, textBrowser):
        """получение истории сообщений с данным пользователем, для отображения в его вкладке"""
        #  true - исходящие, false = входящие
        hist = self.monitor.clientCli.clientDB.getHistoryWithUser(login)
        for x in hist:
            if not x[0]:  # входящее сообщение
                textBrowser.append(f"{self.dateForm(x[1])} ◄◄ {self.red}{x[2]}</span>")
            else:  # исходящие сообщения
                textBrowser.append(f"{self.dateForm(x[1])} ►► {self.blue}{x[2]}</span> ")
        textBrowser.append(f"{'='*10} Конец истории сообщений {'='*10}")
        textBrowser.append(f" ")

    # функция форматирования даты для вывода
    def dateForm(self, date):
        """функция форматирования даты для вывода"""
        result = date.strftime('%d.%m.%Y %H:%M:%S')
        return result


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    progress = ClientGui()
    progress.show()
    sys.exit(app.exec_())
