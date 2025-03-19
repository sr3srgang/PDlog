import os
from time import sleep, time
from datetime import datetime
from labjack_flow import LabJackT7
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import traceback

# User parameters
LOG_DIR = "./logs/"
LOG_FILE = "voltage.log"
ERROR_FILE = "voltage_error.log"
INFLUX_URL = "http://yesnuffleupagus.colorado.edu:8086"
INFLUX_TOKEN = "yelabtoken"
INFLUX_ORG = "yelab"
INFLUX_BUCKET = "sr3"
MEASUREMENT = "PDLogger"
TAG = "Channel"
FIELD = "Volts"
LOG_INTERVAL = .01  # in seconds
PINS = ["AIN10", "AIN12"]  # First pin (AIN8) is the trigger, second pin (AIN6) is logged

def main():
    # Initialize LabJack device
    device = LabJackT7('192.168.1.92')

    # Ensure log directory exists
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    try:
        cycle = 0  # Keeps track of logging cycles
        while True:
            try:
                cycle += 1
                print(f"Cycle {cycle}: Checking trigger pin ({PINS[0]})...")

                # Read trigger pin
                trigger_value = device.read_flow(PINS[0])

                if trigger_value >= 4.9:  # If trigger is high, log data for 3 ms
                    print(f"Trigger HIGH: Logging data from {PINS[1]} for 3 ms...")
                    start_time = time()
                    while (time() - start_time) < 0.003:  # 3 ms logging window
                        voltage = device.read_flow(PINS[1])

                        # Log voltage data
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Millisecond precision
                        log_entry = f"{timestamp}, Pin: {PINS[1]}, Voltage: {voltage:.4f} V"
                        print(log_entry)

                        with open(os.path.join(LOG_DIR, LOG_FILE), "a") as f:
                            f.write(log_entry + "\n")

                        # Format data for InfluxDB
                        record = [
                            {
                                "measurement": MEASUREMENT,
                                "tags": {TAG: PINS[1]},
                                "fields": {FIELD: voltage},
                                "time": datetime.utcnow().isoformat()
                            }
                        ]

                        # Upload to InfluxDB
                        with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG) as client:
                            with client.write_api(write_options=SYNCHRONOUS) as writer:
                                writer.write(bucket=INFLUX_BUCKET, record=record)

                else:
                    print(f"Trigger LOW: Skipping logging for {PINS[1]}.")

            except Exception as e:
                # Log the error
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                error_message = f"{timestamp}, Error occurred: {str(e)}"
                with open(os.path.join(LOG_DIR, ERROR_FILE), "a") as f:
                    f.write(error_message + "\n")
                    f.write("".join(traceback.format_exception(None, e, e.__traceback__)) + "\n")

            # Wait until next interval
            sleep(LOG_INTERVAL)

    except KeyboardInterrupt:
        print("Logging stopped by user.")
    except Exception as e:
        # Catch and log any unexpected errors
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        critical_error = f"{timestamp}, Critical Error: {str(e)}"
        print(critical_error)
        with open(os.path.join(LOG_DIR, ERROR_FILE), "a") as f:
            f.write(critical_error + "\n")
            f.write("".join(traceback.format_exception(None, e, e.__traceback__)) + "\n")
    finally:
        print("Voltage logger terminated.")


if __name__ == "__main__":
    main()
