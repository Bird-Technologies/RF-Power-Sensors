"""
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

@file series_7027_7037.py

Copyright (c) Bird

@author Josh Brown
"""
import pyvisa

class Series_7027():
    """_summary_
    """
    def __init__(self, instrument_resource_string=None):
        self._instrument_resource_string = instrument_resource_string
        self._rm = None
        self._instr_obj = None
        self._timeout = 5000
        self._echo_cmds = False
        self._mfg_id = ""
        self._model = ""
        self._sn = ""
        self._fw = ""
        self._general = ""

        self.sense = None

        try:
            if self._rm is None:
                self._resource_manager = pyvisa.ResourceManager()
        except pyvisa.VisaIOError as visaerror:
            print(f"{visaerror}")
        except pyvisa.VisaIOWarning as visawarning:
            print(f"{visawarning}")

    def connect(self, instrument_resource_string:str=None, timeout:int=None):
        try:
            if instrument_resource_string != None:
                self._instrument_resource_string = instrument_resource_string
                
            self._instr_obj = self._resource_manager.open_resource(
                self._instrument_resource_string
            )

            if timeout is None:
                self._instr_obj.timeout = self._timeout
            else:
                self._instr_obj.timeout = timeout
                self._timeout = timeout

            self._instr_obj.send_end = True
            self._instr_obj.write_termination = "\n"
            self._instr_obj.read_termination = "\n"

            #self._instr_obj.write("*CLS;*RST\n")
            self.write("*CLS;*RST")
            # Ensure sub-classes are updated properly
            self.sense = self.Sense(self._instr_obj)

            # Extract the instrument ID string and populate attributes
            self._general = self.query("*IDN?")
            self._general = self._general.rstrip()
            self._mfg_id, self._model, self._sn, self._fw = self._general.split(',')

        except pyvisa.VisaIOError as visaerr:
            print(f"{visaerr}")
        return
    
    def write(self, cmd):
        self._instr_obj.write(f"{cmd}\n")

    def query(self, cmd):
        return self._instr_obj.query(f"{cmd}\n")

    def disconnect(self):
        """
        Close an instance of an instrument object.

        Args:
            None

        Returns:
            None
        """
        try:
            self._instr_obj.close()
        except pyvisa.VisaIOError as visaerr:
            print(f"{visaerr}")
        return
    
    @property
    def manufacturer_id(self):
        """Returns the instrument/sensor manufacturer ID.

        Returns:
            str: The instrument/sensor manufacturer ID.
        """
        return self._mfg_id
    
    @property
    def model_number(self):
        """Returns the instrument/sensor model number.

        Returns:
            str: The instrument/sensor model number.
        """
        return self._model

    @property
    def firmware_version(self):
        """Returns the instrument/sensor firmware version.

        Returns:
            str: The instrument/sensor firmware version.
        """
        return self._fw

    @property
    def serial_number(self):
        """Returns the instrument/sensor serial number.

        Returns:
            str: The instrument/sensor serial number.
        """
        return self._sn
    
    class Sense():
        """_summary_
        """
        def __init__(self, instrobj):
            """_summary_
            """
            self._instr_obj = instrobj
            self.frequency = self.Frequency(instrobj)
        
        class Frequency():
            """_summary_
            """
            def __init__(self, instrobj):
                """_summary_
                """
                self._instr_obj = instrobj
            
            @property
            def frequency(self):
                """
                Gets the frequency used for amplitude correction when SENSe:CORRection:AUTO is disabled. This is not the frequency measured. 

                Args:
                    None
                """
                return float(self._instr_obj.query(f"SENS:FREQ?\n").rstrip())

            @frequency.setter
            def frequency(self, frequency:float=1.0):
                """
                Sets the frequency used for amplitude correction when SENSe:CORRection:AUTO is disabled. 

                Args:
                    frequency (float, optional): _description_. Defaults to 1.0.
                """
                self._instr_obj.write(f"SENS:FREQ {frequency}\n")

            @property
            def auto(self):
                """
                Get automatic frequency dependent amplitude correction state. 

                Args:
                    None
                """
                return int(self._instr_obj.query(f"SENS:FREQ:AUTO?\n").rstrip())

            @auto.setter
            def auto(self, state:int=True):
                """
                Set automatic frequency dependent amplitude correction state.  

                Args:
                    frequency (float, optional): _description_. Defaults to 1.0.
                """
                self._instr_obj.write(f"SENS:FREQ:AUTO {state}\n")

            @property
            def range_lower(self):
                """Gets minimum calibrated frequency. 

                Returns:
                    float: Min cal frequency.
                """
                return float(self._instr_obj.query(f"SENS:FREQ:RANG:LOW?\n").rstrip())
            
            @property
            def range_upper(self):
                """Gets maximum calibrated frequency. 

                Returns:
                    float: Max cal frequency.
                """
                return float(self._instr_obj.query(f"SENS:FREQ:RANG:UPP?\n").rstrip())
        
