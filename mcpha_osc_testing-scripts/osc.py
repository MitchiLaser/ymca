#!/usr/bin/env python3

import socket
import struct
import numpy as np
import matplotlib.pyplot as plt


class Osc:
    port = 1001

    def __init__(self, ip):
        # flags to control oscilloscope communication
        self.reset = False
        self.start = False
        # Status-Register buffer
        self.status = np.zeros(9, np.uint32)
        # flag to inform about new data
        self.update = False
        # oscilloscope buffer
        self.tot = 100000
        self.buffer = np.zeros(self.tot * 2, np.int16)
        # network socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, self.port))
        self.socket.settimeout(5)

    def stop(self):
        self.socket.close()

    def reset_osc(self):
        self.reset_osc = True

    def start_osc(self):
        self.start_osc = True

    def stop_osc(self):
        self.start_osc = False

    def set_osc_tot(self, value):  # DO not use!
        self._command(18, 0, value)

    def _command(self, code, number, value):
        self.socket.sendall(struct.pack("<Q", code << 56 | number << 52 | (int(value) & 0xFFFFFFFFFFFFF)))

    def _recv_all(self, size):
        """
        Reads data in chunks until the requested size is obtained or a timeout occurs.
        """
        data = bytearray()
        while len(data) < size:
            try:
                packet = self.socket.recv(size - len(data))
                if not packet:
                    return False
                data.extend(packet)
            except socket.timeout:
                return False
        return data

    '''
    Alternative Implementierung mittels Memory-view, noch nicht getestet:

    def _recv_all(self, size):
        data = bytearray(size)
        view = memoryview(data)
        bytes_received = 0
        while bytes_received < size:
            try:
                received = self.socket.recv_into(view[bytes_received:], size - bytes_received)
                if received == 0:
                    return False  # Connection closed
                bytes_received += received
            except socket.timeout:
                return False
        return data
    '''

    def _read_data(self, buffer):
        view = buffer.view(np.uint8)  # convert input buffer to numpy array of type uint8
        size = view.size  # Get the size of the buffer
        try:
            data = self._recv_all(size)  # use _recv_all method to read exactly size bytes from the socket.
            if data is False:
                return False
            view[:] = np.frombuffer(data, np.uint8)
            return True
        except socket.timeout:
            return False

    def _read(self):
        self.update = False
        # send reset commands
        if self.reset_osc:
            self._command(2, 0, 0)
        if self.start_osc:
            self._command(19, 0, 0)
        self.reset_osc = False
        self.start_osc = False
        # read status to check if the oscilloscope is ready
        self._command(11, 0, 0)
        if not self._read_data(self.status):
            return
        if not self.status[8] & 1:  # only perform action when oscilloscope is ready
            self._command(20, 0, 0)
            if self._read_data(self.buffer):
                self.update = True  # set the flag that the data was updated
                self.reset_osc = True
                self.start_osc = True
            else:
                return

    def get_data(self):
        self.update = False
        while not self.update:
            self._read()
        return self.buffer



