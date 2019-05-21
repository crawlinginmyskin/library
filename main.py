from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QMessageBox
import sqlite3
from login import loggingUser


class Ui_MainWindow(QWidget):
    def getText(self):
        text, okPressed = QInputDialog.getText(self, "INPUT", "ENTER KEYWORD:", QLineEdit.Normal, "")
        if okPressed and text != '':
            return text

    def loadData(self):
        c = sqlite3.connect('books.db')
        query = "SELECT ID,AUTHOR,TITLE,PUBLISHER,YEAR_PUBLISHED FROM books WHERE LENT_TO is 'nobody'"
        result = c.execute(query)
        self.tableWidget.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.tableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.tableWidget.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))
        c.close()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.addBtn = QtWidgets.QPushButton(self.centralwidget)
        self.addBtn.setGeometry(QtCore.QRect(10, 510, 93, 28))
        self.addBtn.setObjectName("addBtn")

        self.addBtn.clicked.connect(self.add)

        self.delBtn = QtWidgets.QPushButton(self.centralwidget)
        self.delBtn.setGeometry(QtCore.QRect(130, 510, 93, 28))
        self.delBtn.setObjectName("delBtn")

        self.delBtn.clicked.connect(self.delete)

        self.searchBtn = QtWidgets.QPushButton(self.centralwidget)
        self.searchBtn.setGeometry(QtCore.QRect(510, 510, 93, 28))
        self.searchBtn.setObjectName("searchBtn")

        self.searchBtn.clicked.connect(self.search)

        self.lrBtn = QtWidgets.QPushButton(self.centralwidget)
        self.lrBtn.setGeometry(QtCore.QRect(640, 510, 93, 28))
        self.lrBtn.setObjectName("lrBtn")

        self.lrBtn.clicked.connect(self.lr)

        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(0, 0, 801, 461))
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setRowCount(0)
        self.tableWidget.horizontalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setVisible(False)
        self.loadBtn = QtWidgets.QPushButton(self.centralwidget)
        self.loadBtn.setGeometry(QtCore.QRect(290, 470, 151, 111))
        self.loadBtn.setObjectName("loadBtn")

        self.loadBtn.clicked.connect(self.loadData)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.addBtn.setText(_translate("MainWindow", "Add"))
        self.delBtn.setText(_translate("MainWindow", "Delete"))
        self.searchBtn.setText(_translate("MainWindow", "Search"))
        self.lrBtn.setText(_translate("MainWindow", "Lend/Return"))
        self.loadBtn.setText(_translate("MainWindow", "LOAD"))

    def search(self):
        c = sqlite3.connect('books.db')
        keyword = self.getText()
        result = c.execute("SELECT ID,AUTHOR,TITLE,PUBLISHER,YEAR_PUBLISHED FROM books WHERE AUTHOR LIKE ? OR "
                           "TITLE LIKE ? OR "
                           "PUBLISHER LIKE ? OR "
                           "YEAR_PUBLISHED LIKE ?"
                           , ('%'+keyword+'%', '%'+keyword+'%', '%'+keyword+'%', '%'+keyword+'%'))
        self.tableWidget.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.tableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.tableWidget.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))
        c.close()

    def add(self):
        c = sqlite3.connect('books.db')
        data = []

        for x in range(4):
            data.append(self.getText())
        for x in range(4):
            if data[x] is None:
                QMessageBox.about(self, "ERROR", "You left one of the fields empty")
                return 0
        try:
            int(data[3])
        except ValueError:
            QMessageBox.about(self, "ERROR", "Year of publishing must be an integer")
            return 0
        c.execute("INSERT INTO books(AUTHOR,TITLE,PUBLISHER,YEAR_PUBLISHED,LENT_TO) "
                  "VALUES(?,?,?,?,'nobody')", (data[0],
                                               data[1],
                                               data[2],
                                               int(data[3])))

        c.commit()
        self.loadData()
        c.close()

    def delete(self):
        c = sqlite3.connect('books.db')
        deleteid = self.getText()
        c.execute("DELETE FROM books WHERE ID =?", (deleteid,))
        c.commit()
        c.close()
        self.loadData()
    def lr(self):
        c = sqlite3.connect('books.db')
        conn = c.cursor()
        lrid = self.getText()
        conn.execute("SELECT LENT_TO FROM books WHERE ID=?", (lrid,))
        lendstatus = conn.fetchall()[0][0]
        if lendstatus == 'nobody':
            c.execute("UPDATE books SET LENT_TO = ? WHERE ID =?", (loggingUser.login, lrid))
            c.commit()
            self.loadData()
            QMessageBox.about(self, "SUCCESS", "The book was successfully lent")
        elif lendstatus == loggingUser.login:
            c.execute("UPDATE books SET LENT_TO = 'nobody' WHERE ID = ?", (lrid,))
            c.commit()
            self.loadData()
            QMessageBox.about(self, "SUCCESS", "The book was successfully returned")

        else:
            QMessageBox.about(self, "ERROR", "Operation unavailable")

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    ui.loadData()
    sys.exit(app.exec_())
