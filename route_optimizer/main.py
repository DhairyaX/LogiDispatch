#!/usr/bin/env python3
"""
Logistics Route Optimization Engine — Entry Point.

Orchestrates the end-to-end pipeline:
    1. Load locations
    2. Generate distance / duration matrices
    3. Run VRP optimisation (multi-vehicle)
    4. Compute route metrics
    5. Display professional CLI output

All business logic resides in dedicated services; this module
only performs wiring and high-level flow control.
"""

from __future__ import annotations

import sys

from route_optimizer.optimization.config.settings import settings
from route_optimizer.optimization.data.sample_locations import get_sample_locations
from route_optimizer.optimization.services.metrics_service import MetricsService
from route_optimizer.optimization.services.route_service import RouteService
from route_optimizer.optimization.utils.printer import (
    console,
    print_header,
    print_config_summary,
    print_locations_loaded,
    print_matrix_generated,
    print_optimization_started,
    print_optimization_completed,
    print_fallback_warning,
    print_vehicle_routes,
    print_metrics,
    print_footer,
    print_error,
)
from route_optimizer.optimization.utils.timer import Timer


def main() -> None:
    """Execute the route-optimization pipeline."""
    try:
        # ── Banner ──────────────────────────────────────────────
        print_header()

        # ── Config summary ──────────────────────────────────────
        distance_source = settings.distance.distance_source.value
        optimization_mode = settings.optimizer.optimization_mode.value
        balancing_mode = settings.optimizer.balancing_mode.value
        vehicle_count = settings.optimizer.vehicle_count
        print_config_summary(distance_source, optimization_mode, vehicle_count)

        # ── 1. Load locations ───────────────────────────────────
        locations = get_sample_locations()
        print_locations_loaded(locations)

        # ── 2–3. Generate matrices & optimise ───────────────────
        route_service = RouteService()
        metrics_service = MetricsService()

        print_optimization_started()

        with Timer() as timer:
            vehicle_routes, distance_matrix = route_service.optimize_vrp(
                locations,
                vehicle_count=vehicle_count,
            )

        print_optimization_completed()

        # ── Fallback warning ────────────────────────────────────
        if route_service.used_fallback:
            print_fallback_warning()
            distance_source = "euclidean (fallback)"

        # ── 4. Matrix confirmation ──────────────────────────────
        print_matrix_generated(len(distance_matrix), label="Distance")
        console.print()

        # ── 5. Display per-vehicle routes ───────────────────────
        print_vehicle_routes(vehicle_routes)

        # ── 6. Compute metrics ──────────────────────────────────
        actual_source = route_service.distance_source.value
        metrics = metrics_service.calculate_vrp(
            vehicle_routes,
            timer.elapsed,
            vehicle_count=vehicle_count,
            distance_source=actual_source if not route_service.used_fallback else "euclidean (fallback)",
            optimization_mode=optimization_mode,
            balancing_mode=balancing_mode,
        )

        # ── 7. Display summary ──────────────────────────────────
        print_metrics(metrics)

        # ── 8. Footer ──────────────────────────────────────────
        print_footer()

    except (ValueError, TypeError) as exc:
        print_error(str(exc))
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001 — catch-all for graceful exit
        print_error(f"Unexpected error: {exc}")
        sys.exit(2)


if __name__ == "__main__":
    main()
