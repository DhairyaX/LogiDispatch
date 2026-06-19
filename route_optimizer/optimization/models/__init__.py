"""Domain models package."""

from route_optimizer.optimization.models.location import Location
from route_optimizer.optimization.models.metrics import Metrics
from route_optimizer.optimization.models.route import Route
from route_optimizer.optimization.models.vehicle import Vehicle
from route_optimizer.optimization.models.vehicle_route import VehicleRoute

__all__ = ["Location", "Metrics", "Route", "Vehicle", "VehicleRoute"]
