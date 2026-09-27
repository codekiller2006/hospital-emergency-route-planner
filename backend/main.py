from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.schemas import RouteRequest, RouteResponse, AlgorithmMetrics
from algorithms.q_learning import QLearningRouter
from algorithms.a_star import get_optimized_route as run_a_star
import osmnx as ox
import os

app = FastAPI(title="Emergency Route Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CITY_GRAPH = None

@app.on_event("startup")
async def load_graph():
    global CITY_GRAPH
    graph_path = "data/city_map.graphml"
    if os.path.exists(graph_path):
        CITY_GRAPH = ox.load_graphml(graph_path)
        print("City graph loaded successfully.")
    else:
        print(f"Warning: Graph file not found at {graph_path}. Role 1 needs to push their data.")

@app.post("/route", response_model=RouteResponse)
async def get_route(request: RouteRequest):
    if CITY_GRAPH is None:
        raise HTTPException(status_code=503, detail="Graph data is not yet loaded.")

    try:
        # --- 1. Execute Role 2's A* Algorithm ---
        astar_raw = run_a_star(
            CITY_GRAPH, 
            request.start_lat, 
            request.start_lon, 
            request.end_lat, 
            request.end_lon
        )
        
        astar_metrics = AlgorithmMetrics(
            path=astar_raw["path"],
            execution_time=astar_raw["execution_time"],
            travel_time=astar_raw["travel_time"],
            distance=astar_raw["distance"]
        )

        # --- 2. Execute Role 3's Q-Learning Algorithm ---
        start_node = ox.distance.nearest_nodes(CITY_GRAPH, X=request.start_lon, Y=request.start_lat)
        end_node = ox.distance.nearest_nodes(CITY_GRAPH, X=request.end_lon, Y=request.end_lat)

        q_router = QLearningRouter(CITY_GRAPH, episodes=200)
        q_result = q_router.plan_route(start_node, end_node)

        q_lat_lon_path = []
        for node_id in q_result["path"]:
            node_data = CITY_GRAPH.nodes[node_id]
            q_lat_lon_path.append([node_data['y'], node_data['x']])

        q_learning_metrics = AlgorithmMetrics(
            path=q_lat_lon_path,
            execution_time=q_result["execution_time"],
            travel_time=q_result["travel_time"],
            distance=q_result["distance"]
        )

        # --- 3. Return Combined Response ---
        return RouteResponse(
            astar=astar_metrics,
            q_learning=q_learning_metrics
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))