import sys
import time

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from base import Ui_MainWindow
import threading
from PyQt5.QtWidgets import QTextBrowser
from functools import partial


class MyWin(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyWin, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # Parameters list
        self.param_dict = {
            "com_port": "COM5",
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
        self.ui.pushButton_4.clicked.connect(self.send_data)
        self.ui.pushButton_3.clicked.connect(self.clear_all)
        self.ui.pushButton_5.clicked.connect(self.read_data)
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

    def setup_ui(self):
        self.setWindowTitle("Milandr Terminal")
        self.setFixedSize(self.size())
        self.ui.pushButton.setEnabled(True)
        self.ui.pushButton_2.setEnabled(False)
        self.ui.pushButton_4.setEnabled(False)
        self.ui.pushButton_3.setEnabled(True)
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
        global text_in_browser
        self.ui.textEdit.setText("")
        self.ui.textBrowser.setText("")
        text_in_browser = ""
        return

    def close_port(self):
        global read_data_thread
        self.serial.close()
        self.setup_ui()
        self.ui.textBrowser.append("Port closed successfully")
        read_data_thread = False
        for widget in self.list_of_widgets:
            widget.setEnabled(True)
        return

    def send_data(self):
        try:
            self.serial.write(self.ui.textEdit.toPlainText().encode(self.param_dict['encoding']))
            self.ui.textBrowser.append("Data sent successfully")
        except Exception as error:
            self.ui.textBrowser.setText("Error: " + str(error))
        return

    def read_data(self):
        try:
            data = self.serial.readAll()
            print(f"Data read: {data}")
            self.ui.textBrowser.append(f"Data: '{data.data().decode(self.param_dict['encoding'])}'")
            self.ui.textBrowser.verticalScrollBar().setValue(self.ui.textBrowser.verticalScrollBar().maximum())
        except Exception as error:
            self.ui.textBrowser.setText("Error: " + str(error))
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


def read_data_from_serial_port(serial: QSerialPort, textBrowser: QTextBrowser, encoding: str):
    global read_data_thread
    try:
        while True:
            if read_data_thread:
                kek = serial.waitForReadyRead(1)
                if kek:
                    data = serial.readAll()
                    text = data.data().decode(encoding)
                    # print(f"Data read: {text}")

                    textBrowser.insertPlainText(text)
                    textBrowser.verticalScrollBar().setValue(textBrowser.verticalScrollBar().maximum())
            else:
                break
    except SystemExit:
        textBrowser.setText("Error: :(")


if __name__ == "__main__":
    print(QSerialPortInfo.availablePorts() if QSerialPortInfo.availablePorts() else "No available ports")
    print(QSerialPortInfo.portName(QSerialPortInfo.availablePorts()[0]) if QSerialPortInfo.availablePorts() else "")
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())
