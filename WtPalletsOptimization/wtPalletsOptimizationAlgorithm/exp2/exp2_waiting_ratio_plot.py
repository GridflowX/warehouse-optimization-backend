import os
import pandas as pd
import matplotlib.pyplot as plt

# Print the current working directory to verify the script's location
print("Current working directory:", os.getcwd())

# File names for bus limit 50 and 80
bus_limit_50_files = [
    "exp2_passengerdata_50_392.csv",
    "exp2_passengerdata_50_896s.csv",
    "exp2_passengerdata_50_2968.csv",
    "exp2_passengerdata_50_4032.csv",
    "exp2_passengerdata_50_5040.csv",
    "exp2_passengerdata_50_7952.csv",
]

bus_limit_80_files = [
    "exp2_passengerdata_80_392.csv",
    "exp2_passengerdata_80_896s.csv",
    "exp2_passengerdata_80_2968.csv",
    "exp2_passengerdata_80_4032.csv",
    "exp2_passengerdata_80_5040.csv",
    "exp2_passengerdata_80_7952.csv",
]

# Pod file names (first pod system)
pod_files = [
    "processed_392_pod_2.csv",
    "processed_896_pod_2.csv",
    "processed_2968_pod_2.csv",
    "processed_4032_pod_2.csv",
    "processed_5040_pod_2.csv",
    "processed_7952_pod_2.csv",
]

# Pod-optimized file names
pod_opt_files = [
    "processed_Excel392[2]_allocations.csv",
    "processed_Excel896[2]_allocations.csv",
    "processed_Excel2968[2]_allocations.csv",
    "processed_Excel4032[2]_allocations.csv",
    "processed_Excel5040[2]_allocations.csv",
    "processed_Excel7952[2]_allocations.csv",
]

# Function to calculate average waiting_journey_ratio for any file
def get_ratio_average_waiting_journey(file_name):
    try:
        df = pd.read_csv(file_name)
        df.columns = df.columns.str.strip()  # Trim spaces

        if 'waiting_journey_ratio' not in df.columns:
            print(f"Error: 'waiting_journey_ratio' column missing in {file_name}.")
            return None

        # Ensure column is numeric
        df['waiting_journey_ratio'] = pd.to_numeric(df['waiting_journey_ratio'], errors='coerce')

        # Drop NaN values
        df = df.dropna(subset=['waiting_journey_ratio'])

        # Calculate and return average
        avg = df['waiting_journey_ratio'].mean()
        if pd.isna(avg):
            print(f"Warning: No valid 'waiting_journey_ratio' data in {file_name}.")
            return None
        return avg

    except FileNotFoundError:
        print(f"Error: The file '{file_name}' was not found.")
        return None
    except Exception as e:
        print(f"Error reading file '{file_name}': {e}")
        return None

# Unified passenger counts for the x-axis
passenger_counts = [392, 896, 2968, 4032, 5040, 7952]

# Calculate average waiting_journey_ratio for all systems
avg_waiting_journey_ratio_50 = [get_ratio_average_waiting_journey(file) for file in bus_limit_50_files]
avg_waiting_journey_ratio_80 = [get_ratio_average_waiting_journey(file) for file in bus_limit_80_files]
avg_waiting_journey_ratio_pod = [get_ratio_average_waiting_journey(file) for file in pod_files]
avg_waiting_journey_ratio_pod_opt = [get_ratio_average_waiting_journey(file) for file in pod_opt_files]

# Check for processing errors
all_data = [
    avg_waiting_journey_ratio_50,
    avg_waiting_journey_ratio_80,
    avg_waiting_journey_ratio_pod,
    avg_waiting_journey_ratio_pod_opt
]
if any(None in data for data in all_data):
    print("Warning: Some files could not be processed. Please check the errors above.")
else:
    print("All files processed successfully.")

# Create the plot
plt.figure(figsize=(12, 7))

# Plot each system's data if it contains valid values
if None not in avg_waiting_journey_ratio_50:
    plt.plot(passenger_counts, avg_waiting_journey_ratio_50, marker='o', linestyle='-', color='blue', label='Bus Limit 50')
if None not in avg_waiting_journey_ratio_80:
    plt.plot(passenger_counts, avg_waiting_journey_ratio_80, marker='s', linestyle='-', color='green', label='Bus Limit 80')
if None not in avg_waiting_journey_ratio_pod:
    plt.plot(passenger_counts, avg_waiting_journey_ratio_pod, marker='^', linestyle='-', color='red', label='Pod System')
if None not in avg_waiting_journey_ratio_pod_opt:
    plt.plot(passenger_counts, avg_waiting_journey_ratio_pod_opt, marker='d', linestyle='-', color='purple', label='Pod with Optimisation')

# Add reference lines at 0.25 and 0.5
plt.axhline(y=0.25, color='black', linestyle=':', linewidth=1, label='0.25 Threshold')
plt.axhline(y=0.5, color='black', linestyle='--', linewidth=1, label='0.5 Threshold')

# Determine y-axis limit
all_values = [val for sublist in all_data for val in sublist if val is not None]
y_max = max(all_values) * 1.1 if all_values else 1.0  # 10% buffer or default to 1.0
plt.ylim(0, max(1.0, y_max))

# Labels and title
plt.title('Experiment 2: Average Waiting to Journey Time Ratio vs. Number of Passengers')
plt.xlabel('Number of Passengers')
plt.ylabel('Average Waiting to Journey Time Ratio')
plt.grid(True)
plt.xticks(passenger_counts)
plt.legend()

# Show the plot
plt.show()