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
        self.format = None
        self.pnp = None

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
            self.fetch = self.Fetch(self._instr_obj)
            self.format = self.Format(self._instr_obj)
            self.sense = self.Sense(self._instr_obj)
            self.trigger = self.Trigger(self._instr_obj)
            self.pnp = self.PnP(self._instr_obj)

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
    
    class PnP():
        def __init__(self, instrobj):
            self._instr_obj = instrobj
            self.file = self.File(self._instr_obj)

        def initiate_transfer(self):
            """Initiates a read of the Bird Plug and Play file. This reads file header details into memory
and updates the file size and total number of blocks fields. The command is issued once before blocks of file data can be transferred from the device.
            """
            self._instr_obj.write("PNP:ITRansfer")

        class File():
            def __init__(self, instrobj):
                self._instr_obj = instrobj
                self.block = self.Block(self._instr_obj)
            
            def size(self)->int:
                """Gets the Plug and Play file size.

                Returns:
                    int: File size.
                """
                return self._instr_obj.query("PNP:FILE:SIZE?")
            
            class Block():
                def __init__(self, instrobj):
                    self._instr_obj = instrobj

                def data(self)->str:
                    """Gets the Plug and Play file block data.

                    Returns:
                        str: PnP File Block Data Query
                    """
                    return self._instr_obj.query("PNP:FILE:BLOCk:DATA?")
                
                @property
                def number(self)->int:
                    """Gets the Plug and Play file block number to transfer.

                    Returns:
                        int: The block number to transfer.
                    """
                    return int(self._instr_obj.query("PNP:FILE:BLOCk:NUMBer?").rstrip())
                
                @number.setter
                def number(self, block:int=1):
                    """Sets the Plug and Play file block number to transfer.

                    Args:
                        block (int, optional): The block number to transfer. Defaults to 1.
                    """
                    self._instr_obj.write(f"PNP:FILE:BLOCk:NUMBer {block}")
                
                def total(self)->int:
                    """Gets the total number of blocks for the Plug and Play file transfer.

                    Returns:
                        int: Total number of blocks.
                    """
                    return int(self._instr_obj.query("PNP:FILE:BLOCk:TOTal?").rstrip())
                

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
                """Clear the accumulated average and restart the averaging process with the next measurement.
                """
                self._instr_obj.write("CALC:AVER:CLE")
                
            @property
            def count(self)->int:
                """Gets the number of measurements to average.

                Returns:
                    int: Number of measurements to average.
                """
                return int(self._instr_obj.query("CALC:AVER:COUN?").rstrip())
            
            @count.setter
            def count(self, count:int=1):
                """Sets the number of measurements to average.

                Args:
                    count (_type_): _description_
                """
                self._instr_obj.write(f"CALC:AVER:COUN {count}")

            @property
            def state(self)->int:
                """Get the result averaging state.

                Returns:
                    int: 1 for enabled, 0 for disabled.
                """
                return int(self._instr_obj.query("CALC:AVER:STAT?").rstrip())
            
            @state.setter
            def state(self, enabled:int=0):
                """Set the result averaging state.

                Args:
                    enabled (int, optional): Use 1 to enable averaging, 0 to disable. Defaults to 0.
                """
                self._instr_obj.write(f"CALC:AVER:STAT {enabled}")
        
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
                    self.level = self.Level(self._instr_obj)
                
                @property
                def delay(self)->float:
                    """Get the delay from the begin event to the beginning of the gated time interval.

                    Returns:
                        float: Delay in seconds. 
                    """
                    return float(self._instr_obj.query("CALC:GATE:BEG:DEL?").rstrip())
                
                @delay.setter
                def delay(self, secs:float=0.0):
                    """Set the delay from the begin event to the beginning of the gated time interval. Begin Delay is normally > 0 to begin the gated timing interval after the rising edge.

                    Args:
                        secs (float, optional): Seconds to delay. Defaults to 0.0.
                    """
                    self._instr_obj.write(f"CALC:GATE:BEG:DEL {secs}")

                class Level():
                    def __init__(self, instrobj):
                        self._instr_obj = instrobj
                    
                    @property
                    def high(self)->float:
                        """Get the high threshold for detection of the rising edge of the pulse.

                        Returns:
                            float: High threshold as a percent.
                        """
                        return float(self._instr_obj.query("CALC:GATE:BEG:LEV:HIGH?").rstrip())
                    
                    @high.setter
                    def high(self, value:float=90.0):
                        """Set the high threshold for detection of the rising edge of the pulse.

                        Args:
                            value (float, optional): 0 to 100 percent. Defaults to 90.0.
                        """
                        self._instr_obj.write(f"CALC:GATE:BEG:LEV:HIGH {value}")

                    @property
                    def low(self)->float:
                        """Get the low threshold for detection of the rising edge of the pulse.

                        Returns:
                            float: Low threshold as a percent.
                        """
                        return float(self._instr_obj.query("CALC:GATE:BEG:LEV:LOW?").rstrip())
                    
                    @low.setter
                    def low(self, value:float=10.0):
                        """Set the low threshold for detection of the rising edge of the pulse.

                        Args:
                            value (float, optional): 0 to 100 percent. Defaults to 10.0.
                        """
                        self._instr_obj.write(f"CALC:GATE:BEG:LEV:LOW {value}")
            
            class End():
                def __init__(self, instrobj):
                    self._instr_obj = instrobj
                    self.level = self.Level(self._instr_obj)
                
                @property
                def delay(self)->float:
                    """Get the delay from the end event to the end of the gated time interval.

                    Returns:
                        float: Delay in seconds. 
                    """
                    return float(self._instr_obj.query("CALC:GATE:END:DEL?").rstrip())
                
                @delay.setter
                def delay(self, secs:float=0.0):
                    """Set the delay from the end event to the end of the gated time interval. End Delay is normally < 0 to end the gated timing interval before the falling edge.

                    Args:
                        secs (float, optional): Seconds to delay. Defaults to 0.0.
                    """
                    self._instr_obj.write(f"CALC:GATE:END:DEL {secs}")

                class Level():
                    def __init__(self, instrobj):
                        self._instr_obj = instrobj
                    
                    @property
                    def high(self)->float:
                        """Get the high threshold for detection of the falling edge of the pulse.

                        Returns:
                            float: High threshold as a percent.
                        """
                        return float(self._instr_obj.query("CALC:GATE:END:LEV:HIGH?").rstrip())
                    
                    @high.setter
                    def high(self, value:float=90.0):
                        """Set the high threshold for detection of the falling edge of the pulse.

                        Args:
                            value (float, optional): 0 to 100 percent. Defaults to 90.0.
                        """
                        self._instr_obj.write(f"CALC:GATE:END:LEV:HIGH {value}")

                    @property
                    def low(self)->float:
                        """Get the low threshold for detection of the falling edge of the pulse.

                        Returns:
                            float: Low threshold as a percent.
                        """
                        return float(self._instr_obj.query("CALC:GATE:BEG:LEV:LOW?").rstrip())
                    
                    @low.setter
                    def low(self, value:float=10.0):
                        """Set the low threshold for detection of the falling edge of the pulse.

                        Args:
                            value (float, optional): 0 to 100 percent. Defaults to 10.0.
                        """
                        self._instr_obj.write(f"CALC:GATE:BEG:LEV:LOW {value}")

        class State():
            """_summary_

            Returns:
                _type_: _description_
            """
            def __init__(self, instrobj):
                self._instr_obj = instrobj

            @property
            def enable(self, statenum:int=1)->int:
                """Query of statenum enable/disable status.

                Args:
                    statenum (int, optional): An integer ranging from 1 to 4. Defaults to 1.

                Returns:
                    int: 0 for OFF or 1 for ON.
                """
                tmpval = self._instr_obj.query(f"CALC:STAT{statenum}:ENAB?").rstrip()
                intval = 0
                if "OFF" in tmpval:
                    intval = 0
                else:
                    intval = 1
                return int(intval)
            
            @enable.setter
            def enable(self, statenum:int=1, status:int=0):
                """Set of statenum enable/disable status.

                Args:
                    statenum (int, optional): An integer ranging from 1 to 4. Defaults to 1.
                    status (int, optional): 0 for OFF or 1 for ON. Defaults to 0.
                """
                tmpstr == "ON"
                if status == 0:
                    tmpstr = "OFF"
                self._instr_obj.write(f"CALC:STAT{statenum}:ENAB {tmpstr}")

            @property
            def begin_delay(self, statenum:int=1)->float:
                """Returns position of statenum relative to trigger point.

                Args:
                    statenum (int, optional): An integer ranging from 1 to 4. Defaults to 1. Defaults to 1.

                Returns:
                    float: Delay in seconds from the trigger point.
                """
                return float(self._instr_obj.query(f"CALC:STAT{statenum}:BEG?").rstrip())
            
            @begin_delay.setter
            def begin_delay(self, statenum:int=1, delay:float=0.0):
                """Specifies position of statenum relative to trigger point.

                Args:
                    statenum (int, optional): An integer ranging from 1 to 4. Defaults to 1. Defaults to 1.
                    delay (float, optional): Delay in seconds from the trigger point. Defaults to 0.0.
                """
                self._instr_obj.write(f"CALC:STAT{statenum}:BEG {delay}")

            @property
            def end_delay(self, statenum:int=1)->float:
                """Returns position of statenum relative to trigger point.

                Args:
                    statenum (int, optional): An integer ranging from 1 to 4. Defaults to 1. Defaults to 1.

                Returns:
                    float: Delay in seconds from the trigger point.
                """
                return float(self._instr_obj.query(f"CALC:STAT{statenum}:END?").rstrip())
            
            @begin_delay.setter
            def end_delay(self, statenum:int=1, delay:float=0.0):
                """Specifies position of statenum relative to trigger point.

                Args:
                    statenum (int, optional): An integer ranging from 1 to 4. Defaults to 1. Defaults to 1.
                    delay (float, optional): Delay in seconds from the trigger point. Defaults to 0.0 s.
                """
                self._instr_obj.write(f"CALC:STAT{statenum}:END {delay}")

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

    class Format():
        def __init__(self, instrobj):
            self._instr_obj = instrobj

        def status_register(self)->str:
            """Gets the format of the status registers. Status registers are always formatted as ASCII.

            Returns:
                str: The format of the status registers.
            """
            return self._instr_obj.query("FORM:SREG?")

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
            self.frequency = self.Frequency(self._instr_obj)
            self.period = self.Period(self._instr_obj)
            self.sweep = self.Sweep(self._instr_obj)
        
        class Period():
            def __init__(self, instrobj):
                """_summary_
                """
                self._instr_obj = instrobj
        
        class Sweep():
            def __init__(self, instrobj):
                """_summary_
                """
                self._instr_obj = instrobj
                self.time = self.Time(self._instr_obj)

            class Time():
                def __init__(self, instrobj):
                    self._instr_obj = instrobj
                    self.auto = self.Auto(self._instr_obj)

                class Auto():
                    def __init__(self, instrobj):
                        self._instr_obj = instrobj
                        self.periods = self.Periods(self._instr_obj)
                    
                    class Periods():
                        def __init__(self, instrobj):
                            self._instr_obj = instrobj
                        
                        @property
                        def value(self)->int:
                            """Query how many pulse periods are used as sweep time.

                            Returns:
                                int: Minimum of 1, maximum of 8.
                            """
                            return self._instr_obj.query("SENS:SWE:TIME:AUTO:PER?")
                        
                        @value.setter
                        def value(self, count:int=1):
                            """Set Number of pulse periods to use as sweep time.

                            Args:
                                count (int, optional): Minimum of 1, maximum of 8. Defaults to 1.
                            """
                            self._instr_obj.write(f"SENS:SWE:TIME:AUTO:PER {count}")

                    @property
                    def value(self)->int:
                        """When enabled use measured pulse period as sweep time.

                        Returns:
                            int: 1 for enabled, 0 for disabled. 
                        """
                        return self._instr_obj.query("SENS:SWE:TIME:AUTO?")
                    
                    @value.setter
                    def value(self, enabled:int=0):
                        """When enabled use measured pulse period as sweep time.

                        Args:
                            enabled (int, optional): 1 for enabled, 0 for disabled. Defaults to 0.
                        """
                        self._instr_obj.write(f"SENS:SWE:TIME:AUTO {enabled}")
                    
                    @property
                    def value(self)->float:
                        """Returns the time interval to be returned by TRACe:TIME:DATA?.

                        Returns:
                            float: Seconds (s).
                        """
                        return self._instr_obj.query("SENS:SWE:TIME?")
                    
                    @value.setter
                    def value(self, secs:float=0.0):
                        """Specifies time interval to be returned by TRACe:TIME:DATA?

                        Args:
                            secs (float, optional): Seconds value. Defaults to 0.0.
                        """
                        self._instr_obj.write(f"SENS:SWE:TIME {secs}")
            
            @property
            def delay(self)->float:
                """Returns the beginning of sweep realative to trigger reference point.

                Returns:
                    float: Value in seconds.
                """
                return self._instr_obj.query("SENS:SWE:DEL?")
            
            @delay.setter
            def delay(self, secs:float=0.0):
                """Specifies beginning of sweep realative to trigger reference point.

                Args:
                    secs (float, optional): Seconds relative to trigger reference point. Defaults to 0.0.
                """
                self._instr_obj.write(f"SENS:SWE:DEL {secs}")

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
        
        @property
        def reflected_enable(self)->int:
            """Get reflected power measurement state.

            Returns:
                int: 1 for enabled, 0 for disabled.
            """
            return int(self._instr_obj.query(f"SENS:REFL:ENAB?\n").rstrip())
        
        @reflected_enable.setter
        def reflected_enable(self, state:int=1):
            """Set reflected power measurement state. Reflected power measurement may be disabled for faster forward power measurements.

            Args:
                state (int, optional): Use 1 to enable, 0 to disable. Defaults to 1.
            """
            self._instr_obj.write(f"SENS:REFL:ENAB {state}")