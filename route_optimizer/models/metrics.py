"""
Domain model for route performance metrics.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class VehicleMetrics:
    """Per-vehicle metrics within a VRP solution.

    Attributes:
        vehicle_id:   Vehicle identifier.
        vehicle_name: Human-readable vehicle label.
        num_stops:    Delivery stops (excluding depot return).
        distance:     Total route distance in km.
        duration:     Total route duration in minutes.
    """

    vehicle_id: int
    vehicle_name: str
    num_stops: int
    distance: float
    duration: float


@dataclass(frozen=True)
class Metrics:
    """Immutable value object containing post-optimization statistics.

    Attributes:
        total_stops:              Number of unique delivery stops
                                  (excludes the return to depot).
        total_distance:           Total route distance in kilometres.
        average_distance_per_stop: Mean km between consecutive stops.
        execution_time:           Wall-clock solver time in seconds.
        total_duration:           Total estimated travel time in minutes
                                  (0.0 when duration data is unavailable).
        average_duration_per_stop: Mean minutes between consecutive stops
                                  (0.0 when duration data is unavailable).
        distance_source:          Label indicating the distance backend
                                  used (e.g. "euclidean", "osrm").
        optimization_mode:        Label indicating the metric optimised
                                  (e.g. "distance", "duration").
        vehicle_count:            Number of vehicles available.
        vehicles_used:            Number of vehicles that received stops.
        vehicle_metrics:          Per-vehicle breakdown (empty for TSP).
    """

    total_stops: int
    total_distance: float
    average_distance_per_stop: float
    execution_time: float
    total_duration: float = 0.0
    average_duration_per_stop: float = 0.0
    distance_source: str = "euclidean"
    optimization_mode: str = "distance"
    vehicle_count: int = 1
    vehicles_used: int = 1
    vehicle_metrics: list[VehicleMetrics] = field(default_factory=list)
