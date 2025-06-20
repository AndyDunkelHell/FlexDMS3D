
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
    all_data = []
    all_data_time = []
    for line in lines:
        parts = line.strip().split(',')
        try:
            row = [float(p) for p in parts]
            all_data.append(row)
        except:
            row2 = [str(p) for p in parts]
            all_data_time.append(row2)
            # If parse fails, skip
            pass
    data_array = np.array(all_data)
    time_data_array = np.array(all_data_time)
    return data_array, time_data_array

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

def moving_average(signal, window_size=5):
    """Apply a simple moving average to each column.

    :param signal: 2D numpy array of shape (samples, channels)
    :param window_size: Number of samples for the moving average
    :return: 2D numpy array of smoothed outputs
    """
    smoothed = np.zeros_like(signal)
    for ch in range(signal.shape[1]):
        x = signal[:, ch]
        # Use 'same' mode so the output has the same length.
        smoothed[:, ch] = np.convolve(x, np.ones(window_size) / window_size, mode='same')
    return smoothed

           
# File path to the .txt file
file_path = "Test.txt"  # Replace with your actual file's path
    
# Read the electrode data
raw_data, raw_time_data = read_sensor_data(file_path)

print(f"Raw data shape: {raw_data.shape}")
print(f"Iterative data: {raw_data[:10]}")


it_test = raw_time_data
raw_data = raw_time_data 

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
    plt.title("Iterative movement between 110 and 180 degrees")
    plt.show()
else:
    print("No rows remain after filtering.")


def animate_data(data, t_data):

    filtered_data = data.astype(float)
    print(f"Filtered data shape: {filtered_data.shape}")
    print(f"Filtered data: {filtered_data[:10,2]}")
    filtered_data = filtered_data[:, [2]]
    #filtered_data = moving_average(filtered_data, window_size=5)
    lower_bound = 38.0
    upper_bound = 58

    # 3) Animate the data
    fig, ax = plt.subplots()
    print(filtered_data.shape)
    num_samples, num_ch = filtered_data.shape

    # We'll plot each channel on the same figure
    lines = []
    colors = plt.cm.viridis(np.linspace(0, 1, num_ch))
    for ch in range(num_ch):
        (line,) = ax.plot([], [], color=colors[ch], label=f"Channel {ch+1}")
        lines.append(line)

    # Fix X range from 0 to num_samples, Y range from -550 to 550
    ax.set_xlim(t_data[0], t_data[-1])
    ax.set_ylim(lower_bound, upper_bound)
    ax.set_xlabel("time (s)")
    ax.set_ylabel("Filtered Value")
    ax.legend()

    def init():
        for line in lines:
            line.set_data([], [])
        return lines

    def update(frame):
        # Frame is the index up to which we draw
        x_vals = t_data[:frame]
        for ch, line in enumerate(lines):
            y_vals = filtered_data[:frame, ch]
            line.set_data(x_vals, y_vals)
        return lines

    ani = animation.FuncAnimation(
        fig,
        update,
        frames=num_samples,
        init_func=init,
        blit=True,
        interval= 1  # Adjust animation speed if needed
    )

    

    plt.show()
            
    save_dir = os.path.join(os.path.dirname(sys.argv[0]), 'MyVideo3.mp4')
    print(f'Saving video to {save_dir}...')
    video_writer = animation.FFMpegWriter(fps=30, codec='libx264', bitrate=-1)
    update_func = lambda _i, _n: progress_bar.update(1)
    with tqdm(total=num_samples, desc='Saving video') as progress_bar:
        ani.save(save_dir, writer=video_writer, dpi=100, progress_callback=update_func)
        print('Video saved successfully.')

animate_data(filtered_data[:, 1:], filtered_t)

