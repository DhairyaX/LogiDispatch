"""
Metrics calculation service.

Derives post-optimization statistics from solved routes
and measured execution time.
"""

from __future__ import annotations

from route_optimizer.models.metrics import Metrics, VehicleMetrics
from route_optimizer.models.route import Route
from route_optimizer.models.vehicle_route import VehicleRoute


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
    ) -> Metrics:
        """Derive metrics from a multi-vehicle VRP solution.

        Args:
            vehicle_routes:     Per-vehicle route results.
            execution_time:     Wall-clock solver duration in seconds.
            vehicle_count:      Total vehicles available.
            distance_source:    Label for the distance backend used.
            optimization_mode:  Label for the metric being optimised.

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

        per_vehicle: list[VehicleMetrics] = [
            VehicleMetrics(
                vehicle_id=vr.vehicle_id,
                vehicle_name=vr.vehicle_name,
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
        )
