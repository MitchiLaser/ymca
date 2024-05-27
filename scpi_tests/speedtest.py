#!/usr/bin/env python3

import pyvisa as visa
import sys
from tqdm import tqdm

try:
    # initialise connection to red-pitaya
    rm = visa.ResourceManager('@py')
    rp = rm.open_resource(f"TCPIP::{sys.argv[1]}::5000::SOCKET", read_termination='\r\n')

    # check if the network socket corresponds to a RedPitaya -> If the *IDN? String is not matching the expected one, this script might not work
    device_identification = rp.query("*IDN?").strip()
    # assert device_identification == 'REDPITAYA,INSTR2023,0,05-03'  # used to force this script only working on a specified RP OS version
except AssertionError:
    raise AssertionError(f"Device with ip-address {sys.argv[1]} is not a RedPitaya, returned device identification {device_identification}")

# set up Chanel 2 and the trigger

rp.write('ACQ:RST')
rp.write('ACQ:DATA:FORMAT BIN')
rp.write('ACQ:DATA:UNITS RAW')
rp.write('ACQ:DEC 4')

rp.write('ACQ:START')

# run this script multiple times
for i in tqdm(range(100)):
    rp.write('ACQ:TRIG NOW')

    while 1:  # wait for the trigger buffer to be full
        if rp.query('ACQ:TRIG:FILL?') == '1':
            break
    data = rp.query_binary_values('ACQ:SOUR2:DATA?', datatype='h', is_big_endian=True)

print(f"Length of last dataset: {len(data)}")
