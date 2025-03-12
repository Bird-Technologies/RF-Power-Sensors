"""
Example Description:
        This example shows how to configure the 5000 Series Wideband Power 
        Sensors and acquire measurement data, all through the USB HID
        communications interface.         

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

@file ex03_.py
 
"""
from series_5000 import Bird_5000_Series_Wideband_Power_Sensor


##### Main Program Start #####
my5000 = Bird_5000_Series_Wideband_Power_Sensor("5014")

# Print the sensor identification info to the console.
print(my5000.instrument_identification())

# Perform the calibration check.
cal_status = my5000.check_calibration()

# Set the configuration so the sensor performs average power measurements, no dB offset, using the 400 kHz filter, no CCDF limit.
#my5000.configuration(measurement_type=1, offset_db=0.0, filter=2, units=9, ccdf_limit=0.0)

# Set the dataset readback format to display forward power, reflected power, and temperature. 
my5000.set_data_format("FRT")

# Sample data...
for k in range(0, 10):
    print(my5000.get_one_dataset())

print("Done")
