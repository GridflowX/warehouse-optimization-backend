from itertools import permutations
import random
import networkx as nx
import sqlite3
import pandas as pd
import os
from datetime import datetime
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from commonCoordinates import time_edges, SPEED_KM_PER_HOUR, load_unload, distance_edges, stops, truck_routes_1, truck_routes_2, truck_routes_3, truck_routes_4, truck_routes_5, pallet_counts, capacities, truck_distances, truck_previous_stops, truck_trip_counts, start_node, stop_node, paths, truck_paths, truck_distances_update, truck_previous_stops_update, truck_trip_counts_update, outskirt_stop, central_stops

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

# Function to generate random arrival time
def generate_random_arrival_time():
    return random.randint(0, 64800)  # Full day (midnight to 6 PM)

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
    cursor.execute("SELECT * FROM pallet WHERE flag=? AND destination_stop=? AND truck_id=?", (1, present_stop, truckid))
    p_update = cursor.fetchall()
    print(f"truck {truckid} at {present_stop}: Found {len(p_update)} pallets to unload.")
    for p in p_update:
        pallet_id = p[0]
        unload(pallet_id, t)
        t += load_unload
        number_of_pallet -= 1
    cursor.execute("SELECT * FROM pallet WHERE flag=? AND destination_stop!=? AND truck_id=?",
                   (1, present_stop, truckid))
    p_update = cursor.fetchall()
    junction_unloads = 0
    for p in p_update:
        pallet_id = p[0]
        if findnext(p[7], present_stop, destination_stop) == 0:
            unload_at_junction(pallet_id, present_stop, t)
            t += load_unload
            number_of_pallet -= 1
            junction_unloads += 1
    print(f"truck {truckid} at {present_stop}: Unloaded {junction_unloads} pallets at junction.")
    cursor.execute("SELECT * FROM pallet WHERE arrival_time<=? AND flag=? AND arrival_stop=? AND reached=?",
                   (t, 0, present_stop, 0))
    p_update = cursor.fetchall()
    print(f"truck {truckid} at {present_stop}: Found {len(p_update)} pallets to load.")
    for p in p_update:
        pallet_id = p[0]
        if findnext(p[7], present_stop, destination_stop) == 1 and number_of_pallet < capacity:
            load(pallet_id, t, p[8], p[1], truckid)
            t += load_unload
            overhead.append(pallet_id)
            number_of_pallet += 1
    truckdeparture(overhead, t)
    if graph.has_edge(present_stop, destination_stop):
        travel_time = shortestTravelTime(present_stop, destination_stop)
        distance_traveled = (travel_time * SPEED_KM_PER_HOUR) / 3600
        truck_distances[truckid] += distance_traveled
        truck_previous_stops[truckid] = destination_stop
        truck_trip_counts[truckid] += 1
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

def unload(pallet_id, t):
    cursor.execute("UPDATE pallet SET flag=?, departure_time=?, reached=? WHERE id=?", (0, t, 1, pallet_id))
    conn.commit()

def unload_at_junction(pallet_id, present_stop, t):
    cursor.execute("UPDATE pallet SET arrival_stop=?, flag=?, arrival_time=? WHERE id=?",
                   (present_stop, 0, t, pallet_id))
    conn.commit()

def load(pallet_id, t, delivery_delay, arrival_time, truckid):
    cursor.execute("UPDATE pallet SET flag=?, truck_id=? WHERE id=?", (1, truckid, pallet_id))
    conn.commit()

def findnext(s, present_stop, destination_stop):
    for i in range(len(s)):
        if s[i] == present_stop:
            if i + 1 < len(s) and s[i + 1] == destination_stop:
                return 1
    return 0

# Modified save_to_csv to include additional column processing
def save_to_csv(total_pallet_count, capacity):
    filename = f"exp3_palletdata_{capacity}_{total_pallet_count}.csv"
    try:
        df = pd.read_sql_query("SELECT * FROM pallet", conn)
        df['journey_time'] = df['departure_time'] - df['truck_departure']
        df['total_journey_time'] = df['journey_time'] + df['delivery_delay']
        df = df[df['total_journey_time'] > 0]
        df['delivery_delay_percentage'] = (df['delivery_delay'] / df['total_journey_time']) * 100
        df['delivery_delay_percentage'] = pd.to_numeric(df['delivery_delay_percentage'], errors='coerce').round(2)
        df['waiting_journey_ratio'] = pd.to_numeric(df['delivery_delay'] / df['journey_time'], errors='coerce').round(2)
        df.to_csv(filename, index=False)
        print(f"Final dataset with additional columns saved to {filename}")
    except Exception as e:
        print(f"Error saving CSV file {filename}: {e}")

# Modified log_cost_value for exp3
def log_cost_value(total_distance_all_trucks, total_pallet_count, capacity):
    table_name = f"exp3_{capacity}_costdata"
    total_units_of_energy = total_distance_all_trucks * 1.35
    cursor.execute("SELECT SUM(distance) FROM pallet")
    total_person_km_travelled = cursor.fetchone()[0] or 0
    cost_value = total_units_of_energy / total_person_km_travelled if total_person_km_travelled > 0 else 0
    cursor.execute("SELECT AVG(delivery_delay) FROM pallet")
    avg_delivery_delay = cursor.fetchone()[0] or 0
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            number_of_pallets INTEGER PRIMARY KEY,
            cost_value REAL
        )
    ''')
    cursor.execute(f"SELECT number_of_pallets FROM {table_name} WHERE number_of_pallets = ?", (total_pallet_count,))
    existing_entry = cursor.fetchone()
    if existing_entry:
        cursor.execute(f'''
            UPDATE {table_name}
            SET cost_value = ?
            WHERE number_of_pallets = ?
        ''', (cost_value, total_pallet_count))
        action = "updated"
    else:
        cursor.execute(f'''
            INSERT INTO {table_name} (number_of_pallets, cost_value)
            VALUES (?, ?)
        ''', (total_pallet_count, cost_value))
        action = "appended"
    conn.commit()
    print(f"Cost value {action} in {table_name} for {total_pallet_count} pallets: {cost_value:.4f}")
    return cost_value, avg_delivery_delay

# Modified main_simulation for exp3 with validation
def main_simulation(total_pallet_count, capacity):
    reset_pallet_table()
    initialize_truck_table()
    truck_distances.update(truck_distances_update)
    truck_previous_stops.update(truck_previous_stops_update)
    truck_trip_counts.update(truck_trip_counts_update)
    random.seed(total_pallet_count + 10)
    outskirts_stops = outskirt_stop
    central_stop = central_stops
    b_destined_pallets = int(total_pallet_count * 0.7)
    other_destined_pallets = total_pallet_count - b_destined_pallets
    for i in range(b_destined_pallets):
        arrival_stop = random.choice(outskirts_stops)
        destination_stop = central_stop
        arrival_time = generate_random_arrival_time()
        path = shortestPath(arrival_stop, destination_stop)
        cursor.execute(
            "INSERT INTO pallet (arrival_time, arrival_stop, destination_stop, truck_departure, departure_time, flag, path, delivery_delay, truck_id, reached, t, distance) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (arrival_time, arrival_stop, destination_stop, 0, 0, 0, path, 0, 0, 0, arrival_time, 0)
        )
    for i in range(other_destined_pallets):
        while True:
            arrival_stop = random.choice(outskirts_stops)
            destination_stop = random.choice([stop for stop in elements if stop != arrival_stop and stop != central_stop])
            if arrival_stop != destination_stop:
                break
        arrival_time = generate_random_arrival_time()
        path = shortestPath(arrival_stop, destination_stop)
        cursor.execute(
            "INSERT INTO pallet (arrival_time, arrival_stop, destination_stop, truck_departure, departure_time, flag, path, delivery_delay, truck_id, reached, t, distance) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (arrival_time, arrival_stop, destination_stop, 0, 0, 0, path, 0, 0, 0, arrival_time, 0)
        )
    conn.commit()
    print(f"{total_pallet_count} pallets added successfully for capacity {capacity} (70% destined to 'B', 30% to others).")
    calculate_distance_for_pallets()
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
            total_distance_all_trucks = sum(truck_distances.values())
            cost_value, avg_delivery_delay = log_cost_value(total_distance_all_trucks, total_pallet_count, capacity)
            save_to_csv(total_pallet_count, capacity)
            print(f"\nResults for {total_pallet_count} pallets with capacity {capacity}:")
            print(f"Total distance traveled by each truck (in km):")
            for truckid, distance_in_km in truck_distances.items():
                print(f"truck {truckid}: {distance_in_km:.2f} km (Trips: {truck_trip_counts[truckid]})")
            print(f"Total distance traveled by all trucks: {total_distance_all_trucks:.2f} km")
            print(f"Total trips by all trucks: {sum(truck_trip_counts.values())}")
            print(f"Cost value: {cost_value:.4f}")
            print(f"Average waiting time: {avg_delivery_delay:.2f} seconds")
            print(f"Maximum pallets on any truck: {maxi}")
            break
        cursor.execute("SELECT * FROM truck ORDER BY time")
        trucks = cursor.fetchall()
        if not trucks:
            print("No trucks found in the database! Check truck table initialization.")
            print("No trucks found in the database! Check truck table initialization.")
            break
        print(f"Found {len(trucks)} trucks to process.")
        for truck in trucks:
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

for pallet_count in pallet_counts:
    for capacity in capacities:
        print(f"\nStarting exp3 simulation for {pallet_count} pallets with capacity {capacity}...")
        main_simulation(pallet_count, capacity)

conn.close()