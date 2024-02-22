"""
    Copyright 2024 Bird Technologies

    This example shows how to use PyVisa to connect to and query informantion
    from a Series 7027 or 7037 Statistical Power Sensor.

"""
import pyvisa as visa
import time


MYSENSOR = "USB0::0x1422::0x7037::202100121::INSTR"

rm = visa.ResourceManager()  # Open the resource manager.

series70x7 = rm.open_resource(MYSENSOR) # Open an instance of the sensor object.
series70x7.timeout = 5000

for j in range(1000):
    print(series70x7.query("*IDN?\n").rstrip())
    
series70x7.close()

rm.close()
