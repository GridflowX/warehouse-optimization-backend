import networkx as nx
import itertools
import matplotlib.pyplot as plt
from math import sqrt
import random

# Step 1: Define nodes with coordinates
coords = {
    'A': (0, 1), 'B': (1, 2), 'C': (1, 0), 'D': (2, 2),
    'E': (2, 0), 'F': (3, 2), 'G': (3, 0), 'H': (1, 1),
    'I': (2, 1), 'J': (3, 1)
}

edges = [
    ('A', 'B'), ('A', 'C'), ('A', 'H'), 
    ('B', 'H'), ('B', 'D'),
    ('C', 'H'), ('C', 'E'), 
    ('D', 'I'), ('D', 'F'), 
    ('E', 'I'), ('E', 'G'), 
    ('F', 'J'), 
    ('G', 'J'),
    ('H', 'I'), 
    ('I', 'J'),
]

# Step 2: Create graph with distances
G = nx.Graph()
for u, v in edges:
    dist = round(sqrt((coords[u][0] - coords[v][0])**2 + (coords[u][1] - coords[v][1])**2), 2)
    G.add_edge(u, v, weight=dist)

# Step 3: Get all shortest paths between all nodes
all_pairs_shortest = dict(nx.all_pairs_dijkstra_path(G, weight='weight'))

# Step 4: Define extreme points to start/end
extreme_nodes = ['A','B','F', 'C', 'E', 'D']

# Step 5: For each bus, generate TSP-like path
def tsp_path(start, end, graph, all_paths):
    nodes = list(graph.nodes())
    nodes.remove(start)
    nodes.remove(end)
   
    min_cost = float('inf')
    best_path = []

    # Try 2000 random permutations for feasible unique paths
    for _ in range(2000):
        middle = random.sample(nodes, len(nodes))
        trial = [start] + middle + [end]
       
        cost = 0
        valid = True
        for i in range(len(trial)-1):
            try:
                segment = all_paths[trial[i]][trial[i+1]]
                for j in range(len(segment)-1):
                    cost += graph[segment[j]][segment[j+1]]['weight']
            except:
                valid = False
                break
       
        if valid and cost < min_cost:
            min_cost = cost
            best_path = trial

    return best_path, round(min_cost, 2)

# Step 6: Compute 4 different paths
paths = []
for i in range(5):
    start = extreme_nodes[i]
    end = extreme_nodes[(i+1)%len(extreme_nodes)]
    path, dist = tsp_path(start, end, G, all_pairs_shortest)
    paths.append((path, dist))

# Step 7: Display paths
print("Final Bus Routes (Each covers all 8 nodes):\n")
for i, (p, d) in enumerate(paths):
    print(f"Bus {i+1}: {' → '.join(p)} | Distance: {d} km")

# Step 8: Plot all 4 paths side by side
fig, axs = plt.subplots(1, 5, figsize=(22, 5))
pos = coords

for i, (p, d) in enumerate(paths):
    ax = axs[i]
    nx.draw(G, pos, with_labels=True, node_size=500, node_color='lightblue', ax=ax)
   
    # Draw path edges in red
    path_edges = []
    for j in range(len(p)-1):
        segment = all_pairs_shortest[p[j]][p[j+1]]
        for k in range(len(segment)-1):
            path_edges.append((segment[k], segment[k+1]))
    nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=2.5, ax=ax)
   
    ax.set_title(f"Bus {i+1} Path\nDist: {d} km")

plt.tight_layout()
plt.show()

# Find the shortest path
shortest_bus_index = min(range(5), key=lambda i: paths[i][1])
shortest_path, shortest_dist = paths[shortest_bus_index]

print(f"\n🏆 Shortest Path is by Bus {shortest_bus_index + 1}")
print(f"Path: {' → '.join(shortest_path)}")
print(f"Distance: {shortest_dist} km")