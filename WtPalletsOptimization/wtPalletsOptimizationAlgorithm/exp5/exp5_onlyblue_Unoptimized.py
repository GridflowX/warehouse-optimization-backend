import random
import math
import networkx as nx
import sqlite3
import csv

# Initialize database connection
conn = sqlite3.connect('collide.db')
cursor = conn.cursor()

# Initialize the graph
graph = nx.Graph()

# Stops and positions (Assigning random coordinates for stops as placeholders)
stops = ['A', 'B', 'C', 'D', 'P', 'Q', 'R', 'S']
stop_coordinates = {
    'A': (-12.55, 3.36), 'B': (0, 0), 'C': (0, -7), 'D': (14.75, -15.5),
    'P': (4.35, 10.98), 'Q': (0, 20), 'R': (-14.5, -3.88), 'S': (-14.48, -8.88)
}

graph.add_edge('A', 'B', weight=1170)
graph.add_edge('B', 'Q', weight=1800)
graph.add_edge('B', 'C', weight=630)
graph.add_edge('B', 'R', weight=1350)
graph.add_edge('C', 'D', weight=1530)
graph.add_edge('P', 'Q', weight=900)
graph.add_edge('R', 'S', weight=450)

# Global constants
minimum_distance = 4
board_deboard = 4
walking_speed = 1.39  # in meters per second
pod_speed = 11.11  # in meters per second

# Passenger counts array and corresponding output file names
passenger_counts = [392, 896, 2968, 4032, 5040, 7952]
output_files = [f"{count}_exp5.csv" for count in passenger_counts]


def euclidean_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def nearest_stop(x, y):
    min_distance = float('inf')
    nearest = None
    for stop, (stop_x, stop_y) in stop_coordinates.items():
        distance = euclidean_distance(x, y, stop_x, stop_y)
        if distance < min_distance:
            min_distance = distance
            nearest = stop
    return nearest, min_distance


def generate_coordinates():
    while True:
        x1, y1 = random.randint(-1500, 1500), random.randint(-1600, 2000)
        x2, y2 = random.randint(-1500, 1500), random.randint(-1600, 2000)

        x1 = x1 / 100
        x2 = x2 / 100
        y1 = y1 / 100
        y2 = y2 / 100

        dist_between_coords = euclidean_distance(x1, y1, x2, y2)

        arrival_stop, source_walking_distance = nearest_stop(x1, y1)
        destination_stop, destination_walking_distance = nearest_stop(x2, y2)

        if arrival_stop != destination_stop and dist_between_coords > euclidean_distance(
                *stop_coordinates[arrival_stop], *stop_coordinates[destination_stop]):
            return arrival_stop, destination_stop, x1, y1, x2, y2, source_walking_distance, destination_walking_distance


def generate_random_arrival_time():
    start_time = 6 * 3600
    end_time = 24 * 3600
    return random.randint(start_time, end_time)


def shortestPath(src, dest):
    return nx.dijkstra_path_length(graph, src, dest, weight='weight')


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


def pick(passenger_id, arrival_time, src, dest, path, walking_time, total_travel_time):
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

    waiting_time = pod_departure - arrival_time
    total_travel_time = walking_time + travel_time + waiting_time

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
    cursor.execute("UPDATE pod SET time = ?, current_stop = ?, destination_stop = ? WHERE id = ?",
                   (final_time, dest, dest, id))
    conn.commit()

    cursor.execute(
        "UPDATE passenger SET departure_time = ?, flag = 1, pod_departure = ?, walking_time = ?, waiting_time = ?, total_travel_time = ? WHERE pid = ?",
        (final_time, pod_departure, walking_time, waiting_time, total_travel_time, passenger_id))
    conn.commit()


def check_at_stop(stop):
    cursor.execute(
        "SELECT * FROM pod WHERE current_stop = ? AND destination_stop = ? "
        "AND time IN (SELECT MIN(time) FROM pod WHERE current_stop = ? AND destination_stop = ?)",
        (stop, stop, stop, stop))
    return cursor.fetchone()


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
        x1  REAL,
        y1 REAL,
        x2 REAL,
        y2 REAL,
        walking_time REAL,
        waiting_time INTEGER,
        total_travel_time REAL,
        traveltime INTEGER
    )
    """)
    cursor.execute("UPDATE POD SET TIME = 0")

    for _ in range(passenger_count):
        arrival_stop, destination_stop, x1, y1, x2, y2, source_walking_distance, destination_walking_distance = generate_coordinates()
        arrival_time = generate_random_arrival_time()
        path = ''.join(nx.dijkstra_path(graph, arrival_stop, destination_stop, weight='weight'))

        source_walking_time = 1000 * source_walking_distance / walking_speed
        destination_walking_time = 1000 * destination_walking_distance / walking_speed
        walking_time = source_walking_time + destination_walking_time
        travel_time = shortestPath(arrival_stop, destination_stop)

        cursor.execute(
            "INSERT INTO passenger (arrival_stop, destination_stop, arrival_time, departure_time, flag, pod_departure, from_stop, path, x1, y1, x2, y2, walking_time, waiting_time, total_travel_time, traveltime) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (arrival_stop, destination_stop, arrival_time, 0, 0, 0, None, path, x1, y1, x2, y2, walking_time, 0, 0, travel_time)
        )
    conn.commit()

    while True:
        cursor.execute("SELECT * FROM passenger WHERE flag = 0 AND departure_time = 0 ORDER BY arrival_time")
        passengers = cursor.fetchall()
        if not passengers:
            break
        for passenger in passengers:
            pid, cstop, dest, t, *_tail = passenger
            path = passenger[8]
            walking_time = passenger[13]
            total_travel_time = passenger[15]
            pick(pid, t, cstop, dest, path, walking_time, total_travel_time)

    # Export CSV with destination_time and euclidean distance
    cursor.execute("SELECT * FROM passenger")
    rows = cursor.fetchall()
    with open(output_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(
            ['pid', 'arrival_stop', 'destination_stop', 'arrival_time', 'departure_time', 'flag',
             'pod_departure', 'from_stop', 'path', 'x1', 'y1', 'x2', 'y2',
             'walking_time', 'waiting_time', 'total_travel_time', 'traveltime',
             'destination_time', 'distance']
        )
        for row in rows:
            (pid, arr_stop, dest_stop, arr_time, dep_time, flag, pod_dep, from_stop, path_str,
             x1, y1, x2, y2, walking_time, wait_time, total_time, travel_time) = row
            destination_time = arr_time + travel_time
            distance = euclidean_distance(x1, y1, x2, y2)
            csvwriter.writerow([
                pid, arr_stop, dest_stop, arr_time, dep_time, flag, pod_dep, from_stop, path_str,
                x1, y1, x2, y2, walking_time, wait_time, total_time, travel_time,
                destination_time, distance
            ])

    print(f"Exported {passenger_count} passengers to {output_file}.")

conn.commit()
conn.close()
print("Experiment 5 (only blue) completed successfully.")