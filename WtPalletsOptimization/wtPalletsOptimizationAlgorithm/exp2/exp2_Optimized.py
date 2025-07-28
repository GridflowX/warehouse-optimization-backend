import pandas as pd
import numpy as np
import networkx as nx
import os
from collections import defaultdict

# Graph for routing (time in seconds)
graph = nx.Graph()
graph.add_edges_from([
    ('A', 'B', {'weight': 1170}),
    ('B', 'Q', {'weight': 1800}),
    ('B', 'C', {'weight': 630}),
    ('B', 'R', {'weight': 1350}),
    ('C', 'D', {'weight': 1530}),
    ('P', 'Q', {'weight': 900}),
    ('R', 'S', {'weight': 450}),
])

# Graph for distances (in km)
g = nx.Graph()
g.add_edge('A', 'B', weight=13)
g.add_edge('B', 'Q', weight=20)
g.add_edge('B', 'C', weight=7)
g.add_edge('B', 'R', weight=15)
g.add_edge('C', 'D', weight=17)
g.add_edge('P', 'Q', weight=10)
g.add_edge('R', 'S', weight=5)

board_deboard = 4
#os.makedirs("output", exist_ok=True)
MAX_PODS = 184

# Now CSV files instead of Excel files
csv_files = [
      "392_exp2.csv", "896_exp2.csv","2968_exp2.csv", "4032_exp2.csv", "5040_exp2.csv","7952_exp2.csv",
]

def travel_time(from_stop, to_stop):
    try:
        return nx.dijkstra_path_length(graph, from_stop, to_stop)
    except nx.NetworkXNoPath:
        return float('inf')

def travel_distance(from_stop, to_stop):  # in km
    try:
        return nx.dijkstra_path_length(g, from_stop, to_stop)
    except nx.NetworkXNoPath:
        return 0

for file in csv_files:
    df = pd.read_csv(file)
    df = df.sort_values("arrival_time")
    df["arrival_time"] = pd.to_numeric(df["arrival_time"], errors="coerce").fillna(-1).astype(int)
    df["destination_time"] = pd.to_numeric(df["destination_time"], errors="coerce").fillna(-1).astype(int)

    pod_counter = 0
    active_pods = {}
    allocations = []
    pod_usage_log = defaultdict(list)
    empty_total_km = 0
    nonempty_total_km = 0

    base = os.path.splitext(file)[0]
    out_csv = f"{base}_allocations.csv"

    for _, row in df.iterrows():
        pid = row["pid"]
        arrival_stop = row["arrival_stop"]
        destination_stop = row["destination_stop"]
        arrival_time = row["arrival_time"]
        destination_time = row["destination_time"]
        distance = row.get("distance", travel_time(arrival_stop, destination_stop))

        if pd.isna(arrival_stop) or pd.isna(destination_stop) or destination_time > 90000:
            continue

        assigned = False
        candidates = []
        pods_at_same_stop = []

        for pod_id, (pod_loc, pod_free_time) in active_pods.items():
            if pod_loc == arrival_stop and pod_free_time <= arrival_time:
                pods_at_same_stop.append((pod_free_time, pod_id))

        if pods_at_same_stop:
            pods_at_same_stop.sort()
            pod_free_time, pod_id = pods_at_same_stop[0]
            pod_loc = arrival_stop
            time_to_reach = 0
            pod_arrival_time = arrival_time
            empty_km = 0

        elif pod_counter < MAX_PODS:
            pod_id = pod_counter
            pod_counter += 1
            pod_loc = arrival_stop
            time_to_reach = 0
            pod_arrival_time = arrival_time
            empty_km = 0

        else:
            for pod_id, (pod_loc, pod_free_time) in active_pods.items():
                time_to_reach = travel_time(pod_loc, arrival_stop)
                pod_arrival_time = pod_free_time + time_to_reach
                if pod_arrival_time <= arrival_time:
                    wait_time = arrival_time - pod_arrival_time
                    candidates.append((wait_time, pod_id, pod_loc, pod_free_time, time_to_reach, pod_arrival_time))

            if candidates:
                candidates.sort()
                _, pod_id, pod_loc, pod_free_time, time_to_reach, pod_arrival_time = candidates[0]
                empty_km = travel_distance(pod_loc, arrival_stop)
                empty_total_km += empty_km
            else:
                delayed_options = []
                for pod_id, (pod_loc, pod_free_time) in active_pods.items():
                    time_to_reach = travel_time(pod_loc, arrival_stop)
                    pod_arrival_time = pod_free_time + time_to_reach
                    delay = pod_arrival_time - arrival_time
                    delayed_options.append((delay, pod_id, pod_loc, pod_free_time, time_to_reach, pod_arrival_time))
                delayed_options.sort()
                delay, pod_id, pod_loc, pod_free_time, time_to_reach, pod_arrival_time = delayed_options[0]
                empty_km = travel_distance(pod_loc, arrival_stop)
                empty_total_km += empty_km

        final_travel_time = travel_time(arrival_stop, destination_stop)
        nonempty_km = travel_distance(arrival_stop, destination_stop)
        nonempty_total_km += nonempty_km

        if pod_arrival_time > arrival_time:
            pod_final_time = pod_arrival_time + final_travel_time + board_deboard
        else:
            pod_final_time = arrival_time + final_travel_time + board_deboard

        waiting_time = max(0, pod_arrival_time - arrival_time)
        active_pods[pod_id] = (destination_stop, destination_time + board_deboard)

        allocations.append([
            pid, arrival_stop, destination_stop, arrival_time, destination_time,
            distance, pod_id, pod_arrival_time, pod_loc, time_to_reach,
            waiting_time, pod_final_time, empty_km, nonempty_km
        ])
        pod_usage_log[pod_id].append(pid)

    print(f"\n Summary for {file}")
    print(f" Total Empty Distance: {empty_total_km:.2f} km")
    print(f" Total Non-Empty Distance: {nonempty_total_km:.2f} km")

    df_alloc = pd.DataFrame(allocations, columns=[
        "pid", "arrival_stop", "destination_stop", "arrival_time", "destination_time",
        "distance", "pod_id", "pod_arrival_time", "pod_current_loc", "travel_distance",
        "waiting_time", "pod_final_time", "empty_km", "nonempty_km"
    ])
    df_alloc.to_csv(out_csv, index=False)

    print(f" Done: {file} Allocations saved to {out_csv}")