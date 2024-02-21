"""
Example Description:
    This example shows how to use the 7027/7037 driver to trigger
    measurements then read back the forward and reflected power.

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
mysensor.connect("USB0::0x1422::0x7037::202100121::INSTR", 20000)

# Trigger a measurement then fetch the power
mysensor.trigger.once()
fwd = mysensor.fetch.forward_power()
refl = mysensor.fetch.reflected_power()

# Configure for continuous trigger then loop to query new
# readings.
mysensor.trigger.continuous = 1
for j in range(10):
    time.sleep(0.5)
    print(f"FWD = {mysensor.fetch.forward_power()}")
    print(f"RFL = {mysensor.fetch.reflected_power()}")

# Disable continuous trigger
mysensor.trigger.continuous = 0

mysensor.disconnect()
time.sleep(0.5)
