import sqlite3
import matplotlib.pyplot as plt

# Connect to the database
conn = sqlite3.connect(r'C:\Users\gouri\Downloads\Busdatabase\buss.db')
cursor = conn.cursor()

# Passenger counts to be used as x-coordinates
passenger_counts = [392, 896, 2968, 4032, 5040]

# Fetch cost values for exp4_50_costdata where passenger count matches
cursor.execute("SELECT number_of_passengers, cost_value FROM exp4_50_costdata WHERE number_of_passengers IN (392, 896, 2968, 4032, 5040) ORDER BY number_of_passengers")
data1 = cursor.fetchall()
passengers1, cost_values1 = zip(*data1)  # Unpacking into two lists

# Fetch cost values for exp4_80_costdata where passenger count matches
cursor.execute("SELECT number_of_passengers, cost_value FROM exp4_80_costdata WHERE number_of_passengers IN (392, 896, 2968, 4032, 5040) ORDER BY number_of_passengers")
data2 = cursor.fetchall()
passengers2, cost_values2 = zip(*data2)  # Unpacking into two lists

# Close the connection
conn.close()

# Plot the data
plt.figure(figsize=(8, 5))
plt.plot(passengers1, cost_values1, marker='o', linestyle='-', label='exp4_50_costdata')
plt.plot(passengers2, cost_values2, marker='s', linestyle='-', label='exp4_80_costdata')

# Labels and title
plt.xlabel("Number of Passengers")
plt.ylabel("Cost Value")
plt.title("Cost Values vs. Number of Passengers")
plt.xticks(passenger_counts)  # Ensure x-axis ticks match specified passenger counts
plt.legend()
plt.grid(True)

# Show the plot
plt.show()
