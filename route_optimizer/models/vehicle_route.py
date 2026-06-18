"""
Domain model for a single vehicle's optimised route within a VRP solution.
"""

from dataclasses import dataclass

from route_optimizer.models.location import Location


@dataclass(frozen=True)
class VehicleRoute:
    """Immutable value object representing one vehicle's delivery route.

    Attributes:
        vehicle_id: The vehicle's numeric identifier.
        vehicle_name: Human-readable vehicle label.
        locations:  Ordered list of stops (starts and ends at depot).
        distance:   Total route distance in kilometres.
        duration:   Total estimated travel time in minutes.
    """

    vehicle_id: int
    vehicle_name: str
    locations: list[Location]
    distance: float
    duration: float

    @property
    def num_stops(self) -> int:
        """Delivery stops excluding the depot return."""
        return max(0, len(self.locations) - 2)  # [depot, ..., depot]

    @property
    def is_empty(self) -> bool:
        """True when the vehicle was not assigned any stops."""
        return self.num_stops == 0

    @property
    def is_round_trip(self) -> bool:
        """True when the route starts and ends at the same location."""
        if len(self.locations) < 2:
            return False
        return self.locations[0] == self.locations[-1]
