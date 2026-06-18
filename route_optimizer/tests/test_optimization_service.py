"""
Tests for :mod:`route_optimizer.services.optimization_service`.
"""

from __future__ import annotations

import pytest

from route_optimizer.models.location import Location
from route_optimizer.services.distance_service import DistanceService
from route_optimizer.services.optimization_service import OptimizationService


# ── Fixtures ────────────────────────────────────────────────────


@pytest.fixture
def optimizer() -> OptimizationService:
    return OptimizationService()


@pytest.fixture
def distance_svc() -> DistanceService:
    return DistanceService()


@pytest.fixture
def sample_locations() -> list[Location]:
    """A small set of Gurgaon locations for solver tests."""
    return [
        Location(id=0, name="Warehouse", latitude=28.4949, longitude=77.0895),
        Location(id=1, name="MG Road", latitude=28.4796, longitude=77.0299),
        Location(id=2, name="Sector 29", latitude=28.4602, longitude=77.0640),
        Location(id=3, name="Golf Course Rd", latitude=28.4498, longitude=77.0920),
        Location(id=4, name="Udyog Vihar", latitude=28.5020, longitude=77.0843),
    ]


@pytest.fixture
def distance_matrix(
    distance_svc: DistanceService,
    sample_locations: list[Location],
) -> list[list[int]]:
    return distance_svc.generate_distance_matrix(sample_locations)


# ── Solver Tests ────────────────────────────────────────────────


class TestOptimizationService:
    """Tests for ``OptimizationService.solve``."""

    def test_route_starts_at_depot(
        self,
        optimizer: OptimizationService,
        sample_locations: list[Location],
        distance_matrix: list[list[int]],
    ) -> None:
        """The optimised route must begin at the depot."""
        route = optimizer.solve(sample_locations, distance_matrix, depot_index=0)
        assert route.ordered_locations[0] == sample_locations[0]

    def test_route_ends_at_depot(
        self,
        optimizer: OptimizationService,
        sample_locations: list[Location],
        distance_matrix: list[list[int]],
    ) -> None:
        """The optimised route must return to the depot."""
        route = optimizer.solve(sample_locations, distance_matrix, depot_index=0)
        assert route.ordered_locations[-1] == sample_locations[0]

    def test_route_is_round_trip(
        self,
        optimizer: OptimizationService,
        sample_locations: list[Location],
        distance_matrix: list[list[int]],
    ) -> None:
        """Route model should report ``is_round_trip == True``."""
        route = optimizer.solve(sample_locations, distance_matrix)
        assert route.is_round_trip

    def test_all_locations_visited(
        self,
        optimizer: OptimizationService,
        sample_locations: list[Location],
        distance_matrix: list[list[int]],
    ) -> None:
        """Every location must appear in the route at least once."""
        route = optimizer.solve(sample_locations, distance_matrix)
        visited_ids = {loc.id for loc in route.ordered_locations}
        expected_ids = {loc.id for loc in sample_locations}
        assert expected_ids.issubset(visited_ids)

    def test_each_stop_visited_exactly_once(
        self,
        optimizer: OptimizationService,
        sample_locations: list[Location],
        distance_matrix: list[list[int]],
    ) -> None:
        """Non-depot stops must appear exactly once;
        the depot appears exactly twice (start and end)."""
        route = optimizer.solve(sample_locations, distance_matrix)
        ids = [loc.id for loc in route.ordered_locations]
        depot_id = sample_locations[0].id
        assert ids.count(depot_id) == 2
        for loc in sample_locations[1:]:
            assert ids.count(loc.id) == 1

    def test_total_distance_is_positive(
        self,
        optimizer: OptimizationService,
        sample_locations: list[Location],
        distance_matrix: list[list[int]],
    ) -> None:
        """Total route distance must be > 0."""
        route = optimizer.solve(sample_locations, distance_matrix)
        assert route.total_distance > 0.0

    def test_route_length_equals_locations_plus_one(
        self,
        optimizer: OptimizationService,
        sample_locations: list[Location],
        distance_matrix: list[list[int]],
    ) -> None:
        """Route length = N + 1 (depot repeated at end)."""
        route = optimizer.solve(sample_locations, distance_matrix)
        assert len(route.ordered_locations) == len(sample_locations) + 1

    def test_empty_locations_raises(
        self,
        optimizer: OptimizationService,
    ) -> None:
        """Empty location list must raise ValueError."""
        with pytest.raises(ValueError, match="empty"):
            optimizer.solve([], [], depot_index=0)

    def test_mismatched_matrix_raises(
        self,
        optimizer: OptimizationService,
        sample_locations: list[Location],
    ) -> None:
        """Matrix size mismatch must raise ValueError."""
        bad_matrix = [[0, 1], [1, 0]]  # 2×2 but 5 locations
        with pytest.raises(ValueError, match="row count"):
            optimizer.solve(sample_locations, bad_matrix)

    def test_invalid_depot_index_raises(
        self,
        optimizer: OptimizationService,
        sample_locations: list[Location],
        distance_matrix: list[list[int]],
    ) -> None:
        """Out-of-range depot index must raise ValueError."""
        with pytest.raises(ValueError, match="Depot index"):
            optimizer.solve(sample_locations, distance_matrix, depot_index=99)

    def test_two_location_route(
        self,
        optimizer: OptimizationService,
        distance_svc: DistanceService,
    ) -> None:
        """Minimal case: depot + 1 stop."""
        locs = [
            Location(id=0, name="Depot", latitude=28.4949, longitude=77.0895),
            Location(id=1, name="Stop", latitude=28.4796, longitude=77.0299),
        ]
        matrix = distance_svc.generate_distance_matrix(locs)
        route = optimizer.solve(locs, matrix)
        assert route.ordered_locations[0] == locs[0]
        assert route.ordered_locations[-1] == locs[0]
        assert len(route.ordered_locations) == 3  # depot → stop → depot
