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
                                  ccdflimit:float=0.0e+3):
    status = True
    # Build the configuration command string...
    cmd = f"G,0{measType.value},{dboffset:0.5e},{filtervalue.value:0.5e},{measunits.value},{ccdflimit:0.5e}\r\n"
    sp.write(cmd.encode())
    
    temp = sp.read_until(b'\r\n').decode("utf-8").rstrip().split(',')
    #temp = sp.read_all().decode("utf-8").rstrip()
    if "NAK" in temp[2]:
        status = False
    return status

def get_sample_measurement_data(sp: serial):
    status = True
    sp.write(b'T\r\n')
    temp = sp.read_until(b'\r\n').decode("utf-8").rstrip().split(',')

    cmd = temp[0]
    burst_pwr = float(temp[1])
    temperature = float(temp[2])
    fwd_pwr = float(temp[3])
    rfl_pwr = float(temp[4])
    peak_pwr = float(temp[5])
    filer_value = float(temp[6])
    meas_type = int(temp[7])
    units = temp[8].strip()
    ccdf_factor = float(temp[9])
    crest_factor = float(temp[10])
    duty_cycle = float(temp[11])
    dud = temp[12]
    state = temp[13]
    if "NAK" in temp[13]:
        status = False
    
    return status, burst_pwr, temperature, fwd_pwr, rfl_pwr, peak_pwr, filer_value, meas_type, units, ccdf_factor, crest_factor, duty_cycle

def get_streamed_measurement_data(sp:serial):
    return True

my5000 = serial.Serial(port='COM8', baudrate=9600, parity="N", stopbits=1,bytesize=8)

smodel, sdate, sversion, scomms = get_instrument_identity(my5000)
print(f"Model: {smodel}\nFW Version: {sversion}\nFW Date: {sdate}\nComms Type: {scomms}")

print(get_calibration_status(my5000))

set_measurement_configuration(my5000,
                              MeasurementType.measAverage,
                              0.0,
                              filtervalue=Filter.medium,
                              measunits=PowerUnits.unit_auto_w,
                              ccdflimit=150.0)

status, burst_pwr, temperature, fwd_pwr, rfl_pwr, peak_pwr, filer_value, meas_type, units, ccdf_factor, crest_factor, duty_cycle = get_sample_measurement_data(my5000)

print(f"Sampled measurement:\n\tBurst Power: {burst_pwr}\n\tTemperature: {temperature}\n\tForward Power: {fwd_pwr}\n\tReflected Power: {rfl_pwr}")
my5000.close()