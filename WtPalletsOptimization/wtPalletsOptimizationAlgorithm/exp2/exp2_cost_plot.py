import sqlite3
import matplotlib.pyplot as plt

# Connect to the database
conn = sqlite3.connect(r'C:\Users\gouri\Downloads\Busdatabase\buss.db')
cursor = conn.cursor()

# Use the actual passenger counts in the database
passenger_counts = [392, 896, 2968, 4032, 5040]

# Fetch cost values for exp2_50_costdata
cursor.execute("SELECT number_of_passengers, cost_value FROM exp2_50_costdata WHERE number_of_passengers IN (500, 3000, 4000, 5000) ORDER BY number_of_passengers")
data1 = cursor.fetchall()

# Fetch cost values for exp2_80_costdata
cursor.execute("SELECT number_of_passengers, cost_value FROM exp2_80_costdata WHERE number_of_passengers IN (500, 3000, 4000, 5000) ORDER BY number_of_passengers")
data2 = cursor.fetchall()

# Close the connection
conn.close()

# Handle empty data
passengers1, cost_values1 = zip(*data1) if data1 else ([], [])
passengers2, cost_values2 = zip(*data2) if data2 else ([], [])

# Plot the data
plt.figure(figsize=(8, 5))

if passengers1:
    plt.plot(passengers1, cost_values1, marker='o', linestyle='-', label='exp2_50_costdata')

if passengers2:
    plt.plot(passengers2, cost_values2, marker='s', linestyle='-', label='exp2_80_costdata')

plt.xlabel("Number of Passengers")
plt.ylabel("Cost Value")
plt.title("Cost Values vs. Number of Passengers")
plt.xticks(passenger_counts)
plt.legend()
plt.grid(True)
plt.show()
