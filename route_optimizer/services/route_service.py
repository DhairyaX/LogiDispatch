"""
Route orchestration service.

Coordinates the distance, vehicle, and optimization services to produce
fully-solved routes.  Acts as the single entry-point that
``main.py`` interacts with.
"""

from __future__ import annotations

import logging
from typing import Sequence

from route_optimizer.config.settings import DistanceSource, OptimizationMode, settings
from route_optimizer.models.location import Location
from route_optimizer.models.route import Route
from route_optimizer.models.vehicle_route import VehicleRoute
from route_optimizer.services.distance_service import DistanceService
from route_optimizer.services.optimization_service import OptimizationService

logger = logging.getLogger(__name__)


class RouteService:
    """High-level orchestrator for the route-optimization pipeline."""

    def __init__(
        self,
        distance_service: DistanceService | None = None,
        optimization_service: OptimizationService | None = None,
    ) -> None:
        self._distance_service = distance_service or DistanceService()
        self._optimization_service = optimization_service or OptimizationService()

    # ── Public API ──────────────────────────────────────────────

    @property
    def distance_source(self) -> DistanceSource:
        """The distance source currently being used."""
        return self._distance_service.active_source

    @property
    def used_fallback(self) -> bool:
        """Whether an OSRM fallback to Euclidean occurred."""
        return self._distance_service.used_fallback

    def optimize_route(
        self,
        locations: Sequence[Location],
        depot_index: int = 0,
    ) -> tuple[Route, list[list[int]]]:
        """Run the full TSP optimisation pipeline (single vehicle).

        Backward-compatible Phase 1/2 API.

        Steps:
            1. Generate the distance matrix (Euclidean or OSRM).
            2. Optionally generate a duration matrix.
            3. Select the cost matrix based on ``optimization_mode``.
            4. Solve the TSP.
            5. Return the optimised route **and** the distance matrix.

        Args:
            locations:   List of delivery locations (index 0 = depot).
            depot_index: Index of the depot within *locations*.

        Returns:
            A tuple of ``(Route, distance_matrix)``.

        Raises:
            ValueError: Propagated from downstream services.
        """
        if not locations:
            raise ValueError("At least one location (the depot) is required.")

        distance_matrix, duration_matrix, cost_matrix = self._prepare_matrices(locations)

        route = self._optimization_service.solve(
            locations,
            distance_matrix,
            depot_index,
            cost_matrix=cost_matrix,
            duration_matrix=duration_matrix,
        )

        return route, distance_matrix

    def optimize_vrp(
        self,
        locations: Sequence[Location],
        depot_index: int = 0,
        vehicle_count: int | None = None,
    ) -> tuple[list[VehicleRoute], list[list[int]]]:
        """Run the full VRP optimisation pipeline (multiple vehicles).

        Steps:
            1. Generate the distance matrix (Euclidean or OSRM).
            2. Optionally generate a duration matrix.
            3. Select the cost matrix based on ``optimization_mode``.
            4. Solve the VRP.
            5. Return per-vehicle routes **and** the distance matrix.

        Args:
            locations:     List of delivery locations (index 0 = depot).
            depot_index:   Index of the depot within *locations*.
            vehicle_count: Number of vehicles.  Defaults to
                           ``settings.optimizer.vehicle_count``.

        Returns:
            A tuple of ``(list[VehicleRoute], distance_matrix)``.

        Raises:
            ValueError: Propagated from downstream services.
        """
        if not locations:
            raise ValueError("At least one location (the depot) is required.")

        vc = vehicle_count or settings.optimizer.vehicle_count

        distance_matrix, duration_matrix, cost_matrix = self._prepare_matrices(locations)

        vehicle_routes = self._optimization_service.solve_vrp(
            locations,
            distance_matrix,
            depot_index,
            vehicle_count=vc,
            cost_matrix=cost_matrix,
            duration_matrix=duration_matrix,
        )

        return vehicle_routes, distance_matrix

    # ── Internals ───────────────────────────────────────────────

    def _prepare_matrices(
        self,
        locations: Sequence[Location],
    ) -> tuple[list[list[int]], list[list[int]] | None, list[list[int]] | None]:
        """Generate distance/duration matrices and select cost matrix.

        Returns:
            ``(distance_matrix, duration_matrix, cost_matrix)``
        """
        distance_matrix = self._distance_service.generate_distance_matrix(locations)
        duration_matrix = self._distance_service.generate_duration_matrix(locations)

        opt_mode = settings.optimizer.optimization_mode
        cost_matrix = None
        if opt_mode == OptimizationMode.DURATION and duration_matrix is not None:
            cost_matrix = duration_matrix
            logger.info("Optimising by DURATION.")
        else:
            if opt_mode == OptimizationMode.DURATION and duration_matrix is None:
                logger.warning(
                    "Duration matrix unavailable; falling back to distance optimisation."
                )
            logger.info("Optimising by DISTANCE.")

        return distance_matrix, duration_matrix, cost_matrix
