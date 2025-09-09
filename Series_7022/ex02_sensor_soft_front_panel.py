import pyvisa
import tkinter as tk
from tkinter import ttk
import threading
import time
import math

class PowerSensorUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Bird 7022 Power Sensor")
        self.master.geometry("600x250")

        # VISA setup
        self.rm = pyvisa.ResourceManager()
        try:
            resources = self.rm.list_resources()
            # Filter for USB devices only
            self.usb_resources = [r for r in resources if r.startswith("USB")]
        except Exception as e:
            self.usb_resources = []
            print("Could not enumerate VISA resources:", e)

        self.inst = None
        self.running = False

        # --- UI Layout ---
        # Resource selector
        ttk.Label(master, text="Select USB Resource:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.resource_var = tk.StringVar()
        self.resource_combo = ttk.Combobox(master, textvariable=self.resource_var, values=self.usb_resources, width=50)
        self.resource_combo.grid(row=0, column=1, padx=5, pady=5)
        if self.usb_resources:
            self.resource_combo.current(0)  # select first by default

        # Start/Stop button
        self.start_button = ttk.Button(master, text="Start", command=self.toggle_measurements)
        self.start_button.grid(row=0, column=2, padx=5, pady=5)

        # Measurement display
        self.forward_var = tk.StringVar(value="--")
        self.reflected_var = tk.StringVar(value="--")
        self.vswr_var = tk.StringVar(value="--")
        self.rl_var = tk.StringVar(value="--")
        self.freq_var = tk.StringVar(value="--")
        self.temp_var = tk.StringVar(value="--")

        ttk.Label(master, text="Forward Power (W):").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        ttk.Label(master, textvariable=self.forward_var, font=("Arial", 14)).grid(row=1, column=1, sticky="w")

        ttk.Label(master, text="Reflected Power (W):").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        ttk.Label(master, textvariable=self.reflected_var, font=("Arial", 14)).grid(row=2, column=1, sticky="w")

        ttk.Label(master, text="VSWR:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        ttk.Label(master, textvariable=self.vswr_var, font=("Arial", 14)).grid(row=3, column=1, sticky="w")

        ttk.Label(master, text="Return Loss (dB):").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        ttk.Label(master, textvariable=self.rl_var, font=("Arial", 14)).grid(row=4, column=1, sticky="w")

        ttk.Label(master, text="Frequency (MHz):").grid(row=5, column=0, sticky="e", padx=5, pady=5)
        ttk.Label(master, textvariable=self.freq_var, font=("Arial", 14)).grid(row=5, column=1, sticky="w")

        ttk.Label(master, text="Temp (\u00B0C):").grid(row=6, column=0, sticky="e", padx=5, pady=5)
        ttk.Label(master, textvariable=self.temp_var, font=("Arial", 14)).grid(row=6, column=1, sticky="w")

        master.protocol("WM_DELETE_WINDOW", self.on_close)

    def toggle_measurements(self):
        """Toggle between starting and stopping measurement updates"""
        if not self.running:
            self.start_measurements()
        else:
            self.stop_measurements()

    def start_measurements(self):
        """Open resource and start update thread"""
        resource = self.resource_var.get()
        if not resource:
            print("No VISA resource selected.")
            return

        try:
            self.inst = self.rm.open_resource(resource)
            self.inst.timeout = 5000

            # Get sensor ID for title bar
            sensor_id = self.query_sensor("*IDN?")
            if not sensor_id:
                sensor_id = "Bird 7022 Power Sensor"
            self.master.title(sensor_id[:64])
        except Exception as e:
            print("Failed to open resource:", e)
            return

        if not self.running:
            self.running = True
            self.start_button.config(text="Stop")
            self.update_thread = threading.Thread(target=self.update_readings, daemon=True)
            self.update_thread.start()

    def stop_measurements(self):
        """Stop update thread and close resource"""
        self.running = False
        if self.inst:
            try:
                self.inst.close()
            except Exception:
                pass
            self.inst = None
        self.start_button.config(text="Start")
        # self.master.title("Bird 7022 Power Sensor")

    def query_sensor(self, command):
        """Helper to query the instrument safely"""
        try:
            return self.inst.query(command).strip()
        except Exception:
            return None

    def calculate_vswr(self, fwd_pow:float, rfl_power:float)->float:
        # prevent inadvertent divide by zero scenarios....
        if fwd_pow == 0.0:
            fwd_pow = 0.001
        vswr = (1 + (rfl_power/fwd_pow)) / (1 - (rfl_power/fwd_pow))
        return vswr 

    # Function to convert VSWR to return loss
    def vswr_to_return_loss(self, VSWR:float) -> float:
        """Converts the VSWR value to return loss in dB.

        Args:
            VSWR (float): VSWR value. 

        Returns:
            float: Computed return loss in dB. If there is a problem with
            the math on the input value, the 9.99e+37 value will be returned
            to indicate the error condition.
        """
        try:
            VSWR = float(VSWR)
            if VSWR <= 1:
                return 9.999e+37
            return_Loss = -20 * math.log10((VSWR - 1)/(VSWR + 1))
            return return_Loss
        except:
            return 9.999e+37

    def sample_measurement_data(self, instobj:object):
        response = instobj.query_binary_values(":TRAC:APOW?", datatype='f', is_big_endian=True)
        dud = response[0]
        fwd = response[2]
        rfl = response[4]
        temp = response[6]
        freq = response[8]
        vswr = self.calculate_vswr(fwd_pow=fwd, rfl_power=rfl)
        rl = self.vswr_to_return_loss(vswr)
        return fwd, rfl, temp, freq, vswr, rl
    
    def update_readings(self):
        while self.running:
            if self.inst:
                # Replace with actual SCPI commands for the Bird 7022
                forward, reflected, temp, freq, vswr, rl = self.sample_measurement_data(self.inst)

                # Update UI, formatt the returned values to that they only have four or two decimal places max
                if forward: self.forward_var.set(f"{forward:.4f}")
                if reflected: self.reflected_var.set(f"{reflected:.4f}")
                if vswr: self.vswr_var.set(f"{vswr:.2f}")
                if rl:
                    if rl > 9999999:
                        self.rl_var.set(f"{rl:.3e}")
                    else:
                        self.rl_var.set(f"{rl:.2f}")
                if freq: self.freq_var.set(f"{freq:.2f}")
                if temp: self.temp_var.set(f"{temp:.2f}")

            time.sleep(0.5)  # Poll interval

    def on_close(self):
        self.stop_measurements()
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = PowerSensorUI(root)
    root.mainloop()
