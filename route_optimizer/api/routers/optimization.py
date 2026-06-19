from fastapi import APIRouter, Depends, HTTPException
from route_optimizer.api.schemas.optimization import OptimizationRequest, OptimizationResponse
from route_optimizer.api.services.optimization_service import OptimizationAPIService
from route_optimizer.api.dependencies.services import get_optimization_service

router = APIRouter(prefix="/api/v1/optimization", tags=["Optimization"])

@router.post("/generate-routes", response_model=OptimizationResponse)
def generate_routes(req: OptimizationRequest, service: OptimizationAPIService = Depends(get_optimization_service)):
    return service.generate_routes(req)

@router.post("/simulate-day")
def simulate_day(service: OptimizationAPIService = Depends(get_optimization_service)):
    service.simulate_day()
    return {"status": "success", "message": "Mock operational data generated."}

@router.get("/latest-route", response_model=OptimizationResponse)
def get_latest_route(service: OptimizationAPIService = Depends(get_optimization_service)):
    resp = service.get_latest_response()
    if not resp:
        raise HTTPException(status_code=404, detail="No routes have been generated yet.")
    return resp
