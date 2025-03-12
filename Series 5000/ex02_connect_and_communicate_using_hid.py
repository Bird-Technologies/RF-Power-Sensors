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

@file ex02_connect_and_communicate_using_hid.py
 
"""
import hid
import struct
import time

class Bird_5000_Series_Wideband_Power_Sensor():
    def __init__(self, model_number:str="5012D"):
        self.VENDOR_ID=0x1422
        self.PRODUCT_ID=0x5012
        self._return_fwd_pwr = 1 # - 3 forward power F
        self._return_rfl_pwr = 1 # - 4 reflected power R
        self._return_burst_pwr = 1  # - 1 busrt power B
        self._return_peak_pwr = 1 # - 5 peak power K
        self._return_temp = 1 # - 2 temperature T
        self._return_filter_val = 1 # - 6 filter value I
        self._return_meas_type = 1 # - 7 measure type M
        self._return_units = 1 # - 8 units U
        self._return_ccdf_factor = 1 # - 9 ccdf factor C
        self._return_crest_factor = 1 # - 10 crest factor R
        self._return_duty_cycle = 1 # - 11 duty cycle D
        self._return_ack = 1 # - 13 ACK/NAK A
        self._cmd_delay = 0.3 # 0.3
        self._device = None

        if "5012" in model_number:
            self.PRODUCT_ID = 0x5012
        elif "5014" in model_number:
            self.PRODUCT_ID = 0x5014
        elif "5016" in model_number:
            self.PRODUCT_ID = 0x5016
        elif "5017" in model_number:
            self.PRODUCT_ID = 0x5017
        elif "5018" in model_number:
            self.PRODUCT_ID = 0x5018
        elif "5019" in model_number:
            self.PRODUCT_ID = 0x5019
        elif "5010" in model_number:
            self.PRODUCT_ID = 0x5010

        try:
            self._device = hid.Device(self.VENDOR_ID, self.PRODUCT_ID)
        except hid.HIDException:
            print(0)
        finally:
            print(1)


    def instrument_identification(self)->str:
        """Extracts the instrument identification information for the connected sensor and returns it as a string. 

        Returns:
            str: This comma delimited string will include the sensor manufacturer ID, the model number, serial number, and firmware version.
        """
        model_number, software_date, runtime_version = self._do_initialization()

        return f"{self._device.manufacturer},{model_number},{self._device.serial},{runtime_version}"

    def _do_initialization(self):
        """Issues a command to the sensor telling it to report its identifying information.

        Returns:
            str[]: A list of strings containing the model number, firmware/software date and version.
        """
        # Issue preamble notice
        hex_message = '0350ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
        self._device.write(bytes.fromhex(hex_message))
        
        # I command
        hex_message = '02490d0affffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
        self._device.write(bytes.fromhex(hex_message))
        hex_message = '0353ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
        self._device.write(bytes.fromhex(hex_message))

        response = self._device.read(48, 2000)
        cleaned_response = response[1:]
        decoded_response = cleaned_response.decode('utf-8', errors='ignore')
        model_number, software_date, runtime_version = decoded_response.split("\r\n")[0].split(',')

        return model_number, software_date, runtime_version
    
    def _get_measure_type(self, mtype):
        mstr = "1"
        if mtype < 9:
            mstr = str(mtype.to_bytes(1, "big"))[4:6]
        else:
            if mtype == 9:
                mstr = "09"
            if mtype == 10:
                mstr = "0a"
            if mtype == 11:
                mstr = "0b"
            if mtype == 12:
                mstr = "0c"
            if mtype == 13:
                mstr = "0d"
            if mtype == 14:
                mstr = "0e"
            if mtype == 15:
                mstr = "0f"
        return mstr
    
    def _get_units_type(self, utype):
        ustr = "1"
        if utype < 9:
            ustr = str(utype.to_bytes(1, "big"))[4:6]
        else:
            if utype == 9:
                ustr = "09"
            if utype == 10:
                ustr = "0a"
            if utype == 11:
                ustr = "0b"
            if utype == 12:
                ustr = "0c"
            if utype == 13:
                ustr = "0d"
            if utype == 14:
                ustr = "0e"
            if utype == 15:
                ustr = "0f"
        return ustr
    
    def configuration(self,
                      measurement_type:int=1, 
                      offset_db:float=0.0,
                      filter:int=2,
                      units:int=11,
                      ccdf_limit:float=150.0):
        """This function is used to configure the sensor

        Args:
            measurement_type (int, optional): 0 = None, 1 = Average, 2 = Peak, 3 = Burst, 4 = Crest, 5 = CCDF, 6 = Average Peak. Defaults to 1.
            offset_db (float, optional): The power offset for the measurements. Defaults to 0.0.
            filter (int, optional): Sets the filter speed for the measurements, use 0 for 4500 Hz, 1 for 400 kHz, and 2 for 10 MHz. Defaults to 2.
            units (int, optional): Sets the power units for the measurements to be acquired from the sensor. 0=None, 1=dB, 2=Rho, 3=VSWR, 4=R, 5=RL, 6=dBm, 7=uW, 8=mW, 9=W, 10=kW, 11=Auto W, 12=MHz, 13=kHz, 14=Raw. Defaults to 11.
            ccdf_limit (float, optional): Sets the ccdf limit for the measurements.. Defaults to 150.0.

        Returns:
            _type_: code, ack_nak
        """
        # Perform the cal check before attempting to change the configuration - required
        s1, s2 = my5000.check_calibration()
        
        t1 = time.time()
        # Issue preamble notice
        buffer = '0350ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
        
        self._device.write(bytes.fromhex(buffer))
        time.sleep(self._cmd_delay)

        buffer = "02"
        # G
        buffer += "47"

        # Add a comma...
        buffer += "2c"

        # Set the measurement type
        hotval = ""
        if (measurement_type < 10) and (measurement_type >= 0):
            hotval += self._get_measure_type(measurement_type)
        buffer += hotval

        # Add a comma...
        buffer += "2c"

        # Set the offset dB
        hotval = self._convert_float_to_hex_string(offset_db)
        buffer += hotval

        # Add a comma...
        buffer += "2c"

        # byte 5:8 is filter value in Hz
        temp004 = 0
        if filter == 0:
            temp004 = 4500
        elif filter == 1:
            temp004 = 400.0
        elif filter == 2:
            temp004 = 10000.0
        
        buffer += self._convert_float_to_hex_string(temp004)

        # Add a comma...
        buffer += "2c"

        # byte 9 is power units
        buffer += self._get_units_type(units)

        # Add a comma...
        buffer += "2c"

        # byte 10:13 is CCDF limit in W
        buffer += self._convert_float_to_hex_string(ccdf_limit)

        # Terminate the command
        buffer += "0d0a"

        # pad the remainder of the message string with "ff"; 22 bytes accounted for so 49-22 = 27
        for j in range(0, 5):
            buffer += "ff"
        
        # send the command
        self._device.write(bytes.fromhex(buffer))
        t2 = time.time()
        delta = t2-t1
        config_time = 1.0
        if delta < config_time: 
            time.sleep(config_time - (t2-t1))
        else:
            time.sleep(self._cmd_delay)

        hex_message = '0353ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'

        self._device.write(bytes.fromhex(hex_message))
        time.sleep(config_time)
        response = self._device.read(48, 2000)
        time.sleep(self._cmd_delay)
        cleaned_response = response[1:]
        decoded_response = cleaned_response.decode('utf-8', errors='ignore')[2:]
        code, ack_nak = decoded_response.split("\r\n")[0].split(',')

        # Issue preamble notice
        buffer = '0350ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
        #print(buffer)
        self._device.write(bytes.fromhex(buffer))
        time.sleep(self._cmd_delay)

        # Sample two datasets to ensure config settings are established...
        ds = self.get_one_dataset()
        ds = self.get_one_dataset()

        return code, ack_nak
    
    def _convert_float_to_hex_string(self, floater:float)->str:
        """Accepts a floating point value and converts it to the string version then converted to hex values. 

        Args:
            floater (float): The floating point value to be converted.

        Returns:
            str: The string of hex values that represents the provided floating point number.
        """
        if floater < 0:
            tmp001 = f"{floater:1.4E}"
        else:
            tmp001 = f"{floater:1.5E}"
        tmp002str = ""
        for j in tmp001:
            if j == "E":
                j=j.lower()
            tmp002str += j.encode("utf-8").hex()

        return tmp002str
    
    def check_calibration(self):
        """Peforms a check that the calibration flag is set indicating that the sensor is calibrated. Will return True if calibrated and False otherwise.

        Returns:
            _type_: The success code and either 'ACK' or 'NAK'. 
        """
        # Issue preamble notice
        buffer = '0350ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
        
        self._device.write(bytes.fromhex(buffer))
        time.sleep(self._cmd_delay)

        buffer = "02"
        # F
        buffer += "46"
        # pad the remainder of the message string with "ff"; 22 bytes accounted for so 49-22 = 27
        for j in range(0, 47):
            buffer += "ff"
        
        # send the command
        self._device.write(bytes.fromhex(buffer))

        hex_message = '0353ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
        self._device.write(bytes.fromhex(hex_message))
        time.sleep(self._cmd_delay)
        response = self._device.read(48, 2000)
        time.sleep(self._cmd_delay)
        cleaned_response = response[1:]
        decoded_response = cleaned_response.decode('utf-8', errors='ignore')
        code, ack_nak = decoded_response.split("\r\n")[0].split(',')

        return code, ack_nak

    def set_data_format(self, format_string:str="F"):
        """Establishes which data items are returned to the user when a dataset is retrieved from the sensor. The
        following flags will set the different data elements are returned in the following order: 

        Args:
            format_string (str): F - forward power, R - reflected power, K - peak power, B - burst power,
            R - crest factor, C - CCDF factor, U - units, D - duty cycle, T - temperature, F - filter,
            A - ACK/NAK
        """
        if "F" in format_string:
            self._return_fwd_pwr = 1 # - 3 forward power F
        else:
            self._return_fwd_pwr = 0
        if "R" in format_string:
            self._return_rfl_pwr = 1 # - 4 reflected power R
        else:
            self._return_rfl_pwr = 0
        if "T" in format_string: # - 2 temperature T
            self._return_temp = 1
        else:
            self._return_temp = 0
        if "B" in format_string:
            self._return_burst_pwr = 1
        else:
            self._return_burst_pwr = 0
        if "K" in format_string:
            self._return_peak_pwr = 1
        else:
            self._return_peak_pwr = 0
        if "I" in format_string:
            self._return_filter_val = 1
        else:
            self._return_filter_val = 0
        if "M" in format_string:
            self._return_meas_type = 1
        else:
            self._return_meas_type = 0
        if "U" in format_string:
            self._return_units = 1
        else:
            self._return_units = 0
        if "C" in format_string:
            self._return_ccdf_factor = 1
        else:
            self._return_ccdf_factor = 0
        if "R" in format_string:
            self._return_crest_factor = 1
        else:
            self._return_crest_factor = 0
        if "D" in format_string:
            self._return_duty_cycle = 1
        else:
            self._return_duty_cycle = 0
        if "A" in format_string:
            self._return_ack = 1
        else:
            self._return_ack = 0
        # - 1 busrt power B
        # - 2 temperature T
        # - 3 forward power F
        # - 4 reflected power R
        # - 5 peak power K
        # - 6 filter value I
        # - 7 measure type M
        # - 8 units U
        # - 9 ccdf factor C
        # - 10 crest factor R
        # - 11 duty cycle D
        # - 12 n/a - empty
        # - 13 ACK/NAK A
        
    def get_one_dataset(self):
        """This function will trigger a single measurement sample and return a single data set.

        Returns:
            list: Returns the dataset elements ad defined by the and in the following order - forward power, reflected power, peak power, busrt power, ccdf factor, crest factor, units, duty cycle, temperature, filter value, or ACK/NAK status.
        """
        t1 = time.time()
        # Issue preamble notice
        buffer = '0350ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
        self._device.write(bytes.fromhex(buffer))

        # Issue command to get one dataset
        buffer = "02"
        # T
        buffer += "54"
        # pad the remainder of the message string with "ff"; 2 bytes accounted for so 49-2 = 47
        for j in range(0, 47):
            buffer += "ff"
        # send the command
        self._device.write(bytes.fromhex(buffer))

        # Issue message to return data
        hex_message = '0353ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
        self._device.write(bytes.fromhex(hex_message))
        response = self._device.read(64, 2000)[3:] # responses (report size) said to be 64 bytes max
        decoded_response = response.decode('utf-8', errors='ignore')

        hex_message = '0353ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
        self._device.write(bytes.fromhex(hex_message))
        response = self._device.read(64, 2000)[1:] # responses (report size) said to be 64 bytes max
        decoded_response += response.decode('utf-8', errors='ignore')

        hex_message = '0353ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
        self._device.write(bytes.fromhex(hex_message))
        response = self._device.read(64, 2000)[1:] # responses (report size) said to be 64 bytes max
        decoded_response += response.decode('utf-8', errors='ignore')

        tempval = decoded_response.split("\r\n")[0].split(',')
        fmt_list = self._get_formatted_output(tempval)
        t2 = time.time()

        time.sleep(0.3 - (t2-t1))
        # Extracted array holds the following
        # - 1 busrt power B
        # - 2 temperature T
        # - 3 forward power F
        # - 4 reflected power R
        # - 5 peak power K
        # - 6 filter value I
        # - 7 measure type M
        # - 8 units U
        # - 9 ccdf factor C
        # - 10 crest factor R
        # - 11 duty cycle D
        # - 12 n/a - empty
        # - 13 ACK/NAK A
        return fmt_list
    
    def _get_units(self, value:int=9)->str:
        return_value = "W"
        if value == 0:
            return_value = "None"
        elif value == 1:
            return_value = "dB"
        elif value == 2:
            return_value = "Rho"
        elif value == 3:
            return_value = "VSWR"
        elif value == 4:
            return_value = "R"
        elif value == 5:
            return_value = "RL"
        elif value == 6:
            return_value = "dBm"
        elif value == 7:
            return_value = "uW"
        elif value == 8:
            return_value = "mW"
        elif value == 9:
            return_value = "W"
        elif value == 10:
            return_value = "kW"
        elif value == 11:
            return_value = "Auto W"
        elif value == 12:
            return_value = "MHz"
        elif value == 13:
            return_value = "KHz"
        elif value == 14:
            return_value = "Raw"
        
        return return_value
    
    def _get_formatted_output(self, dataset):
        formatted_list = []
        if self._return_fwd_pwr == 1:
            formatted_list.append(float(dataset[2]))
        if self._return_rfl_pwr == 1:
            formatted_list.append(float(dataset[3]))
        if self._return_peak_pwr == 1:
            formatted_list.append(float(dataset[4]))
        if self._return_burst_pwr == 1:
            formatted_list.append(float(dataset[0]))
        if self._return_crest_factor == 1:
            formatted_list.append(float(dataset[9]))
        if self._return_ccdf_factor == 1:
            formatted_list.append(float(dataset[8]))
        if self._return_units == 1:
            formatted_list.append(self._get_units(int(dataset[7].strip())))
        if self._return_duty_cycle == 1:
            formatted_list.append(float(dataset[10]))
        if self._return_temp == 1:
            formatted_list.append(float(dataset[1]))
        if self._return_filter_val == 1:
            formatted_list.append(float(dataset[5]))
        if self._return_ack == 1:
            formatted_list.append(dataset[12])
        
        return formatted_list
    
    def zero_calibration(self):
        # Z
        print(1)
        return 1 # 0x00 Pass, 0x01 Fail, 0x02 Over

    def start_data_stream(self):
        # D
        # No returns
        print(2)
    
    def stop_data_stream(self):
        # U
        # no returns
        print(1)
    
    def float_to_ieee_hex(self, value):
        # Pack the float into 4 bytes using IEEE 754 format
        packed_value = struct.pack('>f', value)
        # Convert the packed bytes to a hexadecimal string
        hex_value = packed_value.hex()
        return hex_value


##### Main Program Start #####
my5000 = Bird_5000_Series_Wideband_Power_Sensor("5014")
print(my5000.instrument_identification())

s1, s2 = my5000.check_calibration()
db_offset = -0.3

my5000.configuration(measurement_type=1, offset_db=0.0, filter=1, units=9, ccdf_limit=0.0)
my5000.set_data_format("FRTUI")
print("should be 400 kHz...")
for k in range(0, 10):
    print(my5000.get_one_dataset())

my5000.configuration(measurement_type=1, offset_db=0.0, filter=2, units=9, ccdf_limit=0.0)
print("should be 10000 kHz...")
for k in range(0, 10):
    print(my5000.get_one_dataset())

my5000.configuration(measurement_type=1, offset_db=0.0, filter=0, units=9, ccdf_limit=0.0)
print("should be 4.5 kHz...")
for k in range(0, 10):
    print(my5000.get_one_dataset())

my5000.configuration(measurement_type=1, offset_db=0.0, filter=1, units=8, ccdf_limit=0.0)
print("should be 400 kHz...")
for k in range(0, 10):
    print(my5000.get_one_dataset())

my5000.configuration(measurement_type=1, offset_db=0.0, filter=2, units=8, ccdf_limit=0.0)
print("should be 10000 kHz...")
for k in range(0, 10):
    print(my5000.get_one_dataset())

my5000.configuration(measurement_type=1, offset_db=0.0, filter=0, units=8, ccdf_limit=0.0)
print("should be 4.5 kHz...")
for k in range(0, 10):
    print(my5000.get_one_dataset())

code, acknak = my5000.configuration(measurement_type=1, offset_db=0.0, filter=2, units=1)
print(code, ",", acknak)

#my5000.set_data_format("I")

dataset = my5000.get_one_dataset()
print(dataset)

my5000.set_data_format("FTUI")

print("Checking Measurement Type....")
for i in range(1, 10):
    print(f"mtype = {i}")
    code, acknak = my5000.configuration(measurement_type=i, offset_db=0.0, filter=2, units=11)
    
    for k in range(0, 10):
        dataset = my5000.get_one_dataset()
        print(dataset)
        #time.sleep(0.5)

print("Checking Units Type....")
for i in range(1, 10):
    print(f"utype = {i}")
    code, acknak = my5000.configuration(measurement_type=1, offset_db=0.0, filter=0, units=i)
    
    for k in range(0, 10):
        dataset = my5000.get_one_dataset()
        print(dataset)
        #time.sleep(0.5)

print("Done")
