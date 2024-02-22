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

        self.calculate = None
        self.sense = None
        self.trigger = None
        self.fetch = None

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
            self.calculate = self.Calculate(self._instr_obj)
            self.sense = self.Sense(self._instr_obj)
            self.fetch = self.Fetch(self._instr_obj)
            self.trigger = self.Trigger(self._instr_obj)

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
    
    class Calculate():
        """_summary_

        Returns:
            _type_: _description_
        """
        def __init__(self, instrobj):
            self._instr_obj = instrobj
            self.average = self.Average(self._instr_obj)
            self.gate = self.Gate(self._instr_obj)
            self.state = self.State(self._instr_obj)

        class Average():
            """_summary_

            Returns:
                _type_: _description_
            """
            def __init__(self, instrobj):
                self._instr_obj = instrobj
            
            def clear(self):
                val = 1
                
            @property
            def count(self):
                return 0
            
            @count.setter
            def count(self, count):
                val = count
        
        class Gate():
            """_summary_

            Returns:
                _type_: _description_
            """
            def __init__(self, instrobj):
                self._instr_obj = instrobj
                self.begin = self.Begin(self._instr_obj)
                self.end = self.End(self._instr_obj)

            class Begin():
                def __init__(self, instrobj):
                    self._instr_obj = instrobj
            
            class End():
                def __init__(self, instrobj):
                    self._instr_obj = instrobj
        
        class State():
            """_summary_

            Returns:
                _type_: _description_
            """
            def __init__(self, instrobj):
                self._instr_obj = instrobj

    class Fetch():
        """_summary_

        Returns:
            _type_: _description_
        """
        def __init__(self, instrobj):
            self._instr_obj = instrobj
            self.state = self.State(instrobj)
            self.temp = None
        
        def forward_power(self):
            """
            Gets the forward average power from the most recent measurement. 
            This does not initiate a new measurement. 

            Returns:
                float: Power in Watts (w)
            """
            return float(self._instr_obj.query("FETC:AVER?").rstrip())
        
        def reflected_power(self):
            """
            Gets the reflected average power from the most recent measurement.
            This does not initiate a new measurement. 

            Returns:
                float: Power in Watts (w)
            """
            return float(self._instr_obj.query("FETC:REFL:AVER?").rstrip())
        
        def temperature(self):
            """
            Gets the current temperature.  

            Returns:
                float: Temperature in Celcius (C)
            """
            return float(self._instr_obj.query("FETC:TEMP?").rstrip())
        
        def duty_cycle(self):
            """
            Gets the duty cycle for the most recent measurement. The proportion
            of the average pulse width to the average pulse period is returned.
            See Statistics. This does not initiate a new measurement.   

            Returns:
                float: Duty cycle in percent (%)
            """
            return float(self._instr_obj.query("FETC:DCYC?").rstrip())
        
        def frequency(self):
            """
            Gets the RF carrier frequency from the most recent measurement. This
            does not initiate a new measurement.    

            Returns:
                float: Frequency in MHz
            """
            return float(self._instr_obj.query("FETC:FREQ?").rstrip())
        
        def gate_count(self):
            """
            Gets the number of pulses for which statistics have been accumulated.
            This does not initiate a new measurement. See Statistics.     

            Returns:
                int: Count in pulses.
            """
            return int(self._instr_obj.query("FETC:GATE:COUN?").rstrip())
        
        def gate_maximum(self):
            """
            Gets the maximum of gated mean. The mean power in the gate interval is
            determined for each pulse. The maximum of the mean power over all the
            pulses is returned. See Statistics. This does not initiate a new
            measurement.      

            Returns:
                float: Maximum gate power (W).
            """
            return float(self._instr_obj.query("FETC:GATE:MAX?").rstrip())
        
        def gate_minimum(self):
            """
            Gets the minimum of gated mean. The mean power in the gate interval is
            determined for each pulse. The minimum of the mean power over all the
            pulses is returned. See Statistics. This does not initiate a new
            measurement.      

            Returns:
                float: Minimum gate power (W).
            """
            return float(self._instr_obj.query("FETC:GATE:MIN?").rstrip())
        
        def gate_mean(self):
            """
            Gets the mean power in the gate interval for the most recent measurement.
            The mean power in the gate interval is determined for each pulse. The
            average of the mean power over all the pulses is returned. See Statistics.
            This does not initiate a new measurement.       

            Returns:
                float: Mean gate power (W).
            """
            return float(self._instr_obj.query("FETC:GATE:MEAN?").rstrip())
        
        def period(self):
            """
            Get the pulse period for the most recent measurement. The period is
            determined for each pulse. The average of the period over all the pulses
            is returned. See Statistics. This does not initiate a new measurement.       

            Returns:
                float: Period in microseconds (us).
            """
            return float(self._instr_obj.query("FETC:PER?").rstrip())
        
        def pulse_repetition_frequency(self):
            """
            Gets the pulse repetition frequency for the most recent measurement.
            The average pulse repetition frequency is returned. See Statistics.
            This does not initiate a new measurement.        

            Returns:
                float: Frequency (Hz).
            """
            return float(self._instr_obj.query("FETC:PRF?").rstrip())
        
        def pulse_width(self):
            """
            Get the pulse width for the most recent measurement. The width is
            determined for each pulse. The average of the width over all the
            pulses is returned. See Statistics. This does not initiate a new
            measurement.         

            Returns:
                float: Pulse width in microseconds (us).
            """
            return float(self._instr_obj.query("FETC:WID?").rstrip())
        
        def state_mean(self, state):
            """
            Gets the mean power in state interval for most recent measurement.         

            Args:
                state (int): 1 for state1, 2 for state2, 3 for state3, and
                4 for state4.

            Returns:
                float: Mean power for the specified state in watts (W).
            """
            return float(self._instr_obj.query(f"FETC:STAT{state}:MEAN?").rstrip())
        
        def state_maximum(self, state):
            """
            Gets the maximum power in state interval for most recent measurement.         

            Args:
                state (int): 1 for state1, 2 for state2, 3 for state3, and
                4 for state4.

            Returns:
                float: Maximum power for the specified state in watts (W).
            """
            return float(self._instr_obj.query(f"FETC:STAT{state}:MAX?").rstrip())
        
        def state_minimum(self, state):
            """
            Gets the minimum power in state interval for most recent measurement.         

            Args:
                state (int): 1 for state1, 2 for state2, 3 for state3, and
                4 for state4.

            Returns:
                float: Minimum power for the specified state in watts (W).
            """
            return float(self._instr_obj.query(f"FETC:STAT{state}:MIN?").rstrip())
        
        class State():
            """_summary_

            Returns:
                _type_: _description_
            """
            def __init__(self, instrobj):
                self._instr_obj = instrobj

    class Trigger():
        """_summary_

        Returns:
            _type_: _description_
        """
        def __init__(self, instrobj):
            self._instr_obj = instrobj

        @property
        def continuous(self):
            """
            Get continuous trigger mode. 

            Returns:
                int: 0 for OFF, 1 for ON
            """
            return int(self._instr_obj.query("INIT:CONT?").rstrip())
        
        @continuous.setter
        def continuous(self, state:int=0):
            """
            Set continuous trigger mode.

            Args:
                state (int): Pass 0 for OFF, 1 for ON. 
            """
            self._instr_obj.write(f"INIT:CONT {state}")
        
        def once(self):
            """
            Trigger Initiate Immediate Command. Causes trigger to exit the IDLE
            state. Removes the device from the "wait for trigger" state and places
            it in the "idle" state. It does not affect any other settings of
            the trigger system. 
            """
            self._instr_obj.write(f"INIT:IMM")

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
        
