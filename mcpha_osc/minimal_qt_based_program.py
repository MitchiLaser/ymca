#!/usr/bin/env python3

import sys
import struct

import numpy as np
import matplotlib.pyplot as plt

from PyQt5.QtCore import Qt, QTimer, QEventLoop, QCoreApplication, QObject
from PyQt5.QtNetwork import QAbstractSocket, QTcpSocket
from PyQt5.QtWidgets import QApplication


class MCPHA(QObject):

    def __init__(self):
        super(MCPHA, self).__init__(parent=None)  # required for QT
        # initialize variables
        self.reset_osc = False
        self.start_osc = False
        self.status = np.zeros(9, np.uint32)
        # create tabs
        self.osc = OscDisplay(self)
        # create TCP socket
        self.socket = QTcpSocket(self)
        self.socket.connected.connect(self.connected)
        # create event loop
        self.loop = QEventLoop()
        self.socket.readyRead.connect(self.loop.quit)
        self.socket.error.connect(self.loop.quit)
        # create timers
        self.readTimer = QTimer(self)
        self.readTimer.timeout.connect(self.read_timeout)

        print("Init done")

        # Start the application
        self.start()

    def start(self):
        print("Starting")
        self.socket.connectToHost("10.42.0.107", 1001)

    def stop(self):
        self.osc.stop()
        self.readTimer.stop()
        self.loop.quit()
        self.socket.abort()
        print("IO stopped")

    def closeEvent(self, event):
        self.stop()

    def connected(self):
        self.readTimer.start(500)
        print("IO started")
        self.reset_osc = False
        self.start_osc = False
        # Start the oscilloscope
        self.osc.start()

    def command(self, code, number, value):
        self.socket.write(struct.pack("<Q", code << 56 | number << 52 | (int(value) & 0xFFFFFFFFFFFFF)))

    def read_data(self, data):
        view = data.view(np.uint8)  # Ensure buffer is of type unsigned 8-bit integer
        size = view.size  # Get the size of the buffer
        while self.socket.state() == QAbstractSocket.ConnectedState and self.socket.bytesAvailable() < size:
            self.loop.exec_()
        if self.socket.bytesAvailable() < size:
            return False
        else:
            # Read the data from the socket and store it in the corresponding buffer
            view[:] = np.frombuffer(self.socket.read(size), np.uint8)
            print(view.size)
            print(view)
            print("===")
            return True

    def read_timeout(self):
        # send reset commands
        if self.reset_osc:
            self.command(2, 0, 0)
        if self.start_osc:
            self.command(19, 0, 0)
        self.reset_osc = False
        self.start_osc = False
        # read
        self.command(11, 0, 0)
        if not self.read_data(self.status):
            return
        if not self.status[8] & 1:
            self.command(20, 0, 0)
            if self.read_data(self.osc.buffer):
                #self.osc.update()
                self.readTimer.stop()
                x = np.arange(self.osc.tot)
                plt.plot(x, self.osc.buffer[0::2], label="L1")
                plt.plot(x, self.osc.buffer[1::2], label="L2")
                plt.legend()
                plt.show()

                self.reset_osc = True
                self.start_osc = True
            else:
                return

    def reset_osc(self):
        self.reset_osc = True

    def start_osc(self):
        self.start_osc = True

    def stop_osc(self):
        self.start_osc = False


class OscDisplay():
    def __init__(self, mcpha):
        super(OscDisplay, self).__init__()
        # initialize variables
        self.mcpha = mcpha
        self.pre = 10000
        self.tot = 100000
        self.buffer = np.zeros(self.tot * 2, np.int16)

    def start(self):
        self.mcpha.reset_osc = True
        self.mcpha.start_osc = True
        print("oscilloscope started")

    def stop(self):
        self.mcpha.stop_osc()
        print("oscilloscope stopped")


app = QApplication(sys.argv)
window = MCPHA()
sys.exit(app.exec_())
