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
        self._cmd_delay = 0.25 # 0.3

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

        self.device = hid.Device(self.VENDOR_ID, self.PRODUCT_ID)

    def instrument_identification(self):
        # Issue preamble notice
        hex_message = '0350ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
        self.device.write(bytes.fromhex(hex_message))
        
        hex_message = '02490d0affffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
        self.device.write(bytes.fromhex(hex_message))
        hex_message = '0353ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
        self.device.write(bytes.fromhex(hex_message))

        response = self.device.read(48, 2000)
        cleaned_response = response[1:]
        decoded_response = cleaned_response.decode('utf-8', errors='ignore')
        model_number, software_date, runtime_version = decoded_response.split("\r\n")[0].split(',')

        return f"{self.device.manufacturer},{model_number},{self.device.serial},{runtime_version}"

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
                      measurement_type:int, 
                      offset_db:float, 
                      filter:float,
                      units:int,
                      ccdf_limit:float,
                      forward_scale:float,
                      reflected_scale:float):
        """This function is used to configure the sensor. 

        Args:
            measurement_type (int): 0 = None, 1 = Average, 2 = Peak, 3 = Burst, 4 = Crest, 5 = CCDF, 6 = Average Peak, 7 = Avg APM, 8 = APM, 9 = 43 Avg, 10 = 43 Peak, 11 = 43 Peak Avg
            offset_db (float): The power offset for the measurements.
            filter (float): Sets the filter speed for the measurements, accessible through the Filter enumeration with low as 4500 Hz, medium as 400 kHz, and high as 10 MHz.
            units (int): Sets the power units for the measurements to be acquired from the sensor. 0=None, 1=dB, 2=Rho, 3=VSWR, 4=R, 5=RL, 6=dBm, 7=uW, 8=mW, 9=W, 10=kW, 11=Auto W, 12=MHz, 13=kHz, 14=Raw
            ccdf_limit (float): Sets the ccdf limit for the measurements.
            forward_scale (float): Sets the forward power scale for measurements. (5014 only)
            reflected_scale (float): Sets the reflected power scale for measurements (5014 only)
        """
        # Perform the cal check before attempting to change the configuration - required
        s1, s2 = my5000.check_calibration()

        t1 = time.time()
        # Issue preamble notice
        buffer = '0350ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
        #print(buffer)
        self.device.write(bytes.fromhex(buffer))
        time.sleep(self._cmd_delay)

        buffer = "02"
        # G
        buffer += "47"
        # byte 0 is measurement type
        if (measurement_type < 10) and (measurement_type >= 0):
            buffer += self._get_measure_type(measurement_type)
            #buffer += str(measurement_type.to_bytes(1, "big"))[4:6]
        # byte 1:4 is offset value in dB
        buffer += self.float_to_ieee_hex(offset_db)
        # byte 5:8 is filter value in Hz
        buffer += self.float_to_ieee_hex(filter)
        # byte 9 is power units
        buffer += self._get_units_type(units)
        #buffer += str(units.to_bytes(1, "big"))[4:6]
        # byte 10:13 is CCDF limit in W
        buffer += self.float_to_ieee_hex(ccdf_limit)
        # byte 14:17 is forward scale in W
        buffer += self.float_to_ieee_hex(forward_scale)
        # byte 18:21 is reflected scal in W
        buffer += self.float_to_ieee_hex(reflected_scale)
        # pad the remainder of the message string with "ff"; 22 bytes accounted for so 49-22 = 27
        for j in range(0, 25):
            buffer += "ff"
        #print(buffer)
        # send the command
        self.device.write(bytes.fromhex(buffer))
        t2 = time.time()
        delta = t2-t1
        if delta < self._cmd_delay:
            time.sleep(self._cmd_delay - (t2-t1))
        else:
            time.sleep(self._cmd_delay)

        hex_message = '0353ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
        self.device.write(bytes.fromhex(hex_message))
        time.sleep(self._cmd_delay)
        response = self.device.read(48, 2000)
        time.sleep(self._cmd_delay)
        cleaned_response = response[1:]
        decoded_response = cleaned_response.decode('utf-8', errors='ignore')[2:]
        code, ack_nak = decoded_response.split("\r\n")[0].split(',')
        #t2 = time.time()
        #if (t2-t1) < 0.3:
        #    time.sleep(0.3 - (t2-t1))

        return code, ack_nak
    
    def check_calibration(self):
        # Issue preamble notice
        buffer = '0350ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
        #print(buffer)
        self.device.write(bytes.fromhex(buffer))
        time.sleep(self._cmd_delay)

        buffer = "02"
        # F
        buffer += "46"
        # pad the remainder of the message string with "ff"; 22 bytes accounted for so 49-22 = 27
        for j in range(0, 47):
            buffer += "ff"
        #print(buffer)
        # send the command
        self.device.write(bytes.fromhex(buffer))

        hex_message = '0353ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
        self.device.write(bytes.fromhex(hex_message))
        time.sleep(self._cmd_delay)
        response = self.device.read(48, 2000)
        time.sleep(self._cmd_delay)
        cleaned_response = response[1:]
        decoded_response = cleaned_response.decode('utf-8', errors='ignore')
        code, ack_nak = decoded_response.split("\r\n")[0].split(',')
        return code, ack_nak

    def zero_calibration(self):
        # Z
        print(1)
        return 1 # 0x00 Pass, 0x01 Fail, 0x02 Over

    def start_data_stream(self):
        # D
        # No returns
        print(2)
    
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
        t1 = time.time()
        # Issue preamble notice
        buffer = '0350ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
        self.device.write(bytes.fromhex(buffer))

        # Issue command to get one dataset
        buffer = "02"
        # T
        buffer += "54"
        # pad the remainder of the message string with "ff"; 2 bytes accounted for so 49-2 = 47
        for j in range(0, 47):
            buffer += "ff"
        # send the command
        self.device.write(bytes.fromhex(buffer))

        # Issue message to return data
        hex_message = '0353ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
        self.device.write(bytes.fromhex(hex_message))
        response = self.device.read(64, 2000)[3:] # responses (report size) said to be 64 bytes max
        decoded_response = response.decode('utf-8', errors='ignore')
        #print(decoded_response)

        hex_message = '0353ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
        self.device.write(bytes.fromhex(hex_message))
        response = self.device.read(64, 2000)[1:] # responses (report size) said to be 64 bytes max
        decoded_response += response.decode('utf-8', errors='ignore')
        #print(decoded_response)

        hex_message = '0353ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
        self.device.write(bytes.fromhex(hex_message))
        response = self.device.read(64, 2000)[1:] # responses (report size) said to be 64 bytes max
        decoded_response += response.decode('utf-8', errors='ignore')
        #print(decoded_response)

        tempval = decoded_response.split("\r\n")[0].split(',')
        fmt_list = self._get_formatted_output(tempval)
        t2 = time.time()
        #print(t2-t1)
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
my5000 = Bird_5000_Series_Wideband_Power_Sensor("5012D")
print(my5000.instrument_identification())

s1, s2 = my5000.check_calibration()

code, acknak = my5000.configuration(measurement_type=1, offset_db=0.0, filter=10E+6, units=1, ccdf_limit=5.0, forward_scale=5.0, reflected_scale=1.0)
print(code, ",", acknak)

my5000.set_data_format("I")

dataset = my5000.get_one_dataset()
print(dataset)

my5000.set_data_format("FTUI")

print("Checking Measurement Type....")
for i in range(1, 10):
    print(f"mtype = {i}")
    code, acknak = my5000.configuration(measurement_type=i, offset_db=0.0, filter=4.5e+3, units=11, ccdf_limit=5.0, forward_scale=5.0, reflected_scale=1.0)
    
    for k in range(0, 10):
        dataset = my5000.get_one_dataset()
        print(dataset)
        #time.sleep(0.5)

print("Checking Units Type....")
for i in range(1, 10):
    print(f"utype = {i}")
    code, acknak = my5000.configuration(measurement_type=1, offset_db=0.0, filter=10e+6, units=i, ccdf_limit=5.0, forward_scale=5.0, reflected_scale=1.0)
    
    for k in range(0, 10):
        dataset = my5000.get_one_dataset()
        print(dataset)
        #time.sleep(0.5)

print("Checking Filter Type....")
fltr = [10e+6, 400e+3, 4.5e+3]
for i in fltr:
    print(f"filter = {i}")
    code, acknak = my5000.configuration(measurement_type=6, offset_db=0.0, filter=i, units=11, ccdf_limit=5.0, forward_scale=5.0, reflected_scale=1.0)
    
    for k in range(0, 10):
        dataset = my5000.get_one_dataset()
        print(dataset)
        #time.sleep(0.5)
print("Done")
