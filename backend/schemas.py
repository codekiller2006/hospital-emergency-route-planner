from pydantic import BaseModel
from typing import List, Tuple

class RouteRequest(BaseModel):
    start_node: int
    end_node: int

class AlgorithmResult(BaseModel):
    algorithm_name: str
    path: List[int]
    distance_km: float
    execution_time_ms: float
    simulated_time_min: float

class RouteResponse(BaseModel):
    start_node: int
    end_node: int
    results: List[AlgorithmResult]