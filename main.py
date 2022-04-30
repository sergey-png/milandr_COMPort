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


class MyWin(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyWin, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # Parameters list
        if QSerialPortInfo.availablePorts():
            com_port = str(QSerialPortInfo.portName(QSerialPortInfo.availablePorts()[0]))
        else:
            com_port = ""
        self.param_dict = {
            "com_port": f"{com_port}",
            "baud_rate": 115200,
            "stop_bits": 1,
            "data_bits": 8,
            "encoding": "ASCII"
        }
        self.param_dict_keys = list(self.param_dict)
        self.serial = QSerialPort()
        self.ui.textBrowser.setText(str(self.param_dict))

        # Connect signals to slots
        self.ui.pushButton.clicked.connect(self.open_port)
        self.ui.pushButton_2.clicked.connect(self.close_port)
        self.ui.pushButton_3.clicked.connect(self.clear_all)
        self.ui.pushButton_4.clicked.connect(self.send_data)  # Запросить расстояние один раз (ручная обработка
        self.ui.pushButton_5.clicked.connect(self.always_recv_data)  # ЧАСТОТА ИЗМЕРЕНИЙ (кнопку переделать)

        self.setup_ui()
        # THREAD для постоянной отрисовки графика с помощью PYQT-GRAPH
        thread_for_drawing = threading.Thread(target=drawing_thread, daemon=True, args=(self.ui.widget,))
        thread_for_drawing.start()

    def setup_ui(self):
        self.setWindowTitle("Milandr Terminal")
        self.setFixedSize(self.size())
        self.ui.pushButton.setEnabled(True)
        self.ui.pushButton_2.setEnabled(False)
        self.ui.pushButton_3.setEnabled(True)
        self.ui.pushButton_4.setEnabled(False)
        self.ui.pushButton_5.setEnabled(False)
        return

    def open_port(self):
        try:
            self.serial.setPortName(self.param_dict["com_port"])
            eval(f"self.serial.setBaudRate(QSerialPort.Baud{self.param_dict['baud_rate']})")
            self.serial.setDataBits(QSerialPort.DataBits(int(self.param_dict['data_bits'])))
            self.serial.setStopBits(QSerialPort.StopBits(int(self.param_dict['stop_bits'])))
            self.serial.setFlowControl(QSerialPort.NoFlowControl)
            opening_port = self.serial.open(QSerialPort.ReadWrite)
            print(f"Opening port = {opening_port}")
            if opening_port:
                self.ui.pushButton.setEnabled(False)
                self.ui.pushButton_2.setEnabled(True)
                self.ui.pushButton_4.setEnabled(True)
                self.ui.pushButton_5.setEnabled(True)
                # self.ui.pushButton_6.setEnabled(True)
                self.ui.textBrowser.append("Port opened successfully")
                for element in self.param_dict:
                    self.ui.textBrowser.append(str(self.param_dict[element]))
            else:
                self.ui.textBrowser.append("Port opening failed")
        except Exception as error:
            self.ui.textBrowser.setText("Error in port opening func: " + str(error))

    def clear_all(self):
        self.ui.textBrowser.setText("")
        return

    def close_port(self):
        global always_receive_data
        self.serial.close()
        self.setup_ui()
        self.ui.textBrowser.append("Port closed successfully")
        always_receive_data = False
        return

    # TODO отправка запроса на получение данных ОДИН раз
    def send_data(self):
        self.serial.write("".encode(self.param_dict["encoding"]))  # ЗАПРАШИВАЮ ДАННЫЕ (КОД ***)
        return

    # TODO отправка запросов каждые несколько секунд, определяется пользователем
    def always_recv_data(self):
        global always_receive_data
        if always_receive_data is False:
            always_receive_data = True
            try:
                # seconds = float(self.ui.lineEdit.text())
                seconds = 1
                # TODO Используются не секунды, нужно провести вычисления расчетного потребления и вывести на экран
                # TODO
                thread = threading.Thread(target=receive_data_thread,
                                          args=(self.serial, self.ui.textBrowser, self.param_dict, seconds),
                                          daemon=True)
                thread.start()
            except Exception as error:
                self.ui.textBrowser.setText(f"Ошибка, невозможно конвертировать введное значение в число\n{error}")
        else:
            always_receive_data = False
        return


# Устаревший код для отображения всей полученной информации с микроконтроллера
"""
    def auto_read_data(self):
        global read_data_thread
        # Read data from serial port and display it in text browser
        # Start a thread to read data from serial port
        self.ui.textBrowser.setText("")
        if read_data_thread is False:
            read_data_thread = True
            thread = threading.Thread(target=read_data_from_serial_port,
                                      args=(self.serial, self.ui.textBrowser,
                                            self.param_dict['encoding']),
                                      daemon=True)
            thread.start()
        else:
            self.ui.textBrowser.insertPlainText("\nStop reading data from serial port")
            read_data_thread = False
        return
"""

# read_data_thread: bool = False  УСТАРЕЛО
always_receive_data: bool = False
global_data: deque = deque(np.zeros(21))


def receive_data_thread(serial: QSerialPort, textBrowser: QTextBrowser, param_dict: dict, sleep_time: float):
    global global_data, always_receive_data
    encoding = param_dict["encoding"]
    while always_receive_data:
        print(f"global_data = {global_data}")
        try:
            # serial.write("".encode(encoding))  # ЗАПРАШИВАЮ ДАННЫЕ (КОД ***)
            start: bool = False
            counting: int = 0  # Если так и не получим \r 1000 раз, то выйдем из цикла
            summary_text: str = ""
            while always_receive_data:
                kek = serial.waitForReadyRead(1)
                if kek:
                    data = serial.readAll()
                    text = data.data().decode(encoding)
                    print(f"Data read: {[text]}")
                    if text.count("\r") == 1 and start is False:  # Если есть \r
                        start = True
                    elif text.count("\r") == 0 and start is True:  # добавляем текст (должен добавлять посимвольно)
                        summary_text += text
                        counting += 1
                    elif text.count("\r") == 1 and start is True:  # Заканчиваем построение
                        print('Все данные получены, отправляю обработчику')
                        if "\r" not in summary_text:
                            try:
                                incoming_data_handler(summary_text)  # Посылаем данные обработчику, для выяснения
                                # какая команда пришла с микроконтроллера
                            except ValueError:
                                break
                        break
                    if counting > 1000:
                        print('Не получен конец данных')
                        break
                else:
                    continue
        except SystemExit as error:
            textBrowser.setText("Error: " + str(error))
        finally:
            time.sleep(sleep_time)
    return


def incoming_data_handler(data) -> str:
    global global_data
    # TODO Здесь будут обрабатываться полученные символы
    #  написать условия для определенных действий
    # Одно из действий написано, если получим числовое значение, значит пришло новое значение расстояния от датчика
    print("Запуск обработчика полученных компанд")
    if data == "c1":
        # если пришла команда 1
        pass
    elif data == "c2":
        # если пришла команда 2
        pass
    else:
        # если команд не было, то значит пришло число
        try:
            data = float(data)
            global_data.append(data)  # Global Data add
            global_data.popleft()
        except ValueError:
            print("Невозможно преобразовать в числовое значение")
            return


#  Код устарел, более не требуется
"""
def read_data_from_serial_port(serial: QSerialPort, textBrowser: QTextBrowser, encoding: str):
    global read_data_thread
    try:
        while read_data_thread:
            kek = serial.waitForReadyRead(1)
            if kek:
                data = serial.readAll()
                text = data.data().decode(encoding)
                print(f"Data read: {text}")
                if text == "\r" or text == "\n":
                    textBrowser.insertPlainText("\n")
                else:
                    textBrowser.insertPlainText(text)
                textBrowser.verticalScrollBar().setValue(textBrowser.verticalScrollBar().maximum())
    except SystemExit:
        textBrowser.setText("Error: :(")
"""


def drawing_thread(widget: PlotWidget, ):
    global global_data
    widget.setXRange(0, 20)
    widget.setYRange(0, 10)

    while True:
        time.sleep(0.1)
        print("drawing")
        widget.clear()
        widget.plot(list(np.arange(0, 21)), global_data, symbolPen='y')


def demo_data():  # DEMO DATA THREAD
    global global_data
    while True:
        print("sending data")
        print(global_data)
        time.sleep(0.5)
        global_data.append(randint(0, 10))
        global_data.popleft()


if __name__ == "__main__":
    print(global_data)

    print(QSerialPortInfo.availablePorts() if QSerialPortInfo.availablePorts() else "No available ports")
    print(QSerialPortInfo.portName(QSerialPortInfo.availablePorts()[0]) if QSerialPortInfo.availablePorts() else "")
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    # thread1 = threading.Thread(target=demo_data, daemon=True)  # DEMO DATA THREAD
    # thread1.start()
    sys.exit(app.exec_())

"""
Создать кнопку, при нажатии отправляется кодовый сигнал и ждет получения информации(в целом можно оставить функцию,
которая постоянно мониторит получаемую информацию с микроконтроллера.

Создать кнопку, при нажатии отправляется КАЖДУЮ Определнную пользователем Секунду сигнал для получения информации.
(создать флаг переключения)

"""
