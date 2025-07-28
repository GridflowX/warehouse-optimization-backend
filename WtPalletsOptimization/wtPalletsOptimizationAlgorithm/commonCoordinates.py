def getTimeWeight(edgeWeight):
    """
    Returns the time weight for a given edge weight.
    """
    return (edgeWeight * 3600)/40

# Define all edges with time weights
time_edges = [
    ('A', 'B', getTimeWeight(1.4142)),
    ('A', 'C', getTimeWeight(1.4142)),
    ('A', 'H', getTimeWeight(1)),
    ('B', 'H', getTimeWeight(1)),
    ('H', 'C', getTimeWeight(1)),
    ('B', 'D', getTimeWeight(1)),
    ('H', 'I', getTimeWeight(1)),
    ('C', 'E', getTimeWeight(1)),
    ('D', 'F', getTimeWeight(1)),
    ('D', 'I', getTimeWeight(1)),
    ('I', 'J', getTimeWeight(1)),
    ('I', 'E', getTimeWeight(1)),
    ('E', 'G', getTimeWeight(1)),
    ('F', 'J', getTimeWeight(1)),
    ('J', 'G', getTimeWeight(1))
]

# Define all edges with distance weights
distance_edges = [
    ('A', 'B', 1.4142),
    ('A', 'C', 1.4142),
    ('A', 'H', 1),
    ('B', 'H', 1),
    ('H', 'C', 1),
    ('B', 'D', 1),
    ('H', 'I', 1),
    ('C', 'E', 1),
    ('D', 'F', 1),
    ('D', 'I', 1),
    ('I', 'J', 1),
    ('I', 'E', 1),
    ('E', 'G', 1),
    ('F', 'J', 1),
    ('J', 'G', 1)
]

# Define all stop nodes
stops = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

# Define bus routes   
bus_routes_1 = ['A', 'H', 'I', 'E' , 'C' , 'G' , 'J', 'F', 'D', 'B']
bus_routes_2 = ['B', 'D', 'I', 'A' , 'H' , 'C' , 'E', 'G', 'J', 'F']
bus_routes_3 = ['F', 'J', 'G', 'E' , 'I' , 'D' , 'H', 'B', 'A', 'C']
bus_routes_4 = ['C', 'I', 'H', 'A' , 'B' , 'D' , 'F', 'J', 'G', 'E']