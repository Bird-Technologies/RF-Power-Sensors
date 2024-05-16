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
    sp.flush()
    sp.write(b'I\n')
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
    return smodel, sdate, sversion, scomms

def get_calibration_status(sp: serial):
    status = True
    sp.write(b'F\r\n')
    temp = sp.read_all().decode("utf-8").rstrip().split(',')
    if "NAK" in temp[1]:
        status = False
    return status

def set_measurement_configuration(sp: serial,
                                  measType:MeasurementType=MeasurementType.measAverage,
                                  dboffset:float=0.0,
                                  filtervalue:float=Filter.medium,
                                  measunits:PowerUnits=PowerUnits.unit_w,
                                  ccdflimit:float=0.0e+3):
    # Build the configuration command string...
    cmd = f"G,0{measType.value},{dboffset:0.5e},{filtervalue.value:0.5e},{measunits.value},{ccdflimit:0.5e},\r\n"
    sp.write(cmd.encode())
    
    temp = sp.read_all().decode("utf-8").rstrip()
    if "NAK" in temp:
        status = False
    return status

def get_measurement_data(sp: serial):
    sp.flush()
    sleep(0.1)
    sp.write(b'T\n')
    temp = sp.read_all()
    
    sleep(0.5)
    templist = temp.decode("utf-8").rstrip().split(',')
    for item in templist:
        print(f'{item}')
    print(temp)

my5000 = serial.Serial(port='COM3', baudrate=9600, parity="N", stopbits=1,bytesize=8)
#my5000.flush()

set_measurement_configuration(my5000, MeasurementType.measAverage, 1.23458789e0, filtervalue=Filter.medium, measunits=PowerUnits.unit_auto_w, ccdflimit=0.0e+3)

smodel, sdate, sversion, scomms = get_instrument_identity(my5000)
print(f"Model: {smodel}\nFW Version: {sversion}\nFW Date: {sdate}\nComms Type: {scomms}")

print(get_calibration_status(my5000))

get_measurement_data(my5000)

my5000.close()