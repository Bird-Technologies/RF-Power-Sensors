from pywinusb import hid

#VENDOR_ID = 0x1422  # Vendor ID, the same for all Bird Sensors
#PRODUCT_ID = 0x5012  # Replace with your sensor's Product ID, if necessary 

# List all available HID devices
def list_devices():
    for device in hid.enumerate():
        print(f"Manufacturer: {device['manufacturer_string']}")
        print(f"Product: {device['product_string']}")
        print(f"Serial Number: {device['serial_number']}")
        print(f"Vendor ID: {device['vendor_id']:04X}, Product ID: {device['product_id']:04X}")
        print("-" * 40)

# Get and print device info
def device_info(VID, PID):
    device = hid.Device(VID, PID)
    print(f'Device manufacturer: {device.manufacturer}')
    print(f'Product: {device.product}')
    print(f'Serial Number: {device.serial}')

class Bird_Series_5000_Wideband_Power_Sensor():
    def __init__(self, sensor_model:str="5012D"):
        """Makes the connection to the USB sensor. 

        Args:
            sensor_model (str, optional): Required model number of the
            sensor to identify it. Options are "5012D", "5016D", "5017D", "5018D",
            or "5019D". Defaults to "5012D".
        """
        self._VENDOR_ID = 0x1422  # Vendor ID, the same for all Bird Sensors
        self._PRODUCT_ID = 0x5012

        self.device = None
        self.serial_number = None
        self.manufacturer = None
        self.firmware = None
        self.model = None

        if "5012" in sensor_model:
            self._PRODUCT_ID = 0x5012
            self.model = "5012D"
        elif "5016" in sensor_model:
            self._PRODUCT_ID = 0x5016
            self.model = "5016D"
        elif "5017" in sensor_model:
            self._PRODUCT_ID = 0x5017
            self.model = "5017D"
        elif "5018" in sensor_model:
            self._PRODUCT_ID = 0x5018
            self.model = "5018D"
        elif "5019" in sensor_model:
            self._PRODUCT_ID = 0x5019
            self.model = "5019D"

        # Connect to the sensor
        tmpdev = hid.HidDeviceFilter(vendor_id=self._VENDOR_ID, product_id=self._PRODUCT_ID)
        devices = tmpdev.get_devices()
        self.device = devices[0]
        self.serial_number = self.device.serial_number
        self.manufacturer = self.device.vendor_name
        #self.device = hid.Device(self._VENDOR_ID, self._PRODUCT_ID)

        # Assign device information

    def device_identification(self)->str:
        """Get device identification.

        Returns:
            str: Format BIRD,{model},{serial number},{firmware revision}.
        """
        id_string = f"{self.manufacturer},{self.model},{self.serial_number},fw_version_tbd"
        return id_string
    
## Main Program Start
    
my5017 = Bird_Series_5000_Wideband_Power_Sensor("5012D")
print(my5017.device_identification())


dev = hid.HidDevice()
device = hid.Device(VENDOR_ID, PRODUCT_ID)
print(f"Connected to {device.product} from {device.manufacturer}, Serial Number: {device.serial}")
#message = b'\x03' + b'\x50' + b'\xFF'*47
#device.write(message)
#print(f"Sent: {message}")
#response = device.read(48, 4000)
#print(f"Response: {response}")
hex_message = '0350ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
device.write(bytes.fromhex(hex_message))
hex_message = '02490d0affffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
device.write(bytes.fromhex(hex_message))
hex_message = '0353ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
device.write(bytes.fromhex(hex_message))
response = device.read(48, 2000)
cleaned_response = response[1:]
decoded_response = cleaned_response.decode('utf-8', errors='ignore')
model_number, software_date, runtime_version = decoded_response.split("\r\n")[0].split(',')
print(f"Model Number: {model_number}")
print(f"Software Date: {software_date}")
print(f"Runtime Version: {runtime_version}")

#message = b'\x02' + b'\x49' + b'\r\n' + b'\xFF'*44
#device.write(message)
#print(f"Sent: {message}")
#i = 5
#while i > 0:
#    response = device.read(48, 2000)
#    i = i-1 
#    print(f"Response: {response}")