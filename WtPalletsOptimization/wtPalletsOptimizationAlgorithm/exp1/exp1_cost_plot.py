import sqlite3
import matplotlib.pyplot as plt

# Connect to the database
conn = sqlite3.connect('buss.db')
cursor = conn.cursor()

# Passenger counts to be used as x-coordinates
passenger_counts = [392, 896, 2968, 4032, 5040]

# Fetch cost values for exp4_50_costdata where passenger count matches
cursor.execute("SELECT number_of_pallets, cost_value FROM exp1_50_costdata WHERE number_of_pallets IN (392, 896, 2968, 4032, 5040) ORDER BY number_of_pallets")
data1 = cursor.fetchall()
pallets1, cost_values1 = zip(*data1)  # Unpacking into two lists

# Fetch cost values for exp4_80_costdata where passenger count matches
cursor.execute("SELECT number_of_pallets, cost_value FROM exp1_large_truck_costdata WHERE number_of_pallets IN (392, 896, 2968, 4032, 5040) ORDER BY number_of_pallets")
data2 = cursor.fetchall()
pallets2, cost_values2 = zip(*data2)  # Unpacking into two lists

# Close the connection
conn.close()

# Plot the data
plt.figure(figsize=(8, 5))
plt.plot(pallets1, cost_values1, marker='o', linestyle='-', label='exp1_small_truck_costdata')
plt.plot(pallets2, cost_values2, marker='s', linestyle='-', label='exp1_large_truck_costdata')

# Labels and title
plt.xlabel("Number of Pallets")
plt.ylabel("Cost Value")
plt.title("Cost Values vs. Number of Pallets")
plt.xticks(pallet_counts)  # Ensure x-axis ticks match specified pallet counts
plt.legend()
plt.grid(True)

# Show the plot
plt.show()
