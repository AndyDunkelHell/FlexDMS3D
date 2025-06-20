import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import mean_squared_error
from scipy.signal import detrend
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error
from sklearn import preprocessing
# Replace these arrays with your actual data.
# Example dummy data:
df = pd.read_csv('...path_to_your_file.csv')

median_R = np.median(df['R'])
q1 = np.percentile(df['R'], 25)
q3 = np.percentile(df['R'], 75)
iqr = q3 - q1
df['R_norm'] = (df['R'] - median_R) / iqr
df['R_detrend'] = detrend(df['R_norm'], type='linear')
df['R_Diff'] = df['R'].diff()

# A simple rule: if R_Diff > 0, it's an 'up' sweep; if < 0, it's 'down'
df['Direction'] = np.where(df['R_Diff'] > 0, 'up', np.where(df['R_Diff'] < 0.005, 'down', np.nan))

# Drop rows with NaN values
df = df.dropna(subset=['Direction'])

# Now you can split the dataframe into two sets:
df_up = df[df['Direction'] == 'up']
df_down = df[df['Direction'] == 'down']
print("df_up")
print(df_up.head())
print("df_down")
print(df_down.head())   

# Convert your columns to NumPy arrays
R_up = df_up['R_detrend'].values
Angle_up = df_up['Angle(rad)'].values

# Fit a polynomial of degree=2 or 3 (experiment!)
degree = 3
coeffs_up = np.polyfit(R_up.flatten(), Angle_up, degree)
poly_up = np.poly1d(coeffs_up)

# Repeat for the down sweep
R_down = df_down['R_norm'].values
Angle_down = df_down['Angle(rad)'].values

coeffs_down = np.polyfit(R_down.flatten(), Angle_down, degree)
poly_down = np.poly1d(coeffs_down)

print("Up-sweep polynomial:", poly_up)
print("Down-sweep polynomial:", poly_down)

# 1) Plot Up Sweep
plt.figure()
plt.scatter(R_up, Angle_up, s=10, label="Up Sweep Data")
R_fit = np.linspace(min(R_up), max(R_up), 100)
plt.plot(R_fit, poly_up(R_fit), 'r-', label="Up Sweep Fit")
plt.xlabel("Resistance (Ohms)")
plt.ylabel("Angle (rad)")
plt.title("Up Sweep Fit")
plt.legend()
plt.show()

# 2) Plot Down Sweep
plt.figure()
plt.scatter(R_down, Angle_down, s=10, label="Down Sweep Data")
R_fit_down = np.linspace(min(R_down), max(R_down), 100)
plt.plot(R_fit_down, poly_down(R_fit_down), 'g-', label="Down Sweep Fit")
plt.xlabel("Resistance (Ohms)")
plt.ylabel("Angle (rad)")
plt.title("Down Sweep Fit")
plt.legend()
plt.show()

kf = KFold(n_splits=5, shuffle=True, random_state=42)

X_up = R_up.reshape(-1, 1)
y_up = Angle_up

mse_scores = []
for train_index, test_index in kf.split(X_up):
    R_train, R_test = X_up[train_index], X_up[test_index]
    A_train, A_test = y_up[train_index], y_up[test_index]
    
    # Fit polynomial
    coeffs = np.polyfit(R_train.flatten(), A_train, degree)
    poly_model = np.poly1d(coeffs)
    
    # Predict
    A_pred = poly_model(R_test.flatten())
    mse = mean_squared_error(A_test, A_pred)
    mse_scores.append(mse)

print("Up sweep average MSE:", np.mean(mse_scores))

X_down = R_down.reshape(-1, 1)
y_down = Angle_down

mse_scores = []
for train_index, test_index in kf.split(X_down):
    R_train, R_test = X_down[train_index], X_down[test_index]
    A_train, A_test = y_down[train_index], y_down[test_index]
    
    # Fit polynomial
    coeffs = np.polyfit(R_train.flatten(), A_train, degree)
    poly_model = np.poly1d(coeffs)
    
    # Predict
    A_pred = poly_model(R_test.flatten())
    mse = mean_squared_error(A_test, A_pred)
    mse_scores.append(mse)

print("Down sweep average MSE:", np.mean(mse_scores))

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
file_path = "Test4.txt"  # Replace with your actual file's path
    
# Read the electrode data
raw_time_data = read_sensor_data(file_path)

it_test = raw_time_data[:4900]

print(f"Iterative data shape: {it_test.shape}")
print(f"Iterative data: {it_test[:10]}")


# Apply the conversion to the first column of data:
t = np.array([parse_timestamp(ts) for ts in it_test[:, 0]])
print(f"time data: {t[:10]}")

# Convert the necessary columns from string to float.
for i in range(1, 8):
    it_test[:, i] = np.char.strip(it_test[:, i]).astype(float)

col4 = it_test[:, 3].astype(float)
lower_bound = 42.0
upper_bound = 52

# We keep only the rows where col4 is within [lower_bound, upper_bound].
mask = (col4 >= lower_bound) & (col4 <= upper_bound)
# Apply the mask to filter the data and the time vector:
filtered_data = it_test[mask]
filtered_t = t[mask]
print(f"filtered data: {filtered_data[:][:10]}")

df_test = pd.DataFrame(filtered_data[:, 3].astype(float), columns = ["R"])
median_R = np.median(df_test['R'])
q1 = np.percentile(df_test['R'], 25)
q3 = np.percentile(df_test['R'], 75)
iqr = q3 - q1
df_test['R_norm'] = (df_test['R'] - median_R) / iqr
df_test['R_detrend'] = detrend(df_test['R_norm'])
df_test['R_Diff'] = df_test['R'].diff()
# Compute the difference
df_test['R_Diff'] = df_test['R'].diff()

# Apply a rolling (moving average) filter to smooth the differences
# You can adjust the window size based on your data characteristics.
window_size = 50
df_test['R_Diff_smooth'] = df_test['R_Diff'].rolling(window=window_size, center=True).mean()

# Define a small threshold to ignore minor fluctuations
threshold = 0.05  # Adjust based on noise level

# Classify direction using the smoothed difference
df_test['Direction'] = np.where(df_test['R_Diff_smooth'] > threshold, 'up', 'down')

# Optionally, for points where the smoothed diff is NaN (e.g., at the boundaries),
# you can fill them using the original difference or simply set a default.
df_test['Direction'].bfill()
# Convert column 4 values of the filtered data to float for plotting.
if filtered_data.size > 0:
    plt.figure()
    plt.plot(filtered_t, (filtered_data[:, 3].astype(float)))
    plt.xlim([filtered_t[0], filtered_t[-1]])
    plt.xlabel("Time (s)")
    plt.ylabel("Resistance Value")
    plt.title("Resistance value in time frame")
    plt.show()
else:
    print("No rows remain after filtering.")

# Compute predictions from both models for each test sample
pred_up = poly_up(df_test['R_detrend'].values)
pred_down = poly_down(df_test['R_norm'].values)

# Initialize the final prediction array with default values based on the test direction
Angle_pred = np.zeros(len(df_test))
for i in range(len(df_test)):
    if df_test['Direction'].iloc[i] == 'up':
        Angle_pred[i] = pred_up[i]
    else:
        Angle_pred[i] = pred_down[i]

# Plot the angle predictions against time
plt.figure()
plt.plot(filtered_t[df_test.index], Angle_pred, 'r-', label="Prediction")
plt.xlabel("Time (s)")
plt.ylabel("Angle (rad)")
plt.title("Angle Predictions Over Time")
plt.legend()
plt.show()