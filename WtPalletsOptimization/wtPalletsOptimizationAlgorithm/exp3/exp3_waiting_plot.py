import os
import pandas as pd
import matplotlib.pyplot as plt
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from commonCoordinates import pallet_counts

# Print the current working directory to verify the script's location
print("Current working directory:", os.getcwd())

# Generate file names for exp3 based on commonCoordinates data
small_truck_files = [f"exp3_palletdata_50_{count}.csv" for count in pallet_counts]
large_truck_files = [f"exp3_palletdata_80_{count}.csv" for count in pallet_counts]
goodspod_files = [f"{count}_exp3.csv" for count in pallet_counts]
#pod_opt_files = [f"{count}_exp3_allocations.csv" for count in pallet_counts]

# Function to calculate average waiting_time for any file
def get_average_delivery_delay(file_name):
    try:
        df = pd.read_csv(file_name)
        df.columns = df.columns.str.strip()  # Trim spaces

        if 'waiting_time' not in df.columns:
            print(f"Error: 'delivery_delay' column missing in {file_name}.")
            return None

        # Ensure column is numeric
        df['delivery_delay'] = pd.to_numeric(df['delivery_delay'], errors='coerce')

        # Drop NaN values
        df = df.dropna(subset=['delivery_delay'])

        # Return average
        return df['delivery_delay'].mean()

    except FileNotFoundError:
        print(f"Error: The file '{file_name}' was not found.")
        return None
    except Exception as e:
        print(f"Error reading file '{file_name}': {e}")
        return None

# Calculate average delivery delay for all systems
avg_small = [get_average_delivery_delay(file) for file in small_truck_files]
avg_large = [get_average_delivery_delay(file) for file in large_truck_files]
avg_pod = [get_average_delivery_delay(file) for file in goodspod_files]
#avg_waiting_time_pod_opt = [get_average_waiting_time(file) for file in pod_opt_files]

# Check for any processing errors
if None in avg_delivery_delay_small_truck or None in avg_delivery_delay_large_truck or None in avg_delivery_delay_goodspod :#
    #or None in avg_waiting_time_pod_opt:
    print("Warning: Some files could not be processed. Please check the errors above.")

# Plot all four series on the same graph
plt.figure(figsize=(12, 7))
plt.plot(pallet_counts, avg_delivery_delay_small_truck, marker='o', linestyle='-', color='blue', label='truck, passenger limit 50')
plt.plot(pallet_counts, avg_delivery_delay_large_truck, marker='s', linestyle='-', color='green', label='truck, passenger limit 80')
plt.plot(pallet_counts, avg_delivery_delay_goodspod, marker='^', linestyle='-', color='red', label='goodsPods, uniformly distributed across stops')
#plt.plot(pallet_counts, avg_waiting_time_pod_opt, marker='d', linestyle='-', color='purple', label='Pods, optimally distributed across stops')

plt.axhline(y=1800, color='black', linestyle=':', label='30 min (1800s)')
# Labels and title
plt.title('Experiment 3: Average delivery delay vs. Number of Pallets')
plt.xlabel('Number of Pallets')
plt.ylabel('Average Pallet Delivery Delay(seconds)')
plt.grid(True)
plt.xticks(pallet_counts)
plt.legend()
# plt.show()

# Save the plot
plt.savefig('average_deliver_delay_comparison_exp3_pod_opt.png')

# # Show the plot
# plt.show()