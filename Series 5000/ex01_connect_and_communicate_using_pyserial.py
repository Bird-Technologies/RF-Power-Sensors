import serial
from time import sleep

def get_instrument_identity(sp: serial):
    sp.flush()
    sleep(0.1)
    sp.write(b'I\n')
    sleep(0.5)
    temp = sp.read_all()
    templist = temp.decode("utf-8").split(',')
    return temp

def get_measurement_data(sp: serial):
    sp.flush()
    sleep(0.1)
    sp.write(b'T\n')
    sleep(0.5)
    temp = sp.read_all()
    templist = temp.decode("utf-8").rstrip().split(',')
    for item in templist:
        print(f'{item}')
    print(temp)

my5000 = serial.Serial(port='COM8', baudrate=9600, parity="N", stopbits=1,bytesize=8)
my5000.flush()

print(get_instrument_identity(my5000))

get_measurement_data(my5000)

my5000.close()