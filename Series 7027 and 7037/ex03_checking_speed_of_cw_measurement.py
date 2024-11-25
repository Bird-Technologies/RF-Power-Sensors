"""
Example Description:
    This example places the 7027/7037 in CW, non-averaging mode and samples
    the forward power as fast as it can.

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

Copyright (c) Bird

"""
from series_7027_7037 import Series_7027
import time

mysensor = Series_7027()
mysensor.connect("USB0::0x1422::0x7029::242104838::INSTR", 20000)

mysensor.write("CALC:AVER:STAT 1")
mysensor.write("CALCulate:AVERage:COUNt 1")
mysensor.write("SENSe:REFLected:ENABle 1")
mysensor.write("SENSe:FREQuency:AUTO 0")
mysensor.write("SENSe:FREQuency 60E6")
mysensor.write("INITiate:CONTinuous 1")

t1 = time.time()
for j in range(100):
    fwdpow = float(mysensor.query("FETC:AVER?").rstrip())
    t2 = time.time()
    print("Time Elapsed: {0:.3f} s, measured {1:0.3f}".format(t2-t1, fwdpow))
    t1 = t2

mysensor.disconnect()
time.sleep(0.5)
