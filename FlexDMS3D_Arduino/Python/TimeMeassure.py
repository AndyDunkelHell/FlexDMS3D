import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os
from tqdm import tqdm
import sys

# Function to read data from the .txt file
def read_sensor_data(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    all_data_time = []
    for line in lines:
        parts = line.strip().split(',')
        try:
            row = [str(p) for p in parts]
            all_data_time.append(row)
        except:
            pass
        # If parse fails, skip
    time_data_array = np.array(all_data_time)
    return time_data_array
    
def parse_timestamp(ts):
    """
    Given a timestamp in the format "HH:MM:SS:ms",
    convert it to seconds as a float.
    """
    # Split the string by colon.
    h, m, s, ms = ts.split(':')
    # Compute total seconds
    total_seconds = int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    return total_seconds


# File path to the .txt file
file_path = "Test_Stay.txt"  # Replace with your actual file's path
    
# Read the electrode data
raw_time_data = read_sensor_data(file_path)

it_test = raw_time_data[:1341]

print(f"Iterative data shape: {it_test.shape}")
print(f"Iterative data: {it_test[:10]}")


# Apply the conversion to the first column of data:
t = np.array([parse_timestamp(ts) for ts in it_test[:, 0]])
print(f"time data: {t[:10]}")

# Convert the necessary columns from string to float.
for i in range(1, 8):
    it_test[:, i] = np.char.strip(it_test[:, i]).astype(float)

col4 = it_test[:, 3].astype(float)
lower_bound = 38.0
upper_bound = 58

# We keep only the rows where col4 is within [lower_bound, upper_bound].
mask = (col4 >= lower_bound) & (col4 <= upper_bound)
# Apply the mask to filter the data and the time vector:
filtered_data = it_test[mask]
filtered_t = t[mask]
print(f"filtered data: {filtered_t[:][:10]}")


# Convert column 4 values of the filtered data to float for plotting.
if filtered_data.size > 0:
    plt.figure()
    plt.plot(filtered_t, filtered_data[:, 3].astype(float))
    plt.xlim([filtered_t[0], filtered_t[-1]])
    plt.ylim(lower_bound, upper_bound)
    plt.xlabel("Time (s)")
    plt.ylabel("Resistance Value")
    plt.title("Resistance value in time frame")
    plt.show()
else:
    print("No rows remain after filtering.")

# Define the threshold value
threshold = 46.7

# Find indices where the value crosses the threshold
above_threshold_indices = np.where(filtered_data[:, 3].astype(float) > threshold)[0]


# Ensure there are crossings
if above_threshold_indices.size > 0:
    # Measure the time it takes for the value to go above and below the threshold
    start_time = filtered_t[above_threshold_indices[0]]
    end_time = filtered_t[above_threshold_indices[-1]]
    duration = end_time - start_time
    print(f"Time duration above threshold: {duration} seconds")

    # Calculate the standard deviation of the values in this time frame
    values_in_time_frame = filtered_data[above_threshold_indices[0]:above_threshold_indices[-1], 3].astype(float)
    std_deviation = np.std(values_in_time_frame)
    print(f"Standard deviation of values in time frame: {std_deviation}")

    # Plot the values in the time frame
    plt.figure()
    plt.plot(filtered_t[above_threshold_indices[0]:above_threshold_indices[-1]], values_in_time_frame)
    plt.xlim([start_time, end_time])
    plt.ylim(lower_bound, upper_bound)
    plt.xlabel("Time (s)")
    plt.ylabel("Resistance Value")
    plt.title("Values in Time Frame Above Threshold")
    plt.show()
else:
    print("No crossings above and below the threshold found.")