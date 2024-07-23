import ctypes
import numpy as np
from picosdk.picohrdl import picohrdl as hrdl
from picosdk.functions import assert_pico2000_ok
import time

# Create chandle and status ready for use
chandle = ctypes.c_int16()
status = {}

# Open unit
status["openUnit"] = hrdl.HRDLOpenUnit()
assert_pico2000_ok(status["openUnit"])
chandle = status["openUnit"]

# Set mains noise rejection to reject 50 Hz mains noise
status["mainsRejection"] = hrdl.HRDLSetMains(chandle, 0)
assert_pico2000_ok(status["mainsRejection"])

# Set single reading parameters
range_ = hrdl.HRDL_VOLTAGERANGE["HRDL_39_MV"]
conversionTime = hrdl.HRDL_CONVERSIONTIME["HRDL_100MS"]
overflow = ctypes.c_int16(0)
value = ctypes.c_int32()

# Get the minimum and maximum ADC values for scaling
max_value = ctypes.c_int32()
min_value = ctypes.c_int32()
hrdl.HRDLGetMinMaxAdcCounts(chandle, ctypes.byref(min_value), ctypes.byref(max_value), 9)
print("Max ADC Value:", max_value.value)
print("Min ADC Value:", min_value.value)

# Calculate voltage from ADC value
raw_ADC_value = value.value
max_ADC_Value = max_value.value
Vmax = 39000  # microvolts
V = (raw_ADC_value / max_ADC_Value) * Vmax
print("Voltage:", V)

# Initialize data saving parameters
save_data = []
start_time = time.time()
count = 0

# Collect and save data in chunks of 300 samples
for i in range(6000):
    status["getSingleValue"] = hrdl.HRDLGetSingleValue(
        chandle, 9, range_, conversionTime, 0, ctypes.byref(overflow), ctypes.byref(value)
    )
    value_data = value.value
    V = (float(value_data) / float(max_ADC_Value)) * float(Vmax)
    
    if (i + 1) % 300 == 0:
        np.savetxt(f"fungi_data/{count}.txt", save_data, delimiter=',')
        print(f"Saved chunk {count} at sample {i+1}")
        count += 1
        save_data = []

    save_data.append(V)

# Print the elapsed time
print(f"--- {time.time() - start_time} seconds ---")
print("Final saved data:", save_data)

# Close unit
status["closeUnit"] = hrdl.HRDLCloseUnit(chandle)
assert_pico2000_ok(status["closeUnit"])

# Print final status
print("Status:", status)
