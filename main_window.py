import sys
import time
import random
from PyQt5 import QtWidgets, QtCore, QtGui
from base import Ui_MainWindow
import threading
from collections import deque
import numpy as np
from pyqtgraph import PlotWidget
from pymodbus.client.sync import ModbusSerialClient


class MyWin(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyWin, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Параметры
        self.frequency = 1000  # kHz Частота измерений
        self.points = [0, 0, 0]  # Калибровочные точки и их значения расстояния
        self.calibrating_coefficients = []  # Калибровочные коэффициенты

        self.client = ModbusSerialClient(method="rtu", port="COM2", stopbits=1, bytesize=8, parity='N', baudrate=9600)
        self.setup_ui()
        self.ui.pushButton_13.clicked.connect(self.push_button_13)
        self.ui.pushButton_14.clicked.connect(self.push_button_14)
        self.ui.pushButton_15.clicked.connect(self.push_button_15)
        self.ui.pushButton_21.clicked.connect(self.push_button_21)
        self.ui.pushButton_23.clicked.connect(self.push_button_23)
        self.ui.pushButton_24.clicked.connect(self.push_button_23)  # Not an error

        self.ui.pushButton_17.clicked.connect(self.push_button_17)
        self.ui.pushButton_18.clicked.connect(self.push_button_18)
        self.ui.pushButton_19.clicked.connect(self.push_button_19)
        self.ui.pushButton_20.clicked.connect(self.push_button_20)
        self.ui.pushButton_21.clicked.connect(self.push_button_21)
        self.ui.pushButton_22.clicked.connect(self.push_button_22)

    def setup_ui(self):
        self.setWindowTitle("Milandr Terminal")
        self.setFixedSize(self.size())
        self.ui.textBrowser.setText("Служебная информация")
        self.ui.pushButton.setEnabled(False)
        self.ui.pushButton_2.setEnabled(False)
        self.ui.pushButton_3.setEnabled(False)
        self.ui.pushButton_7.setEnabled(False)
        self.ui.listWidget_6.setEnabled(False)
        self.ui.pushButton_14.setEnabled(False)
        self.ui.pushButton_24.setEnabled(False)
        self.ui.pushButton_6.setEnabled(False)
        self.ui.pushButton_8.setEnabled(False)
        self.ui.pushButton_9.setEnabled(False)
        self.ui.pushButton_10.setEnabled(False)
        self.ui.pushButton_11.setEnabled(False)
        self.ui.pushButton_12.setEnabled(False)

        self.ui.textBrowser_2.setText("Информационное окно")
        self.ui.lineEdit_4.setText(str(self.frequency))
        self.ui.widget.setXRange(0, 20)
        self.ui.widget.setYRange(0, 10)
        self.ui.widget_2.setXRange(0, 20)  # Main graph
        self.ui.widget_2.setYRange(0, 10)  # Main graph

        for i in range(17, 23):
            eval(f"self.ui.pushButton_{i}.setEnabled(False)")

        return

    # Connect to COM port
    def push_button_13(self):
        port = "COM" + str(self.ui.spinBox.value())
        self.client = ModbusSerialClient(method="rtu", port=port, stopbits=1, bytesize=8, parity='N', baudrate=9600)
        check = self.client.connect()
        if check is True:
            print(f"Successfully connected to {port}")
            self.ui.pushButton_13.setStyleSheet("background-color: rgb(0, 170, 0); color: rgb(0,0,0); font-size:16px;")
            self.ui.pushButton_13.setEnabled(False)
            self.ui.pushButton_14.setEnabled(True)
        else:
            print(f"Error during connecting")
        # self.client.close()

    # Выбрать режим работы микроконтроллера
    def push_button_14(self):
        selected_type = self.ui.listWidget_7.currentIndex()
        print(f"Selected: {selected_type.row()}")

        # TODO Отправить регистр о режиме работы микроконтроллера

        if selected_type.row() == 2:
            self.ui.pushButton_17.setEnabled(True)
        d = {0: "ручной", 1: "автоматический", 2: "калибровочный"}
        self.ui.textBrowser_2.setText(f"Установлен {d[selected_type.row()]} режим работы")
        self.ui.tabWidget_3.setCurrentIndex(selected_type.row() + 1)

    # Запросить расстояние
    def push_button_15(self):
        # TODO Отправить регистр на считывание расстояния и принять holding_registers
        try:
            result = self.client.write_register(40001, 15, unit=1)  # address=40001, data=15, slave_unit=1
            print(result)
            # time.sleep(0.1)
            result = self.client.read_holding_registers(address=40001, count=10, unit=1)
            print(result.registers)
        except AttributeError:
            print("No connection")

    # Start auto fetching data
    def push_button_23(self):
        global get_data_thread
        if get_data_thread is False:
            self.ui.pushButton_23.setStyleSheet("background-color: rgb(0, 222, 0); color: rgb(0,0,0); font-size:16px;")
            get_data_thread = True
            thread1 = threading.Thread(target=get_data_thread_func,
                                       daemon=True, args=(self.client, self.ui.lcdNumber,
                                                          self.ui.lcdNumber_2, self.ui.widget_2))
            thread1.start()
        else:
            self.ui.pushButton_23.setStyleSheet("background-color: rgb(222, 0, 0); color: rgb(0,0,0); font-size:16px;")
            get_data_thread = False

    def push_button_17(self):
        text = self.ui.lineEdit_2.text()
        try:
            text = int(text)
            self.points[0] = text
            print("Записана первая точка")
            self.ui.pushButton_17.setEnabled(False)
            self.ui.pushButton_18.setEnabled(True)
        except ValueError:
            print("Error with 1st point")

    def push_button_18(self):
        text = self.ui.lineEdit_2.text()
        try:
            text = int(text)
            self.points[0] = text
            print("Записана вторая точка")
            self.ui.pushButton_18.setEnabled(False)
            self.ui.pushButton_19.setEnabled(True)
        except ValueError:
            print("Error with 1st point")

    def push_button_19(self):
        text = self.ui.lineEdit_2.text()
        try:
            text = int(text)
            self.points[0] = text
            print("Записана третья точка")
            self.ui.pushButton_19.setEnabled(False)
            self.ui.pushButton_20.setEnabled(True)
        except ValueError:
            print("Error with 1st point")

    def push_button_20(self):
        # TODO Вычислить калибровочные коэффициенты
        self.ui.pushButton_20.setEnabled(False)
        self.ui.pushButton_22.setEnabled(True)

    # Set frequency
    def push_button_21(self):
        frequency = self.ui.lineEdit_4.text()
        try:
            frequency = int(frequency)
            print(f"Selected frequency is {frequency}")
        except ValueError:
            print("Error with selected frequency")
        finally:
            # TODO Отправить регистр с частотой измерений
            result = self.client.write_register(40001, frequency, unit=1)  # address=40001, data=frequency, slave_unit=1
            print(result)
            self.ui.pushButton_24.setEnabled(True)

    def push_button_22(self):
        # TODO загрузить калибровочную информацию
        self.ui.pushButton_22.setEnabled(False)
        self.ui.pushButton_21.setEnabled(True)
        pass


get_data_thread = False
global_data: deque = deque(np.zeros(21))


def get_data_thread_func(client: ModbusSerialClient, LCD1: QtWidgets.QLCDNumber, LCD2: QtWidgets.QLCDNumber,
                         plot: PlotWidget):
    # Demo data
    thread2 = threading.Thread(target=demo_data, daemon=True, args=(client,))
    thread2.start()
    global get_data_thread, global_data
    while get_data_thread is True:
        time.sleep(0.1)
        result = client.read_holding_registers(40001, 10, unit=1)
        data = list()
        try:
            data = result.registers
            # print(data)
        except AttributeError:
            print("No registers found")
        data = data[0]
        # print(data)
        if global_data[len(global_data) - 1] != data:
            global_data.popleft()
            global_data.append(data)
            plot.clear()
            plot.plot(list(np.arange(0, 21)), global_data, symbolPen='y')
            LCD1.display(data)
            LCD2.display(random.randint(1, 5))


def demo_data(client):
    while True:
        for i in range(0, 11):
            time.sleep(0.1)
            write_result = client.write_register(40001, i, unit=1)
            print(write_result)
        for i in range(9, -1, -1):
            time.sleep(0.1)
            write_result = client.write_register(40001, i, unit=1)
            print(write_result)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())
