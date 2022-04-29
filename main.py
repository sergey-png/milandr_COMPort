import sys
import time

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from base import Ui_MainWindow
import threading
from PyQt5.QtWidgets import QTextBrowser, QTextEdit
from functools import partial
import pyqtgraph as pg
from pyqtgraph import PlotWidget
import numpy as np


class MyWin(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyWin, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # Parameters list
        self.param_dict = {
            "com_port": "COM3",  # str(QSerialPortInfo.portName(QSerialPortInfo.availablePorts()[0]))
            "baud_rate": 115200,
            "stop_bits": 1,
            "data_bits": 8,
            "encoding": "ASCII"
        }
        self.param_dict_keys = list(self.param_dict)
        self.serial = QSerialPort()

        # Connect signals to slots
        self.ui.pushButton.clicked.connect(self.open_port)
        self.ui.pushButton_2.clicked.connect(self.close_port)
        self.ui.pushButton_3.clicked.connect(self.clear_all)
        self.ui.pushButton_4.clicked.connect(self.send_data)  # Запросить расстояние один раз
        self.ui.pushButton_5.clicked.connect(self.always_send_data)  # Запрашивать постоянно каждую ОПРЕДЕЛЕННУЮ секунду
        self.ui.pushButton_6.clicked.connect(self.auto_read_data)
        # listWidgets func on click
        self.list_of_widgets = [self.ui.listWidget, self.ui.listWidget_2, self.ui.listWidget_3, self.ui.listWidget_4,
                                self.ui.listWidget_5]
        for i, widget in enumerate(self.list_of_widgets):
            widget.itemClicked.connect(partial(self.list_widget_clicked, i))

        # Set background color of every item to white for all list widgets
        for widget in self.list_of_widgets:
            for i in range(widget.count()):
                widget.item(i).setBackground(QtGui.QColor(255, 255, 255))
        self.setup_ui()
        self.draw_graph_from_global_data()

    def setup_ui(self):
        self.setWindowTitle("Milandr Terminal")
        self.setFixedSize(self.size())
        self.ui.pushButton.setEnabled(True)
        self.ui.pushButton_2.setEnabled(False)
        self.ui.pushButton_3.setEnabled(True)
        self.ui.pushButton_4.setEnabled(False)
        self.ui.pushButton_5.setEnabled(False)
        self.ui.pushButton_6.setEnabled(False)
        self.ui.textEdit.setEnabled(False)
        self.ui.textEdit.setText("")
        self.ui.textBrowser.setText("")
        for widget in self.list_of_widgets:
            widget.setEnabled(True)
        line = f"You can open port with current parametrs:\n" \
               f"Port name = {self.param_dict['com_port']}; Baud = {self.param_dict['baud_rate']}; Stop bits = " \
               f"{self.param_dict['stop_bits']};Data bits = {self.param_dict['data_bits']}; " \
               f"Encoding = {self.param_dict['encoding']}"
        self.ui.textEdit.setText(line)
        return

    def draw_graph_from_global_data(self):
        return

    # noinspection PyArgumentList
    def list_widget_clicked(self, i):
        widget = self.list_of_widgets[i]  # Get the widget by index
        text = widget.currentItem().text()  # Get the text of the selected item
        # change color of selected item to green
        widget.item(widget.currentRow()).setBackground(QtGui.QColor(0, 255, 0))  # Set the background color of the
        # selected item to green
        # change color of other items to white
        for j in range(widget.count()):
            if j != widget.currentRow():
                widget.item(j).setBackground(QtGui.QColor(255, 255, 255))  # Set the background color of the
                # unselected item to white
        # Set the text of the text edit to the selected item
        # Set parameters of the serial port
        self.param_dict[self.param_dict_keys[i]] = text
        self.ui.textEdit.setText(self.param_dict[self.param_dict_keys[i]])
        print(self.param_dict)
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
                self.ui.pushButton_6.setEnabled(True)
                self.ui.textEdit.setEnabled(True)
                self.ui.textEdit.setText("")
                self.ui.textBrowser.append("Port opened successfully")
                for element in self.param_dict:
                    self.ui.textBrowser.append(str(self.param_dict[element]))
                for widget in self.list_of_widgets:
                    widget.setEnabled(False)
            else:
                self.ui.textBrowser.append("Port opening failed")
        except Exception as error:
            self.ui.textBrowser.setText("Error in port opening func: " + str(error))

    def clear_all(self):
        self.ui.textEdit.setText("")
        self.ui.textBrowser.setText("")
        return

    def close_port(self):
        global read_data_thread, always_send_data
        self.serial.close()
        self.setup_ui()
        self.ui.textBrowser.append("Port closed successfully")
        read_data_thread = False
        always_send_data = False
        for widget in self.list_of_widgets:
            widget.setEnabled(True)
        return

    # TODO отправка запроса на получение данных ОДИН раз
    def send_data(self):
        try:
            self.serial.write("".encode(self.param_dict["encoding"]))  # ЗАПРАШИВАЮ ДАННЫЕ (КОД ***)
        except Exception as error:
            self.ui.textEdit.setText("Error: " + str(error))
        return

    # TODO отправка запросов каждые несколько секунд, определяется пользователем
    def always_send_data(self):
        global always_send_data
        if always_send_data is False:
            always_send_data = True
            try:
                seconds = float(self.ui.lineEdit.text())
                thread = threading.Thread(target=send_data_thread,
                                          args=(self.serial, self.ui.textEdit, self.param_dict, seconds),
                                          daemon=True)
                thread.start()
            except Exception as error:
                self.ui.textEdit.setText(f"Ошибка, невозможно конвертировать введное значение в число\n{error}")
        else:
            always_send_data = False
        return

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


read_data_thread: bool = False
always_send_data: bool = False
global_data = []  # Есть вариант сделать это деком через модуль Collections


def send_data_thread(serial: QSerialPort, textEdit: QTextEdit, param_dict: dict, sleep_time: float):
    global global_data, always_send_data
    encoding = param_dict["encoding"]
    while always_send_data:
        print(f"global_data = {global_data}")
        try:
            # serial.write("".encode(encoding))  # ЗАПРАШИВАЮ ДАННЫЕ (КОД ***)
            start: bool = False
            counting: int = 0  # Если так и не получим \r 1000 раз, то выйдем из цикла
            summary_text: str = ""
            while always_send_data:
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
                        start = True
                        print('Все данные получены, записываю')
                        if "\r" not in summary_text:
                            try:
                                result_number = float(summary_text)
                                global_data.append(result_number)  # Global Data add
                            except ValueError:
                                break
                        break
                    if counting > 1000:
                        print('Не получен конец данных')
                        break
                else:
                    continue
        except SystemExit as error:
            textEdit.setText("Error: " + str(error))
        finally:
            time.sleep(sleep_time)
    return


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


if __name__ == "__main__":
    print(QSerialPortInfo.availablePorts() if QSerialPortInfo.availablePorts() else "No available ports")
    print(QSerialPortInfo.portName(QSerialPortInfo.availablePorts()[0]) if QSerialPortInfo.availablePorts() else "")
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())

"""
Создать кнопку, при нажатии отправляется кодовый сигнал и ждет получения информации(в целом можно оставить функцию,
которая постоянно мониторит получаемую информацию с микроконтроллера.

Создать кнопку, при нажатии отправляется КАЖДУЮ Определнную пользователем Секунду сигнал для получения информации.
(создать флаг переключения)

"""
# TODO ---ДОБАВИТЬ ПРИМЕР ПОСТРОЕНИЯ ГРАФИКА В РЕАЛЬНОМ ВРЕМЕНИ (можно использовать заглушку, которая будет добавлять
#  данные в дек) нужен также thread который будет постоянно рисовать график.
