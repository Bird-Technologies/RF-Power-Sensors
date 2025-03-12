# Copyright 2020 Bird

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
# to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import serial
import datetime

# The following functino is necssary to convert the measurement data from Bird's FP format to the standard IEEE FP format.
def bird_float_2_IEEE_float(hex):
    temp = [0, 0, 0, 0]
    i = 0
    for h in hex:
        temp[i] = ord(h)
        i += 1
    mantissa = (temp[1]<<16) + (temp[2]<<8) + (temp[3])

    if temp[1] & 0x80:
        mantissa = mantissa + 0xff
        sign = -1

    else:
        sign = 1

    fexp = temp[0]

    if (fexp >= 0x80):
        fexp -= 1 << 8

    f = sign*((float(mantissa))/(0x800000))

    if (fexp < 0):
        while fexp != 0:
            f = f/2
            fexp += 1

    else:
        while fexp != 0:
            f = f*2
            fexp -= 1

    return f


class Bird4421B540Class:

    def __init__(self):
        self.baud = 9600
        self.stop_bits = serial.STOPBITS_ONE
        self.sensor = serial.Serial()
        self.commands = {
            "ID": bytearray(b'I'),
            "FWD": bytearray(b'F'),
            "REF": bytearray(b'R'),
            "TEMP": bytearray(b'T'),
        }
        self.log_file = None

    def connect(self, comm='COM7'):
        self.sensor.port = comm
        self.sensor.baudrate = self.baud
        self.sensor.bytesize = serial.EIGHTBITS       
        self.sensor.parity = serial.PARITY_NONE       
        self.sensor.stopbits = self.stop_bits        
        self.sensor.timeout = 1                
        self.sensor.xonxoff = False          
        self.sensor.rtscts = False                   
        self.sensor.dsrdtr = False                   
        self.sensor.writeTimeout = 2  
        self.sensor.open()
        self.sensor.flushInput()
        self.sensor.flushOutput()

    def send_command(self, command):
        try:
            fc = self.commands[str(command)]
            self.sensor.write(fc)
            fwd_pwr_read = self.sensor.read(4)
            ret_val = [fwd_pwr_read[i:i + 1] for i in range(0, len(fwd_pwr_read))]  # byte to byte array split
            return ret_val
        except KeyError:
            return

    def close(self):
        self.sensor.close()


birdMod1 = Bird4421B540Class()
try:
    birdMod1.connect('COM4')

    while True:
        fwd_power_raw = birdMod1.send_command('FWD')
        fwd_power = bird_float_2_IEEE_float(fwd_power_raw)
        fwd_power = fwd_power * fwd_power                           # result needs to be squared to get power reading
        rfl_power_raw = birdMod1.send_command('REF')
        rfl_power = bird_float_2_IEEE_float(rfl_power_raw)
        rfl_power = rfl_power * rfl_power                           # result needs to be squared to get power reading
        temperature_raw = birdMod1.send_command('TEMP')
        temperature = bird_float_2_IEEE_float(temperature_raw)
        print("Measured FWD Power (W): {}".format(fwd_power))
        print("Measured RFL Power (W): {}".format(rfl_power))
        print("Temperature (C): {}".format(temperature))
        print("----------------------------------------------------------------------------")
finally:
    birdMod1.close()
 
