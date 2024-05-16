import serial
from time import sleep

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

my5000 = serial.Serial(port='COM8', baudrate=9600, parity="N", stopbits=1,bytesize=8)
#my5000.flush()

smodel, sdate, sversion, scomms = get_instrument_identity(my5000)
print(f"Model: {smodel}\nFW Version: {sversion}\nFW Date: {sdate}\nComms Type: {scomms}")

print(get_calibration_status(my5000))

get_measurement_data(my5000)

my5000.close()