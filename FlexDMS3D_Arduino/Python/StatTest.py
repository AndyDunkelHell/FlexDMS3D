import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

# Load your CSV file
df = pd.read_csv("...path_to_your_file.csv")

# Print first few rows to verify structure
print(df.head())

# List the columns to test. Adjust these to match your CSV’s column names.
columns = ["h", "Angle(rad)", "R"]

for col in columns:
    data = df[col].dropna()  # Remove any missing values
    
    # Plot histogram
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.hist(data, bins=20, edgecolor='black')
    plt.title(f"Histogram of {col}")
    plt.xlabel(col)
    plt.ylabel("Frequency")
    
    # Q-Q plot against a normal distribution
    plt.subplot(1, 2, 2)
    stats.probplot(data, dist="norm", plot=plt)
    plt.title(f"Q-Q Plot of {col}")
    
    plt.tight_layout()
    plt.show()

    # Perform the Shapiro-Wilk normality test
    stat, p = stats.shapiro(data)
    print(f"Shapiro-Wilk test for {col}: W = {stat:.3f}, p-value = {p:.3f}")
    if p > 0.05:
        print(f"→ {col} appears to be normally distributed (fail to reject H0).\n")
    else:
        print(f"→ {col} does not appear to be normally distributed (reject H0).\n")

# Divide the data into two groups (here, we simply split the dataframe in half)
mid_index = len(df) // 2
group1 = df.iloc[:mid_index]
group2 = df.iloc[mid_index:]

# Choose a column to test (for example, the "calculated_angle")
col_to_test = "R"
data1 = group1[col_to_test].dropna()
data2 = group2[col_to_test].dropna()

# a. Levene's test for equality of variances
levene_stat, levene_p = stats.levene(data1, data2)
print(f"Levene's test for equality of variances in {col_to_test}:")
print(f"Statistic = {levene_stat:.6f}, p-value = {levene_p:.3f}")
if levene_p > 0.05:
    print("→ Variances appear to be equal across the groups (homogeneous samples).\n")
else:
    print("→ Variances differ significantly across the groups (samples may come from different populations).\n")

# b. Kolmogorov-Smirnov test to compare the distributions of the two groups
ks_stat, ks_p = stats.ks_2samp(data1, data2)
print(f"Kolmogorov-Smirnov test for {col_to_test}:")
print(f"Statistic = {ks_stat:.6f}, p-value = {ks_p:.3f}")
if ks_p > 0.05:
    print("→ The two samples do not differ significantly (they likely come from the same distribution).\n")
else:
    print("→ The two samples differ significantly (they may come from different populations).\n")

