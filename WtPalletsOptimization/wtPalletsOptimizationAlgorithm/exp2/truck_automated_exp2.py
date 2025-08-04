from itertools import permutations
import random
import networkx as nx
import sqlite3
import pandas as pd
import os
from datetime import datetime
import numpy as np  # Add numpy for bimodal Gaussian distribution
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from commonCoordinates import time_edges, SPEED_KM_PER_HOUR, load_unload, distance_edges, stops, truck_routes_1, truck_routes_2, truck_routes_3, truck_routes_4, truck_routes_5, pallet_counts, capacities, truck_distances, truck_previous_stops, truck_trip_counts, start_node, stop_node, paths, truck_paths, truck_distances_update, truck_previous_stops_update, truck_trip_counts_update

current_dir = os.path.dirname(os.path.abspath(__file__))

# Define truck stops
elements = stops

# Connect to the SQLite database
conn = sqlite3.connect(os.path.join(current_dir, 'truck.db'))
cursor = conn.cursor()

# Define truck network graph (travel times in seconds)
graph = nx.Graph()
for u, v, w in time_edges:
    graph.add_edge(u, v, weight=w)

# Function to generate bimodal arrival time
def generate_bimodal_truck_arrival_time():
    """
    Generates a pallet arrival time using a bimodal Gaussian distribution.
    - Morning peak: 8 AM (28,800 sec) with std dev 114 minutes.
    - Evening peak: 6 PM (64,800 sec) with std dev 60 minutes.
    Returns:
        int: Arrival time in seconds from midnight.
    """
    # Morning and evening peak parameters
    mean_morning, mean_evening = 28800, 64800  # 8 AM and 6 PM in seconds
    stddev_morning, stddev_evening = 114 * 60, 60 * 60  # 114 min and 60 min in seconds

    # Randomly choose a peak period (controlled by the seed)
    if random.choice([1, 2]) == 1:
        arrival_time = int(np.random.normal(mean_morning, stddev_morning))
    else:
        arrival_time = int(np.random.normal(mean_evening, stddev_evening))

    # Ensure arrival time is non-negative and within a reasonable day range (0 to 86,400 sec)
    return max(0, min(arrival_time, 86400))


# Function to find the shortest path
def shortestPath(src, dest):
    shortest_path = nx.dijkstra_path(graph, src, dest, weight='weight')
    return ''.join(shortest_path)


# Function to calculate travel time (returns time in seconds)
def shortestTravelTime(src, dest):
    return nx.dijkstra_path_length(graph, src, dest, weight='weight')


# Function to reset the pallet table
def reset_pallet_table():
    cursor.execute("DELETE FROM pallet")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='pallet'")
    conn.commit()
    print("pallet table cleared and primary key reset.")


# Function to initialize the truck table
def initialize_truck_table():
    cursor.execute("DELETE FROM truck")
    for idx, (start, stop, path) in enumerate(zip(start_node, stop_node, paths), start=1):
        cursor.execute(
        "INSERT INTO truck (id, present_stop, destination_stop, time, path, pallet_count) VALUES (?, ?, ?, ?, ?, ?)",
        (idx, start, stop, 0, path, 0)
    )
    conn.commit()
    print("truck table initialized.")


# Function to calculate distance for pallets
def calculate_distance_for_pallets():
    cursor.execute("SELECT id, path FROM pallet")
    pallets = cursor.fetchall()
    for pallet in pallets:
        pallet_id, path = pallet
        total_distance = 0
        for i in range(len(path) - 1):
            stop1, stop2 = path[i], path[i + 1]
            if graph.has_edge(stop1, stop2):
                travel_time = graph[stop1][stop2]['weight']
                distance = (travel_time * SPEED_KM_PER_HOUR) / 3600
                total_distance += distance
        cursor.execute("UPDATE pallet SET distance = ? WHERE id = ?", (total_distance, pallet_id))
    conn.commit()
    print("Distance updated for all pallets.")


# Function to process truck operations
def truckfunction(truckid, present_stop, destination_stop, next_stop, truckpath, t, number_of_pallet, capacity):
    overhead = []

    # pallet deboarding
    cursor.execute("SELECT * FROM pallet WHERE flag=? AND destination_stop=? AND truck_id=?", (1, present_stop, truckid))
    p_update = cursor.fetchall()
    print(f"truck {truckid} at {present_stop}: Found {len(p_update)} pallets to deboard.")
    for p in p_update:
        pallet_id = p[0]
        deboard(pallet_id, t)
        t += load_unload
        number_of_pallet -= 1

    # pallet deboarding at junctions
    cursor.execute("SELECT * FROM pallet WHERE flag=? AND destination_stop!=? AND truck_id=?",
                   (1, present_stop, truckid))
    p_update = cursor.fetchall()
    junction_deboards = 0
    for p in p_update:
        pallet_id = p[0]
        if findnext(p[7], present_stop, destination_stop) == 0:
            deboard_at_junction(pallet_id, present_stop, t)
            t += load_unload
            number_of_pallet -= 1
            junction_deboards += 1
    print(f"truck {truckid} at {present_stop}: Deboarded {junction_deboards} pallets at junction.")

    # pallet boarding
    cursor.execute("SELECT * FROM pallet WHERE arrival_time<=? AND flag=? AND arrival_stop=? AND reached=?",
                   (t, 0, present_stop, 0))
    p_update = cursor.fetchall()
    print(f"truck {truckid} at {present_stop}: Found {len(p_update)} pallets to board.")
    for p in p_update:
        pallet_id = p[0]
        if findnext(p[7], present_stop, destination_stop) == 1 and number_of_pallet < capacity:
            board(pallet_id, t, p[8], p[1], truckid)
            t += load_unload
            overhead.append(pallet_id)
            number_of_pallet += 1

    truckdeparture(overhead, t)

    # Calculate distance traveled by the truck
    if graph.has_edge(present_stop, destination_stop):
        travel_time = shortestTravelTime(present_stop, destination_stop)
        distance_traveled = (travel_time * SPEED_KM_PER_HOUR) / 3600
        truck_distances[truckid] += distance_traveled
        truck_previous_stops[truckid] = destination_stop
        truck_trip_counts[truckid] += 1

    # Update time
    travel_time = shortestTravelTime(present_stop, destination_stop)
    t += travel_time
    cursor.execute("UPDATE truck SET present_stop=?, destination_stop=?, time=?, pallet_count=? WHERE id=?",
                   (destination_stop, next_stop, t, number_of_pallet, truckid))
    conn.commit()
    return number_of_pallet


# Supporting functions
def truckdeparture(overhead, t):
    for o in overhead:
        cursor.execute("SELECT * FROM pallet WHERE id=?", (o,))
        p = cursor.fetchone()
        delivery_delay = p[8] + (t - p[1])
        cursor.execute("UPDATE pallet SET truck_departure=?, delivery_delay=? WHERE id=?", (t, delivery_delay, o))
        conn.commit()


def deboard(pallet_id, t):
    cursor.execute("UPDATE pallet SET flag=?, departure_time=?, reached=? WHERE id=?", (0, t, 1, pallet_id))
    conn.commit()


def deboard_at_junction(pallet_id, present_stop, t):
    cursor.execute("UPDATE pallet SET arrival_stop=?, flag=?, arrival_time=? WHERE id=?",
                   (present_stop, 0, t, pallet_id))
    conn.commit()


def board(pallet_id, t, delivery_delay, arrival_time, truckid):
    cursor.execute("UPDATE pallet SET flag=?, truck_id=? WHERE id=?", (1, truckid, pallet_id))
    conn.commit()


def findnext(s, present_stop, destination_stop):
    for i in range(len(s)):
        if s[i] == present_stop:
            if i + 1 < len(s) and s[i + 1] == destination_stop:
                return 1
    return 0


# Alternative method to save data using pandas
def save_to_csv(total_pallet_count, capacity):
    filename = f"exp2_palletdata_{capacity}_{total_pallet_count}.csv"  # Changed to exp2
    try:
        df = pd.read_sql_query("SELECT * FROM pallet", conn)
        df.to_csv(filename, index=False)
        print(f"Final dataset saved to {filename}")
    except Exception as e:
        print(f"Error saving CSV file {filename}: {e}")


# Modified function to log cost value to SQLite tables and calculate avg_delivery_delay
def log_cost_value(total_distance_all_truckes, total_pallet_count, capacity):
    table_name = f"exp2_{capacity}_costdata"  # Changed to exp2
    total_units_of_energy = total_distance_all_truckes * 1.35
    cursor.execute("SELECT SUM(distance) FROM pallet")
    total_person_km_travelled = cursor.fetchone()[0] or 0
    cost_value = total_units_of_energy / total_person_km_travelled if total_person_km_travelled > 0 else 0

    # Calculate average waiting time
    cursor.execute("SELECT AVG(delivery_delay) FROM pallet")
    avg_delivery_delay = cursor.fetchone()[0] or 0

    # Check if the pallet count already exists in the table
    cursor.execute(f"SELECT number_of_pallets FROM {table_name} WHERE number_of_pallets = ?",
                   (total_pallet_count,))
    existing_entry = cursor.fetchone()

    if existing_entry:
        # Update existing row
        cursor.execute(f'''
            UPDATE {table_name}
            SET cost_value = ?
            WHERE number_of_pallets = ?
        ''', (cost_value, total_pallet_count))
        action = "updated"
    else:
        # Insert new row
        cursor.execute(f'''
            INSERT INTO {table_name} (number_of_pallets, cost_value)
            VALUES (?, ?)
        ''', (total_pallet_count, cost_value))
        action = "appended"

    conn.commit()
    print(f"Cost value {action} in {table_name} for {total_pallet_count} pallets: {cost_value:.4f}")

    return cost_value, avg_delivery_delay


# Main simulation function
def main_simulation(total_pallet_count, capacity):
    reset_pallet_table()
    initialize_truck_table()
    truck_distances.update(truck_distances_update)
    truck_previous_stops.update(truck_previous_stops_update)
    truck_trip_counts.update(truck_trip_counts_update)

    # Set random seed for reproducibility
    random.seed(total_pallet_count)
    np.random.seed(total_pallet_count)  # Seed numpy's random number generator too
    pairs = list(permutations(elements, 2))
    num_pairs = len(pairs)

    for i in range(total_pallet_count):
        pair = pairs[i % num_pairs]
        arrival_stop, destination_stop = pair
        arrival_time = generate_bimodal_truck_arrival_time()  # Use new bimodal function
        path = shortestPath(arrival_stop, destination_stop)
        cursor.execute(
            "INSERT INTO pallet (arrival_time, arrival_stop, destination_stop, truck_departure, departure_time, flag, path, delivery_delay, truck_id, reached, t, distance) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (arrival_time, arrival_stop, destination_stop, 0, 0, 0, path, 0, 0, 0, arrival_time, 0)
        )
    conn.commit()
    print(f"{total_pallet_count} pallets added successfully for capacity {capacity}.")
    calculate_distance_for_pallets()

    # Debug: Verify initial pallet state
    cursor.execute("SELECT COUNT(*) FROM pallet WHERE reached=0")
    initial_remaining = cursor.fetchone()[0]
    print(f"Initial pallets with reached=0: {initial_remaining}")

    i = 2
    maxi = 0
    while True:
        cursor.execute("SELECT COUNT(*) FROM pallet WHERE reached=0")
        remaining_pallets = cursor.fetchone()[0]
        print(f"Remaining pallets: {remaining_pallets}")
        if remaining_pallets == 0:
            total_distance_all_truckes = sum(truck_distances.values())
            cost_value, avg_delivery_delay = log_cost_value(total_distance_all_truckes, total_pallet_count, capacity)
            print(f"Debug: total_pallet_count before save_to_csv = {total_pallet_count}")
            save_to_csv(total_pallet_count, capacity)
            print(f"Debug: total_pallet_count before results = {total_pallet_count}")
            print(f"\nResults for {total_pallet_count} pallets with capacity {capacity}:")
            print(f"Total distance traveled by each truck (in km):")
            for truckid, distance_in_km in truck_distances.items():
                print(f"truck {truckid}: {distance_in_km:.2f} km (Trips: {truck_trip_counts[truckid]})")
            print(f"Total distance traveled by all truckes: {total_distance_all_truckes:.2f} km")
            print(f"Total trips by all truckes: {sum(truck_trip_counts.values())}")
            print(f"Cost value: {cost_value:.4f}")
            print(f"Average waiting time: {avg_delivery_delay:.2f} seconds")
            print(f"Maximum pallets on any truck: {maxi}")
            break

        cursor.execute("SELECT * FROM truck ORDER BY time")
        truckes = cursor.fetchall()
        if not truckes:
            print("No truckes found in the database! Check truck table initialization.")
            break
        print(f"Found {len(truckes)} truckes to process.")
        for truck in truckes:
            truckid, present_stop, destination_stop, t, path, truck_pallet_count = truck
            print(f"Processing truck {truckid} at {t}, Current stop: {present_stop}, Destination: {destination_stop}")
            truck_path = truck_paths.get(path)

            if truck_path:
                next_stop = truck_path[i % len(truck_path)]
                truck_pallet_count = truckfunction(
                    truckid, present_stop, destination_stop, next_stop,
                    truck_path, t, truck_pallet_count, capacity
                )
            else:
                print(f"Warning: Unknown path '{path}' for truck ID {truckid}")
            maxi = max(maxi, truck_pallet_count)
        i += 1


# Using pallet counts and capacities from commonCoordinates

for pallet_count in pallet_counts:
    for capacity in capacities:
        print(f"\nStarting simulation for {pallet_count} pallets with capacity {capacity}...")
        main_simulation(pallet_count, capacity)

conn.close()