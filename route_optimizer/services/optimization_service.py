"""
Optimization service — wraps Google OR-Tools to solve the
Travelling Salesman Problem (TSP) and Vehicle Routing Problem (VRP).

All solver configuration and invocation logic is isolated here so
that future constraint additions (capacity, time windows) remain
localised.
"""

from __future__ import annotations

from typing import Sequence

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from route_optimizer.config.settings import settings
from route_optimizer.models.location import Location
from route_optimizer.models.route import Route
from route_optimizer.models.vehicle_route import VehicleRoute


class OptimizationService:
    """Solves TSP (1 vehicle) and VRP (N vehicles) using OR-Tools."""

    def __init__(self) -> None:
        self._time_limit = settings.optimizer.solver_time_limit_seconds
        self._first_strategy = settings.optimizer.first_solution_strategy
        self._metaheuristic = settings.optimizer.local_search_metaheuristic

    # ── Public API ──────────────────────────────────────────────

    def solve(
        self,
        locations: Sequence[Location],
        distance_matrix: list[list[int]],
        depot_index: int = 0,
        cost_matrix: list[list[int]] | None = None,
        duration_matrix: list[list[int]] | None = None,
    ) -> Route:
        """Run the TSP solver (single vehicle) and return a :class:`Route`.

        Backward-compatible Phase 1/2 API.

        Args:
            locations:       Ordered list of locations matching the matrix indices.
            distance_matrix: NxN integer distance matrix (scaled km).
            depot_index:     Index of the depot / warehouse in *locations*.
            cost_matrix:     Optional alternative NxN matrix used as the
                             solver's arc cost.
            duration_matrix: Optional NxN integer duration matrix (scaled
                             minutes).

        Returns:
            A :class:`Route` containing the ordered stops and total distance.

        Raises:
            ValueError: If inputs are invalid or the solver finds no solution.
        """
        vehicle_routes = self.solve_vrp(
            locations=locations,
            distance_matrix=distance_matrix,
            depot_index=depot_index,
            vehicle_count=1,
            cost_matrix=cost_matrix,
            duration_matrix=duration_matrix,
        )
        # Single vehicle — convert to legacy Route.
        vr = vehicle_routes[0]
        return Route(
            ordered_locations=vr.locations,
            total_distance=vr.distance,
            total_duration=vr.duration,
        )

    def solve_vrp(
        self,
        locations: Sequence[Location],
        distance_matrix: list[list[int]],
        depot_index: int = 0,
        vehicle_count: int = 1,
        cost_matrix: list[list[int]] | None = None,
        duration_matrix: list[list[int]] | None = None,
    ) -> list[VehicleRoute]:
        """Run the VRP solver and return a list of per-vehicle routes.

        When ``vehicle_count`` is 1, this degenerates to the TSP.

        Args:
            locations:       Ordered locations matching matrix indices.
            distance_matrix: NxN integer distance matrix (scaled km).
            depot_index:     Index of the depot / warehouse.
            vehicle_count:   Number of delivery vehicles.
            cost_matrix:     Optional cost matrix for solver objective.
            duration_matrix: Optional duration matrix for reporting.

        Returns:
            A list of :class:`VehicleRoute`, one per vehicle.

        Raises:
            ValueError: On invalid inputs or no feasible solution.
        """
        self._validate_inputs(locations, distance_matrix, depot_index)

        if vehicle_count < 1:
            raise ValueError(
                f"Vehicle count must be >= 1, got {vehicle_count}."
            )

        # Cap vehicles at number of delivery stops.
        num_stops = len(locations) - 1  # exclude depot
        effective_vehicles = min(vehicle_count, max(num_stops, 1))

        solver_matrix = cost_matrix if cost_matrix is not None else distance_matrix
        num_locations = len(locations)
        scaling_factor = settings.distance.scaling_factor

        # ── 1. Routing index manager ────────────────────────────
        manager = pywrapcp.RoutingIndexManager(
            num_locations,       # number of nodes
            effective_vehicles,  # number of vehicles
            depot_index,         # depot
        )

        # ── 2. Routing model ────────────────────────────────────
        routing = pywrapcp.RoutingModel(manager)

        # ── 3. Transit callback ─────────────────────────────────
        def _cost_callback(from_index: int, to_index: int) -> int:
            """Return the cost between two nodes."""
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return solver_matrix[from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(_cost_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # ── 3b. Distance dimension (balances load across vehicles) ──
        if effective_vehicles > 1:
            # Compute a reasonable upper bound for any single vehicle.
            max_single = sum(
                max(row) for row in solver_matrix
            )
            routing.AddDimension(
                transit_callback_index,
                0,              # no slack
                max_single,     # maximum distance per vehicle
                True,           # start cumul to zero
                "Distance",
            )
            distance_dimension = routing.GetDimensionOrDie("Distance")
            # Penalise the span (max - min across vehicles) to
            # encourage even distribution of work.
            distance_dimension.SetGlobalSpanCostCoefficient(100)

        # ── 4. Search parameters ────────────────────────────────
        search_params = pywrapcp.DefaultRoutingSearchParameters()

        search_params.first_solution_strategy = getattr(
            routing_enums_pb2.FirstSolutionStrategy,
            self._first_strategy,
        )
        search_params.local_search_metaheuristic = getattr(
            routing_enums_pb2.LocalSearchMetaheuristic,
            self._metaheuristic,
        )
        search_params.time_limit.seconds = self._time_limit

        # ── 5. Solve ────────────────────────────────────────────
        solution = routing.SolveWithParameters(search_params)

        if solution is None:
            raise ValueError(
                "OR-Tools could not find a feasible solution. "
                "Check the distance matrix and solver settings."
            )

        # ── 6. Extract per-vehicle routes ───────────────────────
        vehicle_routes: list[VehicleRoute] = []

        for v in range(effective_vehicles):
            ordered: list[Location] = []
            route_indices: list[int] = []

            index = routing.Start(v)
            while not routing.IsEnd(index):
                node = manager.IndexToNode(index)
                ordered.append(locations[node])
                route_indices.append(node)
                index = solution.Value(routing.NextVar(index))
            # Close the loop.
            ordered.append(locations[depot_index])
            route_indices.append(depot_index)

            # ── Compute distance ────────────────────────────────
            total_distance_km = 0.0
            for k in range(len(route_indices) - 1):
                total_distance_km += distance_matrix[route_indices[k]][route_indices[k + 1]]
            total_distance_km /= scaling_factor

            # ── Compute duration ────────────────────────────────
            total_duration_min = 0.0
            if duration_matrix is not None:
                for k in range(len(route_indices) - 1):
                    total_duration_min += duration_matrix[route_indices[k]][route_indices[k + 1]]
                total_duration_min /= scaling_factor

            vehicle_routes.append(
                VehicleRoute(
                    vehicle_id=v,
                    vehicle_name=f"Vehicle {v + 1}",
                    locations=ordered,
                    distance=total_distance_km,
                    duration=total_duration_min,
                )
            )

        return vehicle_routes

    # ── Validation ──────────────────────────────────────────────

    @staticmethod
    def _validate_inputs(
        locations: Sequence[Location],
        distance_matrix: list[list[int]],
        depot_index: int,
    ) -> None:
        """Sanity-check inputs before handing them to the solver."""
        if not locations:
            raise ValueError("Location list must not be empty.")

        n = len(locations)
        if len(distance_matrix) != n:
            raise ValueError(
                f"Distance matrix row count ({len(distance_matrix)}) "
                f"does not match location count ({n})."
            )
        for i, row in enumerate(distance_matrix):
            if len(row) != n:
                raise ValueError(
                    f"Distance matrix row {i} has {len(row)} columns; expected {n}."
                )

        if not (0 <= depot_index < n):
            raise ValueError(
                f"Depot index {depot_index} is out of range [0, {n})."
            )
