"""
Vehicle management service.

Creates and manages the fleet of delivery vehicles used
by the VRP solver.
"""

from __future__ import annotations

from route_optimizer.config.settings import settings
from route_optimizer.models.vehicle import Vehicle


class VehicleService:
    """Service for creating and validating delivery vehicle fleets."""

    def __init__(self, vehicle_count: int | None = None) -> None:
        self._vehicle_count = (
            vehicle_count if vehicle_count is not None
            else settings.optimizer.vehicle_count
        )

    @property
    def vehicle_count(self) -> int:
        """Number of vehicles in the fleet."""
        return self._vehicle_count

    def create_fleet(self) -> list[Vehicle]:
        """Create a list of Vehicle instances based on configuration.

        Returns:
            A list of :class:`Vehicle` objects.

        Raises:
            ValueError: If vehicle count is less than 1.
        """
        if self._vehicle_count < 1:
            raise ValueError(
                f"Vehicle count must be >= 1, got {self._vehicle_count}."
            )
        return [
            Vehicle(id=i, name=f"Vehicle {i + 1}")
            for i in range(self._vehicle_count)
        ]

    def validate_fleet_size(self, num_stops: int) -> int:
        """Return the effective vehicle count, capped at the number of stops.

        If there are more vehicles than delivery stops, the effective
        count is reduced (extra vehicles would have empty routes).

        Args:
            num_stops: Number of delivery stops (excluding depot).

        Returns:
            Effective vehicle count.
        """
        if num_stops <= 0:
            return 1
        return min(self._vehicle_count, num_stops)
