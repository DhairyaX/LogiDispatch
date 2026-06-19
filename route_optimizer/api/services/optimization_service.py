from typing import List
from route_optimizer.optimization.models.location import Location
from route_optimizer.optimization.services.route_service import RouteService
from route_optimizer.optimization.services.metrics_service import MetricsService
from route_optimizer.optimization.utils.timer import Timer
from datetime import datetime, timezone

from route_optimizer.api.schemas.optimization import OptimizationRequest, OptimizationResponse, VehicleRouteSchema, RouteLocation
from route_optimizer.api.schemas.analytics import AnalyticsResponse
from route_optimizer.api.core.exceptions import OptimizationError

from route_optimizer.api.services.driver_service import DriverService
from route_optimizer.api.services.vehicle_service import VehicleService
from route_optimizer.api.services.delivery_service import DeliveryService
from route_optimizer.database.repositories.route_repository import RouteRepository
from route_optimizer.database.repositories.route_snapshot_repository import RouteSnapshotRepository
from route_optimizer.database.repositories.analytics_repository import AnalyticsRepository
from route_optimizer.api.schemas.driver import DriverCreate
from route_optimizer.api.schemas.vehicle import VehicleCreate
from route_optimizer.api.schemas.delivery import DeliveryCreate

import random

# Central Depot
DEPOT = Location(
    id=0,
    name="Cyber City (Warehouse)",
    latitude=28.4949,
    longitude=77.0895
)

import logging

logger = logging.getLogger(__name__)

class OptimizationAPIService:
    def __init__(self, driver_svc: DriverService, vehicle_svc: VehicleService, delivery_svc: DeliveryService):
        self.driver_svc = driver_svc
        self.vehicle_svc = vehicle_svc
        self.delivery_svc = delivery_svc
        self.route_repo = RouteRepository()
        self.snapshot_repo = RouteSnapshotRepository()
        self.analytics_repo = AnalyticsRepository()

    def generate_routes(self, req: OptimizationRequest) -> OptimizationResponse:
        logger.info("[Optimization Started]")
        
        # 1. Fetch available resources
        available_drivers = [d for d in self.driver_svc.get_all() if d.status == "Available"]
        available_vehicles = [v for v in self.vehicle_svc.get_all() if v.status == "Available"]
        deliveries = [d for d in self.delivery_svc.get_all() if d.status in ("Pending", "Assigned")]

        logger.info(f"Available Drivers Found: {len(available_drivers)}")
        logger.info(f"Available Vehicles Found: {len(available_vehicles)}")
        logger.info(f"Deliveries Found: {len(deliveries)}")

        if not available_drivers or not available_vehicles:
            raise OptimizationError("No available fleet to assign routes.")
        if not deliveries:
            raise OptimizationError("No pending deliveries to optimize.")

        active_fleet_count = min(req.vehicleCount, len(available_vehicles))

        # 2. Convert to domain Location objects
        locations: List[Location] = [DEPOT]
        id_map = {0: "0"} # Map Integer ID to String ID
        
        for idx, d in enumerate(deliveries, start=1):
            id_map[idx] = d.id
            loc = Location(
                id=idx,
                name=d.address,
                latitude=d.latitude,
                longitude=d.longitude
            )
            locations.append(loc)

        # 3. Optimize via existing OR-Tools engine
        route_service = RouteService()
        metrics_service = MetricsService()

        try:
            with Timer() as timer:
                vehicle_routes, distance_matrix = route_service.optimize_vrp(
                    locations,
                    vehicle_count=active_fleet_count,
                    optimization_mode=req.optimizationMode,
                    balancing_mode=req.balancingMode
                )
            
            logger.info(f"Routes Generated: {len(vehicle_routes)}")
            
            # Archive existing active routes
            self.route_repo.archive_all_active()

            # Filter active routes that actually have stops
            active_routes = [vr for vr in vehicle_routes if len(vr.locations) > 1]
            
            if len(active_routes) > len(available_drivers):
                raise OptimizationError(f"Not enough available drivers. Need {len(active_routes)} but only have {len(available_drivers)}.")

            # Format Response using String IDs mapped back
            routes_schema = []
            saved_route_ids = []
            created_at = datetime.now(timezone.utc).isoformat()
            
            # Extract assigned metrics to pass to MetricsService
            driver_assignments = {}
            vehicle_assignments = {}

            for idx, vr in enumerate(vehicle_routes):
                locs = []
                delivery_ids = []
                for l in vr.locations:
                    real_id = id_map[l.id]
                    if real_id != "0":
                        delivery_ids.append(real_id)
                    locs.append(RouteLocation(
                        id=real_id, 
                        name=l.name, 
                        latitude=l.latitude, 
                        longitude=l.longitude
                    ))
                
                v_obj = available_vehicles[vr.vehicle_id] if vr.vehicle_id < len(available_vehicles) else available_vehicles[0]
                
                # Assign driver ONLY if route is active
                is_active = len(locs) > 1
                d_obj = available_drivers[idx] if is_active and idx < len(available_drivers) else None
                
                if d_obj:
                    driver_assignments[vr.vehicle_id] = {"id": d_obj.id, "name": d_obj.name}
                
                # Always map vehicle ID and name
                vehicle_assignments[vr.vehicle_id] = {"id": v_obj.id, "name": v_obj.name}
                
                routes_schema.append(VehicleRouteSchema(
                    vehicle_id=v_obj.id,
                    vehicle_name=v_obj.name,
                    driver_id=d_obj.id if d_obj else None,
                    driver_name=d_obj.name if d_obj else None,
                    locations=locs,
                    distance=vr.distance,
                    duration=vr.duration
                ))

                # Individual route persistence
                if is_active:
                    route_doc = {
                        "driverId": d_obj.id if d_obj else None,
                        "driverName": d_obj.name if d_obj else None,
                        "vehicleId": v_obj.id,
                        "vehicleName": v_obj.name,
                        "deliveryIds": delivery_ids,
                        "stopCount": len(delivery_ids),
                        "totalDistanceKm": vr.distance,
                        "totalDurationMinutes": vr.duration,
                        "routeSequence": [loc.model_dump() for loc in locs],
                        "status": "Active",
                        "createdAt": created_at
                    }
                    
                    logger.info(f"Saving Route: {v_obj.id}")
                    saved_doc = self.route_repo.create(route_doc)
                    saved_route_ids.append(saved_doc["id"])
                    logger.info(f"Saved Route: {saved_doc['id']}")

            logger.info("Routes Saved Successfully")
            
            actual_source = route_service.distance_source.value
            metrics = metrics_service.calculate_vrp(
                vehicle_routes,
                timer.elapsed,
                vehicle_count=active_fleet_count,
                distance_source=actual_source,
                optimization_mode=req.optimizationMode,
                balancing_mode=req.balancingMode,
                driver_assignments=driver_assignments,
                vehicle_assignments=vehicle_assignments
            )
            from dataclasses import asdict
            metrics_dict = asdict(metrics)

            # Persist Snapshot Data
            snapshot_data = {
                "generatedAt": created_at,
                "optimizationMode": req.optimizationMode,
                "balancingMode": req.balancingMode,
                "vehiclesUsed": metrics.vehicles_used,
                "fleetUtilization": metrics.vehicle_utilization_rate,
                "totalDistance": metrics.total_distance,
                "totalDuration": metrics.total_duration,
                "routes": [r.model_dump() for r in routes_schema],
                "metrics": metrics_dict
            }
            saved_snapshot = self.snapshot_repo.create(snapshot_data)

            resp = OptimizationResponse(
                id=saved_snapshot["id"],
                vehiclesUsed=metrics.vehicles_used,
                fleetUtilization=metrics.vehicle_utilization_rate,
                totalDistance=metrics.total_distance,
                totalDuration=metrics.total_duration,
                routes=routes_schema,
                metrics=metrics_dict
            )
            
            # Persist Analytics Data
            analytics_data = {
                "createdAt": created_at,
                "fleetUtilization": metrics.vehicle_utilization_rate,
                "workloadStandardDeviation": metrics.stop_distribution_stddev,
                "distanceStandardDeviation": metrics.distance_distribution_stddev,
                "durationStandardDeviation": metrics.duration_distribution_stddev,
                "averageStopsPerVehicle": metrics.total_stops / (metrics.vehicles_used or 1),
                "averageDistancePerVehicle": metrics.total_distance / (metrics.vehicles_used or 1),
                "averageDurationPerVehicle": metrics.total_duration / (metrics.vehicles_used or 1),
                "maxDistance": metrics.max_distance_per_vehicle,
                "minDistance": metrics.min_distance_per_vehicle,
                "maxDuration": metrics.max_duration_per_vehicle,
                "minDuration": metrics.min_duration_per_vehicle
            }
            self.analytics_repo.create(analytics_data)

            logger.info("Returning Response")
            return resp

        except Exception as e:
            raise OptimizationError(f"Engine failed: {str(e)}")

    def get_latest_analytics(self) -> AnalyticsResponse | None:
        latest = self.analytics_repo.get_latest()
        if latest:
            return AnalyticsResponse(**latest)
        return None
    
    def get_latest_response(self) -> OptimizationResponse | None:
        latest = self.snapshot_repo.get_latest()
        if latest:
            return OptimizationResponse(**latest)
        return None

    def simulate_day(self):
        """Populates the DB with mock day data for UI demonstration"""
        for i in range(5):
            self.driver_svc.create(DriverCreate(name=f"Demo Driver {i+1}", phone="555-0000", status="Available"))
            self.vehicle_svc.create(VehicleCreate(name=f"E-Van {i+1}", vehicleNumber=f"EV-{100+i}", status="Available"))
        
        # Add deliveries around Gurgaon
        lat_base, lon_base = 28.4595, 77.0266
        for i in range(15):
            self.delivery_svc.create(DeliveryCreate(
                customerName=f"Customer {i+1}",
                phoneNumber="555-1111",
                address=f"Location {i+1}",
                latitude=lat_base + random.uniform(-0.05, 0.05),
                longitude=lon_base + random.uniform(-0.05, 0.05),
                priority="Medium",
                status="Pending",
                packageWeight=random.uniform(1.0, 15.0)
            ))
