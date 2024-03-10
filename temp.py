import wmi

def get_cpu_temp():
    try:
        w = wmi.WMI(namespace=r"root\OpenHardwareMonitor")
        temperature_info = w.Sensor()
        for sensor in temperature_info:
            if sensor.SensorType == 'Temperature' and 'CPU' in sensor.Name:
                return sensor.Value
    except Exception as e:
        print("Error:", e)
    return None

if __name__ == "__main__":
    temperature = get_cpu_temp()
    if temperature is not None:
        print(f"CPU Temperature: {temperature} °C")
    else:
        print("Unable to retrieve CPU temperature.")


# import psutil
# input("Press Enter to exit...")
# import platform
# import ctypes

# def get_temp():
#     if platform.system() == "Windows":
#         # Load the kernel32 library
#         kernel32 = ctypes.windll.kernel32
#         # Create a buffer to store temperature info
#         buf = ctypes.create_string_buffer(128)
#         # Call the GetSystemFirmwareTable function to get the temperature
#         status = kernel32.GetSystemFirmwareTable(b"ACPI", 0, buf, ctypes.sizeof(buf))
#         # Parse the buffer to get the temperature
#         if status != 0:
#             temp_data = buf.raw
#             # Temperature data starts from byte offset 30, and it's 1 byte long
#             temperature = temp_data[30]
#             return temperature
#         else:
#             return None
#     else:
#         # For Linux or macOS, you can use psutil directly
#         return psutil.sensors_temperatures()['cpu_thermal'][0].current

# if __name__ == "__main__":
#     input("Press Enter to exit...")
#     temperature = get_temp()
#     if temperature is not None:
#         print(f"CPU Temperature: {temperature} °C")
#         input("Press Enter to exit...")
#     else:
#         print("Unable to retrieve CPU temperature.")
