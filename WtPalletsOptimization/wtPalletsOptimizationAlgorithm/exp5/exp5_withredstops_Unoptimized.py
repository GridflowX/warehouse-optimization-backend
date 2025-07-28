from itertools import permutations
import random
import networkx as nx
import sqlite3
import csv
import math

# Initialize database connection
conn = sqlite3.connect('collide.db')
cursor = conn.cursor()

# Initialize the graph
graph = nx.Graph()

# Full stops list for passenger distribution and pod placement
stops = ['A', 'B', 'C', 'D', 'P', 'Q', 'R', 'S', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']

# Intermediate node set
intermediate_nodes = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

# Stop coordinates
stop_coordinates = {
    'A': (-12.55, 3.36), 'B': (0, 0), 'C': (0, -7), 'D': (14.75, -15.5),
    'P': (4.35, 10.98), 'Q': (0, 20), 'R': (-14.5, -3.88), 'S': (-14.48, -8.88),
    '1': (-8.14, 13.72), '2': (7.98, 18.40), '3': (11.128, -5.194),
    '4': (-6.01, -11.99), '5': (-2.78, 7.66), '6': (4.128, -12.109),
    '7': (9.17, 14.60), '8': (0.54, 13.36), '9': (-12.94, -15.2), '10': (-5.41, -3.71),
    'a': (0, 13.72), 'b': (2.32, 15.63), 'c': (7.563, -11.368), 'd': (0, 7.66),
    'e': (5.306, -10.064), 'f': (3.84, 12.03), 'g': (2.85, 14.47), 'h': (-5.974, -1.60)
}

# Original edges
graph.add_edge('A', 'B', weight=1170)
graph.add_edge('B', 'Q', weight=1800)
graph.add_edge('B', 'C', weight=630)
graph.add_edge('B', 'R', weight=1350)
graph.add_edge('C', 'D', weight=1530)
graph.add_edge('P', 'Q', weight=900)
graph.add_edge('R', 'S', weight=450)

# Intermediate edges
graph.add_edge('Q', 'a', weight=564.4)
graph.add_edge('a', 'd', weight=545.9)
graph.add_edge('d', 'B', weight=688.9)
graph.add_edge('B', 'h', weight=557.2)
graph.add_edge('R', 'h', weight=794.5)
graph.add_edge('C', 'e', weight=550.8)
graph.add_edge('e', 'c', weight=234.5)
graph.add_edge('c', 'D', weight=745.4)
graph.add_edge('Q', 'b', weight=499.5)
graph.add_edge('g', 'b', weight=45)
graph.add_edge('g', 'f', weight=232.6)
graph.add_edge('f', 'P', weight=124.6)
graph.add_edge('1', 'a', weight=732.6)
graph.add_edge('5', 'd', weight=250.3)
graph.add_edge('2', 'b', weight=567.0)
graph.add_edge('8', 'g', weight=230.6)
graph.add_edge('7', 'f', weight=532.8)
graph.add_edge('10', 'h', weight=196.3)
graph.add_edge('9', 'S', weight=585.5)
graph.add_edge('4', 'C', weight=702.7)
graph.add_edge('6', 'e', weight=212.6)
graph.add_edge('3', 'c', weight=640.7)

# Global constants
minimum_distance = 4
board_deboard = 4
walking_speed = 1.39
pod_speed = 11.11

passenger_counts = [392, 896, 2968, 4032, 5040, 7952]
output_files = [f"{count}_exp5_blue_red.csv" for count in passenger_counts]

def euclidean_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def nearest_stop(x, y):
    min_distance = float('inf')
    nearest = None
    for stop, (sx, sy) in stop_coordinates.items():
        dist = euclidean_distance(x, y, sx, sy)
        if dist < min_distance:
            min_distance = dist
            nearest = stop
    return nearest, min_distance

def generate_coordinates():
    while True:
        x1, y1 = random.randint(-1500, 1500) / 100, random.randint(-1600, 2000) / 100
        x2, y2 = random.randint(-1500, 1500) / 100, random.randint(-1600, 2000) / 100

        dist = euclidean_distance(x1, y1, x2, y2)
        arrival, d1 = nearest_stop(x1, y1)
        dest, d2 = nearest_stop(x2, y2)

        if arrival in intermediate_nodes or dest in intermediate_nodes:
            continue
        if arrival != dest and dist > euclidean_distance(*stop_coordinates[arrival], *stop_coordinates[dest]):
            return arrival, dest, x1, y1, x2, y2, d1, d2

def generate_random_arrival_time():
    return random.randint(6 * 3600, 24 * 3600)

def shortestPath(src, dest):
    return nx.dijkstra_path_length(graph, src, dest, weight='weight')

def collision(comming_to_stop, time, stop, pid):
    if stop in stops:
        for c in comming_to_stop:
            _, _, _, start_time, stop_time, _ = c
            if abs(start_time - time) < minimum_distance:
                time = start_time + minimum_distance
    return time

def emptypod(stop, src, final_pod, present_start_time):
    path = nx.dijkstra_path(graph, stop, src, weight='weight')
    id, _, _, _ = final_pod
    for i in range(len(path) - 1):
        if path[i] in stops:
            cursor.execute("SELECT * FROM journey WHERE src = ? AND start_time >= ? ORDER BY start_time",
                           (path[i], present_start_time - minimum_distance))
            coming = cursor.fetchall()
            present_start_time = collision(coming, present_start_time, path[i], id)
        present_stop_time = present_start_time + shortestPath(path[i], path[i + 1])
        cursor.execute("INSERT INTO journey (src, dest, start_time, stop_time, pid) VALUES (?, ?, ?, ?, ?)",
                       (path[i], path[i + 1], present_start_time, present_stop_time, id))
        conn.commit()
        present_start_time = present_stop_time
    return present_start_time

def pick(passenger_id, arrival_time, src, dest, path, walking_time, total_travel_time):
    min_arrival_time = float('inf')
    final_pod = None
    pod_departure = 0

    try:
        if not nx.has_path(graph, src, dest):
            paths = []
            for i_node in intermediate_nodes:
                if nx.has_path(graph, src, i_node) and nx.has_path(graph, i_node, dest):
                    paths.append((src, i_node, dest))
            if paths:
                path = min(paths, key=lambda p: shortestPath(p[0], p[1]) + shortestPath(p[1], p[2]))
            else:
                return
        else:
            path = (src, dest)

        for stop in [src, dest] + [s for s in stops if s not in [src, dest]]:
            cursor.execute("SELECT * FROM pod WHERE current_stop = ? AND destination_stop = ?", (stop, stop))
            for pod in cursor.fetchall():
                id, _, _, stop_time = pod
                weight = shortestPath(stop, src)
                arrival_at_src = max(stop_time, arrival_time) + weight
                if arrival_at_src < min_arrival_time:
                    min_arrival_time = arrival_at_src
                    final_pod = pod

    except nx.NetworkXNoPath:
        return

    if not final_pod:
        return

    id, stop, _, time = final_pod
    travel_time = shortestPath(src, dest)

    pod_departure = emptypod(stop, src, final_pod, max(arrival_time, time)) if stop != src else max(arrival_time, time)

    waiting_time = pod_departure - arrival_time
    total_travel_time = walking_time + travel_time + waiting_time

    present_start_time = pod_departure
    for i in range(len(path) - 1):
        if path[i] in stops:
            cursor.execute("SELECT * FROM journey WHERE src = ? AND start_time >= ? ORDER BY start_time",
                           (path[i], present_start_time - minimum_distance))
            coming = cursor.fetchall()
            present_start_time = collision(coming, present_start_time, path[i], passenger_id)
        stop_time = present_start_time + shortestPath(path[i], path[i + 1])
        cursor.execute("INSERT INTO journey (src, dest, start_time, stop_time, pid) VALUES (?, ?, ?, ?, ?)",
                       (path[i], path[i + 1], present_start_time, stop_time, passenger_id))
        conn.commit()
        present_start_time = stop_time

    final_time = present_start_time + board_deboard * 2
    cursor.execute("UPDATE pod SET time = ?, current_stop = ?, destination_stop = ? WHERE id = ?",
                   (final_time, dest, dest, id))
    conn.commit()
    cursor.execute(
        "UPDATE passenger SET departure_time = ?, flag = 1, pod_departure = ?, walking_time = ?, waiting_time = ?, total_travel_time = ? WHERE pid = ?",
        (final_time, pod_departure, walking_time, waiting_time, total_travel_time, passenger_id))
    conn.commit()

# Main loop
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
            x1 REAL, y1 REAL, x2 REAL, y2 REAL,
            walking_time REAL,
            waiting_time INTEGER,
            total_travel_time REAL,
            traveltime INTEGER
        )
    """)
    cursor.execute("DROP TABLE IF EXISTS journey")
    cursor.execute("""
        CREATE TABLE journey (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            src TEXT,
            dest TEXT,
            start_time INTEGER,
            stop_time INTEGER,
            pid INTEGER NOT NULL
        )
    """)
    cursor.execute("UPDATE pod SET time = 0")

    for _ in range(passenger_count):
        arrival_stop, destination_stop, x1, y1, x2, y2, d1, d2 = generate_coordinates()
        arrival_time = generate_random_arrival_time()
        path = ''.join(nx.dijkstra_path(graph, arrival_stop, destination_stop, weight='weight'))
        s_walk_time = 1000 * d1 / walking_speed
        d_walk_time = 1000 * d2 / walking_speed
        walking_time = s_walk_time + d_walk_time
        traveltime = shortestPath(arrival_stop, destination_stop)

        cursor.execute("""
            INSERT INTO passenger (arrival_stop, destination_stop, arrival_time, departure_time, flag, pod_departure,
                from_stop, path, x1, y1, x2, y2, walking_time, waiting_time, total_travel_time, traveltime)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (arrival_stop, destination_stop, arrival_time, 0, 0, 0, None, path, x1, y1, x2, y2,
              walking_time, 0, 0, traveltime))
    conn.commit()

    while True:
        cursor.execute("SELECT * FROM passenger WHERE flag = 0 AND departure_time = 0 ORDER BY arrival_time")
        passengers = cursor.fetchall()
        if not passengers:
            break
        for passenger in passengers:
            pid, src, dest, t, *_rest, path, x1, y1, x2, y2, walking_time, waiting_time, total_travel_time, traveltime = passenger
            pick(pid, t, src, dest, path, walking_time, total_travel_time)

    cursor.execute("SELECT * FROM passenger")
    rows = cursor.fetchall()
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'pid', 'arrival_stop', 'destination_stop', 'arrival_time', 'departure_time', 'flag',
            'pod_departure', 'from_stop', 'path', 'x1', 'y1', 'x2', 'y2',
            'walking_time', 'waiting_time', 'total_travel_time', 'traveltime', 'destination_time', 'distance'
        ])
        for row in rows:
            destination_time = row[3] + row[15]
            distance = row[16] + row[13]
            writer.writerow(list(row) + [destination_time, distance])

    cursor.execute("SELECT AVG(waiting_time) FROM passenger WHERE waiting_time IS NOT NULL")
    avg_waiting = cursor.fetchone()[0]
    print(f"Average waiting time for {passenger_count} passengers: {avg_waiting:.2f} seconds")
    print(f"Exported {passenger_count} passengers to {output_file}.")

conn.commit()
conn.close()
print("Database operations completed successfully.")