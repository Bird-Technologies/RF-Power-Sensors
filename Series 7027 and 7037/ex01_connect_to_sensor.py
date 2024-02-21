"""
Example Description:
    This example shows how to use the 7027/7037 driver to connect to and
    query informantion from a Series 7027 or 7037 Statistical Power Sensor.

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

@file series_7027_7037.py

Copyright (c) Bird

"""

from series_7027_7037 import Series_7027
import time

mysensor = Series_7027()
mysensor.connect("USB0::0x1422::0x7037::202100121::INSTR", 20000)

# The query of the instrument ID happens within the connect()
# method. Below, "private" member variables are used to acquire
# the sensor info.
print(mysensor._mfg_id)
print(mysensor._model)
print(mysensor._fw)
print(mysensor._sn)

# But it is better to get this info using public member property
# calls. 
print(mysensor.manufacturer_id)
print(mysensor.model_number)
print(mysensor.firmware_version)
print(mysensor.serial_number)

mysensor.disconnect()
time.sleep(0.5)
