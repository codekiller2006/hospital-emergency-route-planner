from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.schemas import RouteRequest, RouteResponse, AlgorithmMetrics

app = FastAPI(title="Emergency Route Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# CHANGED: Endpoint is now exactly /route as requested by Role 5
@app.post("/route", response_model=RouteResponse) 
async def get_route(request: RouteRequest):
    try:
        astar_result = AlgorithmMetrics(
            path=[[request.start_lat, request.start_lon], [23.3500, 85.3150]],
            execution_time=0.012,
            travel_time=542.4,
            distance=3840.2
        )

        q_learning_result = AlgorithmMetrics(
            path=[[request.start_lat, request.start_lon], [23.3480, 85.3200]],
            execution_time=0.034,
            travel_time=481.7,
            distance=4210.5
        )

        return RouteResponse(
            astar=astar_result,
            q_learning=q_learning_result
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))