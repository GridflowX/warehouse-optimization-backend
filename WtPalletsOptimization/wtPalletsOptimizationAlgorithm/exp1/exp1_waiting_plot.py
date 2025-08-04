# import os
# import pandas as pd
# import matplotlib.pyplot as plt

# import sys

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from commonCoordinates import pallet_counts


# # Print the current working directory to verify the script's location
# # print("Current working directory:", os.getcwd())

# # Generate file names for exp2 based on commonCoordinates data
# small_truck_files = [f"exp1_palletdata_50_{count}.csv" for count in pallet_counts]
# large_truck_files = [f"exp1_palletdata_80_{count}.csv" for count in pallet_counts]
# goodspod_files = [f"{count}_exp1.csv" for count in pallet_counts]
# # goodspod_opt_files = [f"{count}_exp1_allocations.csv" for count in pallet_counts]

# # Function to calculate average delivery_delay for any file
# def get_average_delivery_delay(file_name):
#     try:
#         df = pd.read_csv(file_name)
#         df.columns = df.columns.str.strip()  # Trim spaces

#         if 'delivery_delay' not in df.columns:
#             #print(f"Error: 'delivery_delay' column missing in {file_name}.")
#             return None

#         # Ensure column is numeric
#         df['delivery_delay'] = pd.to_numeric(df['delivery_delay'], errors='coerce')

#         # Drop NaN values
#         df = df.dropna(subset=['delivery_delay'])

#         # Return average
#         return df['delivery_delay'].mean()

#     except FileNotFoundError:
#         #print(f"Error: The file '{file_name}' was not found.")
#         return None
#     except Exception as e:
#         #print(f"Error reading file '{file_name}': {e}")
#         return None

# # Calculate average delivery delay for all systems
# avg_delivery_delay_small_truck = [get_average_delivery_delay(file) for file in small_truck_files]
# avg_delivery_delay_large_truck = [get_average_delivery_delay(file) for file in large_truck_files]
# avg_delivery_delay_goodspod = [get_average_delivery_delay(file) for file in goodspod_files]
# # avg_delivery_delay_goodspod_opt = [get_average_delivery_delay(file) for file in goodspod_opt_files]

# # Check for any processing errors
# if None in avg_delivery_delay_small_truck or None in avg_delivery_delay_large_truck or None in avg_delivery_delay_goodspod :#or None in avg_delivery_delay_goodspod_opt:
#     print("Warning: Some files could not be processed. Please check the errors above.")

# # Plot all four series on the same graph
# plt.figure(figsize=(10, 6))
# plt.plot(pallet_counts, avg_delivery_delay_small_truck, marker='o', linestyle='-', color='blue', label='small_truck')
# plt.plot(pallet_counts, avg_delivery_delay_large_truck, marker='s', linestyle='-', color='green', label='large_truck')
# plt.plot(pallet_counts, avg_delivery_delay_goodspod, marker='^', linestyle='-', color='red', label='Pod based Robotic System')
# # plt.plot(pallet_counts, avg_delivery_delay_goodspod_opt, marker='d', linestyle='-', color='purple', label='GoodsPods, optimally distributed across stops')

# plt.axhline(y=1800, color='black', linestyle=':', label='30 min (1800s)')
# # Labels and title
# plt.title('Experiment 1: Average Waiting Time vs. Number of Pallets')
# plt.xlabel('Number of Pallets')
# plt.ylabel('Average Pallet Waiting Time(seconds)')
# plt.grid(True)
# plt.xticks(pallet_counts)
# plt.legend()

# # Adjust layout to prevent cropping
# plt.tight_layout()

# # Save the plot with specified DPI for consistent dimensions
# plt.savefig('exp1_a.png', dpi=100, bbox_inches='tight')

# # # Show the plot
# # plt.show()


import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from commonCoordinates import pallet_counts

# File names
small_truck_files = [f"exp1_palletdata_50_{count}.csv" for count in pallet_counts]
large_truck_files = [f"exp1_palletdata_80_{count}.csv" for count in pallet_counts]
goodspod_files = [f"{count}_exp1.csv" for count in pallet_counts]

def get_average_delivery_delay(file_name):
    try:
        df = pd.read_csv(file_name)
        df.columns = df.columns.str.strip()
        if 'delivery_delay' not in df.columns:
            return None
        df['delivery_delay'] = pd.to_numeric(df['delivery_delay'], errors='coerce')
        df = df.dropna(subset=['delivery_delay'])
        return df['delivery_delay'].mean()
    except Exception:
        return None

# Get average delays
avg_small = [get_average_delivery_delay(f) for f in small_truck_files]
avg_large = [get_average_delivery_delay(f) for f in large_truck_files]
avg_pod = [get_average_delivery_delay(f) for f in goodspod_files]

# Bar plot
x = np.arange(len(pallet_counts))
width = 0.15  # Narrower bar width

plt.figure(figsize=(10, 6))
plt.bar(x - width, avg_small, width, label='Small Truck', color='blue')
plt.bar(x, avg_large, width, label='Large Truck', color='green')
plt.bar(x + width, avg_pod, width, label='Pod based Robotic System', color='red')

plt.axhline(y=1800, color='black', linestyle=':', label='30 min (1800s)')

plt.title('Experiment 1: Average Waiting Time vs. Number of Pallets')
plt.xlabel('Number of Pallets')
plt.ylabel('Average Pallet Waiting Time (seconds)')
plt.xticks(x, pallet_counts)
plt.grid(axis='y')
plt.legend()
plt.tight_layout()
plt.savefig('exp1_barplot_narrow.png', dpi=100, bbox_inches='tight')
# plt.show()

