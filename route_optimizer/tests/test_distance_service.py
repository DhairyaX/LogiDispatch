"""
Tests for :mod:`route_optimizer.optimization.services.distance_service`.
"""

from __future__ import annotations

import math

import pytest

from route_optimizer.optimization.config.settings import DistanceSource
from route_optimizer.optimization.models.location import Location
from route_optimizer.optimization.services.distance_service import DistanceService


# ── Fixtures ────────────────────────────────────────────────────


@pytest.fixture
def service() -> DistanceService:
    """Return a fresh DistanceService pinned to Euclidean."""
    return DistanceService(source=DistanceSource.EUCLIDEAN)


@pytest.fixture
def warehouse() -> Location:
    return Location(id=0, name="Warehouse", latitude=28.4949, longitude=77.0895)


@pytest.fixture
def stop_a() -> Location:
    return Location(id=1, name="Stop A", latitude=28.4796, longitude=77.0299)


@pytest.fixture
def stop_b() -> Location:
    return Location(id=2, name="Stop B", latitude=28.4602, longitude=77.0640)


# ── Distance Calculation Tests ──────────────────────────────────


class TestCalculateDistance:
    """Tests for ``DistanceService.calculate_distance``."""

    def test_distance_to_self_is_zero(
        self, service: DistanceService, warehouse: Location
    ) -> None:
        """Distance from a location to itself must be 0."""
        assert service.calculate_distance(warehouse, warehouse) == 0.0

    def test_distance_is_positive(
        self, service: DistanceService, warehouse: Location, stop_a: Location
    ) -> None:
        """Distance between distinct locations must be > 0."""
        dist = service.calculate_distance(warehouse, stop_a)
        assert dist > 0.0

    def test_distance_is_symmetric(
        self, service: DistanceService, warehouse: Location, stop_a: Location
    ) -> None:
        """d(A, B) must equal d(B, A)."""
        d1 = service.calculate_distance(warehouse, stop_a)
        d2 = service.calculate_distance(stop_a, warehouse)
        assert math.isclose(d1, d2, rel_tol=1e-9)

    def test_triangle_inequality(
        self,
        service: DistanceService,
        warehouse: Location,
        stop_a: Location,
        stop_b: Location,
    ) -> None:
        """d(A,C) ≤ d(A,B) + d(B,C)."""
        d_ac = service.calculate_distance(warehouse, stop_b)
        d_ab = service.calculate_distance(warehouse, stop_a)
        d_bc = service.calculate_distance(stop_a, stop_b)
        assert d_ac <= d_ab + d_bc + 1e-9

    def test_distance_is_in_reasonable_range(
        self, service: DistanceService, warehouse: Location, stop_a: Location
    ) -> None:
        """Gurgaon locations are within ~20 km of each other."""
        dist = service.calculate_distance(warehouse, stop_a)
        assert 0 < dist < 20.0

    def test_rejects_non_location_origin(self, service: DistanceService) -> None:
        """Passing a non-Location origin must raise TypeError."""
        loc = Location(id=1, name="X", latitude=28.0, longitude=77.0)
        with pytest.raises(TypeError, match="origin"):
            service.calculate_distance("not_a_location", loc)  # type: ignore[arg-type]

    def test_rejects_non_location_destination(self, service: DistanceService) -> None:
        """Passing a non-Location destination must raise TypeError."""
        loc = Location(id=1, name="X", latitude=28.0, longitude=77.0)
        with pytest.raises(TypeError, match="destination"):
            service.calculate_distance(loc, 42)  # type: ignore[arg-type]


# ── Distance Matrix Tests ──────────────────────────────────────


class TestGenerateDistanceMatrix:
    """Tests for ``DistanceService.generate_distance_matrix``."""

    def test_matrix_dimensions(
        self,
        service: DistanceService,
        warehouse: Location,
        stop_a: Location,
        stop_b: Location,
    ) -> None:
        """Matrix must be NxN."""
        locs = [warehouse, stop_a, stop_b]
        matrix = service.generate_distance_matrix(locs)
        n = len(locs)
        assert len(matrix) == n
        assert all(len(row) == n for row in matrix)

    def test_matrix_diagonal_is_zero(
        self,
        service: DistanceService,
        warehouse: Location,
        stop_a: Location,
        stop_b: Location,
    ) -> None:
        """Diagonal entries must be 0."""
        matrix = service.generate_distance_matrix([warehouse, stop_a, stop_b])
        for i in range(len(matrix)):
            assert matrix[i][i] == 0

    def test_matrix_is_symmetric(
        self,
        service: DistanceService,
        warehouse: Location,
        stop_a: Location,
        stop_b: Location,
    ) -> None:
        """matrix[i][j] must equal matrix[j][i]."""
        matrix = service.generate_distance_matrix([warehouse, stop_a, stop_b])
        n = len(matrix)
        for i in range(n):
            for j in range(n):
                assert matrix[i][j] == matrix[j][i]

    def test_matrix_values_are_non_negative(
        self,
        service: DistanceService,
        warehouse: Location,
        stop_a: Location,
        stop_b: Location,
    ) -> None:
        """All matrix entries must be ≥ 0."""
        matrix = service.generate_distance_matrix([warehouse, stop_a, stop_b])
        for row in matrix:
            for val in row:
                assert val >= 0

    def test_empty_list_raises_value_error(self, service: DistanceService) -> None:
        """An empty location list must raise ValueError."""
        with pytest.raises(ValueError, match="empty"):
            service.generate_distance_matrix([])

    def test_single_location_matrix(
        self, service: DistanceService, warehouse: Location
    ) -> None:
        """A single location produces a 1×1 zero matrix."""
        matrix = service.generate_distance_matrix([warehouse])
        assert matrix == [[0]]
