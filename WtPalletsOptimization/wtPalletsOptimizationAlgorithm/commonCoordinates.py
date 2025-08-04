import json

try:
    with open("common_coordinates_data.json") as f:
        guideway_data = json.load(f)
except FileNotFoundError:
    guideway_data = {}

def getTimeWeight(edgeWeight):
    """
    Returns the time weight for a given edge weight.
    """
    return (edgeWeight * 3600)/40

# # Define all edges with time weights
# time_edges = [
#     ('A', 'B', getTimeWeight(1.4142)),
#     ('A', 'C', getTimeWeight(1.4142)),
#     ('A', 'H', getTimeWeight(1)),
#     ('B', 'H', getTimeWeight(1)),
#     ('H', 'C', getTimeWeight(1)),
#     ('B', 'D', getTimeWeight(1)),
#     ('H', 'I', getTimeWeight(1)),
#     ('C', 'E', getTimeWeight(1)),
#     ('D', 'F', getTimeWeight(1)),
#     ('D', 'I', getTimeWeight(1)),
#     ('I', 'J', getTimeWeight(1)),
#     ('I', 'E', getTimeWeight(1)),
#     ('E', 'G', getTimeWeight(1)),
#     ('F', 'J', getTimeWeight(1)),
#     ('J', 'G', getTimeWeight(1))
# ]
# # Define all edges with time weights
# time_edges = [
#     ('A', 'B', getTimeWeight(1.4142)),
#     ('A', 'C', getTimeWeight(1.4142)),
#     ('A', 'H', getTimeWeight(1)),
#     ('B', 'H', getTimeWeight(1)),
#     ('H', 'C', getTimeWeight(1)),
#     ('B', 'D', getTimeWeight(1)),
#     ('H', 'I', getTimeWeight(1)),
#     ('C', 'E', getTimeWeight(1)),
#     ('D', 'F', getTimeWeight(1)),
#     ('D', 'I', getTimeWeight(1)),
#     ('I', 'J', getTimeWeight(1)),
#     ('I', 'E', getTimeWeight(1)),
#     ('E', 'G', getTimeWeight(1)),
#     ('F', 'J', getTimeWeight(1)),
#     ('J', 'G', getTimeWeight(1))
# ]

# # Define all edges with distance weights
# distance_edges = [
#     ('A', 'B', 1.4142),
#     ('A', 'C', 1.4142),
#     ('A', 'H', 1),
#     ('B', 'H', 1),
#     ('H', 'C', 1),
#     ('B', 'D', 1),
#     ('H', 'I', 1),
#     ('C', 'E', 1),
#     ('D', 'F', 1),
#     ('D', 'I', 1),
#     ('I', 'J', 1),
#     ('I', 'E', 1),
#     ('E', 'G', 1),
#     ('F', 'J', 1),
#     ('J', 'G', 1)
# ]
# # Define all edges with distance weights
# distance_edges = [
#     ('A', 'B', 1.4142),
#     ('A', 'C', 1.4142),
#     ('A', 'H', 1),
#     ('B', 'H', 1),
#     ('H', 'C', 1),
#     ('B', 'D', 1),
#     ('H', 'I', 1),
#     ('C', 'E', 1),
#     ('D', 'F', 1),
#     ('D', 'I', 1),
#     ('I', 'J', 1),
#     ('I', 'E', 1),
#     ('E', 'G', 1),
#     ('F', 'J', 1),
#     ('J', 'G', 1)
# ]

# ID to letter mapping
id_to_letter = {
    0: "A", 1: "B", 2: "C", 3: "D", 4: "E",
    5: "F", 6: "G", 7: "H", 8: "I", 9: "J"
}
# ID to letter mapping
id_to_letter = {
    0: "A", 1: "B", 2: "C", 3: "D", 4: "E",
    5: "F", 6: "G", 7: "H", 8: "I", 9: "J"
}

# Construct edges
time_edges = []
distance_edges = []
# Construct edges
time_edges = []
distance_edges = []

for edge in guideway_data.get("edges", []):
    src = id_to_letter[edge["source"]]
    tgt = id_to_letter[edge["target"]]
    length = edge["length"]
for edge in guideway_data.get("edges", []):
    src = id_to_letter[edge["source"]]
    tgt = id_to_letter[edge["target"]]
    length = edge["length"]

    time_edges.append((src, tgt, getTimeWeight(length)))
    distance_edges.append((src, tgt, length))
    time_edges.append((src, tgt, getTimeWeight(length)))
    distance_edges.append((src, tgt, length))

# Define all stop nodes
stops = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

# Define all routes
truck_routes_1 = ['A', 'H', 'I', 'E' , 'C' , 'G' , 'J', 'F', 'D', 'B', 'D', 'F', 'J', 'G', 'C', 'E', 'I', 'H']
truck_routes_2 = ['B', 'D', 'I', 'A' , 'H' , 'C' , 'E', 'G', 'J', 'F', 'J', 'G', 'E', 'C', 'H', 'A', 'I', 'D']
truck_routes_3 = ['F', 'J', 'G', 'E' , 'I' , 'D' , 'H', 'B', 'A', 'C', 'A', 'B', 'H', 'D', 'I', 'E', 'G', 'J']
truck_routes_4 = ['C', 'I', 'H', 'A' , 'B' , 'D' , 'F', 'J', 'G', 'E', 'G', 'J', 'F', 'D', 'B', 'A', 'H', 'I']
truck_routes_5 = ['E', 'G', 'C', 'A' , 'B' , 'H' , 'I', 'J', 'F', 'D', 'F', 'J', 'I', 'H', 'B', 'A', 'C', 'G']

MAX_GOODSPODS = 100 #184

# Global constants
minimum_distance = 4
load_unload = 4
SPEED_KM_PER_HOUR = 40

pallet_counts = [896]

#truck capacities
small_truck =  50
large_truck = 80
capacities = [small_truck, large_truck]

# Initialize dictionaries
truck_distances = {1: 0, 2: 0, 3: 0, 4: 0 ,5: 0}
truck_previous_stops = {1: None, 2: None, 3: None, 4: None, 5: None}
truck_trip_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

truck_distances_update = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
truck_previous_stops_update = {1: None, 2: None, 3: None, 4: None, 5: None}
truck_trip_counts_update = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

# Function to initialize the truck table
start_node = ['A', 'B', 'F', 'C', 'E']
stop_node = ['H', 'D', 'J', 'I', 'G']
paths = ["AHIECGJFDB", "BDIAHCEGJF", "FJGEIDHBAC", "CIHABDFJGE", "EGCABHIJFD"]

truck_paths = {
    'AHIECGJFDB': truck_routes_1,
    'BDIAHCEGJF': truck_routes_2,
    'FJGEIDHBAC': truck_routes_3,
    'CIHABDFJGE': truck_routes_4,
    'EGCABHIJFD': truck_routes_5
}

desti_stop = 'I'

outskirt_stop = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
central_stops = 'I'

# goodsPod distribution for Experiment 4 based on Experiment 3
goodspod_distribution = {
    'A': 6, 'B': 140, 'C': 8, 'D': 8,
    'E': 7, 'F': 6, 'G': 4
}

# experiment 4 other stops
other_stops_exp4 = ['A', 'B', 'C', 'D', 'E', 'F', 'G']