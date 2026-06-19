from route_optimizer.optimization.models.location import Location
from route_optimizer.optimization.services.distance_service import DistanceService
from route_optimizer.optimization.services.optimization_service import OptimizationService

# 1. Create fake locations
depot = Location(id=0, name="Depot", latitude=28.4949, longitude=77.0895)
l1 = Location(id=1, name="Loc 1", latitude=28.5000, longitude=77.1000)
l2 = Location(id=2, name="Loc 2", latitude=28.5100, longitude=77.0900)
locations = [depot, l1, l2]

# 2. Get matrices
ds = DistanceService()
distance_matrix = ds.generate_distance_matrix(locations)
duration_matrix = ds.generate_duration_matrix(locations)

print("Dist matrix:", distance_matrix)
print("Dur matrix:", duration_matrix)

# 3. Test solve_vrp
opt = OptimizationService()
try:
    print("Testing DURATION + DISTANCE_OPTIMAL")
    routes = opt.solve_vrp(
        locations=locations,
        distance_matrix=distance_matrix,
        depot_index=0,
        vehicle_count=2,
        cost_matrix=duration_matrix,
        duration_matrix=duration_matrix,
        optimization_mode="duration",
        balancing_mode="distance_optimal",
        balance_weight=100
    )
    for r in routes:
        print(r)
except Exception as e:
    import traceback
    traceback.print_exc()
