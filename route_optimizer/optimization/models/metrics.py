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
        driver_id:    Driver identifier.
        driver_name:  Human-readable driver label.
        num_stops:    Delivery stops (excluding depot return).
        distance:     Total route distance in km.
        duration:     Total route duration in minutes.
    """

    vehicle_id: str | int
    vehicle_name: str
    driver_id: str | None
    driver_name: str | None
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
    max_stops_per_vehicle:    Maximum stops assigned to any single vehicle.
    min_stops_per_vehicle:    Minimum stops assigned to any single vehicle.
    stop_distribution_stddev: Standard deviation of stops across the fleet.
    vehicle_utilization_rate: Percentage of vehicles used (0.0 to 100.0).
    balancing_mode:           Label indicating the balancing strategy.
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
    max_stops_per_vehicle: int = 0
    min_stops_per_vehicle: int = 0
    max_distance_per_vehicle: float = 0.0
    min_distance_per_vehicle: float = 0.0
    max_duration_per_vehicle: float = 0.0
    min_duration_per_vehicle: float = 0.0
    stop_distribution_stddev: float = 0.0
    distance_distribution_stddev: float = 0.0
    duration_distribution_stddev: float = 0.0
    vehicle_utilization_rate: float = 100.0
    balancing_mode: str = "balanced"
