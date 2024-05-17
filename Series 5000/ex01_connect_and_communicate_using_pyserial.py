"""
Example Description:
        This example shows how to configure the 5000 Series Wideband Power 
        Sensors and acquire measurement data, all through the RS-232
        communications interface.         

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

@file ex01_connect_and_communicate_using_pyserial.py
 
"""
import serial
from time import sleep
from enum import Enum

class MeasurementType(Enum):
    measNone = 0
    measAverage = 1
    measPeak = 2
    measBurst = 3
    measCrest = 4
    measCcdf = 5
    measAvgPeak = 6
    measAvgApm = 7

class Filter(Enum):
    low = 4.5e+3
    medium = 400e+3
    high = 10e+6

class PowerUnits(Enum):
    unit_none = "00"
    unit_db = "01"
    unit_rho = "02"
    unit_vswr = "03"
    unit_r = "04"
    unit_rl = "05"
    unit_dbm = "06"
    unit_micro_w = "07"
    unit_milli_w = "08"
    unit_w = "09"
    unit_kw = "0A"
    unit_auto_w = "0B"
    unit_mhz = "0C"
    unit_khz = "0D"

smodel = ""
sdate = ""
sversion = ""
scomms = ""

def get_instrument_identity(sp: serial):
    """Sends an 'I' command to the 5000 sensor. The sensor will respond with
    its interrogation string detailing its model number and software date and version
    numbers followed by serial number. 

    Args:
        sp (serial): An instance of a pyserial object. 

    Returns:
        smodel (string): The sensor model number.
        sdate (string): The firmware build date. 
        sversion (string): The firmward version number.
        scomms (string): The type of communications interface being used. 
        sserial (string): The sensor serial number. 
    """
    sp.flush()
    sp.write(b'I\r\n')
    temp = sp.read_until(b'rs232\r\n').decode("utf-8").split(',')
    while ("501" in temp[0]) is False:
        sp.write(b'I\n')
        tmp2 = sp.read_all()
        temp = sp.read_until(b'rs232\r\n').decode("utf-8").split(',')
    smodel = temp[0]
    sdate = temp[1]
    tmp3 = temp[2].split('\n')
    sversion = tmp3[0].rstrip()
    scomms = tmp3[1].rstrip()

    # Now get the serial number....
    sp.write(b'S\r\n')
    temp = sp.read_until(b'\r\n').decode("utf-8").split(',')
    sserial = temp[1].rstrip()

    return smodel, sdate, sversion, scomms, sserial

def get_calibration_status(sp: serial)->bool:
    """Peforms a check that the calibration flag is set indicating that
    the sensor is calibrated. Will return True if calibrated and False
    otherwise. 

    Args:
        sp (serial): An instance of a pyserial object.

    Returns:
        bool: Will return True if calibrated and False otherwise. 
    """
    status = True
    sp.write(b'F\r\n')
    temp = sp.read_until(b'\r\n').decode("utf-8").rstrip().split(',')
    #temp = sp.read_all().decode("utf-8").rstrip().split(',')
    if "NAK" in temp[1]:
        status = False
    return status

def set_measurement_configuration(sp: serial,
                                  measType:MeasurementType=MeasurementType.measAverage,
                                  dboffset:float=0.0,
                                  filtervalue:float=Filter.high,
                                  measunits:PowerUnits=PowerUnits.unit_auto_w,
                                  ccdflimit:float=150.0)->bool:
    """This function is used to configure the sensor. 

    Args:
        sp (serial): An instance of a pyserial object.
        measType (MeasurementType, optional): Applies the type of measurement to be performed: average, peak, burst, crest, ccdf, average peak, average APM, or none. Available options are accessible through the MeasurementType enumeration. Defaults to MeasurementType.measAverage.
        dboffset (float, optional): The power offset for the measurements. Defaults to 0.0.
        filtervalue (float, optional): Sets the filter speed for the measurements, accessible through the Filter enumeration with low as 4500 Hz, medium as 400 kHz, and high as 10 MHz. Defaults to Filter.high.
        measunits (PowerUnits, optional): Sets the power units for the measurements to be acquired from the sensor. See the PowerUnits enumeration for options. Defaults to PowerUnits.unit_auto_w.
        ccdflimit (float, optional): Sets the ccdf limit for the measurements. Defaults to 0.0e+3.

    Returns:
        bool: Will return True if no erroneous conditions were encountered and False otherwise. 
    """
    status = True
    # Build the configuration command string...
    cmd = f"G,0{measType.value},{dboffset:0.5e},{filtervalue.value:0.5e},{measunits.value},{ccdflimit:0.5e}\r\n"
    sp.write(cmd.encode())
    
    temp = sp.read_until(b'\r\n').decode("utf-8").rstrip().split(',')
    #temp = sp.read_all().decode("utf-8").rstrip()
    if "NAK" in temp[2]:
        status = False
    return status

def perform_zero_calibration(sp: serial)->str:
    """Performs a zero calibration on the sensor. The calibration process takes 
    about 60 seconds to complete and must be done with no RF power applied. 

    Args:
        sp (serial): An instance of a pyserial object.

    Returns:
        str: "Pass" for a successful calibration, "Fail" for unsuccessful, and "Over"
        for conditions where it appears RF power is actively being applied to the 
        sensor. 
    """
    status = "Pass"
    # change the timeout value to up to 60 seconds to align with the procedure expectations.
    sp.timeout = 120.0
    sp.write(b'Z\r\n')
    temp = sp.read_until(b'\r\n').decode("utf-8").rstrip().split(',')
    sp.timeout = 2.0
    if "01" in temp[1]:
        status = "Fail"
    elif "02" in temp[1]:
        status = "Over"
    return status

def get_sample_measurement_data(sp: serial):
    """This function will trigger a single measurement sample and return a single data set.

    Args:
        sp (serial): An instance of a pyserial object.

    Returns:
        status (bool): Will return True if no erroneous conditions were encountered and False otherwise. 
        burst_pwr (float): Returns the burst power.
        temperature (float): Returns the internal temperature of the sensor in degree Celcius.
        fwd_pwr (float): Returns the forward power.
        rfl_pwr (float): Returns the reflected power. 
        peak_pwr (float): Returns the peak power.
        filter_value (float): Returns the filter value used during the measurement.
        meas_type (int): Returns the measurement type used during the measurement. 
        units (str): Returns the units.
        ccdf_factor (float): Returns the CCDF factor.
        crest_factor (float): Returns the crest factor. 
        duty_cycle (float): Returns the duty_cycle. 
    """
    status = True
    sp.write(b'T\r\n')
    temp = sp.read_until(b'\r\n').decode("utf-8").rstrip().split(',')

    cmd = temp[0]
    burst_pwr = float(temp[1])
    temperature = float(temp[2])
    fwd_pwr = float(temp[3])
    rfl_pwr = float(temp[4])
    peak_pwr = float(temp[5])
    filter_value = float(temp[6])
    meas_type = int(temp[7])
    units = temp[8].strip()
    ccdf_factor = float(temp[9])
    crest_factor = float(temp[10])
    duty_cycle = float(temp[11])
    dud = temp[12]
    state = temp[13]
    if "NAK" in temp[13]:
        status = False
    
    return status, burst_pwr, temperature, fwd_pwr, rfl_pwr, peak_pwr, filter_value, meas_type, units, ccdf_factor, crest_factor, duty_cycle

def get_streamed_measurement_data(sp:serial, measurement_count:int=10):
    """This function will place the sensor in to measurement streaming mode, sampling at 300ms for
    the number of measurements defined by measurement_count, then halt streaming and return data
    in a tuple of lists.

    Args:
        sp (serial): An instance of a pyserial object.

    Returns:
        status (bool): Will return True if no erroneous conditions were encountered and False otherwise. 
        burst_pwr (float): Returns the burst power.
        temperature (float): Returns the internal temperature of the sensor in degree Celcius.
        fwd_pwr (float): Returns the forward power.
        rfl_pwr (float): Returns the reflected power. 
        peak_pwr (float): Returns the peak power.
        filter_value (float): Returns the filter value used during the measurement.
        meas_type (int): Returns the measurement type used during the measurement. 
        units (str): Returns the units.
        ccdf_factor (float): Returns the CCDF factor.
        crest_factor (float): Returns the crest factor. 
        duty_cycle (float): Returns the duty_cycle. 
    """
    status = True
    cmd = []
    burst_pwr = []
    temperature = []
    fwd_pwr = []
    rfl_pwr = []
    peak_pwr = []
    filter_value = []
    meas_type = []
    units = []
    ccdf_factor = []
    crest_factor = []
    duty_cycle = []
    dud = []
    state = []

    sp.write(b'D\r\n')  # starts the sensor measurement streaming

    for j in range(measurement_count):
        # Data will become available for readback every 300 ms....
        sleep(0.3)
        temp = sp.read_until(b'\r\n').decode("utf-8").rstrip().split(',')

        cmd.append(temp[0])
        burst_pwr.append(temp[1])
        temperature.append(temp[2])
        fwd_pwr.append(temp[3])
        rfl_pwr.append(temp[4])
        peak_pwr.append(temp[5])
        filter_value.append(temp[6])
        meas_type.append(temp[7])
        units.append(temp[8].strip())
        ccdf_factor.append(temp[9])
        crest_factor.append(temp[10])
        duty_cycle.append(temp[11])
        dud.append(temp[12])
        state.append(temp[13])
        if "NAK" in temp[13]:
            status = False

        #print(f"count = {j+1}, fwd = {fwd_pwr[j]}")

    sp.write(b'U\r\n')  # stops the sensor measurement streaming

    return status, burst_pwr, temperature, fwd_pwr, rfl_pwr, peak_pwr, filter_value, meas_type, units, ccdf_factor, crest_factor, duty_cycle


### MAIN PROGRAM STARTS HERE ###
my5000 = serial.Serial(port='COM8', baudrate=9600, parity="N", stopbits=1,bytesize=8)

smodel, sdate, sversion, scomms, ssn = get_instrument_identity(my5000)
print(f"Model: {smodel}\nFW Version: {sversion}\nFW Date: {sdate}\nComms Type: {scomms}\nSN: {ssn}")

print(get_calibration_status(my5000))

set_measurement_configuration(my5000,
                              MeasurementType.measAverage,
                              0.0,
                              filtervalue=Filter.medium,
                              measunits=PowerUnits.unit_auto_w,
                              ccdflimit=150.0)

#perform_zero_calibration(my5000)

status, burst_pwr, temperature, fwd_pwr, rfl_pwr, peak_pwr, filer_value, meas_type, units, ccdf_factor, crest_factor, duty_cycle = get_sample_measurement_data(my5000)

print(f"Sampled measurement:\n\tBurst Power: {burst_pwr}\n\tTemperature: {temperature}\n\tForward Power: {fwd_pwr}\n\tReflected Power: {rfl_pwr}")

status, brst, tmp_c, fwd, rfl, pk, fltr, mtype, unit, ccdf, crstfctr, dtycyc = get_streamed_measurement_data(my5000, measurement_count=10)

print("Streamed measurements:")
for j in range(len(brst)):
    print(f"\tBurst Power: {brst[j]}\tTemperature: {tmp_c[j]}\tForward Power: {fwd[j]}\tReflected Power: {rfl[j]}")

my5000.close()