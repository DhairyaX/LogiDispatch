"""
Tests for Phase 3 VRP (Vehicle Routing Problem) optimisation.

Covers:
    - Vehicle model creation
    - Vehicle service fleet management
    - VRP solver correctness (stop coverage, duplicate prevention,
      depot handling, multi-vehicle assignment)
    - VRP metrics computation
    - Edge cases (vehicles > stops, single vehicle, empty stops)
"""

from __future__ import annotations

import pytest

from route_optimizer.optimization.config.settings import DistanceSource
from route_optimizer.optimization.models.location import Location
from route_optimizer.optimization.models.vehicle import Vehicle
from route_optimizer.optimization.models.vehicle_route import VehicleRoute
from route_optimizer.optimization.services.distance_service import DistanceService
from route_optimizer.optimization.services.metrics_service import MetricsService
from route_optimizer.optimization.services.optimization_service import OptimizationService
from route_optimizer.optimization.services.vehicle_service import VehicleService


# ── Fixtures ────────────────────────────────────────────────────


@pytest.fixture
def sample_locations() -> list[Location]:
    """A set of Gurgaon locations sufficient for VRP testing."""
    return [
        Location(id=0, name="Warehouse",        latitude=28.4949, longitude=77.0895),
        Location(id=1, name="MG Road",           latitude=28.4796, longitude=77.0299),
        Location(id=2, name="Sector 29",         latitude=28.4602, longitude=77.0640),
        Location(id=3, name="Golf Course Road",  latitude=28.4498, longitude=77.0920),
        Location(id=4, name="Udyog Vihar",       latitude=28.5020, longitude=77.0843),
        Location(id=5, name="DLF Phase 3",       latitude=28.4944, longitude=77.1050),
        Location(id=6, name="Sohna Road",        latitude=28.4140, longitude=77.0560),
    ]


@pytest.fixture
def distance_service() -> DistanceService:
    """Euclidean-only distance service for deterministic testing."""
    return DistanceService(source=DistanceSource.EUCLIDEAN)


@pytest.fixture
def optimization_service() -> OptimizationService:
    return OptimizationService()


@pytest.fixture
def distance_matrix(
    distance_service: DistanceService,
    sample_locations: list[Location],
) -> list[list[int]]:
    """Euclidean distance matrix for the sample locations."""
    return distance_service.generate_distance_matrix(sample_locations)


# ── Vehicle Model Tests ─────────────────────────────────────────


class TestVehicleModel:
    """Tests for the Vehicle dataclass."""

    def test_vehicle_creation(self) -> None:
        v = Vehicle(id=0, name="Vehicle 1")
        assert v.id == 0
        assert v.name == "Vehicle 1"

    def test_vehicle_str(self) -> None:
        v = Vehicle(id=1, name="Vehicle 2")
        assert str(v) == "Vehicle 2"

    def test_vehicle_is_frozen(self) -> None:
        v = Vehicle(id=0, name="X")
        with pytest.raises(AttributeError):
            v.name = "Y"  # type: ignore[misc]


# ── VehicleRoute Model Tests ────────────────────────────────────


class TestVehicleRouteModel:
    """Tests for the VehicleRoute dataclass."""

    def test_num_stops_excludes_depot(self) -> None:
        depot = Location(id=0, name="W", latitude=0, longitude=0)
        a = Location(id=1, name="A", latitude=1, longitude=1)
        b = Location(id=2, name="B", latitude=2, longitude=2)
        vr = VehicleRoute(
            vehicle_id=0,
            vehicle_name="V1",
            locations=[depot, a, b, depot],
            distance=10.0,
            duration=5.0,
        )
        assert vr.num_stops == 2

    def test_empty_route(self) -> None:
        depot = Location(id=0, name="W", latitude=0, longitude=0)
        vr = VehicleRoute(
            vehicle_id=0,
            vehicle_name="V1",
            locations=[depot, depot],
            distance=0.0,
            duration=0.0,
        )
        assert vr.is_empty
        assert vr.num_stops == 0

    def test_round_trip(self) -> None:
        depot = Location(id=0, name="W", latitude=0, longitude=0)
        a = Location(id=1, name="A", latitude=1, longitude=1)
        vr = VehicleRoute(
            vehicle_id=0,
            vehicle_name="V1",
            locations=[depot, a, depot],
            distance=5.0,
            duration=3.0,
        )
        assert vr.is_round_trip


# ── Vehicle Service Tests ───────────────────────────────────────


class TestVehicleService:
    """Tests for VehicleService."""

    def test_create_fleet(self) -> None:
        svc = VehicleService(vehicle_count=3)
        fleet = svc.create_fleet()
        assert len(fleet) == 3
        assert fleet[0].name == "Vehicle 1"
        assert fleet[2].name == "Vehicle 3"

    def test_create_fleet_single(self) -> None:
        svc = VehicleService(vehicle_count=1)
        fleet = svc.create_fleet()
        assert len(fleet) == 1

    def test_create_fleet_zero_raises(self) -> None:
        svc = VehicleService(vehicle_count=0)
        with pytest.raises(ValueError, match="Vehicle count"):
            svc.create_fleet()

    def test_validate_fleet_size_caps_at_stops(self) -> None:
        svc = VehicleService(vehicle_count=10)
        assert svc.validate_fleet_size(num_stops=3) == 3

    def test_validate_fleet_size_normal(self) -> None:
        svc = VehicleService(vehicle_count=3)
        assert svc.validate_fleet_size(num_stops=10) == 3


# ── VRP Solver Tests ────────────────────────────────────────────


class TestVRPSolver:
    """Tests for OptimizationService.solve_vrp."""

    def test_vrp_returns_routes_for_each_vehicle(
        self,
        optimization_service: OptimizationService,
        sample_locations: list[Location],
        distance_matrix: list[list[int]],
    ) -> None:
        """solve_vrp should return one VehicleRoute per vehicle."""
        routes = optimization_service.solve_vrp(
            sample_locations, distance_matrix, vehicle_count=3,
        )
        # May get fewer if solver caps at # stops
        assert len(routes) >= 1
        assert len(routes) <= 3

    def test_every_stop_visited_exactly_once(
        self,
        optimization_service: OptimizationService,
        sample_locations: list[Location],
        distance_matrix: list[list[int]],
    ) -> None:
        """All delivery stops must appear exactly once across all routes."""
        routes = optimization_service.solve_vrp(
            sample_locations, distance_matrix, vehicle_count=3,
        )

        # Collect non-depot stops.
        all_stops: list[int] = []
        for vr in routes:
            for loc in vr.locations[1:-1]:  # exclude depot at start/end
                all_stops.append(loc.id)

        expected_stops = {loc.id for loc in sample_locations if loc.id != 0}
        assert set(all_stops) == expected_stops, "Not all stops visited"
        assert len(all_stops) == len(expected_stops), "Duplicate stop detected"

    def test_no_duplicate_stops(
        self,
        optimization_service: OptimizationService,
        sample_locations: list[Location],
        distance_matrix: list[list[int]],
    ) -> None:
        """No delivery stop should appear in more than one vehicle's route."""
        routes = optimization_service.solve_vrp(
            sample_locations, distance_matrix, vehicle_count=3,
        )

        all_stops: list[int] = []
        for vr in routes:
            for loc in vr.locations[1:-1]:
                assert loc.id not in all_stops, f"Stop {loc.id} duplicated"
                all_stops.append(loc.id)

    def test_every_route_starts_at_depot(
        self,
        optimization_service: OptimizationService,
        sample_locations: list[Location],
        distance_matrix: list[list[int]],
    ) -> None:
        """Every vehicle route must start at the depot."""
        routes = optimization_service.solve_vrp(
            sample_locations, distance_matrix, vehicle_count=3,
        )
        for vr in routes:
            assert vr.locations[0].id == 0

    def test_every_route_ends_at_depot(
        self,
        optimization_service: OptimizationService,
        sample_locations: list[Location],
        distance_matrix: list[list[int]],
    ) -> None:
        """Every vehicle route must end at the depot."""
        routes = optimization_service.solve_vrp(
            sample_locations, distance_matrix, vehicle_count=3,
        )
        for vr in routes:
            assert vr.locations[-1].id == 0

    def test_every_route_is_round_trip(
        self,
        optimization_service: OptimizationService,
        sample_locations: list[Location],
        distance_matrix: list[list[int]],
    ) -> None:
        """Every vehicle route should be a round trip."""
        routes = optimization_service.solve_vrp(
            sample_locations, distance_matrix, vehicle_count=2,
        )
        for vr in routes:
            assert vr.is_round_trip

    def test_distances_are_positive(
        self,
        optimization_service: OptimizationService,
        sample_locations: list[Location],
        distance_matrix: list[list[int]],
    ) -> None:
        """Non-empty routes should have positive distance."""
        routes = optimization_service.solve_vrp(
            sample_locations, distance_matrix, vehicle_count=2,
        )
        for vr in routes:
            if not vr.is_empty:
                assert vr.distance > 0

    def test_single_vehicle_degenerates_to_tsp(
        self,
        optimization_service: OptimizationService,
        sample_locations: list[Location],
        distance_matrix: list[list[int]],
    ) -> None:
        """With 1 vehicle, VRP should visit all stops in a single route."""
        routes = optimization_service.solve_vrp(
            sample_locations, distance_matrix, vehicle_count=1,
        )
        assert len(routes) == 1
        assert routes[0].num_stops == len(sample_locations) - 1

    def test_vehicles_greater_than_stops(
        self,
        optimization_service: OptimizationService,
        sample_locations: list[Location],
        distance_matrix: list[list[int]],
    ) -> None:
        """When vehicles > stops, effective count should be capped."""
        routes = optimization_service.solve_vrp(
            sample_locations, distance_matrix, vehicle_count=20,
        )
        # Effective vehicles capped at num_stops (6 in fixture)
        num_stops = len(sample_locations) - 1
        assert len(routes) <= num_stops

        # All stops still visited.
        all_stops = []
        for vr in routes:
            for loc in vr.locations[1:-1]:
                all_stops.append(loc.id)
        assert len(all_stops) == num_stops

    def test_zero_vehicles_raises(
        self,
        optimization_service: OptimizationService,
        sample_locations: list[Location],
        distance_matrix: list[list[int]],
    ) -> None:
        """Zero vehicles should raise ValueError."""
        with pytest.raises(ValueError, match="Vehicle count"):
            optimization_service.solve_vrp(
                sample_locations, distance_matrix, vehicle_count=0,
            )


# ── VRP Metrics Tests ───────────────────────────────────────────


class TestVRPMetrics:
    """Tests for MetricsService.calculate_vrp."""

    def test_total_stops_summed(
        self,
        optimization_service: OptimizationService,
        sample_locations: list[Location],
        distance_matrix: list[list[int]],
    ) -> None:
        """Total stops should equal sum of per-vehicle stops."""
        routes = optimization_service.solve_vrp(
            sample_locations, distance_matrix, vehicle_count=3,
        )
        svc = MetricsService()
        metrics = svc.calculate_vrp(routes, 1.0, vehicle_count=3)
        assert metrics.total_stops == sum(vr.num_stops for vr in routes)

    def test_total_distance_summed(
        self,
        optimization_service: OptimizationService,
        sample_locations: list[Location],
        distance_matrix: list[list[int]],
    ) -> None:
        """Total distance should equal sum of per-vehicle distances."""
        routes = optimization_service.solve_vrp(
            sample_locations, distance_matrix, vehicle_count=2,
        )
        svc = MetricsService()
        metrics = svc.calculate_vrp(routes, 1.0, vehicle_count=2)
        expected = round(sum(vr.distance for vr in routes), 4)
        assert metrics.total_distance == expected

    def test_vehicles_used_count(
        self,
        optimization_service: OptimizationService,
        sample_locations: list[Location],
        distance_matrix: list[list[int]],
    ) -> None:
        """vehicles_used should count non-empty routes."""
        routes = optimization_service.solve_vrp(
            sample_locations, distance_matrix, vehicle_count=2,
        )
        svc = MetricsService()
        metrics = svc.calculate_vrp(routes, 1.0, vehicle_count=2)
        expected_used = sum(1 for vr in routes if not vr.is_empty)
        assert metrics.vehicles_used == expected_used

    def test_vehicle_metrics_breakdown(
        self,
        optimization_service: OptimizationService,
        sample_locations: list[Location],
        distance_matrix: list[list[int]],
    ) -> None:
        """Per-vehicle metrics should be populated."""
        routes = optimization_service.solve_vrp(
            sample_locations, distance_matrix, vehicle_count=3,
        )
        svc = MetricsService()
        metrics = svc.calculate_vrp(routes, 1.0, vehicle_count=3)
        assert len(metrics.vehicle_metrics) == len(routes)

    def test_empty_routes_raises(self) -> None:
        """Empty route list should raise ValueError."""
        svc = MetricsService()
        with pytest.raises(ValueError, match="vehicle routes"):
            svc.calculate_vrp([], 1.0, vehicle_count=1)


# ── Backward Compatibility Tests ────────────────────────────────


class TestBackwardCompatibility:
    """Verify Phase 1/2 single-vehicle API still works."""

    def test_solve_returns_route(
        self,
        optimization_service: OptimizationService,
        sample_locations: list[Location],
        distance_matrix: list[list[int]],
    ) -> None:
        """The legacy solve() should still return a Route."""
        from route_optimizer.optimization.models.route import Route
        route = optimization_service.solve(
            sample_locations, distance_matrix,
        )
        assert isinstance(route, Route)
        assert route.total_distance > 0
        assert route.is_round_trip


# ── Balancing Tests ─────────────────────────────────────────────


class TestWorkloadBalancing:
    """Tests for workload balancing features."""

    def test_strict_balancing_limits_variance(
        self,
        optimization_service: OptimizationService,
        sample_locations: list[Location],
        distance_matrix: list[list[int]],
    ) -> None:
        """STRICT balancing should result in a lower standard deviation than DISTANCE_OPTIMAL."""
        routes_strict = optimization_service.solve_vrp(
            sample_locations, 
            distance_matrix, 
            vehicle_count=5,
            balancing_mode="strict",
            balance_weight=100
        )
        routes_optimal = optimization_service.solve_vrp(
            sample_locations, 
            distance_matrix, 
            vehicle_count=5,
            balancing_mode="distance_optimal",
            balance_weight=100
        )
        
        svc = MetricsService()
        metrics_strict = svc.calculate_vrp(routes_strict, 1.0, vehicle_count=5)
        metrics_optimal = svc.calculate_vrp(routes_optimal, 1.0, vehicle_count=5)
        
        # Strict mode should distribute workload more fairly than purely optimal mode
        assert metrics_strict.stop_distribution_stddev <= metrics_optimal.stop_distribution_stddev
        
        # Strict mode should use more or equal number of vehicles
        assert metrics_strict.vehicles_used >= metrics_optimal.vehicles_used

    def test_utilization_calculation(self) -> None:
        """Verify utilization calculation logic in MetricsService."""
        depot = Location(id=0, name="W", latitude=0, longitude=0)
        vr1 = VehicleRoute(0, "V1", [depot, depot, depot], 10.0, 5.0) # 1 stop
        vr2 = VehicleRoute(1, "V2", [depot, depot, depot], 10.0, 5.0) # 1 stop
        vr3 = VehicleRoute(2, "V3", [depot, depot], 0.0, 0.0) # 0 stops (idle)
        
        svc = MetricsService()
        metrics = svc.calculate_vrp([vr1, vr2, vr3], 1.0, vehicle_count=4)
        
        # 2 vehicles used out of 4 available = 50%
        assert metrics.vehicles_used == 2
        assert metrics.vehicle_utilization_rate == 50.0
