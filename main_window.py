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
        self.port = 6
        self.frequency = 1000  # kHz Частота измерений
        self.points = [0, 0, 0, 0, 0]  # ЗНАЧЕНИЯ НАПРЯЖЕНИЯ НА КОНТРОЛЬНЫХ ТОЧКАХ
        self.calibrating_coefficients = []  # Калибровочные коэффициенты

        self.client = ModbusSerialClient(method="rtu", port="COM4", stopbits=1, bytesize=8, parity='N', baudrate=19200)
        self.setup_ui()
        self.ui.pushButton_13.clicked.connect(self.push_button_13)
        self.ui.pushButton_14.clicked.connect(self.push_button_14)
        self.ui.pushButton_15.clicked.connect(self.push_button_15)
        self.ui.pushButton_23.clicked.connect(self.push_button_23)
        self.ui.pushButton_24.clicked.connect(self.push_button_24)

        self.ui.pushButton_17.clicked.connect(self.push_button_17)
        self.ui.pushButton_18.clicked.connect(self.push_button_18)
        self.ui.pushButton_19.clicked.connect(self.push_button_19)
        self.ui.pushButton_20.clicked.connect(self.push_button_20)
        self.ui.pushButton_21.clicked.connect(self.push_button_21)
        self.ui.pushButton_22.clicked.connect(self.push_button_22)
        self.ui.pushButton_25.clicked.connect(self.push_button_25)
        self.ui.pushButton_26.clicked.connect(self.push_button_26)

    def setup_ui(self):
        self.setWindowTitle("Milandr Terminal")
        self.setFixedSize(self.size())
        self.ui.textBrowser.setText("Служебная информация")
        self.ui.spinBox.setValue(self.port)  # set COM{defined_number}
        self.ui.pushButton.setEnabled(False)
        self.ui.pushButton_2.setEnabled(False)
        self.ui.pushButton_3.setEnabled(False)
        self.ui.pushButton_7.setEnabled(False)
        self.ui.listWidget_6.setEnabled(False)
        self.ui.pushButton_14.setEnabled(False)
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

        for i in range(17, 27):
            if i == 23 or i == 24:
                continue
            eval(f"self.ui.pushButton_{i}.setEnabled(False)")

        return

    # Connect to COM port
    def push_button_13(self):
        port = "COM" + str(self.ui.spinBox.value())
        self.client = ModbusSerialClient(method="rtu", port=port, stopbits=1, bytesize=8, parity='N', baudrate=19200)
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
        selected_type = self.ui.listWidget_7.currentIndex().row() + 1
        print(f"Selected: {selected_type}")

        # Отправить регистр о режиме работы микроконтроллера
        self.client.write_register(address=0, value=selected_type, unit=1)

        if selected_type == 3:
            self.ui.pushButton_17.setEnabled(True)
        d = {1: "ручной", 2: "автоматический", 3: "калибровочный"}
        self.ui.textBrowser_2.setText(f"Установлен {d[selected_type]} режим работы")
        self.ui.tabWidget_3.setCurrentIndex(selected_type)

    # Запросить расстояние
    def push_button_15(self):
        # принять holding_registers
        global global_data
        try:
            result = self.client.read_holding_registers(address=17, count=4, unit=1)
            print(result.registers)
            distance = float(f"{result.registers[0]}.{result.registers[1]}")  # дистанция
            error = float(f"{result.registers[2]}.{result.registers[3]}")  # погрешность
            self.ui.lcdNumber.display(distance)  # вывод дистации
            global_data.popleft()
            global_data.append(distance)
            # TODO вомзожен вывод погрешности
            self.ui.lcdNumber_2.display(error)  # вывод погрешности
            self.ui.widget_2.clear()
            self.ui.widget_2.plot(list(np.arange(0, 21)), global_data, symbolPen='y')

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

    def push_button_17(self):  # точка 0 = 5 мм
        # TODO считать значение текущего напряжения с микроконтроллера и записать в
        #  self.points[0] = U
        res = self.client.read_holding_registers(address=1, count=2, unit=1)
        mess = res.registers
        result = float(f"{mess[0]}.{mess[1]}")
        print(result)
        self.points[0] = result
        print("Записана первая точка")
        self.ui.pushButton_17.setEnabled(False)
        self.ui.pushButton_18.setEnabled(True)

    def push_button_18(self):  # точка 1 = 7.4 мм
        # TODO считать значение текущего напряжения с микроконтроллера и записать в
        #  self.points[1] = U
        res = self.client.read_holding_registers(address=1, count=2, unit=1)
        mess = res.registers
        result = float(f"{mess[0]}.{mess[1]}")
        print(result)
        self.points[1] = result
        print("Записана вторая точка")
        self.ui.pushButton_18.setEnabled(False)
        self.ui.pushButton_19.setEnabled(True)

    def push_button_19(self):  # точка 2 = 8.6 мм
        # TODO считать значение текущего напряжения с микроконтроллера и записать в
        #  self.points[2] = U
        res = self.client.read_holding_registers(address=1, count=2, unit=1)
        mess = res.registers
        result = float(f"{mess[0]}.{mess[1]}")
        print(result)
        self.points[2] = result
        print("Записана третья точка")
        self.ui.pushButton_19.setEnabled(False)
        self.ui.pushButton_25.setEnabled(True)

    def push_button_25(self):  # точка 3 = 10.4 мм
        # TODO считать значение текущего напряжения с микроконтроллера и записать в
        #  self.points[3] = U
        res = self.client.read_holding_registers(address=1, count=2, unit=1)
        mess = res.registers
        result = float(f"{mess[0]}.{mess[1]}")
        print(result)
        self.points[3] = result
        print("Записана четвертая точка")
        self.ui.pushButton_25.setEnabled(False)
        self.ui.pushButton_26.setEnabled(True)

    def push_button_26(self):  # точка 4 = 12.8 мм
        # TODO считать значение текущего напряжения с микроконтроллера и записать в
        #  self.points[4] = U
        res = self.client.read_holding_registers(address=1, count=2, unit=1)
        mess = res.registers
        result = float(f"{mess[0]}.{mess[1]}")
        print(result)
        self.points[4] = result
        print("Записана пятая точка")
        self.ui.pushButton_26.setEnabled(False)
        self.ui.pushButton_20.setEnabled(True)

    def push_button_20(self):
        # TODO Вычислить калибровочные коэффициенты по полученным значениям напряжения в контр точках
        self.calibrating_coefficients = [3.34, -4.755, 12.038, 0.317]
        self.ui.pushButton_20.setEnabled(False)
        self.ui.pushButton_22.setEnabled(True)

    def push_button_22(self):
        # TODO загрузить калибровочную информацию
        registers = []
        for number in self.calibrating_coefficients:
            if number < 0:
                registers.append(0)
                number *= -1
            else:
                registers.append(1)
            num = str(number)
            num = list(map(int, num.split('.')))
            registers += num
        print(registers)
        self.client.write_registers(address=3, values=registers, unit=1)
        res = self.client.read_holding_registers(address=0, count=23, unit=1)
        print(res.registers)
        self.ui.pushButton_22.setEnabled(False)
        self.ui.pushButton_21.setEnabled(True)
        pass

    # Set frequency
    def push_button_21(self):
        frequency = self.ui.lineEdit_4.text()
        try:
            frequency = float(frequency)
            print(f"Selected frequency is {frequency}")
        except ValueError:
            print("Error with selected frequency")
        finally:
            freq = list(map(int, str(frequency).split('.')))
            print(freq)
            # TODO Отправить регистр с частотой измерений
            self.client.write_registers(address=15, values=freq, unit=1)

            self.ui.pushButton_24.setEnabled(True)

    def push_button_24(self):
        global get_data_thread
        if get_data_thread is False:
            self.ui.pushButton_24.setStyleSheet("background-color: rgb(0, 222, 0); color: rgb(0,0,0); font-size:16px;")
            get_data_thread = True
            thread1 = threading.Thread(target=get_data_thread_func,
                                       daemon=True, args=(self.client, self.ui.lcdNumber,
                                                          self.ui.lcdNumber_2, self.ui.widget_2))
            thread1.start()
        else:
            self.ui.pushButton_24.setStyleSheet("background-color: rgb(222, 0, 0); color: rgb(0,0,0); font-size:16px;")
            get_data_thread = False


get_data_thread = False
global_data: deque = deque(np.zeros(21))


def get_data_thread_func(client: ModbusSerialClient, LCD1: QtWidgets.QLCDNumber, LCD2: QtWidgets.QLCDNumber,
                         plot: PlotWidget):
    global get_data_thread, global_data
    while get_data_thread is True:
        time.sleep(0.05)
        result = client.read_holding_registers(address=17, count=4, unit=1)
        data = list()
        try:
            data = result.registers
            # print(data)
        except AttributeError:
            print("No registers found")
        result1 = float(f"{data[0]}.{data[1]}")
        result2 = float(f"{data[2]}.{data[3]}")
        print(result1, result2)
        # print(data)
        # if global_data[len(global_data) - 1] != result1:
        global_data.popleft()
        global_data.append(result1)
        plot.clear()
        plot.plot(list(np.arange(0, 21)), global_data, symbolPen='y')
        LCD1.display(result1)
        LCD2.display(random.randint(1, 5))  # result 2 должен быть в случае получения погрешности


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())
