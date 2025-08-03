import os
import pandas as pd
import matplotlib.pyplot as plt

import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from commonCoordinates import passenger_counts


# Print the current working directory to verify the script's location
# print("Current working directory:", os.getcwd())

# Generate file names for exp2 based on commonCoordinates data
bus_limit_50_files = [f"exp1_passengerdata_50_{count}.csv" for count in passenger_counts]
bus_limit_80_files = [f"exp1_passengerdata_80_{count}.csv" for count in passenger_counts]
pod_files = [f"{count}_exp1.csv" for count in passenger_counts]
pod_opt_files = [f"{count}_exp1_allocations.csv" for count in passenger_counts]

# Function to calculate average waiting_time for any file
def get_average_waiting_time(file_name):
    try:
        df = pd.read_csv(file_name)
        df.columns = df.columns.str.strip()  # Trim spaces

        if 'waiting_time' not in df.columns:
            #print(f"Error: 'waiting_time' column missing in {file_name}.")
            return None

        # Ensure column is numeric
        df['waiting_time'] = pd.to_numeric(df['waiting_time'], errors='coerce')

        # Drop NaN values
        df = df.dropna(subset=['waiting_time'])

        # Return average
        return df['waiting_time'].mean()

    except FileNotFoundError:
        #print(f"Error: The file '{file_name}' was not found.")
        return None
    except Exception as e:
        #print(f"Error reading file '{file_name}': {e}")
        return None

# Calculate average waiting times for all systems
avg_waiting_time_50 = [get_average_waiting_time(file) for file in bus_limit_50_files]
avg_waiting_time_80 = [get_average_waiting_time(file) for file in bus_limit_80_files]
avg_waiting_time_pod = [get_average_waiting_time(file) for file in pod_files]
avg_waiting_time_pod_opt = [get_average_waiting_time(file) for file in pod_opt_files]

# Check for any processing errors
if None in avg_waiting_time_50 or None in avg_waiting_time_80 or None in avg_waiting_time_pod or None in avg_waiting_time_pod_opt:
    print("Warning: Some files could not be processed. Please check the errors above.")

# Plot all four series on the same graph
plt.figure(figsize=(10, 6))
plt.plot(passenger_counts, avg_waiting_time_50, marker='o', linestyle='-', color='blue', label='Bus, passenger limit 50')
plt.plot(passenger_counts, avg_waiting_time_80, marker='s', linestyle='-', color='green', label='Bus, passenger limit 80')
plt.plot(passenger_counts, avg_waiting_time_pod, marker='^', linestyle='-', color='red', label='Pods, uniformly distributed across stops')
plt.plot(passenger_counts, avg_waiting_time_pod_opt, marker='d', linestyle='-', color='purple', label='Pods, optimally distributed across stops')

plt.axhline(y=1800, color='black', linestyle=':', label='30 min (1800s)')
# Labels and title
plt.title('Experiment 1: Average Waiting Time vs. Number of Passengers (with Optimised Pod)')
plt.xlabel('Number of Passengers')
plt.ylabel('Average Passenger Waiting Time(seconds)')
plt.grid(True)
plt.xticks(passenger_counts)
plt.legend()

# Adjust layout to prevent cropping
plt.tight_layout()

# Save the plot with specified DPI for consistent dimensions
plt.savefig('exp1_a.png', dpi=100, bbox_inches='tight')

# # Show the plot
# plt.show()