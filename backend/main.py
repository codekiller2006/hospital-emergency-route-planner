# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.schemas import RouteRequest, RouteResponse, AlgorithmResult
import time

app = FastAPI(title="Emergency Route Planner API")

# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/calculate-routes", response_model=RouteResponse)
async def calculate_routes(request: RouteRequest):
    """
    Calculates routes using A* and Q-Learning based on start and end nodes.
    Requires algorithm integrations from Role 2 and Role 3.
    """
    try:
        # TODO: Import actual graph from data/ (Role 1)
        
        # --- Mock A* Execution (Role 2 integration goes here) ---
        start_time = time.time()
        # a_star_path, a_star_dist = run_a_star(graph, request.start_node, request.end_node)
        a_star_time = (time.time() - start_time) * 1000
        
        a_star_result = AlgorithmResult(
            algorithm_name="A* with Custom Heuristic",
            path=[request.start_node, 101, 102, request.end_node], # Mock path
            distance_km=4.5,
            execution_time_ms=a_star_time,
            simulated_time_min=12.5
        )

        # --- Mock Q-Learning Execution (Role 3 integration goes here) ---
        start_time = time.time()
        # q_learning_path, q_learning_dist = run_q_learning(graph, request.start_node, request.end_node)
        q_time = (time.time() - start_time) * 1000
        
        q_learning_result = AlgorithmResult(
            algorithm_name="Q-Learning",
            path=[request.start_node, 201, 202, 203, request.end_node], # Mock path
            distance_km=5.1,
            execution_time_ms=q_time,
            simulated_time_min=9.0
        )

        return RouteResponse(
            start_node=request.start_node,
            end_node=request.end_node,
            results=[a_star_result, q_learning_result]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))