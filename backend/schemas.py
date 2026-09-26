from pydantic import BaseModel
from typing import List

class RouteRequest(BaseModel):
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float

class AlgorithmMetrics(BaseModel):
    path: List[List[float]]
    execution_time: float
    travel_time: float
    distance: float

class RouteResponse(BaseModel):
    astar: AlgorithmMetrics
    q_learning: AlgorithmMetrics