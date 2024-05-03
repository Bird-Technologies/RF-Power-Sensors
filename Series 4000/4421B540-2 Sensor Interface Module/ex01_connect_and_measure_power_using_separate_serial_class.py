"""
Example Description:
        This example shows how to use the 4421B540-2 sensor interface module
        to query forward and reflected power and temperature of a connected 
        402x sensor.

        The code uses the Bird4421B540Class class that is defined in a separate
        module file to better exhibit object oriented programming concepts. 

@verbatim

The MIT License (MIT)

Copyright (c) 2024 Bird

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

@file ex01_connect_and_measure_power_using_separate_serial_class.py
 
"""

from interface_module_4421B540_2_serial import Bird4421B540Class
from time import sleep

birdMod1 = Bird4421B540Class()

try:
    birdMod1.connect('COM4')

    while True:
        fwd_power = birdMod1.measure_forward_power()
    
        rfl_power = birdMod1.measure_reflected_power()

        temperature = birdMod1.measure_temperature()
        
        print(f"Measured FWD Power (W): {fwd_power:0.4}")
        print(f"Measured RFL Power (W): {rfl_power:0.4}")
        print(f"Temperature (C): {temperature:0.4}")
        print("----------------------------------------------------------------------------")
        sleep(1.0)
finally:
    birdMod1.close()

