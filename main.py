import sys

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from base import Ui_MainWindow


class MyWin(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyWin, self).__init__(parent)
        self.setupUi(self)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())
