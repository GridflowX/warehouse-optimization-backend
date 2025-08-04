from itertools import permutations
import random
import networkx as nx
import sqlite3
import csv
import numpy as np  # For generating bimodal Gaussian distribution
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from commonCoordinates import time_edges, distance_edges, stops, minimum_distance, load_unload, pallet_counts

current_dir = os.path.dirname(os.path.abspath(__file__))

# Initialize database connection
conn = sqlite3.connect(os.path.join(current_dir, 'collide.db'))
cursor = conn.cursor()

# Initialize the time-based graph
graph = nx.Graph()

# Define all edges with time weights
for u, v, w in time_edges:
    graph.add_edge(u, v, weight=w)

# Initialize the distance-based graph (for distance calculation)
distance_graph = nx.Graph()
for u, v, w in distance_edges:
    distance_graph.add_edge(u, v, weight=w)

# Output files for exp2
output_files = [f"{count}_exp2.csv" for count in pallet_counts]

# Utility functions
def generate_bimodal_arrival_time():
    mean1, mean2 = 28800, 64800  # 8 AM and 6 PM in seconds
    stddev1, stddev2 = 6840, 3600
    return int(np.random.normal(mean1, stddev1)) if random.choice([1, 2]) == 1 else int(np.random.normal(mean2, stddev2))

def shortestPath(src, dest):
    return nx.dijkstra_path_length(graph, src, dest, weight='weight')

def distancePath(src, dest):
    return nx.dijkstra_path_length(distance_graph, src, dest, weight='weight')

def collision(comming_to_stop, time, stop, pid):
    for c in comming_to_stop:
        _, _, _, start_time, stop_time, _ = c
        if abs(start_time - time) < minimum_distance:
            time = start_time + minimum_distance
    return time

def emptygoodspod(stop, src, final_goodspod, present_start_time):
    path = nx.dijkstra_path(graph, stop, src, weight='weight')
    id, _, _, _ = final_goodspod
    for i in range(len(path) - 1):
        cursor.execute("SELECT * FROM journey WHERE src = ? AND start_time >= ? ORDER BY start_time",
                       (path[i], present_start_time - minimum_distance))
        coming_to_stop = cursor.fetchall()
        present_start_time = collision(coming_to_stop, present_start_time, path[i], id)
        present_stop_time = present_start_time + shortestPath(path[i], path[i + 1])
        cursor.execute("INSERT INTO journey (src, dest, start_time, stop_time, pid) VALUES (?, ?, ?, ?, ?)",
                       (path[i], path[i + 1], present_start_time, present_stop_time, id))
        conn.commit()
        present_start_time = present_stop_time
    return present_start_time

def pick(pallet_id, arrival_time, src, dest, path):
    min_time = float('inf')
    final_goodspod = None
    goodspod_departure = 0
    for stop in stops:
        goodspod = check_at_stop(stop)
        if goodspod:
            id, _, _, stop_time = goodspod
            weight = shortestPath(stop, src)
            if stop != src:
                if stop_time > arrival_time:
                    if stop_time + weight < min_time:
                        final_goodspod = goodspod
                        min_time = stop_time + weight
                else:
                    if arrival_time + weight < min_time:
                        final_goodspod = goodspod
                        min_time = arrival_time + weight
            else:
                if stop_time < min_time:
                    final_goodspod = goodspod
                    min_time = stop_time
    if not final_goodspod:
        return
    id, stop, _, time = final_goodspod
    travel_time = shortestPath(src, dest)
    if stop != src:
        goodspod_departure = emptygoodspod(stop, src, final_goodspod, max(arrival_time, time))
    else:
        goodspod_departure = max(arrival_time, time)
    present_start_time = goodspod_departure
    for i in range(len(path) - 1):
        cursor.execute("SELECT * FROM journey WHERE src = ? AND start_time >= ? ORDER BY start_time",
                       (path[i], present_start_time - minimum_distance))
        coming_to_stop = cursor.fetchall()
        present_start_time = collision(coming_to_stop, present_start_time, path[i], pallet_id)
        present_stop_time = present_start_time + shortestPath(path[i], path[i + 1])
        cursor.execute("INSERT INTO journey (src, dest, start_time, stop_time, pid) VALUES (?, ?, ?, ?, ?)",
                       (path[i], path[i + 1], present_start_time, present_stop_time, pallet_id))
        conn.commit()
        present_start_time = present_stop_time
    final_time = present_start_time + load_unload * 2
    cursor.execute("UPDATE goodspod SET time = ?, current_stop = ?, destination_stop = ? WHERE id = ?",
                   (final_time, dest, dest, id))
    conn.commit()
    cursor.execute("UPDATE pallet SET departure_time = ?, flag = 1, goodspod_departure = ? WHERE pid = ?",
                   (final_time, goodspod_departure, pallet_id))
    cursor.execute("UPDATE pallet SET delivery_delay = ? WHERE pid = ?",
                   (goodspod_departure - arrival_time, pallet_id))
    conn.commit()

def check_at_stop(stop):
    cursor.execute(
        "SELECT * FROM goodspod WHERE current_stop = ? AND destination_stop = ? "
        "AND time IN (SELECT MIN(time) FROM goodspod WHERE current_stop = ? AND destination_stop = ?)",
        (stop, stop, stop, stop))
    return cursor.fetchone()

# Process each pallet count individually
for pallet_count, output_file in zip(pallet_counts, output_files):
    cursor.execute("DELETE FROM JOURNEY")
    cursor.execute("DROP TABLE IF EXISTS pallet")
    cursor.execute("""
    CREATE TABLE pallet (
        pid INTEGER PRIMARY KEY,
        arrival_stop TEXT,
        destination_stop TEXT,
        arrival_time INTEGER,
        departure_time INTEGER,
        flag INTEGER,
        goodspod_departure INTEGER,
        from_stop TEXT,
        path TEXT,
        travel_time INTEGER,
        delivery_delay INTEGER
    )
    """)
    cursor.execute("UPDATE goodspod SET TIME = 0")

    # Generate pallets for this set
    for _ in range(pallet_count):
        arrival_stop, destination_stop = random.sample(stops, 2)
        arrival_time = generate_bimodal_arrival_time()
        path = ''.join(nx.dijkstra_path(graph, arrival_stop, destination_stop, weight='weight'))
        travel_time = shortestPath(arrival_stop, destination_stop)
        cursor.execute(
            "INSERT INTO pallet (arrival_stop, destination_stop, arrival_time, departure_time, flag, goodspod_departure, from_stop, path, travel_time, delivery_delay) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (arrival_stop, destination_stop, arrival_time, 0, 0, 0, None, path, travel_time, 0)
        )
    conn.commit()

    # Process pallets
    while True:
        cursor.execute("SELECT * FROM pallet WHERE flag = 0 AND departure_time = 0 ORDER BY arrival_time")
        pallets = cursor.fetchall()
        if not pallets:
            break
        for pallet in pallets:
            pid, cstop, dest, t, _, _, _, _, path, _, _ = pallet
            pick(pid, t, cstop, dest, path)

    # Export to CSV with new columns
    cursor.execute("SELECT * FROM pallet")
    rows = cursor.fetchall()
    with open(output_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(
            ['pid', 'arrival_stop', 'destination_stop', 'arrival_time', 'departure_time', 'flag', 'goodspod_departure',
             'from_stop', 'path', 'travel_time', 'delivery_delay', 'destination_time', 'distance'])
        for row in rows:
            pid, arr_stop, dest_stop, arr_time, dep_time, flag, goodspod_dep, from_stop, path_str, travel_time, wait_time = row
            destination_time = arr_time + travel_time
            distance = distancePath(arr_stop, dest_stop)
            csvwriter.writerow([
                pid, arr_stop, dest_stop, arr_time, dep_time, flag, goodspod_dep, from_stop, path_str,
                travel_time, wait_time, destination_time, distance
            ])

    print(f"Exported {pallet_count} pallets to {output_file}.")

# Close database connection
conn.commit()
conn.close()
print("Database operations completed successfully.")