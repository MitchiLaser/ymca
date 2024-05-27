#!/usr/bin/env python3

import pyvisa as visa
import sys
import matplotlib.pyplot as plt

rm = visa.ResourceManager('@py')
rp = rm.open_resource(f"TCPIP::{sys.argv[1]}::5000::SOCKET", read_termination='\r\n')

rp.write('ACQ:RST')
rp.write('ACQ:DATA:FORMAT BIN')
rp.write('ACQ:DATA:UNITS RAW')
rp.write('ACQ:DEC 4')

rp.write('ACQ:START')

rp.write('ACQ:TRIG NOW')

while 1:  # wait for the trigger buffer to be full
    if rp.query('ACQ:TRIG:FILL?') == '1':
        break
data = rp.query_binary_values('ACQ:SOUR2:DATA?', datatype='h', is_big_endian=True)

# plot measured data
plt.plot(list(range(len(data))), data)
plt.show()
