"""
Example Description:
        This example shows how to use the 4421B540-2 sensor interface module
        to "arm" to sample a power applied for a short interval.

        The code uses the Bird4421B540Class class that is defined in a separate
        module file to better exhibit object oriented programming concepts. 

@verbatim

The MIT License (MIT)

Copyright (c) 2026 Bird

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

@file ex03_sample_briefly_applied_power.py
 
"""

from interface_module_4421B540_2_serial import Bird4421B540Class
from time import sleep, time
from statistics import mean

birdMod1 = Bird4421B540Class()

try:
    birdMod1.connect('COM4')
    ctr = 0
    while True:
        tmp_fwd_pwr = []
        pwr_thrsh = 90.0
        # sample forward power until it goes above a threshold...
        print("Waiting for trigger...")
        fwd_power = birdMod1.measure_forward_power()
        while fwd_power < pwr_thrsh:
            fwd_power = birdMod1.measure_forward_power()
        t1 = time()
        print("Triggered!")
        
        # then sample and average power until it drops below the threshold...
        tmp_fwd_pwr.append(fwd_power)
        while fwd_power > pwr_thrsh:
            fwd_power = birdMod1.measure_forward_power()
            tmp_fwd_pwr.append(fwd_power)

        t2 = time()
        print("End of pulse gate.")

        # calculate the average power over that sampled interval...
        if len(tmp_fwd_pwr) > 1:
            tmp_fwd_pwr.remove(min(tmp_fwd_pwr))
        average_fwd_power = mean(tmp_fwd_pwr)
        print(f"Average power = {average_fwd_power}")
        print("Pulse Gate Time: {0:.3f} s".format(t2-t1))
        print(tmp_fwd_pwr)
        tmp_fwd_pwr.clear()
        
        print("----------------------------------------------------------------------------")
        ctr += 1
        if ctr > 9:
            break
        sleep(0.05)
finally:
    birdMod1.close()

