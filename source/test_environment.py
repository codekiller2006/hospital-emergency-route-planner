import networkx as nx

from src.environment import (
    load_graph,
    get_open_graph
)


G = load_graph(
    "data/simulated/normal.graphml"
)

print("Nodes:", len(G.nodes))
print("Edges:", len(G.edges))


source = list(G.nodes)[0]
target = list(G.nodes)[100]


route = nx.shortest_path(
    G,
    source,
    target,
    weight="travel_time"
)


travel_time = nx.shortest_path_length(
    G,
    source,
    target,
    weight="travel_time"
)


print()
print("Source:", source)
print("Target:", target)
print("Route:", route)
print("Travel time:", travel_time, "seconds")