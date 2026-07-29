"""
Example Description:
        This class code presents a Python driver concept which can be
        used with the 4421B540-2 sensor interface module.  

        This particular version of the driver uses the 32-bit pyserial
        module to establish serial communications. 

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

@file interface_module_4421B540_2_serial.py
 
"""

import serial

class Bird4421B540Class:

    def __init__(self):
        self.__sensor = serial.Serial()
        self.__baud = 9600
        self.__stop_bits = serial.STOPBITS_ONE
        self.__commands = {
            "ID": bytearray(b'I'),
            "FWD": bytearray(b'F'),
            "REF": bytearray(b'R'),
            "TEMP": bytearray(b'T'),
            "V": bytearray(b'V')
        }
        self.log_file = None
        self.__sensor_model = ""
        self.__sensor_cal_date = ""

    def connect(self, comm='COM4'):
        self.__sensor.port = comm
        self.__sensor.baudrate = self.__baud
        self.__sensor.bytesize = serial.EIGHTBITS       
        self.__sensor.parity = serial.PARITY_NONE       
        self.__sensor.stopbits = self.__stop_bits        
        self.__sensor.timeout = 1                
        self.__sensor.xonxoff = False          
        self.__sensor.rtscts = False                   
        self.__sensor.dsrdtr = False                   
        self.__sensor.writeTimeout = 2  
        self.__sensor.open()
        self.__sensor.flushInput()
        self.__sensor.flushOutput()
        

    def __send_command(self, command:str):
        try:
            fc = self.__commands[str(command)]
            self.__sensor.write(fc)
            fwd_pwr_read = self.__sensor.read(4)
            ret_val = [fwd_pwr_read[i:i + 1] for i in range(0, len(fwd_pwr_read))]  # byte to byte array split
            return ret_val
        except KeyError:
            return
        
    def get_sensor_identification(self):
        fc = self.__commands[str("ID")]
        self.__sensor.write(fc)
        id_read = self.__sensor.read(32).decode('utf-8').split(' ')
        self.__sensor_model = id_read[0]
        self.__sensor_cal_date = id_read[1]
        huh_str = id_read[2]
        id_read = self.__sensor.read(32)
        this_str = list(id_read)
        # that_str = id_read[12].encode('utf-8')
        return self.__sensor_model, self.__sensor_cal_date, huh_str
    
    def get_the_v(self):
        fc = self.__commands[str("V")]
        #fc = 'V'
        self.__sensor.write(fc)
        raw_val = self.__sensor.read(4)
        val1 = raw_val[0]
        val2 = raw_val[1]
        val3 = raw_val[2]
        val4 = raw_val[3]
        #fwd_power = self.__bird_float_2_IEEE_float(raw_val)
        #self.__sensor_model = id_read[0]
        #self.__sensor_cal_date = id_read[1]
        ret_val = [raw_val[i:i + 1] for i in range(0, len(raw_val))]  # byte to byte array split
        return ret_val

    def measure_forward_power(self)->float:
        """This method returns the forward power as measured by the sensor. 

        Returns:
            float: The forward power of the sensor.
        """
        fwd_power_raw = self.__send_command('FWD')
        fwd_power = self.__bird_float_2_IEEE_float(fwd_power_raw)
        fwd_power = fwd_power * fwd_power                           # result needs to be squared to get power reading
        return fwd_power
    
    def measure_reflected_power(self)->float:
        """This method returns the reflected power as measured by the sensor.

        Returns:
            float: The reflected power of the sensor. 
        """
        rfl_power_raw = self.__send_command('REF')
        rfl_power = self.__bird_float_2_IEEE_float(rfl_power_raw)
        rfl_power = rfl_power * rfl_power                           # result needs to be squared to get power reading
        return rfl_power 
    
    def measure_temperature(self)->float:
        """This method returns the internal temperature of the sensor. 

        Returns:
            float: The internal temperature of the sensor. 
        """
        temperature_raw = self.__send_command('TEMP')
        temperature = self.__bird_float_2_IEEE_float(temperature_raw)
        return temperature

    def __bird_float_2_IEEE_float(self, hex)->float:
        """This method is necssary to convert the measurement data from 
        Bird's FP format to the standard IEEE FP format.

        Args:
            hex (_type_): This is the Bird format which is a list of 
            four hex values. 

        Returns:
            float: The floating point value of the converted hex data. 
        """
        temp = [0, 0, 0, 0]
        i = 0
        for h in hex:
            temp[i] = ord(h)
            i += 1
        mantissa = (temp[1]<<16) + (temp[2]<<8) + (temp[3])

        if temp[1] & 0x80:
            mantissa = mantissa + 0xff
            sign = -1
        else:
            sign = 1

        fexp = temp[0]

        if (fexp >= 0x80):
            fexp -= 1 << 8

        f = sign*((float(mantissa))/(0x800000))

        if (fexp < 0):
            while fexp != 0:
                f = f/2
                fexp += 1
        else:
            while fexp != 0:
                f = f*2
                fexp -= 1

        return f
    
    def close(self):
        self.__sensor.close()