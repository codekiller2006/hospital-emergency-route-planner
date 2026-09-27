"""
Role 2: Baseline AI & Custom Heuristic — A* Pathfinding Module

This module implements the A* search algorithm over a networkx graph
representing a city's street network.
"""

import heapq
import math
import time
from typing import Dict, List, Optional, Tuple
import networkx as nx

FREE_FLOW_SPEED_MPS = 40 * 1000 / 3600
TRAFFIC_WEIGHT = 0.35
RISK_WEIGHT = 0.50
DEFAULT_RISK_PENALTY_SEC = 120.0
EARTH_RADIUS_M = 6371000.0

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_M * c

def find_nearest_node(graph: nx.Graph, lat: float, lon: float):
    try:
        import osmnx as ox
        return ox.distance.nearest_nodes(graph, X=lon, Y=lat)
    except ImportError:
        nearest_node = None
        nearest_dist = float("inf")
        for node, data in graph.nodes(data=True):
            node_lat, node_lon = data.get("y"), data.get("x")
            if node_lat is None or node_lon is None:
                continue
            dist = haversine_distance(lat, lon, node_lat, node_lon)
            if dist < nearest_dist:
                nearest_dist = dist
                nearest_node = node
        if nearest_node is None:
            raise ValueError("Graph has no nodes with 'x'/'y' coordinate data.")
        return nearest_node

def _cheapest_parallel_edge(edge_dict: dict, cost_key) -> dict:
    if edge_dict and all(isinstance(v, dict) for v in edge_dict.values()):
        return min(edge_dict.values(), key=cost_key)
    return edge_dict

def get_edge_cost(graph: nx.Graph, u, v, edge_data: Optional[dict] = None) -> float:
    if edge_data is None:
        edge_dict = graph.get_edge_data(u, v)
        if edge_dict is None:
            return float("inf")
        edge_data = _cheapest_parallel_edge(
            edge_dict, lambda d: d.get("length", 1.0) * d.get("traffic_weight", 1.0)
        )

    length_m = edge_data.get("length", 1.0)
    traffic_weight = edge_data.get("traffic_weight", 1.0)
    high_risk = edge_data.get("high_risk", False)
    risk_penalty = edge_data.get("risk_penalty", DEFAULT_RISK_PENALTY_SEC)

    base_time = (length_m / FREE_FLOW_SPEED_MPS) * traffic_weight
    if high_risk:
        base_time += risk_penalty

    return base_time

def dynamic_heuristic(graph: nx.Graph, node, goal) -> float:
    node_data = graph.nodes[node]
    goal_data = graph.nodes[goal]

    dist_m = haversine_distance(node_data["y"], node_data["x"], goal_data["y"], goal_data["x"])
    h_distance = dist_m / FREE_FLOW_SPEED_MPS

    traffic_samples = []
    risk_flag = False

    if node in graph:
        for _, edge_dict in graph[node].items():
            candidates = (
                edge_dict.values()
                if edge_dict and all(isinstance(v, dict) for v in edge_dict.values())
                else [edge_dict]
            )
            for e in candidates:
                traffic_samples.append(e.get("traffic_weight", 1.0))
                if e.get("high_risk", False):
                    risk_flag = True

    avg_traffic = sum(traffic_samples) / len(traffic_samples) if traffic_samples else 1.0
    h_traffic = max(0.0, avg_traffic - 1.0) * 60.0
    h_risk = 90.0 if risk_flag else 0.0

    return h_distance + TRAFFIC_WEIGHT * h_traffic + RISK_WEIGHT * h_risk

def a_star_search(graph: nx.Graph, start_node, goal_node) -> Tuple[Optional[List], float]:
    if start_node == goal_node:
        return [start_node], 0.0

    counter = 0 
    open_heap = [(0.0, counter, start_node)]
    open_set = {start_node}
    closed_set = set()

    came_from: Dict = {}
    g_score: Dict = {start_node: 0.0}

    while open_heap:
        _, _, current = heapq.heappop(open_heap)

        if current in closed_set:
            continue
        if current == goal_node:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path, g_score[goal_node]

        closed_set.add(current)
        open_set.discard(current)

        for neighbor in graph.neighbors(current):
            if neighbor in closed_set:
                continue

            edge_dict = graph.get_edge_data(current, neighbor)
            if edge_dict is None:
                continue
            best_edge = _cheapest_parallel_edge(
                edge_dict, lambda d: get_edge_cost(graph, current, neighbor, d)
            )

            tentative_g = g_score[current] + get_edge_cost(graph, current, neighbor, best_edge)

            if tentative_g < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score = tentative_g + dynamic_heuristic(graph, neighbor, goal_node)

                if neighbor not in open_set:
                    counter += 1
                    heapq.heappush(open_heap, (f_score, counter, neighbor))
                    open_set.add(neighbor)

    return None, float("inf")

def get_optimized_route(
    graph: nx.Graph, start_lat: float, start_lon: float, end_lat: float, end_lon: float
) -> dict:
    start_time = time.perf_counter()

    start_node = find_nearest_node(graph, start_lat, start_lon)
    end_node = find_nearest_node(graph, end_lat, end_lon)

    node_path, travel_time_seconds = a_star_search(graph, start_node, end_node)

    execution_time = time.perf_counter() - start_time

    if node_path is None:
        return {
            "path": [[start_lat, start_lon], [end_lat, end_lon]],
            "execution_time": round(execution_time, 6),
            "travel_time": float("inf"),
            "distance": float("inf"),
        }

    path_coords: List[List[float]] = []
    total_distance_m = 0.0

    for i, node in enumerate(node_path):
        node_data = graph.nodes[node]
        path_coords.append([node_data["y"], node_data["x"]])

        if i > 0:
            prev_node = node_path[i - 1]
            edge_dict = graph.get_edge_data(prev_node, node)
            if edge_dict:
                best_edge = _cheapest_parallel_edge(edge_dict, lambda d: d.get("length", 0.0))
                total_distance_m += best_edge.get("length", 0.0)

    return {
        "path": path_coords,
        "execution_time": round(execution_time, 6),
        "travel_time": round(travel_time_seconds, 2),
        "distance": round(total_distance_m, 2),
    }