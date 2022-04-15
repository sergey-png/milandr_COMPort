import sys

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo

from PyQt5.QtWidgets import QApplication, QLabel, QScrollArea, QVBoxLayout, QWidget


def main():
    app = QApplication([])
    layout = QVBoxLayout()
    scroll = QScrollArea()
    info = QSerialPortInfo.availablePorts()
    for i in info:
        s = "Name: " + i.portName() + "\n"
        s += "Location: " + i.systemLocation() + "\n"
        s += "Description: " + i.description() + "\n"
        s += "Manufacturer: " + i.manufacturer() + "\n"
        s += "Serial Number: " + i.serialNumber() + "\n"
        s += "System Location: " + i.systemLocation() + "\n"
        s += "Vendor Identifier: " + str(i.vendorIdentifier()) + "\n"
        s += "Product Identifier: " + str(i.productIdentifier()) + "\n"
        s += "Busy: " + str(i.isBusy()) + "\n"
        s += "------------------------------\n"
        layout.addWidget(QLabel(s))
    if not info:
        layout.addWidget(QLabel("No serial ports found"))
    workPage = QWidget()
    workPage.setLayout(layout)
    scroll.setWindowTitle("Serial Port Info")
    scroll.setWidget(workPage)
    scroll.show()
    return app.exec_()


if __name__ == "__main__":
    main()
    sys.exit(0)
