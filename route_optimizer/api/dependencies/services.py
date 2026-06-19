from route_optimizer.api.services.driver_service import DriverService
from route_optimizer.api.services.vehicle_service import VehicleService
from route_optimizer.api.services.delivery_service import DeliveryService
from route_optimizer.api.services.optimization_service import OptimizationAPIService

# In-memory singletons for mock persistence
_driver_service = DriverService()
_vehicle_service = VehicleService()
_delivery_service = DeliveryService()
_optimization_service = OptimizationAPIService(_driver_service, _vehicle_service, _delivery_service)

def get_driver_service() -> DriverService:
    return _driver_service

def get_vehicle_service() -> VehicleService:
    return _vehicle_service

def get_delivery_service() -> DeliveryService:
    return _delivery_service

def get_optimization_service() -> OptimizationAPIService:
    return _optimization_service
