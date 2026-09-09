"""
@verbatim

The MIT License (MIT)

Copyright (c) 2026 Bird

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

@file series_7022.py

Copyright (c) Bird

@author Josh Brown
"""
import pyvisa

class Series_7022():
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
        self.calibration = None
        self.commmon = None
        self.format = None
        self.input = None
        self.measure = None
        self.pnp = None
        self.sense = None
        self.trace = None
        self.trigger = None
        self.status = None
        self.system = None
        self.unit = None
        

        try:
            if self._rm is None:
                self._resource_manager = pyvisa.ResourceManager()
        except pyvisa.VisaIOError as visaerror:
            print(f"{visaerror}")
        except pyvisa.VisaIOWarning as visawarning:
            print(f"{visawarning}")

    def connect(self, instrument_resource_string:str=None, timeout_ms:int=None):
        try:
            if instrument_resource_string != None:
                self._instrument_resource_string = instrument_resource_string
                
            self._instr_obj = self._resource_manager.open_resource(
                self._instrument_resource_string
            )

            if timeout_ms is None:
                self._instr_obj.timeout = self._timeout
            else:
                self._instr_obj.timeout = timeout_ms
                self._timeout = timeout_ms

            self._instr_obj.send_end = True
            self._instr_obj.write_termination = "\n"
            self._instr_obj.read_termination = "\n"

            #self._instr_obj.write("*CLS;*RST\n")
            self.write("*CLS;*RST")

            # Ensure sub-classes are updated properly
            self.calculate      = self.Calculate(self._instr_obj)
            self.calibration    = self.Calibration(self._instr_obj)
            self.common         = self.Common(self._instr_obj)
            self.format         = self.Format(self._instr_obj)
            self.input          = self.Input(self._instr_obj)
            self.sense          = self.Sense(self._instr_obj)
            self.measure        = self.Measure(self._instr_obj)
            self.pnp            = self.Pnp(self._instr_obj)
            self.system         = self.System(self._instr_obj)
            self.trace          = self.Trace(self._instr_obj)
            self.unit           = self.Unit(self._instr_obj)
            #self.trigger = self.Trigger(self._instr_obj)
            #self.pnp = self.PnP(self._instr_obj)

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
    
    @property
    def timeout_value(self):
        return self._instr_obj.timeout
    
    class Calibration():
        def __init__(self, instrobj):
            self.__instr_obj = instrobj
            
            self.zero   = self.Zero(self.__instr_obj)
        
        class Zero():
            def __init__(self, instrobj):
                self.__instr_obj = instrobj

            def execute(self):
                """Starts the zero calibration process.
                """
                val = self.__instr_obj.write(f"CALibration:ZERO")
                # print(val)
            
            def get_duration(self)->float:
                """Gets estimated time in seconds to perform a zero cal.

                Returns:
                    float: Time in seconds. 
                """
                val = float(self.__instr_obj.query(f"CALibration:ZERO:DURation?"))
                return val
        
        def reload(self):
            """Reload the calibration table.
            """
            val = self.__instr_obj.write(f"CALibration:RELoad")
            # print(val)

    class Calculate():
        def __init__(self, instrobj):
            self.__instr_obj = instrobj
            
            self.averagepower   = self.AveragePower(self.__instr_obj)
        
        @property
        def state(self)->int:
            """Controls whether post-processing is enabled.

            Args:
                enabled (int, optional): 0 for disabled and 1 for enabled. Defaults to 0.
            """
            val = int(self.__instr_obj.query(f"CALCulate:STATe?"))
            return val
        
        @state.setter
        def state(self, enabled:int=0):
            """Controls whether post-processing is enabled.

            Args:
                enabled (int, optional): 0 for disabled and 1 for enabled. Defaults to 0.
            """
            val = self.__instr_obj.write(f"CALCulate:STATe {enabled}")
        
        class AveragePower():
            def __init__(self, instrobj):
                self.__instr_obj = instrobj

                self.smoothing   = self.Smoothing(self.__instr_obj)

            class Smoothing():
                def __init__(self, instrobj):
                    self.__instr_obj = instrobj

                @property
                def level(self)->int:
                    """Selects a level of measurement data smoothing.

                    Returns:
                        int: 0 for NONE, 1 for LOW, 2 for MEDIUM, or 3 for HIGH.
                    """
                    val = int(self.__instr_obj.query(f"CALCulate:APOWer:SMOothing?"))
                    return val
                
                @level.setter
                def level(self, level:int=0):
                    """Selects a level of measurement data smoothing.

                    Args:
                        level (int, optional): 0 for NONE, 1 for LOW, 2 for MEDIUM, or 3 for HIGH. Defaults to 0.
                    """
                    selection = None
                    if level == 0:
                        selection = "NONE"
                    elif level == 1:
                        selection = "LOW"
                    elif level == 2:
                        selection == "MEDium"
                    elif level == 3:
                        selection == "HIGH"
                    else:
                        selection = "NONE"

                    val = self.__instr_obj.write(f"CALCulate:APOWer:SMOothing {selection}")

                @property
                def points(self)->int:
                    """The number of measurement points to include in the running average. 

                    Returns:
                        int: Number of points 0 to 32. 
                    """
                    val = int(self.__instr_obj.query(f"CALCulate:APOWer:SMOothing:POINts?"))
                    return val
                
                @level.setter
                def level(self, count:int=8):
                    """Specifies a number of measurement points to include in the running average.

                    Args:
                        count (int, optional): Number of points 0 to 32. Defaults to 8.
                    """
                    val = self.__instr_obj.write(f"CALCulate:APOWer:SMOothing:POINts {count}")

    class Common():
        def __init__(self, instrobj):
            self.__instr_obj = instrobj
        
        def cls(self):
            """Clear status.
            """
            val = self.__instr_obj.write(f"*CLS")

        @property
        def ese(self)->int:
            """Gets or sets the standard event status enable register.

            Returns:
                int: 0 to 255
            """
            val = int(self.__instr_obj.query(f"*ESE?"))
            return val
        
        @ese.setter
        def ese(self, parameter:int=255):
            val = self.__instr_obj.write(f"*ESE {parameter}")

        def esr(self)->int:
            """Queries the standard event status register. 

            Returns:
                int: 0 to 255.
            """
            val = int(self.__instr_obj.query(f"*ESR?"))
            return val
        
        def idn(self)->str:
            """Identification query.

            Returns:
                str: Inclusive of manufacturer, model, serial number, and firmware version. 
            """
            val = self.__instr_obj.query(f"*IDN?")
            return val
        
        def reset(self):
            """Reset command.
            """
            val = self.__instr_obj.write(f"*RST")

        def wait(self):
            """Reset command.
            """
            val = self.__instr_obj.write(f"*RST")

        @property
        def opc(self)->int:
            """Operation complete command. 

            Returns:
                int: 0 if not complete, 1 if complete. 
            """
            val = int(self.__instr_obj.query(f"*OPC?"))
            return val
        
        @opc.setter
        def opc(self):
            val = self.__instr_obj.write(f"*OPC")

        @property
        def sre(self)->int:
            """Service request enable command. 

            Returns:
                int: Values 0 to 255 to indicate different service request events. 
            """
            val = int(self.__instr_obj.query(f"*SRE?"))
            return val

        @sre.setter
        def sre(self, value:int=0):
            """Service request enable commmand.

            Args:
                value (int, optional): Values 0 to 255 to indicate different service request events.. Defaults to 0.
            """
            val = self.__instr_obj.write(f"*SRE {value}")

        def status_byte(self)->int:
            """Read the status byte.

            Returns:
                int: Values 0 to 255. 
            """
            val = int(self.__instr_obj.query(f"*STB?"))
            return val
        
        def trigger(self):
            """Initiate a trigger event.
            """
            val = self.__instr_obj.write(f"*TRG")

        def self_test(self)->int:
            """Self test query.

            Returns:
                int: Values -32767 to 32767.
            """
            val = int(self.__instr_obj.query(f"*TST?"))
            return val

    class Format():
        def __init__(self, instrobj):
            self.__instr_obj = instrobj
        
        def byte_order(self)->int:
            """Gets the byte order for binary data.

            Returns:
                int: TBD
            """
            val = int(self.__instr_obj.query(f"FORMat:BORDer?"))
            return val
        
        def data(self)->int:
            """Gets the format of the TRACe data.

            Returns:
                int: TBD
            """
            val = int(self.__instr_obj.query(f"FORMat:DATA?"))
            return val
        
        def status_registers(self)->int:
            """Gets the format of the status registers.

            Returns:
                int: TBD
            """
            val = int(self.__instr_obj.query(f"FORMat:SREGister?"))
            return val

    class Unit():
        def __init__(self, instrobj):
            self.__instr_obj = instrobj
        
        def power(self)->str:
            """Gest the power amplitude unit. 

            Returns:
                str: W
            """
            val = int(self.__instr_obj.query(f"UNIT:POWer?"))
            return val
    
        def frequency(self)->str:
            """Gest the frequency unit. 

            Returns:
                str: MHz
            """
            val = int(self.__instr_obj.query(f"UNIT:FREQ?"))
            return val
    
        def time(self)->str:
            """Gest the time unit. 

            Returns:
                str: SEC
            """
            val = int(self.__instr_obj.query(f"UNIT:TIME?"))
            return val
        
        def temperature(self)->str:
            """Gest the temperature unit. 

            Returns:
                str: C
            """
            val = int(self.__instr_obj.query(f"UNIT:TEMP?"))
            return val

    class Measure():
        def __init__(self, instrobj):
            self.__instr_obj = instrobj
            #self.zero   = self.Zero(self.__instr_obj)
        
        @property
        def configure(self):
            """Get or set the measurement configuration.

            Returns:
                _type_: Forward and reflected power, frequency, temperature, VSWR, return loss, burst or peak power, and statistical.
            """
            value = float(self.__instr_obj.query("CONFigure?"))
            return value
        
        @configure.setter
        def configure(self, mode=0):
            """Get or set the measurement configuration.

            Args:
                mode (int, optional): 0 for FORward power, 1 for REFlected power, 2 for FREQuency, 3 for TEMPerature, 4 for VSWR, 5 for return loss, 6 for burst, 7 for peak power, and 8 for statistical.. Defaults to 0.
            """
            if mode == 1:
                md = "REFLected"
            elif mode == 2:
                md = "FREQuency"
            elif mode == 3:
                md = "TEMPerature"
            elif mode == 4:
                md = "VSWR"
            elif mode == 5:
                md = "RLOSs"
            elif mode == 6:
                md = "BURSt"
            elif mode == 7:
                md = "PEAK"
            elif mode == 8:
                md = "STATistical"
            elif mode == 0:
                md = "FORWard"
            else:
                md = "FORWard"

            val = self.__instr_obj.write(f"CONFigure {md}")
        
        def fetch(self)->float:
            """Retrieve a measurement. 

            Returns:
                float: The measurement the sensor is configured for. Note that a measurement must be triggered before the data can be retrieved.  
            """
            value = float(self.__instr_obj.query("FETCh?"))
            return value

        def measure(self)->float:
            """Configure, intiate, and retrieve a measurement. 

            Returns:
                float: The measurement the sensor is configured for. 
            """
            value = float(self.__instr_obj.query("MEASure?"))
            return value
        
        def read(self)->float:
            """Initiate and retrieve a measurement. 

            Returns:
                float: The measurement the sensor is configured for. 
            """
            value = float(self.__instr_obj.query("READ?"))
            return value
        
        def forward(self)->float:
            """Initiate and retrieve a forward average power measurement. 

            Returns:
                float: The forward power measurement in watts. 
            """
            value = float(self.__instr_obj.query("FORWard?"))
            return value
        
        def reflected(self)->float:
            """Initiate and retrieve a reflected average power measurement. 

            Returns:
                float: The reflected power measurement in watts. 
            """
            value = float(self.__instr_obj.query("REFLected?"))
            return value
        
        def frequency(self)->float:
            """Initiate and retrieve a frequency measurement. 

            Returns:
                float: The frequency in MHz. 
            """
            value = float(self.__instr_obj.query("FREQ?"))
            return value
        
        def temperature(self)->float:
            """Initiate and retrieve a temperature measurement. 

            Returns:
                float: The temperature in degrees C. 
            """
            value = float(self.__instr_obj.query("TEMP?"))
            return value
        
        def vswr(self)->float:
            """Initiate and retrieve a VSWR measurement. 

            Returns:
                float: The VSWR value. 
            """
            value = float(self.__instr_obj.query("VSWR?"))
            return value
        
        def return_loss(self)->float:
            """Initiate and retrieve a return loss measurement. 

            Returns:
                float: The return loss in dB. 
            """
            value = float(self.__instr_obj.query("RLOSs?"))
            return value
        
        def burst(self)->float:
            """Initiate and retrieve a burst power measurement. 

            Returns:
                float: Burst power in watts. 
            """
            value = float(self.__instr_obj.query("BURSt?"))
            return value
        
        def peak(self)->float:
            """Initiate and retrieve a peak power measurement. 

            Returns:
                float: Peak power in watts. 
            """
            value = float(self.__instr_obj.query("PEAK?"))
            return value
        
        def statistical(self)->list[float]:
            """Initiate and retrieve a list of CCDF distribution values.

            Returns:
                list[float]: A numeric list representative of the CCDF distribution values. 
            """
            ccdf_list = float(self.__instr_obj.query("STAT?")).split(',')
            return ccdf_list

    class Pnp():
        def __init__(self, instrobj):
            self.__instr_obj = instrobj
            #self.zero   = self.Zero(self.__instr_obj)
            self.file     = self.File(self.__instr_obj)

        def available(self):
            value = float(self.__instr_obj.query("PNP:AVAilable?"))
            return value
        
        def version(self):
            value = float(self.__instr_obj.query("PNP:VERSion?"))
            return value
        
        def itranser(self):
            value = float(self.__instr_obj.write("PNP:ITRAnsfer"))
            return value

        class File():
            def __init__(self, instrobj):
                self.__instr_obj = instrobj

                self.block     = self.Block(self.__instr_obj)

            def get_size(self):
                value = float(self.__instr_obj.query("PNP:FILE:SIZE?"))
                return value
        
            class Block():
                def __init__(self, instrobj):
                    self.__instr_obj = instrobj

                def total(self):
                    value = float(self.__instr_obj.query("PNP:BLOCk:TOTal?"))
                    return value
                
                def data(self):
                    value = float(self.__instr_obj.query("PNP:BLOCk:DATA?"))
                    return value
                
                @property
                def number(self):
                    value = float(self.__instr_obj.query("PNP:FILE:BLOCk:NUMBer?"))
                    return value
                
                @number.setter
                def number(self, count=500):
                    val = self.__instr_obj.write(f"PNP:FILE:BLOCk:NUMBer {count}")
        
    class Sense():
        def __init__(self, instrobj):
            self.__instr_obj = instrobj
            
            self.correction     = self.Correction(self.__instr_obj)
            self.statistical    = self.Statistical(self.__instr_obj)
            self.time           = self.Time(self.__instr_obj)

        @property
        def frequency(self):
            value = float(self.__instr_obj.query("SENS:FREQ?"))
            return value
        
        @frequency.setter
        def frequency(self, freq_megahz=500):
            """Specifies the frequency set point.

            Args:
                freq_megahz (int, optional): Frequency in megaherz. Defaults to 500.
            """
            val = f"SENS:FREQ {freq_megahz}"
            val = self.__instr_obj.write(f"SENS:FREQ {freq_megahz}")
            print(val)

        @property
        def dutycycle(self)->float:
            value = float(self.__instr_obj.query("SENS:DUTY?"))
            return value
        
        @dutycycle.setter
        def dutycycle(self, percentage=50):
            """Sets or gets the duty cycle of the waveform. 

            Args:
                percentage (int, optional): 0 to 100. Defaults to 50.
            """
            val = f"SENS:DUTY {percentage}"
            val = self.__instr_obj.write(f"SENS:DUTY {percentage}")
            print(val)

        @property
        def auto_duty(self)->int:
            value = int(self.__instr_obj.query("SENS:AUTO:DUTY?"))
            return value
        
        @auto_duty.setter
        def auto_duty(self, enable=1):
            """Controls whether the duty cycle is estimated by the sensor or not.

            Args:
                enable (int, optional): 0 to disable and 1 to enable. Defaults to 1.
            """
            val = self.__instr_obj.write(f"SENS:AUTODUTY {enable}")
            # print(val)

        class Correction():
            def __init__(self, instrobj):
                self.__instr_obj = instrobj
            
            @property
            def auto(self):
                value = self.__instr_obj.query(f"SENSe:CORRection:AUTO?")
                return value

            @auto.setter
            def auto(self, state):
                val = self.__instr_obj.write(f"SENSe:CORRection:AUTO {state}")
                print(val)

        class Statistical():
            def __init__(self, instrobj):
                self.__instr_obj = instrobj

            @property
            def enable(self):
                value = self.__instr_obj.query(f"SENSe:STATistical:ENABle?")
                return value

            @enable.setter
            def enable(self, state):
                val = self.__instr_obj.write(f"SENSe:STATistical:ENABle {state}")
                print(val)

            @property
            def windowing(self):
                value = self.__instr_obj.query(f"SENSe:STATistical:WINDowing?")
                return value

            @windowing.setter
            def windowing(self, state):
                val = self.__instr_obj.write(f"SENSe:STATistical:WINDowing {state}")
                print(val)
            
            @property
            def samples(self):
                value = self.__instr_obj.query(f"SENSe:STATistical:SAMPles?")
                return value

            @samples.setter
            def samples(self, count):
                val = self.__instr_obj.write(f"SENSe:STATistical:SAMPles {count}")
                print(val)

            @property
            def confidence(self):
                value = self.__instr_obj.query(f"SENSe:STATistical:CONFidence?")
                return value

            @confidence.setter
            def confidence(self, count):
                val = self.__instr_obj.write(f"SENSe:STATistical:CONFidence {count}")
                print(val)

            @property
            def etolerance(self):
                value = self.__instr_obj.query(f"SENSe:STATistical:ETOL?")
                return value

            @etolerance.setter
            def etolerance(self, count):
                val = self.__instr_obj.write(f"SENSe:STATistical:ETOL {count}")
                print(val)

            @property
            def duration(self):
                value = self.__instr_obj.query(f"SENSe:STATistical:DUR?")
                return value

            @duration.setter
            def duration(self, count):
                val = self.__instr_obj.write(f"SENSe:STATistical:DUR {count}")
                print(val)

            @property
            def rmode(self):
                value = self.__instr_obj.query(f"SENSe:STATistical:RMOD?")
                return value

            @rmode.setter
            def rmode(self, count):
                val = self.__instr_obj.write(f"SENSe:STATistical:RMOD {count}")
                print(val)

            @property
            def range(self):
                value = self.__instr_obj.query(f"SENSe:STATistical:RANG?")
                return value

            @range.setter
            def range(self, count):
                val = self.__instr_obj.write(f"SENSe:STATistical:RANG {count}")
                print(val)

        class Time():
            """
            For controlling the state and properties of the time domain mode. 
            """
            def __init__(self, instrobj):
                self.__instr_obj = instrobj
            
            @property
            def enable(self)->int:
                """Used to enable and change the attributes that control the time domain mode functionality. 

                Returns:
                    int: 0 for disabled and 1 for enabled
                """
                value = self.__instr_obj.query(f"SENSe:TIME:ENABle?")
                return value

            @enable.setter
            def enable(self, state:int=0):
                """Used to enable and change the attributes that control the time domain mode functionality.

                Args:
                    state (int, optional): 0 for disabled and 1 for enabled. Defaults to 0.
                """
                val = self.__instr_obj.write(f"SENSe:TIME:ENABle {state}")
                print(val)

            @property
            def windowing(self):
                value = self.__instr_obj.query(f"SENSe:TIME:WIND?")
                return value

            @windowing.setter
            def windowing(self, count):
                val = self.__instr_obj.write(f"SENSe:TIME:WIND {count}")
                print(val)
            
            @property
            def base(self):
                value = self.__instr_obj.query(f"SENSe:TIME:BASE?")
                return value

            @base.setter
            def base(self, count):
                val = self.__instr_obj.write(f"SENSe:TIME:BASE {count}")
                print(val)

    class Status():
        def __init__(self, instrobj):
            self.__instr_obj = instrobj
            
            self.operation      = self.Operation(self.__instr_obj)
            self.questionable   = self.Questionable(self.__instr_obj)
            self.measurement    = self.Measurement(self.__instr_obj)

        def preset(self):
            """Restore status to the factory presets. 
            """
            val = self.__instr_obj.write(f"STAT:PRESet")

        class Operation():
            def __init__(self, instrobj):
                self.__instr_obj = instrobj
            
            def event(self)->int:
                """Read the OPER event register bits

                Returns:
                    int: _description_
                """
                value = int(self.__instr_obj.query(f"STAT:OPER:EVENt?"))
                return value
            
            @property
            def enable(self)->int:
                """Reads or writes the OPER enable register bits. 

                Returns:
                    int: 0 to 32767.
                """
                value = int(self.__instr_obj.query(f"STAT:OPER:ENABle?"))
                return value
            
            @enable.setter
            def enable(self, value:int=0):
                val = self.__instr_obj.write(f"STAT:OPER:ENABle {value}")

            def condition(self)->int:
                """Read teh OPER condition register bits.

                Returns:
                    int: 0 to 32767.
                """
                value = int(self.__instr_obj.query(f"STAT:OPER:CONDition?"))
                return value
        
            @property
            def negative_transition(self):
                """Gets or sets the negative transition filter."""
                value = int(self.__instr_obj.query(f"STAT:OPER:NTR?"))
                return value
            
            @negative_transition.setter
            def negative_transition(self, value=0):
                val = self.__instr_obj.write(f"STAT:OPER:NTR {value}")

            @property
            def positive_transition(self):
                """Gets or sets the positive transition filter."""
                value = int(self.__instr_obj.query(f"STAT:OPER:PTR?"))
                return value
            
            @positive_transition.setter
            def positive_transition(self, value=0):
                val = self.__instr_obj.write(f"STAT:OPER:PTR {value}")

        class Questionable():
            def __init__(self, instrobj):
                self.__instr_obj = instrobj

            def event(self)->int:
                """Read the QUEStionable condition register bits.

                Returns:
                    int: 0 to 32767.
                """
                value = int(self.__instr_obj.query(f"STAT:QUES:EVENt?"))
                return value
        
            @property
            def enable(self)->int:
                """Reads or writes the QUES enable register bits. 

                Returns:
                    int: 0 to 32767.
                """
                value = int(self.__instr_obj.query(f"STAT:QUES:ENABle?"))
                return value
            
            @enable.setter
            def enable(self, value:int=0):
                val = self.__instr_obj.write(f"STAT:QUES:ENABle {value}")

            def condition(self)->int:
                """Read the MEAS condition register bits.

                Returns:
                    int: 0 to 32767.
                """
                value = int(self.__instr_obj.query(f"STAT:QUES:CONDition?"))
                return value
            
            @property
            def negative_transition(self):
                """Gets or sets the negative transition filter."""
                value = int(self.__instr_obj.query(f"STAT:QUES:NTR?"))
                return value
            
            @negative_transition.setter
            def negative_transition(self, value=0):
                val = self.__instr_obj.write(f"STAT:QUES:NTR {value}")

            @property
            def positive_transition(self):
                """Gets or sets the positive transition filter."""
                value = int(self.__instr_obj.query(f"STAT:QUES:PTR?"))
                return value
            
            @positive_transition.setter
            def positive_transition(self, value=0):
                val = self.__instr_obj.write(f"STAT:QUES:PTR {value}")

        class Measurement():
            def __init__(self, instrobj):
                self.__instr_obj = instrobj

            def event(self)->int:
                """Read the MEASurement condition register bits.

                Returns:
                    int: 0 to 32767.
                """
                value = int(self.__instr_obj.query(f"STAT:MEAS:EVENt?"))
                return value
        
            @property
            def enable(self)->int:
                """Reads or writes the MEAS enable register bits. 

                Returns:
                    int: 0 to 32767.
                """
                value = int(self.__instr_obj.query(f"STAT:MEAS:ENABle?"))
                return value
            
            @enable.setter
            def enable(self, value:int=0):
                val = self.__instr_obj.write(f"STAT:MEAS:ENABle {value}")

            def condition(self)->int:
                """Read the MEAS condition register bits.

                Returns:
                    int: 0 to 32767.
                """
                value = int(self.__instr_obj.query(f"STAT:MEAS:CONDition?"))
                return value
            
            @property
            def negative_transition(self):
                """Gets or sets the negative transition filter."""
                value = int(self.__instr_obj.query(f"STAT:MEAS:NTR?"))
                return value
            
            @negative_transition.setter
            def negative_transition(self, value=0):
                val = self.__instr_obj.write(f"STAT:MEAS:NTR {value}")

            @property
            def positive_transition(self):
                """Gets or sets the positive transition filter."""
                value = int(self.__instr_obj.query(f"STAT:MEAS:PTR?"))
                return value
            
            @positive_transition.setter
            def positive_transition(self, value=0):
                val = self.__instr_obj.write(f"STAT:MEAS:PTR {value}")

    class System():
        def __init__(self, instrobj):
            self.__instr_obj = instrobj

            self.identity   = self.Identity(self.__instr_obj)
            self.error      = self.Error(self.__instr_obj)

        def version(self)->str:
            """Returns the SCPI version.

            Returns:
                str: The SCPI version. 
            """
            value = self.__instr_obj.query(f"SYSTem:VERSion?")
            return value
        
        def capability(self)->str:
            """Returns the device capability.

            Returns:
                str: The device capability. 
            """
            value = self.__instr_obj.query(f"SYSTem:CAPability?")
            return value
        
        def timestamp(self)->str:
            """Returns the latest timestamp from the device.

            Returns:
                str: The latest timestamp from the device. 
            """
            value = self.__instr_obj.query(f"SYSTem:TIMEstamp?")
            return value
        
        def preset(self):
            """Restores factory settings without clearing status or errors. 
            """
            value = self.__instr_obj.write(f"SYSTem:PRESet")
            return value
        
        class Error():
            def __init__(self, instrobj):
                self.__instr_obj = instrobj

            def count(self)->int:
                """Get the number of errors in the error queue.

                Returns:
                    int: Number of errors. 
                """
                value = int(self.__instr_obj.query(f"SYSTem:ERRor:COUNt?"))
                return value
            
            def next(self)->str:
                """Get the next error from the error queue.

                Returns:
                    str: Number of errors. 
                """
                value = self.__instr_obj.query(f"SYSTem:ERRor:NEXT?")
                return value
            
        class Identity():
            def __init__(self, instrobj):
                self.__instr_obj = instrobj

            def model(self)->str:
                """Get the device model name. 

                Returns:
                    str: The device model name.
                """
                value = self.__instr_obj.query(f"SYSTem:IDENtity:MODel?")
                return value

            def serial_number(self)->str:
                """Get the device serial number. 

                Returns:
                    str: The device serial number.
                """
                value = self.__instr_obj.query(f"SYSTem:IDENtity:SN?")
                return value
            
            def manufacture_date(self)->str:
                """Get the device manufacture date. 

                Returns:
                    str: The device manufacture date.
                """
                value = self.__instr_obj.query(f"SYSTem:IDENtity:MFGDate?")
                return value
            
            def calibration_date(self)->str:
                """Get the device calibration date. 

                Returns:
                    str: The device calibration date.
                """
                value = self.__instr_obj.query(f"SYSTem:IDENtity:CALDate?")
                return value
            
            def hardware_revision(self)->str:
                """Get the device hardware revision. 

                Returns:
                    str: The device hardware revision.
                """
                value = self.__instr_obj.query(f"SYSTem:IDENtity:HWRev?")
                return value
            
            def firmware_revision(self)->str:
                """Get the device firmware revision. 

                Returns:
                    str: The device firmware revision.
                """
                value = self.__instr_obj.query(f"SYSTem:IDENtity:FWRev?")
                return value
            
    class Trace():
        def __init__(self, instrobj):
            self.__instr_obj = instrobj

            self.data = self.Data(self.__instr_obj)

        class Data():
            def __init__(self, instrobj):
                self.__instr_obj = instrobj
            
            def average_power(self):
                value = self.__instr_obj.query(f"TRACe:APOWer:DATA?")
                return value
            
            def statistical(self):
                value = self.__instr_obj.query(f"TRACe:STATistical:DATA?")
                return value
            
            def time(self):
                value = self.__instr_obj.query(f"TRACe:TIME:DATA?")
                return value

    class Trigger():
        def __init__(self, instrobj):
            self.__instr_obj = instrobj

            self.initiate = self.Initiate(self.__instr_obj)
            self.level = self.Level(self.__instr_obj)
            self.external = self.External(self.__instr_obj)

        def abort(self):
            """Place triggering into the IDLE state.
            """
            val = self.__instr_obj.write(f"TRIG:ABORt")
        
        class External():
            def __init__(self, instrobj):
                self.__instr_obj = instrobj

            @property
            def polarity(self)->int:
                """Defines the polarity of the external trigger

                Returns:
                    int: 1 for input and 0 for output
                """
                val = self.__instr_obj.query(f"TRIG:EXT:POL?")
            
            @polarity.setter
            def polarity(self, state:int=1):
                """Defines the polarity of the external trigger

                Args:
                    state (int, optional): 1 for input and 0 for output. Defaults to 1.
                """
                val = self.__instr_obj.query(f"TRIG:EXT:POL {state}")

        class Initiate():
            def __init__(self, instrobj):
                self.__instr_obj = instrobj

            @property
            def continuous(self)->bool:
                """Enables/disables continuous trigger mode.

                Returns:
                    bool: 0 for OFF, 1 for ON
                """
                val = self.__instr_obj.query(f"TRIG:INIT:CONT?")
                return bool(val)

            @continuous.setter
            def continuous(self, state:bool=0):
                """Enables/disables continuous trigger mode.

                Args:
                    state (bool, optional): 0 for OFF, 1 for ON. Defaults to 0.
                """
                val = self.__instr_obj.write(f"TRIG:INIT:CONT {state}")

            def immediate(self):
                """Causes triggering to exit the IDLE state.
                """
                val = self.__instr_obj.write(f"TRIG:INIT:IMM")
            
        class Level():
            def __init__(self, instrobj):
                self.__instr_obj = instrobj

            @property
            def level(self)->float:
                """Specifies an internal trigger level. 

                Returns:
                    float: The level at which the sensor will trigger a measurement. 
                """
                val = self.__instr_obj.query(f"TRIG:LEV?")
                return float(val)
            
            @level.setter
            def level(self, level:float=0.5):
                """Specifies an internal trigger level. 

                Args:
                    level (float, optional): Defaults to 0.5.
                """
                val = self.__instr_obj.query(f"TRIG:LEV {level}")

            @property
            def auto(self)->bool:
                """Enable/disable auto level detection. 

                Returns:
                    bool: 0 for disabled, 1 for enabled. 
                """
                val = self.__instr_obj.query(f"TRIG:LEV:AUTO?")
                return bool(val)
            
            @auto.setter
            def auto(self, state:bool=0):
                """Enable/disable auto level detection.

                Args:
                    state (bool, optional): 1 for enabled and 0 for disabled. Defaults to 0.
                """
                val = self.__instr_obj.query(f"TRIG:LEV:AUTO {state}")
        
        @property
        def mode(self)->int:
            """Specifies the trigger mode. 

            Returns:
                int: 0 for Manual, 1 for Normal, 2 for Single, and 3 for Auto.
            """
            val = self.__instr_obj.query(f"TRIG:MODE?")
            return int(val)
        
        @mode.setter
        def mode(self, mode:int=1):
            """Specifies the trigger mode. 

            Args:
                mode (int, optional): 0 for Manual, 1 for Normal, 2 for Single, and 3 for Auto.. Defaults to 1.
            """
            if mode == 0:
                trg_mode = "MANual"
            elif mode == 2: 
                trg_mode = "SINGle"
            elif mode == 3:
                trg_mode = "AUTO"
            else:
                trg_mode = "NORMal"
            val = self.__instr_obj.query(f"TRIG:MODE {trg_mode}")

        @property
        def source(self)->int:
            """Selects the trigger source.

            Returns:
                int: 0 for External, 1 for Internal, 2 for Manual, and 3 for Immediate. 
            """
            val = self.__instr_obj.query(f"TRIG:SOURce?")
            return int(val)
        
        @source.setter
        def source(self, source:int=1):
            """Selects the trigger source. 

            Args:
                source (int, optional): 0 for External, 1 for Internal, 2 for Manual, and 3 for Immediate. Defaults to 1.
            """
            if source == 0:
                src = "EXTernal"
            elif source == 2: 
                src = "MANual"
            elif source == 3:
                src = "IMMediate"
            else:
                src = "INTernal"
            val = self.__instr_obj.write(f"TRIG:SOURce {src}")
       
        @property
        def hysteresis(self)->float:
            """Hysteresis (time) used with the trigger level.

            Returns:
                float: Time in seconds.
            """
            val = self.__instr_obj.query(f"TRIG:HYSTeresis?")
            return float(val)
        
        @hysteresis.setter
        def hysteresis(self, secs:float=0.0):
            """Hysteresis (time) used with the trigger level. 

            Args:
                secs (float, optional): From 0 to 500 seconds. Defaults to 0.0.
            """
            val = self.__instr_obj.write(f"TRIG:HYSTeresis {secs}")

        @property
        def holdoff(self)->float:
            """Gets the trigger holdoff delay.

            Returns:
                float: 0 to 500 s. 
            """
            val = self.__instr_obj.query(f"TRIG:HOLDoff?")
            return float(val)
        
        @holdoff.setter
        def holdoff(self, delay:float=0.0):
            """Sets the trigger holdoff delay.

            Args:
                delay (float, optional): 0 to 500 s. Defaults to 0.0.
            """
            val = self.__instr_obj.write(f"TRIG:HOLDoff {delay}")

        @property
        def delay(self)->float:
            """Gets the trigger delay.

            Returns:
                float: Delay time in seconds. 
            """
            val = self.__instr_obj.query(f"TRIG:DELay?")
            return float(val)
        
        @delay.setter
        def delay(self, delay:float=0):
            """Sets the trigger delay.

            Args:
                delay (float, optional): Delay time in seconds. Defaults to 0.
            """
            val = self.__instr_obj.write(f"TRIG:DELay {delay}")

        @property
        def slope(self)->int:
            """Gets the edge of the signal where the event occurs.

            Returns:
                int: 0 for Positive, 1 for Negative, or 2 for Either.
            """
            val = self.__instr_obj.query(f"TRIG:SLOPe?")
            return int(val)
        
        @slope.setter
        def slope(self, value:int=0):
            """Sets the edge of the signal where the event occurs.

            Args:
                value (int, optional): 0 for Positive, 1 for Negative, or 2 for Either. Defaults to 0.
            """
            if value == 0:
                setting = "POSitive"
            elif value == 1:
                setting = "NEGative"
            elif value == 2:
                setting = "EITHer"
            else:
                setting = "POSitive"
            val = self.__instr_obj.write(f"TRIG:SLOPe {setting}")

        @property
        def arm(self)->int:
            """Manually arms/disarms the trigger.

            Returns:
                int: 0 for disarmed, 1 for armed. 
            """
            val = self.__instr_obj.query(f"TRIG:ARM?")
            return int(val)
        
        @arm.setter
        def arm(self, state:int=0):
            """Manually arms/disarms the trigger.

            Args:
                state (int, optional): 0 for disarmed, 1 for armed. Defaults to disarmed.
            """
            val = self.__instr_obj.write(f"TRIG:ARM {state}")

    class Input():
        def __init__(self, instrobj):
            self.__instr_obj = instrobj

        @property
        def filter(self)->int:
            """Gets or sets the bandwidth filter. 

            Returns:
                float: 0 for disable, 1 for low (400 kHz), 2 for medium (5 MHz), or 3 for high (20 MHz).
            """
            val = self.__instr_obj.query(f"INPut:FILTer?")
            if val == 0.0:
                val = 0
            elif val == 0.4:
                val = 1
            elif val == 5.0:
                val = 2
            else:
                val = 3
            return int(val)

        @filter.setter
        def filter(self, value:float=0):
            """Gets or sets the bandwidth filter. 

            Args:
                value (float, optional): 0 for disable, 1 for low (400 kHz), 2 for medium (5 MHz), or 3 for high (20 MHz).. Defaults to 0.
            """
            val = self.__instr_obj.write(f"INPut:FILTer {value}")

    def set_mode(self, mode:str="average"):
        """Sets the mode of operation for the sensor.

        Args:
            mode (str, optional): "average" for average power mode, "statistical" for statistical mode, or "time_domain" for time domain mode. Defaults to "average".
        """
        if "average" in mode:
            self.write("SENS:TIME:ENAB 0")
            self.write("SENS:STAT:ENAB 0")
            self.write("STAT:MEAS:ENAB 15")
        elif "statistical":
            self.write("SENS:TIME:ENAB 0")
            self.write("SENS:STAT:ENAB 1")
            self.write("STAT:MEAS:ENAB 15")
        elif "time_domain":
            self.write("SENS:TIME:ENAB 1")
            self.write("SENS:STAT:ENAB 0")
            self.write("STAT:MEAS:ENAB 239")
    
    def get_mode(self)->int:
        """Queries the sensor for the mode of operation. 

        Returns:
            int: 0 for average power mode, 1 for statistical mode, or 2 for time domain mode. 
        """
        stats_enabled = self.query("SENS:STAT:ENAB?").rstrip()
        tdomain_enabled = self.query("SENS:TIME:ENAB?").rstrip()
        modeval = 0

        if (stats_enabled == 0) and (tdomain_enabled == 0):
            modeval = 0
        elif (stats_enabled == 1) and (tdomain_enabled == 0):
            modeval = 1
        elif (stats_enabled == 0) and (tdomain_enabled == 1):
            modeval = 2
        
        return modeval
    
    @property
    def auto_frequency_correct(self)->int:
        """Gets or sets the auto frequency correction mode. 

        Returns:
            int: 0 for disabled or 1 for enabled. 
        """
        return int(self.query("SENS:CORR:AUTO?").rstrip())	#0 or 1).rstrip()
    
    @auto_frequency_correct.setter
    def auto_frequency_correct(self, setval:int=1):
        """Gets or sets the auto frequency correction mode. 

        Args:
            setval (int, optional): 0 for disabled or 1 for enabled. Defaults to 1.
        """
        self.write(f"SENS:CORR:AUTO {setval}")

    @property
    def correction_frequency(self)->float:
        return float(self.query("SENS:FREQ?").rstrip())
    
    @correction_frequency.setter
    def correction_frequency(self, setval:float=450.0):
        self.write(f"SENS:FREQ {setval}")
    
    @property
    def auto_duty_cycle_correct(self)->int:
        return int(self.query("SENS:DUTY:AUTO?").rstrip())	#0 or 1).rstrip()

    @auto_duty_cycle_correct.setter
    def auto_duty_cycle_correct(self, setval:int=1):
        self.write(f"SENS:DUTY:AUTO {setval}")
    
    @property
    def correction_duty_cycle(self)->float:
        return float(self.query("SENS:DUTY?").rstrip())
    
    @correction_duty_cycle.setter
    def correction_duty_cycle(self, setval:float=50.0):
        self.write(f"SENS:DUTY {setval}")

    @property
    def average_power_smoothing(self)->str:
        smooth = self.query("CALC:APOW:SMO?").rstrip()
        sval = "none"
        if "LOW" in smooth:
            sval = "low"
        elif "MED" in smooth:
            sval = "medium"
        elif "HIGH" in smooth:
            sval = "high"
        return sval
    
    @average_power_smoothing.setter
    def average_power_smoothing(self, setval:str="none"):
        smooth = "NONE"
        if "none" in setval:
            smooth = setval.upper()
        elif "low" in setval:
            smooth = setval.upper()
        elif "med" in setval:
            smooth = "MED"
        elif "high" in setval:
            smooth = setval.upper()
        
        self.write(f"SENS:DUTY {smooth}")

    @property
    def filtering(self):
        print(1)
    
    @filtering.setter
    def filter(self, setval:str="none"):
        print(1)
        #To set the bandwidth/filtering....
        #"INP:FILT 0."	= NONE
        #"INP:FILT 0.0045."	= 4.5 kHz
        #"INP:FILT 0.5."	= 500 kHz
        #"INP:FILT 5."		= 5 MHz
        #"INP:FILT?."

