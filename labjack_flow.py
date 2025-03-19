from labjack import ljm
import numpy as np

class LabJackT7:
    def __init__(self, ip_address):
        self.ip_address = ip_address

    def read_voltage(self, pin):
        #print(f"Attempting to read {pin} from LabJack...")

        handle = ljm.openS("T7", "ETHERNET", self.ip_address)
        #print("Successfully opened LabJack handle.")
        voltage = ljm.eReadName(handle, pin)
        print(f"volts for {pin}: {voltage:.4f}")
        ljm.close(handle)  # Ensure the handle is properly closed after use
        return voltage

    def read_flow(self, pin):
        #print(f"Calling read_voltage for {pin}...")
        volts = self.read_voltage(pin)  # Pass pin to read_voltage
        #print(f"Voltage read from {pin}: {volts:.4f}")
        
        
        flow = volts 
        
        
        
        return flow


# Example usage:
# out = LabJackT7("192.168.1.120").read_flow("AIN0")
# out = LabJackT7("192.168.1.120").read_flow("AIN2")



