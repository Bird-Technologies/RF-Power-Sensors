"""
Example Description:
        This example shows how the zero calibration function might be used. 

@verbatim

The MIT License (MIT)

Copyright (c) 2025 Bird

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

@endverbatim

@file ex01_perform_zero_calibration.py
 
"""

import pyvisa as visa
import csv
import time
import math

# Instrument resource string
MY7022 = "USB0::0x1422::0x7022::141100792::INSTR"

# Open the resource manager and instrument
rm = visa.ResourceManager()
my7022 = rm.open_resource(MY7022)
my7022.write("*RST")
my7022.write("*CLS")
time.sleep(1.5)

print(my7022.query("*IDN?"))

# Set up for average measure mode
my7022.write("SENS:TIME:ENAB 0")
my7022.write("SENS:STAT:ENAB 0")
my7022.write("STAT:MEAS:ENAB 15")

# Modify the reading timeout value to up to 31s
print(my7022.timeout)
my7022.timeout = 31000
print(my7022.timeout)

# Issue the zero calibration command
my7022.write("CAL:ZERO")

# Query the *OPC? status
t1 = time.time()
value = my7022.query("*OPC?")
t2 = time.time()

print(f"Elapsed time: {t2-t1:0.3f} s")

my7022.close()
rm.close()
