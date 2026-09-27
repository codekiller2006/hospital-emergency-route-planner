import os
import random
import copy
import osmnx as ox


def load_graph(filename):

    G = ox.load_graphml(filename)

    for u, v, key, data in G.edges(
        keys=True,
        data=True
    ):

        if "length" in data:
            data["length"] = float(data["length"])

        if "travel_time" in data:
            data["travel_time"] = float(
                data["travel_time"]
            )

        if "speed_kph" in data:
            data["speed_kph"] = float(
                data["speed_kph"]
            )

    return G


def simulate_traffic(
    G,
    percentage=10,
    multiplier=2.0,
    seed=42
):

    simulated_graph = copy.deepcopy(G)

    random.seed(seed)

    edges = list(
        simulated_graph.edges(keys=True)
    )

    affected_count = int(
        len(edges) * percentage / 100
    )

    affected_edges = random.sample(
        edges,
        affected_count
    )

    for u, v, key in affected_edges:

        data = simulated_graph[u][v][key]

        original_time = float(
            data["travel_time"]
        )

        data["travel_time"] = (
            original_time * multiplier
        )

        data["status"] = "congested"

        data["traffic_multiplier"] = multiplier

    return simulated_graph


def simulate_road_closures(
    G,
    percentage=5,
    seed=42
):

    simulated_graph = copy.deepcopy(G)

    random.seed(seed)

    edges = list(
        simulated_graph.edges(keys=True)
    )

    affected_count = int(
        len(edges) * percentage / 100
    )

    closed_edges = random.sample(
        edges,
        affected_count
    )

    for u, v, key in closed_edges:

        data = simulated_graph[u][v][key]

        data["status"] = "closed"
        data["travel_time"] = float("inf")

    return simulated_graph


def get_open_graph(G):

    H = G.copy()

    closed_edges = []

    for u, v, key, data in H.edges(
        keys=True,
        data=True
    ):

        if data.get("status") == "closed":

            closed_edges.append(
                (u, v, key)
            )

    H.remove_edges_from(closed_edges)

    return H


def save_graph(G, filename):

    folder = os.path.dirname(filename)

    if folder:
        os.makedirs(
            folder,
            exist_ok=True
        )

    ox.save_graphml(
        G,
        filename
    )

    print("Saved:", filename)