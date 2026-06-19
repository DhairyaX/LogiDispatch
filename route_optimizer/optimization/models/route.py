"""
Domain model for an optimized delivery route.
"""

from dataclasses import dataclass, field

from route_optimizer.optimization.models.location import Location


@dataclass(frozen=True)
class Route:
    """Immutable value object representing a solved delivery route.

    Attributes:
        ordered_locations: The sequence of locations in visit order,
                           starting and ending at the depot / warehouse.
        total_distance:    Total travel distance of the route in kilometres.
        total_duration:    Total estimated travel time in minutes (0.0 when
                           duration data is unavailable).
    """

    ordered_locations: list[Location]
    total_distance: float
    total_duration: float = 0.0

    @property
    def num_stops(self) -> int:
        """Number of stops *including* the depot appearances."""
        return len(self.ordered_locations)

    @property
    def is_round_trip(self) -> bool:
        """True when the route starts and ends at the same location."""
        if len(self.ordered_locations) < 2:
            return False
        return self.ordered_locations[0] == self.ordered_locations[-1]
