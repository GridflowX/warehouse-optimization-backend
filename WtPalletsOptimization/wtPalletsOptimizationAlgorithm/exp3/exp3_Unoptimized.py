import random
import networkx as nx
import sqlite3
import csv
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from commonCoordinates import time_edges, distance_edges, stops, minimum_distance, board_deboard, passenger_counts, desti_stop

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

# Output files for exp3
output_files = [f"{count}_exp3.csv" for count in passenger_counts]

# Utility functions
def generate_uniform_arrival_time():
    start_time = 6 * 3600
    end_time = 24 * 3600
    return random.randint(start_time, end_time)

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

def emptypod(stop, src, final_pod, present_start_time):
    path = nx.dijkstra_path(graph, stop, src, weight='weight')
    id, _, _, _ = final_pod
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

def pick(passenger_id, arrival_time, src, dest, path):
    min_time = float('inf')
    final_pod = None
    pod_departure = 0
    for stop in stops:
        pod = check_at_stop(stop)
        if pod:
            id, _, _, stop_time = pod
            weight = shortestPath(stop, src)
            if stop != src:
                if stop_time > arrival_time:
                    if stop_time + weight < min_time:
                        final_pod = pod
                        min_time = stop_time + weight
                else:
                    if arrival_time + weight < min_time:
                        final_pod = pod
                        min_time = arrival_time + weight
            else:
                if stop_time < min_time:
                    final_pod = pod
                    min_time = stop_time
    if not final_pod:
        return
    id, stop, _, time = final_pod
    travel_time = shortestPath(src, dest)
    if stop != src:
        pod_departure = emptypod(stop, src, final_pod, max(arrival_time, time))
    else:
        pod_departure = max(arrival_time, time)
    present_start_time = pod_departure
    for i in range(len(path) - 1):
        cursor.execute("SELECT * FROM journey WHERE src = ? AND start_time >= ? ORDER BY start_time",
                       (path[i], present_start_time - minimum_distance))
        coming_to_stop = cursor.fetchall()
        present_start_time = collision(coming_to_stop, present_start_time, path[i], passenger_id)
        present_stop_time = present_start_time + shortestPath(path[i], path[i + 1])
        cursor.execute("INSERT INTO journey (src, dest, start_time, stop_time, pid) VALUES (?, ?, ?, ?, ?)",
                       (path[i], path[i + 1], present_start_time, present_stop_time, passenger_id))
        conn.commit()
        present_start_time = present_stop_time
    final_time = present_start_time + board_deboard * 2
    waiting_time = pod_departure - arrival_time
    cursor.execute("UPDATE pod SET time = ?, current_stop = ?, destination_stop = ? WHERE id = ?",
                   (final_time, dest, dest, id))
    conn.commit()
    cursor.execute("UPDATE passenger SET departure_time = ?, flag = 1, pod_departure = ?, waiting_time = ? WHERE pid = ?",
                   (final_time, pod_departure, waiting_time, passenger_id))
    conn.commit()

def check_at_stop(stop):
    cursor.execute(
        "SELECT * FROM pod WHERE current_stop = ? AND destination_stop = ? "
        "AND time IN (SELECT MIN(time) FROM pod WHERE current_stop = ? AND destination_stop = ?)",
        (stop, stop, stop, stop))
    return cursor.fetchone()

# Main simulation loop
for passenger_count, output_file in zip(passenger_counts, output_files):
    cursor.execute("DELETE FROM JOURNEY")
    cursor.execute("DROP TABLE IF EXISTS passenger")
    cursor.execute("""
    CREATE TABLE passenger (
        pid INTEGER PRIMARY KEY,
        arrival_stop TEXT,
        destination_stop TEXT,
        arrival_time INTEGER,
        departure_time INTEGER,
        flag INTEGER,
        pod_departure INTEGER,
        from_stop TEXT,
        path TEXT,
        traveltime INTEGER,
        waiting_time INTEGER
    )
    """)
    cursor.execute("UPDATE POD SET TIME = 0")

    # Generate passengers
    for pid in range(passenger_count):
        arrival_stop = random.choice(stops)
        if random.random() <= 0.7:
            destination_stop = desti_stop if arrival_stop != desti_stop else random.choice([stop for stop in stops if stop != arrival_stop])
        else:
            destination_stop = random.choice([stop for stop in stops if stop != arrival_stop])
        arrival_time = generate_uniform_arrival_time()
        travel_time = shortestPath(arrival_stop, destination_stop)
        path = ''.join(nx.dijkstra_path(graph, arrival_stop, destination_stop, weight='weight'))
        cursor.execute(
            "INSERT INTO passenger (arrival_stop, destination_stop, arrival_time, departure_time, flag, pod_departure, from_stop, path, traveltime, waiting_time) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (arrival_stop, destination_stop, arrival_time, 0, 0, 0, None, path, travel_time, 0)
        )
    conn.commit()

    # Process passengers
    while True:
        cursor.execute("SELECT * FROM passenger WHERE flag = 0 AND departure_time = 0 ORDER BY arrival_time")
        passengers = cursor.fetchall()
        if not passengers:
            break
        for passenger in passengers:
            pid, cstop, dest, t, _, _, _, _, path, _, _ = passenger
            pick(pid, t, cstop, dest, path)

    # Export to CSV with new columns
    cursor.execute("SELECT * FROM passenger")
    rows = cursor.fetchall()
    with open(output_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([
            'pid', 'arrival_stop', 'destination_stop', 'arrival_time', 'departure_time', 'flag', 'pod_departure',
            'from_stop', 'path', 'traveltime', 'waiting_time', 'destination_time', 'distance'
        ])
        for row in rows:
            pid, arr_stop, dest_stop, arr_time, dep_time, flag, pod_dep, from_stop, path_str, travel_time, wait_time = row
            destination_time = arr_time + travel_time
            distance = distancePath(arr_stop, dest_stop)
            csvwriter.writerow([
                pid, arr_stop, dest_stop, arr_time, dep_time, flag, pod_dep, from_stop, path_str,
                travel_time, wait_time, destination_time, distance
            ])

    print(f"Exported {passenger_count} passengers to {output_file}.")

# Close database connection
conn.commit()
conn.close()
print("Experiment 3 completed successfully.")