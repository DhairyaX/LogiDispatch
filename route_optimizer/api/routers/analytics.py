from fastapi import APIRouter, Depends, HTTPException
from route_optimizer.api.schemas.analytics import AnalyticsResponse
from route_optimizer.api.services.optimization_service import OptimizationAPIService
from route_optimizer.api.dependencies.services import get_optimization_service

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])

@router.get("/fleet", response_model=AnalyticsResponse)
def get_fleet_analytics(service: OptimizationAPIService = Depends(get_optimization_service)):
    stats = service.get_latest_analytics()
    if not stats:
        raise HTTPException(status_code=404, detail="No analytics available. Run optimization first.")
    return stats

@router.get("/routes", response_model=AnalyticsResponse)
def get_routes_analytics(service: OptimizationAPIService = Depends(get_optimization_service)):
    stats = service.get_latest_analytics()
    if not stats:
        raise HTTPException(status_code=404, detail="No analytics available. Run optimization first.")
    return stats

@router.get("/workload", response_model=AnalyticsResponse)
def get_workload_analytics(service: OptimizationAPIService = Depends(get_optimization_service)):
    stats = service.get_latest_analytics()
    if not stats:
        raise HTTPException(status_code=404, detail="No analytics available. Run optimization first.")
    return stats
