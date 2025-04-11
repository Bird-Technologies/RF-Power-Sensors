"""
Example Description:
        This example shows how to use the 4421B540-2 sensor interface module
        to sample measurements and log them to file. 

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

@file ex02_log_power_measurments_to_file.py
 
"""

from interface_module_4421B540_2_serial import Bird4421B540Class
import time
import math
import csv

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


def compute_vswr_from_power(fwd_pwr:float, rfl_pwr:float)->float:
    vswr_calc = (1 + math.sqrt(rfl_pwr/fwd_pwr)) / (1 - math.sqrt(rfl_pwr/fwd_pwr))
    return vswr_calc


# Create a file to save data to
output_data_path = time.strftime("C:\\Temp\\4421B_rf_power_data_%Y-%m-%d_%H-%M-%S.csv")

birdMod1 = Bird4421B540Class()

try:
    birdMod1.connect('COM4')

    with open(output_data_path, mode='a', newline='') as file:
        writer = csv.writer(file)

        # Define the header for the CSV
        header = ['Time (s)', 'Fwd_Power (W)', 'Refl_Power (W)', "Temperature (deg C)"]

        writer.writerow(header)  # Write the header

        log_duration = 10.0
        elapsed_time = 0.0
        print_interval_flag = 60.0
        debug_print = 1

        t1 = time.time() # Start the timer...
        start_time = t1
        print("Testing started....")

        while elapsed_time < log_duration:
            # Loop to for the expected duration and log data points to file
            # Fetch readings from the instrument
            forward_power = birdMod1.measure_forward_power()
            reflected_power = birdMod1.measure_reflected_power()
            #vswr = compute_vswr_from_power(forward_power, reflected_power)
            #rl = vswr_to_return_loss(vswr)
            temp = birdMod1.measure_temperature()
            
            if debug_print == 1:
                print(f"fwd = {forward_power:0.2f} W, rfl = {reflected_power:0.2f} W, temp = {temp:0.2f} C")

            t2 = time.time()
            delta_interval = t2-t1
            if delta_interval < 1.0:
                time.sleep(1.0 - delta_interval)
                t2 = time.time()
                elapsed_time = t2-start_time
            etime = f"{elapsed_time:0.3f}"
            t1 = t2

            data = [etime, forward_power, reflected_power, temp]

            writer.writerow(data)   # Write the data

            if elapsed_time > print_interval_flag:
                print(f"Elapsed time: {t2-t1:0.3f} s")
                print_interval_flag += 60.0

        print("Testing ended!!!")

finally:
    birdMod1.close()

