"""
Metrics calculation service.

Derives post-optimization statistics from solved routes
and measured execution time.
"""

from __future__ import annotations

import math

from route_optimizer.optimization.models.metrics import Metrics, VehicleMetrics
from route_optimizer.optimization.models.route import Route
from route_optimizer.optimization.models.vehicle_route import VehicleRoute


class MetricsService:
    """Stateless service that computes delivery-route KPIs."""

    def calculate(
        self,
        route: Route,
        execution_time: float,
        distance_source: str = "euclidean",
        optimization_mode: str = "distance",
    ) -> Metrics:
        """Derive metrics from a single-vehicle solved route.

        Backward-compatible Phase 1/2 API.

        Args:
            route:              A completed :class:`Route` (must be a round-trip).
            execution_time:     Wall-clock solver duration in seconds.
            distance_source:    Label for the distance backend used.
            optimization_mode:  Label for the metric being optimised.

        Returns:
            A :class:`Metrics` value object.

        Raises:
            ValueError: If the route has no stops.
        """
        if not route.ordered_locations:
            raise ValueError("Cannot compute metrics for an empty route.")

        total_stops = route.num_stops - 1
        total_distance = route.total_distance
        total_duration = route.total_duration

        avg_distance = (
            total_distance / total_stops if total_stops > 0 else 0.0
        )
        avg_duration = (
            total_duration / total_stops if total_stops > 0 else 0.0
        )

        return Metrics(
            total_stops=total_stops,
            total_distance=round(total_distance, 4),
            average_distance_per_stop=round(avg_distance, 4),
            execution_time=round(execution_time, 6),
            total_duration=round(total_duration, 4),
            average_duration_per_stop=round(avg_duration, 4),
            distance_source=distance_source,
            optimization_mode=optimization_mode,
        )

    def calculate_vrp(
        self,
        vehicle_routes: list[VehicleRoute],
        execution_time: float,
        vehicle_count: int,
        distance_source: str = "euclidean",
        optimization_mode: str = "distance",
        balancing_mode: str = "balanced",
        driver_assignments: dict[int, dict[str, str]] | None = None,
        vehicle_assignments: dict[int, dict[str, str]] | None = None,
    ) -> Metrics:
        """Derive metrics from a multi-vehicle VRP solution.

        Args:
            vehicle_routes:     Per-vehicle route results.
            execution_time:     Wall-clock solver duration in seconds.
            vehicle_count:      Total vehicles available.
            distance_source:    Label for the distance backend used.
            optimization_mode:  Label for the metric being optimised.
            balancing_mode:     Label for the workload balancing strategy.

        Returns:
            A :class:`Metrics` value object with per-vehicle breakdown.

        Raises:
            ValueError: If no vehicle routes are provided.
        """
        if not vehicle_routes:
            raise ValueError("Cannot compute metrics without vehicle routes.")

        total_stops = sum(vr.num_stops for vr in vehicle_routes)
        total_distance = sum(vr.distance for vr in vehicle_routes)
        total_duration = sum(vr.duration for vr in vehicle_routes)

        vehicles_used = sum(1 for vr in vehicle_routes if not vr.is_empty)

        avg_distance = (
            total_distance / total_stops if total_stops > 0 else 0.0
        )
        avg_duration = (
            total_duration / total_stops if total_stops > 0 else 0.0
        )

        # ── Workload distribution metrics ──
        stops_per_vehicle = [vr.num_stops for vr in vehicle_routes]
        max_stops = max(stops_per_vehicle) if stops_per_vehicle else 0
        min_stops = min(stops_per_vehicle) if stops_per_vehicle else 0

        distances_per_vehicle = [vr.distance for vr in vehicle_routes]
        max_dist = max(distances_per_vehicle) if distances_per_vehicle else 0.0
        min_dist = min(distances_per_vehicle) if distances_per_vehicle else 0.0

        durations_per_vehicle = [vr.duration for vr in vehicle_routes]
        max_dur = max(durations_per_vehicle) if durations_per_vehicle else 0.0
        min_dur = min(durations_per_vehicle) if durations_per_vehicle else 0.0

        if len(stops_per_vehicle) > 1:
            mean_stops = sum(stops_per_vehicle) / len(stops_per_vehicle)
            variance_stops = sum((s - mean_stops) ** 2 for s in stops_per_vehicle) / len(stops_per_vehicle)
            stddev_stops = math.sqrt(variance_stops)

            mean_distance = sum(distances_per_vehicle) / len(distances_per_vehicle)
            variance_distance = sum((d - mean_distance) ** 2 for d in distances_per_vehicle) / len(distances_per_vehicle)
            stddev_distance = math.sqrt(variance_distance)

            mean_duration = sum(durations_per_vehicle) / len(durations_per_vehicle)
            variance_duration = sum((d - mean_duration) ** 2 for d in durations_per_vehicle) / len(durations_per_vehicle)
            stddev_duration = math.sqrt(variance_duration)
        else:
            stddev_stops = 0.0
            stddev_distance = 0.0
            stddev_duration = 0.0

        utilization_rate = (vehicles_used / vehicle_count * 100.0) if vehicle_count > 0 else 0.0
        driver_assignments = driver_assignments or {}
        vehicle_assignments = vehicle_assignments or {}
        per_vehicle: list[VehicleMetrics] = [
            VehicleMetrics(
                vehicle_id=vehicle_assignments.get(vr.vehicle_id, {}).get("id", str(vr.vehicle_id)),
                vehicle_name=vehicle_assignments.get(vr.vehicle_id, {}).get("name", vr.vehicle_name),
                driver_id=driver_assignments.get(vr.vehicle_id, {}).get("id"),
                driver_name=driver_assignments.get(vr.vehicle_id, {}).get("name"),
                num_stops=vr.num_stops,
                distance=round(vr.distance, 4),
                duration=round(vr.duration, 4),
            )
            for vr in vehicle_routes
        ]

        return Metrics(
            total_stops=total_stops,
            total_distance=round(total_distance, 4),
            average_distance_per_stop=round(avg_distance, 4),
            execution_time=round(execution_time, 6),
            total_duration=round(total_duration, 4),
            average_duration_per_stop=round(avg_duration, 4),
            distance_source=distance_source,
            optimization_mode=optimization_mode,
            vehicle_count=vehicle_count,
            vehicles_used=vehicles_used,
            vehicle_metrics=per_vehicle,
            max_stops_per_vehicle=max_stops,
            min_stops_per_vehicle=min_stops,
            max_distance_per_vehicle=round(max_dist, 4),
            min_distance_per_vehicle=round(min_dist, 4),
            max_duration_per_vehicle=round(max_dur, 4),
            min_duration_per_vehicle=round(min_dur, 4),
            stop_distribution_stddev=round(stddev_stops, 4),
            distance_distribution_stddev=round(stddev_distance, 4),
            duration_distribution_stddev=round(stddev_duration, 4),
            vehicle_utilization_rate=round(utilization_rate, 2),
            balancing_mode=balancing_mode,
        )
