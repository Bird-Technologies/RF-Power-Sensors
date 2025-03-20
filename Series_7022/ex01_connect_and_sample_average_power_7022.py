"""
Example Description:
        This example samples forward and reflected power, VSWR, and the
        meter's temperature, calculates return loss for a specified duration
        and logs to time-stamped *.csv file. 

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

@file ex01_connect_and_sample_average_power_7022.py
 
"""

import pyvisa as visa
import csv
import time
import math

def calculate_vswr(fwd_pow:float, rfl_power:float)->float:
    vswr = (1 + (rfl_power/fwd_pow)) / (1 - (rfl_power/fwd_pow))
    return vswr 

# Function to convert VSWR to return loss
def vswr_to_return_loss(VSWR:float) -> float:
    """Converts the VSWR value to return loss in dB.

    Args:
        VSWR (float): VSWR value. 

    Returns:
        float: Computed return loss in dB. If there is a problem with
        the math on the input value, the 9.99e+37 value will be returned
        to indicate the error condition.
    """
    try:
        VSWR = float(VSWR)
        if VSWR <= 1:
            return 9.999e+37
        Return_Loss = -20 * math.log10((VSWR - 1)/(VSWR + 1))
        return f"{Return_Loss:.2f}"
    except:
        return 9.999e+37

    
# Create a file to save data to
output_data_path = time.strftime("C:\\Temp\\rf_power_data_%Y-%m-%d_%H-%M-%S.csv")

# Instrument resource string
MY7022 = "USB0::0x1422::0x7022::141100792::INSTR"

# Open the resource manager and instrument
rm = visa.ResourceManager()
my7022 = rm.open_resource(MY7022)
my7022.write("*RST")
my7022.write("*CLS")
time.sleep(1.5)

print(my7022.query("*IDN?"))

t1 = time.time()
for j in range (100):
    response = my7022.query_binary_values(":TRAC:APOW?", datatype='f', is_big_endian=True)
    dud = response[0]
    fwd = response[2]
    rfl = response[4]
    temp = response[6]
    freq = response[8]
    vswr = calculate_vswr(fwd_pow=fwd, rfl_power=rfl)
    rl = vswr_to_return_loss(vswr)
    t2 = time.time()
    elapsed_time = f"{t2-t1:.3f}"
    print(f"MEAS {j} -> FREQ = {freq:3.3f} MHz, FWD_POW = {fwd:0.4f} W, RFL_POW = {rfl:0.4f}, VSWR = {vswr:0.2f}, RET_LOSS = {rl} dBm, TEMP = {temp:0.2f} C, Elapsed Time = {elapsed_time}")
    time.sleep(0.01)

my7022.close()
rm.close()
