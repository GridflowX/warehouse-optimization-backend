import os
import pandas as pd
import matplotlib.pyplot as plt

# Print the current working directory to verify the script's location
print("Current working directory:", os.getcwd())

# File names for bus limit 50 and 80
bus_limit_50_files = [
    "exp4_passengerdata_50_392.csv",
    "exp4_passengerdata_50_896.csv",
    "exp4_passengerdata_50_2968.csv",
    "exp4_passengerdata_50_4032.csv",
    "exp4_passengerdata_50_5040.csv",
    "exp4_passengerdata_50_7952.csv"
]

bus_limit_80_files = [
    "exp4_passengerdata_80_392.csv",
    "exp4_passengerdata_80_896.csv",
    "exp4_passengerdata_80_2968.csv",
    "exp4_passengerdata_80_4032.csv",
    "exp4_passengerdata_80_5040.csv",
    "exp4_passengerdata_80_7952.csv"
]

# Pod file names uniform (first pod system)
pod_files = [
    "392_exp4_uniform.csv","896_exp4_uniform.csv","2968_exp4_uniform.csv","4032_exp4_uniform.csv",
    "5040_exp4_uniform.csv","7952_exp4_uniform.csv"
]


# Pod-optimized file names
pod_opt_files = [
    "392_exp4_uniform_allocations.csv","896_exp4_uniform_allocations.csv","2968_exp4_uniform_allocations.csv","4032_exp4_uniform_allocations.csv",
    "5040_exp4_uniform_allocations.csv","7952_exp4_uniform_allocations.csv"
]

# Alternative pod system 1 file names using exp3 not optimized
pod_alt1_files = [
    "392_exp4_non-uniform.csv","896_exp4_non-uniform.csv","2968_exp4_non-uniform.csv","4032_exp4_non-uniform.csv",
    "5040_exp4_non-uniform.csv","7952_exp4_non-uniform.csv"
]

# Alternative pod system 2 file names optimized
pod_alt2_files = [
    "392_exp4_non-uniform_allocations.csv","2968_exp4_non-uniform_allocations.csv","4032_exp4_non-uniform_allocations.csv","7952_exp4_non-uniform_allocations.csv",
    "5040_exp4_non-uniform_allocations.csv","7952_exp4_non-uniform_allocations.csv"
]

# Function to calculate average waiting_time for any file
def get_average_waiting_time(file_name):
    try:
        df = pd.read_csv(file_name)
        df.columns = df.columns.str.strip()  # Trim spaces

        if 'waiting_time' not in df.columns:
            print(f"Error: 'waiting_time' column missing in {file_name}.")
            return None

        # Ensure column is numeric
        df['waiting_time'] = pd.to_numeric(df['waiting_time'], errors='coerce')

        # Drop NaN values
        df = df.dropna(subset=['waiting_time'])

        # Return average
        return df['waiting_time'].mean()

    except FileNotFoundError:
        print(f"Error: The file '{file_name}' was not found.")
        return None
    except Exception as e:
        print(f"Error reading file '{file_name}': {e}")
        return None

# Unified passenger counts for the x-axis
passenger_counts = [ 7952]

# Calculate average waiting times for all systems
avg_waiting_time_50 = [get_average_waiting_time(file) for file in bus_limit_50_files]
avg_waiting_time_80 = [get_average_waiting_time(file) for file in bus_limit_80_files]
avg_waiting_time_pod = [get_average_waiting_time(file) for file in pod_files]
avg_waiting_time_pod_opt = [get_average_waiting_time(file) for file in pod_opt_files]
avg_waiting_time_pod_alt1 = [get_average_waiting_time(file) for file in pod_alt1_files]
avg_waiting_time_pod_alt2 = [get_average_waiting_time(file) for file in pod_alt2_files]

# Check for any processing errors
if (None in avg_waiting_time_50 or None in avg_waiting_time_80 or
    None in avg_waiting_time_pod or None in avg_waiting_time_pod_opt or
    None in avg_waiting_time_pod_alt1 or None in avg_waiting_time_pod_alt2):
    print("Warning: Some files could not be processed. Please check the errors above.")

# Plot all six series on the same graph
plt.figure(figsize=(12, 7))
plt.plot(passenger_counts, avg_waiting_time_50, marker='o', linestyle='-', color='blue', label='Bus, passenger limit 50')
plt.plot(passenger_counts, avg_waiting_time_80, marker='s', linestyle='-', color='green', label='Bus, passenger limit 80')
plt.plot(passenger_counts, avg_waiting_time_pod, marker='^', linestyle='-', color='red', label='Pods, uniformly distributed across stops')
plt.plot(passenger_counts, avg_waiting_time_pod_opt, marker='d', linestyle='-', color='purple', label='Pods, optimally distributed across stops')
plt.plot(passenger_counts, avg_waiting_time_pod_alt1, marker='*', linestyle='-', color='orange', label='Pods, Distribution as per end of experiment 3')
plt.plot(passenger_counts, avg_waiting_time_pod_alt2, marker='v', linestyle='-', color='cyan', label='Pods With Optimisation(Distribution as per end of experiment 3)')


plt.axhline(y=1800, color='black', linestyle=':', label='30 min (1800s)')
# Labels and title
plt.title('Experiment 4: Average Waiting Time vs. Number of Passengers (with Multiple Pod Systems)')
plt.xlabel('Number of Passengers')
plt.ylabel('Average Waiting Time')
plt.grid(True)
plt.xticks(passenger_counts)
plt.legend()

# Save the plot
plt.savefig('average_waiting_time_comparison_exp4_all_systems.png')

# Show the plot
plt.show()