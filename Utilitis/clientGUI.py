# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\new.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    """Класс окна client GUI"""
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(583, 481)
        self.loginBtn = QtWidgets.QPushButton(Form)
        self.loginBtn.setGeometry(QtCore.QRect(420, 20, 75, 23))
        self.loginBtn.setObjectName("loginBtn")
        self.paramBtn = QtWidgets.QPushButton(Form)
        self.paramBtn.setGeometry(QtCore.QRect(500, 20, 75, 23))
        self.paramBtn.setObjectName("paramBtn")
        self.loginEdit = QtWidgets.QTextEdit(Form)
        self.loginEdit.setGeometry(QtCore.QRect(290, 20, 111, 21))
        self.loginEdit.setObjectName("loginEdit")
        self.tabWidget2 = QtWidgets.QTabWidget(Form)
        self.tabWidget2.setGeometry(QtCore.QRect(436, 60, 141, 401))
        self.tabWidget2.setObjectName("tabWidget2")
        self.tab_21 = QtWidgets.QWidget()
        self.tab_21.setObjectName("tab_21")
        self.listView = QtWidgets.QListWidget(self.tab_21)
        self.listView.setGeometry(QtCore.QRect(0, 1, 131, 371))
        self.listView.setObjectName("listView")
        self.tabWidget2.addTab(self.tab_21, "")
        self.tab_22 = QtWidgets.QWidget()
        self.tab_22.setObjectName("tab_22")
        self.listView_2 = QtWidgets.QListWidget(self.tab_22)
        self.listView_2.setGeometry(QtCore.QRect(0, 0, 131, 371))
        self.listView_2.setObjectName("listView_2")
        self.tabWidget2.addTab(self.tab_22, "")
        self.tabWidget = QtWidgets.QTabWidget(Form)
        self.tabWidget.setGeometry(QtCore.QRect(20, 60, 411, 401))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("#all")
        self.textBrowser = QtWidgets.QTextBrowser(self.tab)
        self.textBrowser.setGeometry(QtCore.QRect(10, 10, 381, 211))
        self.textBrowser.setObjectName("#all")
        self.sendAllButton = QtWidgets.QPushButton(self.tab)
        self.sendAllButton.setGeometry(QtCore.QRect(294, 340, 101, 23))
        self.sendAllButton.setObjectName("sendAllButton")
        self.sendAllButton.setEnabled(False)
        self.textEdit = QtWidgets.QTextEdit(self.tab)
        self.textEdit.setGeometry(QtCore.QRect(10, 230, 381, 91))
        self.textEdit.setObjectName("textEdit")
        self.tabWidget.addTab(self.tab, "")

        self.passwordEdit = QtWidgets.QTextEdit(Form)
        self.passwordEdit.setGeometry(QtCore.QRect(290, 50, 111, 21))
        self.passwordEdit.setObjectName("passwordEdit")
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(186, 20, 91, 20))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(230, 50, 47, 13))
        self.label_2.setObjectName("label_2")

        self.retranslateUi(Form)
        self.tabWidget2.setCurrentIndex(0)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        """Подписи кнопок"""
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Messenger"))
        self.loginBtn.setText(_translate("Form", "Войти"))
        self.paramBtn.setText(_translate("Form", "Опции"))
        self.tabWidget2.setTabText(self.tabWidget2.indexOf(self.tab_21), _translate("Form", "Общий"))
        self.tabWidget2.setTabText(self.tabWidget2.indexOf(self.tab_22), _translate("Form", "Личный"))
        self.sendAllButton.setText(_translate("Form", "Отправить всем"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Form", "Общий чат"))
        self.label.setText(_translate("Form", "Имя пользоателя"))
        self.label_2.setText(_translate("Form", "Пароль"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

