from itertools import permutations
import random
import networkx as nx
import sqlite3
import pandas as pd
import os
from datetime import datetime
import math

# Define bus stops
elements = ['A', 'B', 'C', 'D', 'P', 'Q', 'R', 'S']

# Connect to the SQLite database
conn = sqlite3.connect('exp5Bus.db')
cursor = conn.cursor()

# Define bus network graph (travel times in seconds)
graph = nx.Graph()
graph.add_edge('A', 'B', weight=1170)
graph.add_edge('B', 'Q', weight=1800)
graph.add_edge('B', 'C', weight=630)
graph.add_edge('B', 'R', weight=1350)
graph.add_edge('C', 'D', weight=1530)
graph.add_edge('P', 'Q', weight=900)
graph.add_edge('R', 'S', weight=450)

# Constants
board_deboard = 4
SPEED_KM_PER_HOUR = 40
WALKING_SPEED = 1.39  # in meters per second

# Stop coordinates
stop_coordinates = {
    'A': (-12.55, 3.36), 'B': (0, 0), 'C': (0, -7), 'D': (14.75, -15.5),
    'P': (4.35, 10.98), 'Q': (0, 20), 'R': (-14.5, -3.88), 'S': (-14.48, -8.88)
}

# Bus Paths
bus1_path = ['A', 'B', 'C', 'D', 'C', 'B']  # Bus ID = 1
bus2_path = ['D', 'C', 'B', 'A', 'B', 'C']  # Bus ID = 2
bus3_path = ['P', 'Q', 'B', 'R', 'S', 'R', 'B', 'Q']  # Bus ID = 3
bus4_path = ['S', 'R', 'B', 'Q', 'P', 'Q', 'B', 'R']  # Bus ID = 4

# Initialize dictionaries
bus_distances = {1: 0, 2: 0, 3: 0, 4: 0}
bus_previous_stops = {1: None, 2: None, 3: None, 4: None}
bus_trip_counts = {1: 0, 2: 0, 3: 0, 4: 0}

# Utility function to calculate Euclidean distance
def euclidean_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Utility function to get the nearest stop based on Euclidean distance
def nearest_stop(x, y):
    min_distance = float('inf')
    nearest = None
    print(f"Calculating distances for ({x}, {y}):")
    for stop, (stop_x, stop_y) in stop_coordinates.items():
        distance = euclidean_distance(x, y, stop_x, stop_y)

        if distance < min_distance:
            min_distance = distance
            nearest = stop

    return nearest, min_distance

# Generate random coordinates with condition
def generate_coordinates():
    while True:
        x1, y1 = random.randint(-15, 15), random.randint(-16, 20)
        x2, y2 = random.randint(-15, 15), random.randint(-16, 20)
        dist_between_coords = euclidean_distance(x1, y1, x2, y2)
        arrival_stop, source_walking_distance = nearest_stop(x1, y1)
        destination_stop, destination_walking_distance = nearest_stop(x2, y2)
        if arrival_stop != destination_stop and dist_between_coords > euclidean_distance(
                *stop_coordinates[arrival_stop], *stop_coordinates[destination_stop]):
            return arrival_stop, destination_stop, x1, y1, x2, y2, source_walking_distance, destination_walking_distance

# Function to generate random arrival time
def generate_random_arrival_time():
    return random.randint(0, 64800)

# Function to find the shortest path
def shortestPath(src, dest):
    shortest_path = nx.dijkstra_path(graph, src, dest, weight='weight')
    return ''.join(shortest_path)

# Function to calculate travel time (returns time in seconds)
def shortestTravelTime(src, dest):
    return nx.dijkstra_path_length(graph, src, dest, weight='weight')

# Function to reset the passenger table
def reset_passenger_table():
    cursor.execute("DROP TABLE IF EXISTS passenger")
    cursor.execute("""
    CREATE TABLE passenger (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        arrival_time INTEGER,
        arrival_stop TEXT,
        destination_stop TEXT,
        bus_departure INTEGER,
        departure_time INTEGER,
        flag INTEGER,
        path TEXT,
        waiting_time INTEGER,
        bus_id INTEGER,
        reached INTEGER,
        t INTEGER,
        distance REAL,
        x1 REAL,
        y1 REAL,
        x2 REAL,
        y2 REAL,
        walking_time REAL,
        total_travel_time REAL
    )
    """)
    conn.commit()
    print("Passenger table reset.")

# Function to initialize the bus table
def initialize_bus_table():
    cursor.execute("DELETE FROM bus")
    cursor.execute(
        "INSERT INTO bus (id, present_stop, destination_stop, time, path, passenger_count) VALUES (?, ?, ?, ?, ?, ?)",
        (1, 'A', 'B', 0, 'ABCD', 0))
    cursor.execute(
        "INSERT INTO bus (id, present_stop, destination_stop, time, path, passenger_count) VALUES (?, ?, ?, ?, ?, ?)",
        (2, 'D', 'C', 0, 'DCBA', 0))
    cursor.execute(
        "INSERT INTO bus (id, present_stop, destination_stop, time, path, passenger_count) VALUES (?, ?, ?, ?, ?, ?)",
        (3, 'P', 'Q', 0, 'PQBRS', 0))
    cursor.execute(
        "INSERT INTO bus (id, present_stop, destination_stop, time, path, passenger_count) VALUES (?, ?, ?, ?, ?, ?)",
        (4, 'S', 'R', 0, 'SRBQP', 0))
    conn.commit()
    print("Bus table initialized.")

# Function to calculate distance for passengers
def calculate_distance_for_passengers():
    cursor.execute("SELECT id, path FROM passenger")
    passengers = cursor.fetchall()
    for passenger in passengers:
        passenger_id, path = passenger
        total_distance = 0
        for i in range(len(path) - 1):
            stop1, stop2 = path[i], path[i + 1]
            if graph.has_edge(stop1, stop2):
                travel_time = graph[stop1][stop2]['weight']
                distance = (travel_time * SPEED_KM_PER_HOUR) / 3600
                total_distance += distance
        cursor.execute("UPDATE passenger SET distance = ? WHERE id = ?", (total_distance, passenger_id))
    conn.commit()
    print("Distance updated for all passengers.")

# Function to process bus operations
def busfunction(busid, present_stop, destination_stop, next_stop, buspath, t, number_of_passenger, capacity):
    overhead = []

    # Passenger deboarding
    cursor.execute("SELECT * FROM passenger WHERE flag=? AND destination_stop=? AND bus_id=?", (1, present_stop, busid))
    p_update = cursor.fetchall()
    print(f"Bus {busid} at {present_stop}: Found {len(p_update)} passengers to deboard.")
    for p in p_update:
        passenger_id = p[0]
        deboard(passenger_id, t)
        t += board_deboard
        number_of_passenger -= 1

    # Passenger deboarding at junctions
    cursor.execute("SELECT * FROM passenger WHERE flag=? AND destination_stop!=? AND bus_id=?",
                   (1, present_stop, busid))
    p_update = cursor.fetchall()
    junction_deboards = 0
    for p in p_update:
        passenger_id = p[0]
        if findnext(p[7], present_stop, destination_stop) == 0:  # Index adjusted for new table
            deboard_at_junction(passenger_id, present_stop, t)
            t += board_deboard
            number_of_passenger -= 1
            junction_deboards += 1
    print(f"Bus {busid} at {present_stop}: Deboarded {junction_deboards} passengers at junction.")

    # Passenger boarding
    cursor.execute("SELECT * FROM passenger WHERE arrival_time<=? AND flag=? AND arrival_stop=? AND reached=?",
                   (t, 0, present_stop, 0))
    p_update = cursor.fetchall()
    print(f"Bus {busid} at {present_stop}: Found {len(p_update)} passengers to board.")
    for p in p_update:
        passenger_id = p[0]
        if findnext(p[7], present_stop, destination_stop) == 1 and number_of_passenger < capacity:
            board(passenger_id, t, p[8], p[1], busid)  # Indices adjusted
            t += board_deboard
            overhead.append(passenger_id)
            number_of_passenger += 1

    busdeparture(overhead, t)

    # Calculate distance traveled by the bus
    if graph.has_edge(present_stop, destination_stop):
        travel_time = shortestTravelTime(present_stop, destination_stop)
        distance_traveled = (travel_time * SPEED_KM_PER_HOUR) / 3600
        bus_distances[busid] += distance_traveled
        bus_previous_stops[busid] = destination_stop
        bus_trip_counts[busid] += 1

    # Update time
    travel_time = shortestTravelTime(present_stop, destination_stop)
    t += travel_time
    cursor.execute("UPDATE bus SET present_stop=?, destination_stop=?, time=?, passenger_count=? WHERE id=?",
                   (destination_stop, next_stop, t, number_of_passenger, busid))
    conn.commit()
    return number_of_passenger

# Supporting functions
def busdeparture(overhead, t):
    for o in overhead:
        cursor.execute("SELECT * FROM passenger WHERE id=?", (o,))
        p = cursor.fetchone()
        waiting_time = p[8] + (t - p[1])  # Index 8 is waiting_time
        bus_travel_time = p[4] - t if p[4] else 0  # Index 4 is bus_departure
        total_travel_time = bus_travel_time + p[17] if p[17] else 0  # Index 17 is walking_time
        cursor.execute("UPDATE passenger SET bus_departure=?, waiting_time=?, total_travel_time=? WHERE id=?",
                       (t, waiting_time, total_travel_time, o))
        conn.commit()

def deboard(passenger_id, t):
    cursor.execute("SELECT * FROM passenger WHERE id=?", (passenger_id,))
    p = cursor.fetchone()
    bus_travel_time = t - p[4] if p[4] else 0  # Index 4 is bus_departure
    total_travel_time = bus_travel_time + p[17]  # Index 17 is walking_time
    cursor.execute("UPDATE passenger SET flag=?, departure_time=?, reached=?, total_travel_time=? WHERE id=?",
                   (0, t, 1, total_travel_time, passenger_id))
    conn.commit()

def deboard_at_junction(passenger_id, present_stop, t):
    cursor.execute("UPDATE passenger SET arrival_stop=?, flag=?, arrival_time=? WHERE id=?",
                   (present_stop, 0, t, passenger_id))
    conn.commit()

def board(passenger_id, t, waiting_time, arrival_time, busid):
    cursor.execute("UPDATE passenger SET flag=?, bus_id=? WHERE id=?", (1, busid, passenger_id))
    conn.commit()

def findnext(s, present_stop, destination_stop):
    for i in range(len(s)):
        if s[i] == present_stop:
            if i + 1 < len(s) and s[i + 1] == destination_stop:
                return 1
    return 0

# Save to CSV
def save_to_csv(total_passenger_count, capacity):
    filename = f"exp5_passengerdata_{capacity}_{total_passenger_count}.csv"
    try:
        df = pd.read_sql_query("SELECT * FROM passenger", conn)
        df.to_csv(filename, index=False)
        print(f"Final dataset saved to {filename}")
    except Exception as e:
        print(f"Error saving CSV file {filename}: {e}")

# Log cost value and calculate avg_waiting_time
def log_cost_value(total_distance_all_buses, total_passenger_count, capacity):
    table_name = f"exp5_{capacity}_costdata"
    total_units_of_energy = total_distance_all_buses * 1.35
    cursor.execute("SELECT SUM(distance) FROM passenger")
    total_person_km_travelled = cursor.fetchone()[0] or 0
    cost_value = total_units_of_energy / total_person_km_travelled if total_person_km_travelled > 0 else 0

    cursor.execute("SELECT AVG(waiting_time) FROM passenger")
    avg_waiting_time = cursor.fetchone()[0] or 0

    cursor.execute(f"SELECT number_of_passengers FROM {table_name} WHERE number_of_passengers = ?", (total_passenger_count,))
    existing_entry = cursor.fetchone()

    if existing_entry:
        cursor.execute(f"UPDATE {table_name} SET cost_value = ? WHERE number_of_passengers = ?", (cost_value, total_passenger_count))
    else:
        cursor.execute(f"INSERT INTO {table_name} (number_of_passengers, cost_value) VALUES (?, ?)", (total_passenger_count, cost_value))
    conn.commit()
    print(f"Cost value updated in {table_name} for {total_passenger_count} passengers: {cost_value:.4f}")

    return cost_value, avg_waiting_time

# Main simulation function
def main_simulation(total_passenger_count, capacity):
    reset_passenger_table()
    initialize_bus_table()
    bus_distances.update({1: 0, 2: 0, 3: 0, 4: 0})
    bus_previous_stops.update({1: None, 2: None, 3: None, 4: None})
    bus_trip_counts.update({1: 0, 2: 0, 3: 0, 4: 0})

    random.seed(total_passenger_count)

    for i in range(total_passenger_count):
        arrival_stop, destination_stop, x1, y1, x2, y2, source_walking_distance, destination_walking_distance = generate_coordinates()
        arrival_time = generate_random_arrival_time()
        path = shortestPath(arrival_stop, destination_stop)
        source_walking_time = 1000 * source_walking_distance / WALKING_SPEED
        destination_walking_time = 1000 * destination_walking_distance / WALKING_SPEED
        walking_time = source_walking_time + destination_walking_time

        cursor.execute(
            "INSERT INTO passenger (arrival_time, arrival_stop, destination_stop, "
            "bus_departure, departure_time, flag, path, waiting_time, bus_id, reached, t, distance, x1, y1, x2, y2, walking_time, total_travel_time) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (arrival_time, arrival_stop, destination_stop, 0, 0, 0, path, 0, 0, 0, arrival_time, 0, x1, y1, x2, y2, walking_time, 0)
        )
    conn.commit()
    print(f"{total_passenger_count} Passengers added successfully for capacity {capacity} with walking times.")
    calculate_distance_for_passengers()

    cursor.execute("SELECT COUNT(*) FROM passenger WHERE reached=0")
    initial_remaining = cursor.fetchone()[0]
    print(f"Initial passengers with reached=0: {initial_remaining}")

    i = 2
    maxi = 0
    while True:
        cursor.execute("SELECT COUNT(*) FROM passenger WHERE reached=0")
        remaining_passengers = cursor.fetchone()[0]
        print(f"Remaining passengers: {remaining_passengers}")
        if remaining_passengers == 0:
            total_distance_all_buses = sum(bus_distances.values())
            cost_value, avg_waiting_time = log_cost_value(total_distance_all_buses, total_passenger_count, capacity)
            save_to_csv(total_passenger_count, capacity)
            print(f"\nResults for {total_passenger_count} passengers with capacity {capacity}:")
            print(f"Total distance traveled by each bus (in km):")
            for busid, distance_in_km in bus_distances.items():
                print(f"Bus {busid}: {distance_in_km:.2f} km (Trips: {bus_trip_counts[busid]})")
            print(f"Total distance traveled by all buses: {total_distance_all_buses:.2f} km")
            print(f"Total trips by all buses: {sum(bus_trip_counts.values())}")
            print(f"Cost value: {cost_value:.4f}")
            print(f"Average waiting time: {avg_waiting_time:.2f} seconds")
            print(f"Maximum passengers on any bus: {maxi}")
            break

        cursor.execute("SELECT * FROM bus ORDER BY time")
        buses = cursor.fetchall()
        if not buses:
            print("No buses found in the database! Check bus table initialization.")
            break
        print(f"Found {len(buses)} buses to process.")
        for bus in buses:
            busid, present_stop, destination_stop, t, path, bus_passenger_count = bus
            print(f"Processing Bus {busid} at {t}, Current stop: {present_stop}, Destination: {destination_stop}")
            if path == 'ABCD':
                next_stop = bus1_path[i % 6]
                bus_passenger_count = busfunction(busid, present_stop, destination_stop, next_stop, bus1_path, t,
                                                  bus_passenger_count, capacity)
            elif path == 'DCBA':
                next_stop = bus2_path[i % 6]
                bus_passenger_count = busfunction(busid, present_stop, destination_stop, next_stop, bus2_path, t,
                                                  bus_passenger_count, capacity)
            elif path == 'PQBRS':
                next_stop = bus3_path[i % 8]
                bus_passenger_count = busfunction(busid, present_stop, destination_stop, next_stop, bus3_path, t,
                                                  bus_passenger_count, capacity)
            else:
                next_stop = bus4_path[i % 8]
                bus_passenger_count = busfunction(busid, present_stop, destination_stop, next_stop, bus4_path, t,
                                                  bus_passenger_count, capacity)
            maxi = max(maxi, bus_passenger_count)
        i += 1

# Process all passenger counts for both capacities
passenger_counts = [392, 896, 2968, 4032, 5040, 7952]
capacities = [50,80]

for passenger_count in passenger_counts:
    for capacity in capacities:
        print(f"\nStarting simulation for {passenger_count} passengers with capacity {capacity}...")
        main_simulation(passenger_count, capacity)

conn.close()