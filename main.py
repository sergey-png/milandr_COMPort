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

        self.com_port = "COM1"
        self.baud_rate = 9600
        self.data_bits = 8
        self.parity = "None"
        self.stop_bits = 1
        self.encoding = "ASCII"
        # Parameters list
        self.param_list = [self.com_port, self.baud_rate, self.stop_bits, self.data_bits, self.encoding]
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
        self.param_list[i] = text
        self.ui.textEdit.setText(self.param_list[i])
        return

    def open_port(self):
        try:
            self.serial.setPortName(self.com_port)
            eval(f"self.serial.setBaudRate(QSerialPort.Baud{int(self.baud_rate)})")
            self.serial.setDataBits(QSerialPort.DataBits(int(self.data_bits)))
            self.serial.setStopBits(QSerialPort.StopBits(int(self.stop_bits)))
            self.serial.setFlowControl(QSerialPort.NoFlowControl)
            if self.serial.open(QSerialPort.ReadWrite):
                self.ui.pushButton.setEnabled(False)
                self.ui.pushButton_2.setEnabled(True)
                self.ui.pushButton_4.setEnabled(True)
                self.ui.pushButton_5.setEnabled(True)
                self.ui.pushButton_6.setEnabled(True)
                self.ui.textEdit.setEnabled(True)
                self.ui.textBrowser.append("Port opened successfully")
                for element in self.param_list:
                    self.ui.textBrowser.append(element)
                for widget in self.list_of_widgets:
                    widget.setEnabled(False)
            else:
                self.ui.textBrowser.append("Port opening failed")
        except Exception as error:
            self.ui.textBrowser.setText("Error: " + str(error))

    def clear_all(self):
        self.ui.textEdit.setText("")
        self.ui.textBrowser.setText("")
        return

    def close_port(self):
        self.serial.close()
        self.setup_ui()
        self.ui.textBrowser.append("Port closed successfully")
        for widget in self.list_of_widgets:
            widget.setEnabled(True)
        return

    def send_data(self):
        try:
            self.serial.write(self.ui.textEdit.toPlainText().encode(self.encoding))
            self.ui.textEdit.setText("")
            self.ui.textBrowser.append("Data sent successfully")
        except Exception as error:
            self.ui.textBrowser.setText("Error: " + str(error))
        return

    def read_data(self):
        try:
            data = self.serial.readAll()
            self.ui.textBrowser.append(data.data().decode(self.encoding))
        except Exception as error:
            self.ui.textBrowser.setText("Error: " + str(error))
        return

    def auto_read_data(self):
        global read_data_thread
        # Read data from serial port and display it in text browser
        # Start a thread to read data from serial port
        if read_data_thread is False:
            read_data_thread = True
            thread = threading.Thread(target=read_data_from_serial_port, args=(self.serial, self.ui.textBrowser,
                                                                               self.encoding), daemon=True)
            thread.start()
        else:
            self.ui.textBrowser.append("Stop reading data from serial port")
            read_data_thread = False
        return


def read_data_from_serial_port(serial: QSerialPort, textBrowser: QTextBrowser, encoding: str):
    global read_data_thread
    try:
        while True:
            time.sleep(0.1)
            if read_data_thread:
                data = serial.readAll()
                textBrowser.append(data.data().decode(encoding))
            else:
                break
    except Exception as error:
        textBrowser.setText("Error: " + str(error))


read_data_thread = False

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())
