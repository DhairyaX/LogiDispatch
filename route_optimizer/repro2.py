from route_optimizer.api.services.optimization_service import OptimizationAPIService
from route_optimizer.api.services.driver_service import DriverService
from route_optimizer.api.services.vehicle_service import VehicleService
from route_optimizer.api.services.delivery_service import DeliveryService
from route_optimizer.api.schemas.optimization import OptimizationRequest

try:
    svc = OptimizationAPIService(DriverService(), VehicleService(), DeliveryService())
    req = OptimizationRequest(vehicleCount=3, optimizationMode="distance", balancingMode="strict")
    res = svc.generate_routes(req)
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()
