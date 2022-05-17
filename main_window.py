import sys
import time
from random import randint
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from base import Ui_MainWindow
import threading
from PyQt5.QtWidgets import QTextBrowser
from functools import partial
from collections import deque
import numpy as np
import pyqtgraph as pg
from pyqtgraph import PlotWidget
from pymodbus.client.sync import ModbusSerialClient


class MyWin(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyWin, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.client = ModbusSerialClient(method="rtu", port="COM2", stopbits=1, bytesize=8, parity='N', baudrate=9600)
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Milandr Terminal")
        self.setFixedSize(self.size())
        self.ui.widget.setXRange(0, 20)
        self.ui.widget.setYRange(0, 10)
        self.ui.widget_2.setXRange(0, 20)  # Main graph
        self.ui.widget_2.setYRange(0, 10)  # Main graph
        return


global_data: deque = deque(np.zeros(21))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())
