import pandas as pd
import numpy as np
import networkx as nx
import os
from collections import defaultdict

import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from commonCoordinates import time_edges, distance_edges, stops, MAX_GOODSPODS, load_unload, pallet_counts

# Graph for routing (time in seconds)
graph = nx.Graph()
# Define all edges with time weights
for u, v, w in time_edges:
    graph.add_edge(u, v, weight=w)

# Graph for distances (in km)
g = nx.Graph()
for u, v, w in distance_edges:
    g.add_edge(u, v, weight=w)

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
    
csv_files = [
    f"{count}_exp3.csv" for count in pallet_counts
]

for file in csv_files:
    df = pd.read_csv(file)
    df = df.sort_values("arrival_time")
    df["arrival_time"] = pd.to_numeric(df["arrival_time"], errors="coerce").fillna(-1).astype(int)
    df["destination_time"] = pd.to_numeric(df["destination_time"], errors="coerce").fillna(-1).astype(int)

    goodspod_counter = 0
    active_goodspods = {}
    allocations = []
    goodspod_usage_log = defaultdict(list)
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
        goodspods_at_same_stop = []

        for goodspod_id, (goodspod_loc, goodspod_free_time) in active_goodspods.items():
            if goodspod_loc == arrival_stop and goodspod_free_time <= arrival_time:
                goodspods_at_same_stop.append((goodspod_free_time, goodspod_id))

        if goodspods_at_same_stop:
            goodspods_at_same_stop.sort()
            goodspod_free_time, goodspod_id = goodspods_at_same_stop[0]
            goodspod_loc = arrival_stop
            time_to_reach = 0
            goodspod_arrival_time = arrival_time
            empty_km = 0

        elif goodspod_counter < MAX_GOODSPODS:
            goodspod_id = goodspod_counter
            goodspod_counter += 1
            goodspod_loc = arrival_stop
            time_to_reach = 0
            goodspod_arrival_time = arrival_time
            empty_km = 0

        else:
            for goodspod_id, (goodspod_loc, goodspod_free_time) in active_goodspods.items():
                time_to_reach = travel_time(goodspod_loc, arrival_stop)
                goodspod_arrival_time = goodspod_free_time + time_to_reach
                if goodspod_arrival_time <= arrival_time:
                    wait_time = arrival_time - goodspod_arrival_time
                    candidates.append((wait_time, goodspod_id, goodspod_loc, goodspod_free_time, time_to_reach, goodspod_arrival_time))

            if candidates:
                candidates.sort()
                _, goodspod_id, goodspod_loc, goodspod_free_time, time_to_reach, goodspod_arrival_time = candidates[0]
                empty_km = travel_distance(goodspod_loc, arrival_stop)
                empty_total_km += empty_km
            else:
                delayed_options = []
                for goodspod_id, (goodspod_loc, goodspod_free_time) in active_goodspods.items():
                    time_to_reach = travel_time(goodspod_loc, arrival_stop)
                    goodspod_arrival_time = goodspod_free_time + time_to_reach
                    delay = goodspod_arrival_time - arrival_time
                    delayed_options.append((delay, goodspod_id, goodspod_loc, goodspod_free_time, time_to_reach, goodspod_arrival_time))
                delayed_options.sort()
                delay, goodspod_id, goodspod_loc, goodspod_free_time, time_to_reach, goodspod_arrival_time = delayed_options[0]
                empty_km = travel_distance(goodspod_loc, arrival_stop)
                empty_total_km += empty_km

        final_travel_time = travel_time(arrival_stop, destination_stop)
        nonempty_km = travel_distance(arrival_stop, destination_stop)
        nonempty_total_km += nonempty_km

        if goodspod_arrival_time > arrival_time:
            goodspod_final_time = goodspod_arrival_time + final_travel_time + load_unload
        else:
            goodspod_final_time = arrival_time + final_travel_time + load_unload

        delivery_delay = max(0, goodspod_arrival_time - arrival_time)
        active_goodspods[goodspod_id] = (destination_stop, destination_time + load_unload)

        allocations.append([
            pid, arrival_stop, destination_stop, arrival_time, destination_time,
            distance, goodspod_id, goodspod_arrival_time, goodspod_loc, time_to_reach,
            delivery_delay, goodspod_final_time, empty_km, nonempty_km
        ])
        goodspod_usage_log[goodspod_id].append(pid)

    print(f"\nSummary for {file}")
    print(f" Total Empty Distance: {empty_total_km:.2f} km")
    print(f" Total Non-Empty Distance: {nonempty_total_km:.2f} km")

    df_alloc = pd.DataFrame(allocations, columns=[
        "pid", "arrival_stop", "destination_stop", "arrival_time", "destination_time",
        "distance", "goodspod_id", "goodspod_arrival_time", "goodspod_current_loc", "travel_distance",
        "delivery_delay", "goodspod_final_time", "empty_km", "nonempty_km"
    ])
    df_alloc.to_csv(out_csv, index=False)

    print(f" Done: {file}  Allocations saved to {out_csv}")