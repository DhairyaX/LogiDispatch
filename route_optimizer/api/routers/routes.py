from fastapi import APIRouter
from typing import List
from route_optimizer.api.schemas.route import RouteResponse
from route_optimizer.database.repositories.route_repository import RouteRepository

router = APIRouter(prefix="/api/v1/routes", tags=["Routes"])
route_repo = RouteRepository()

@router.get("/", response_model=List[RouteResponse])
def get_all_routes():
    docs = route_repo.get_all()
    return [RouteResponse(**doc) for doc in docs]

@router.get("/active", response_model=List[RouteResponse])
def get_active_routes():
    docs = route_repo.get_active()
    return [RouteResponse(**doc) for doc in docs]

@router.get("/latest", response_model=RouteResponse)
def get_latest_route():
    doc = route_repo.get_latest()
    if doc:
        return RouteResponse(**doc)
    return None
