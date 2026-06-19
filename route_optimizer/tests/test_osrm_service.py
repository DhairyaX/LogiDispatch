"""
Tests for :mod:`route_optimizer.optimization.services.osrm_service` and
OSRM-related integration through the distance service.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from route_optimizer.cache.route_cache import RouteCache
from route_optimizer.optimization.config.settings import DistanceSource, OptimizationMode
from route_optimizer.optimization.models.location import Location
from route_optimizer.optimization.services.distance_service import DistanceService
from route_optimizer.optimization.services.osrm_service import OsrmService, OsrmServiceError


# ── Fixtures ────────────────────────────────────────────────────


@pytest.fixture
def sample_locations() -> list[Location]:
    """A small set of Gurgaon locations."""
    return [
        Location(id=0, name="Warehouse", latitude=28.4949, longitude=77.0895),
        Location(id=1, name="MG Road",   latitude=28.4796, longitude=77.0299),
        Location(id=2, name="Sector 29", latitude=28.4602, longitude=77.0640),
    ]


@pytest.fixture
def mock_osrm_distance_response() -> dict:
    """Simulated OSRM response for distance annotation."""
    return {
        "code": "Ok",
        "distances": [
            [0.0,    6200.0, 4100.0],
            [6200.0, 0.0,    3500.0],
            [4100.0, 3500.0, 0.0],
        ],
    }


@pytest.fixture
def mock_osrm_duration_response() -> dict:
    """Simulated OSRM response for duration annotation."""
    return {
        "code": "Ok",
        "durations": [
            [0.0,   780.0, 540.0],
            [780.0, 0.0,   420.0],
            [540.0, 420.0, 0.0],
        ],
    }


@pytest.fixture
def mock_osrm_combined_response() -> dict:
    """Simulated OSRM response with both distance and duration."""
    return {
        "code": "Ok",
        "distances": [
            [0.0,    6200.0, 4100.0],
            [6200.0, 0.0,    3500.0],
            [4100.0, 3500.0, 0.0],
        ],
        "durations": [
            [0.0,   780.0, 540.0],
            [780.0, 0.0,   420.0],
            [540.0, 420.0, 0.0],
        ],
    }


@pytest.fixture
def cache() -> RouteCache:
    """A fresh, enabled cache instance."""
    return RouteCache(enabled=True)


# ── Cache Tests ─────────────────────────────────────────────────


class TestRouteCache:
    """Tests for ``RouteCache``."""

    def test_set_and_get(self, cache: RouteCache) -> None:
        """Stored values should be retrievable."""
        cache.set("key1", {"data": 42})
        assert cache.get("key1") == {"data": 42}

    def test_miss_returns_none(self, cache: RouteCache) -> None:
        """Missing keys return None."""
        assert cache.get("nonexistent") is None

    def test_disabled_cache_returns_none(self) -> None:
        """When disabled, get always returns None."""
        c = RouteCache(enabled=False)
        c.set("key1", {"data": 1})
        assert c.get("key1") is None

    def test_clear_empties_store(self, cache: RouteCache) -> None:
        """Clear should remove all entries."""
        cache.set("a", 1)
        cache.set("b", 2)
        assert cache.size == 2
        cache.clear()
        assert cache.size == 0

    def test_hit_counter(self, cache: RouteCache) -> None:
        """Hits counter increments on cache hits."""
        cache.set("k", "v")
        cache.get("k")
        cache.get("k")
        assert cache.hits == 2
        assert cache.misses == 0

    def test_miss_counter(self, cache: RouteCache) -> None:
        """Miss counter increments on cache misses."""
        cache.get("missing")
        assert cache.misses == 1
        assert cache.hits == 0


# ── OSRM Service Tests (mocked HTTP) ───────────────────────────


class TestOsrmServiceDistanceMatrix:
    """Tests for ``OsrmService.get_distance_matrix``."""

    @patch("route_optimizer.optimization.services.osrm_service.requests.get")
    def test_returns_scaled_distance_matrix(
        self,
        mock_get: MagicMock,
        sample_locations: list[Location],
        mock_osrm_distance_response: dict,
    ) -> None:
        """Matrix values should be km * 1000 (scaling factor)."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_osrm_distance_response
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        svc = OsrmService(cache=RouteCache(enabled=False))
        matrix = svc.get_distance_matrix(sample_locations)

        assert len(matrix) == 3
        assert len(matrix[0]) == 3
        # 6200m = 6.2km -> 6.2 * 1000 = 6200
        assert matrix[0][1] == 6200
        # Diagonal should be 0
        assert matrix[0][0] == 0

    @patch("route_optimizer.optimization.services.osrm_service.requests.get")
    def test_matrix_dimensions(
        self,
        mock_get: MagicMock,
        sample_locations: list[Location],
        mock_osrm_distance_response: dict,
    ) -> None:
        """Matrix should be NxN."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_osrm_distance_response
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        svc = OsrmService(cache=RouteCache(enabled=False))
        matrix = svc.get_distance_matrix(sample_locations)
        n = len(sample_locations)
        assert len(matrix) == n
        assert all(len(row) == n for row in matrix)

    def test_empty_locations_raises(self) -> None:
        """Empty location list must raise ValueError."""
        svc = OsrmService(cache=RouteCache(enabled=False))
        with pytest.raises(ValueError, match="empty"):
            svc.get_distance_matrix([])


class TestOsrmServiceDurationMatrix:
    """Tests for ``OsrmService.get_duration_matrix``."""

    @patch("route_optimizer.optimization.services.osrm_service.requests.get")
    def test_returns_scaled_duration_matrix(
        self,
        mock_get: MagicMock,
        sample_locations: list[Location],
        mock_osrm_duration_response: dict,
    ) -> None:
        """Matrix values should be minutes * 1000 (scaling factor)."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_osrm_duration_response
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        svc = OsrmService(cache=RouteCache(enabled=False))
        matrix = svc.get_duration_matrix(sample_locations)

        assert len(matrix) == 3
        # 780s = 13min -> 13 * 1000 = 13000
        assert matrix[0][1] == 13000
        assert matrix[0][0] == 0

    def test_empty_locations_raises(self) -> None:
        """Empty location list must raise ValueError."""
        svc = OsrmService(cache=RouteCache(enabled=False))
        with pytest.raises(ValueError, match="empty"):
            svc.get_duration_matrix([])


class TestOsrmServiceRouteData:
    """Tests for ``OsrmService.get_route_data``."""

    @patch("route_optimizer.optimization.services.osrm_service.requests.get")
    def test_returns_both_matrices(
        self,
        mock_get: MagicMock,
        sample_locations: list[Location],
        mock_osrm_combined_response: dict,
    ) -> None:
        """get_route_data should return distance_matrix and duration_matrix."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_osrm_combined_response
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        svc = OsrmService(cache=RouteCache(enabled=False))
        data = svc.get_route_data(sample_locations)

        assert "distance_matrix" in data
        assert "duration_matrix" in data
        assert len(data["distance_matrix"]) == 3
        assert len(data["duration_matrix"]) == 3


# ── OSRM Error Handling Tests ───────────────────────────────────


class TestOsrmServiceErrors:
    """Tests for OSRM error handling."""

    @patch("route_optimizer.optimization.services.osrm_service.requests.get")
    def test_timeout_raises_osrm_error(
        self,
        mock_get: MagicMock,
        sample_locations: list[Location],
    ) -> None:
        """Timeout should raise OsrmServiceError."""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout("timed out")

        svc = OsrmService(cache=RouteCache(enabled=False))
        with pytest.raises(OsrmServiceError, match="timed out"):
            svc.get_distance_matrix(sample_locations)

    @patch("route_optimizer.optimization.services.osrm_service.requests.get")
    def test_connection_error_raises_osrm_error(
        self,
        mock_get: MagicMock,
        sample_locations: list[Location],
    ) -> None:
        """Connection failure should raise OsrmServiceError."""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("refused")

        svc = OsrmService(cache=RouteCache(enabled=False))
        with pytest.raises(OsrmServiceError, match="Could not connect"):
            svc.get_distance_matrix(sample_locations)

    @patch("route_optimizer.optimization.services.osrm_service.requests.get")
    def test_osrm_error_code_raises(
        self,
        mock_get: MagicMock,
        sample_locations: list[Location],
    ) -> None:
        """Non-Ok OSRM response code should raise OsrmServiceError."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"code": "InvalidQuery", "message": "bad"}
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        svc = OsrmService(cache=RouteCache(enabled=False))
        with pytest.raises(OsrmServiceError, match="InvalidQuery"):
            svc.get_distance_matrix(sample_locations)


# ── Fallback Logic Tests ───────────────────────────────────────


class TestDistanceServiceFallback:
    """Tests for OSRM-to-Euclidean fallback in DistanceService."""

    @patch("route_optimizer.optimization.services.distance_service.DistanceService._osrm_distance_matrix")
    def test_fallback_on_osrm_failure(
        self,
        mock_osrm: MagicMock,
        sample_locations: list[Location],
    ) -> None:
        """When OSRM fails, Euclidean matrix should be returned."""
        mock_osrm.side_effect = Exception("network error")

        svc = DistanceService(source=DistanceSource.OSRM)
        matrix = svc.generate_distance_matrix(sample_locations)

        # Should return a valid matrix (Euclidean fallback)
        assert len(matrix) == 3
        assert all(len(row) == 3 for row in matrix)
        # Diagonal should be 0
        assert all(matrix[i][i] == 0 for i in range(3))
        # Should flag that fallback was used
        assert svc.used_fallback

    def test_euclidean_source_produces_matrix(
        self,
        sample_locations: list[Location],
    ) -> None:
        """Explicitly selecting Euclidean should work as in Phase 1."""
        svc = DistanceService(source=DistanceSource.EUCLIDEAN)
        matrix = svc.generate_distance_matrix(sample_locations)

        assert len(matrix) == 3
        assert all(matrix[i][i] == 0 for i in range(3))
        assert not svc.used_fallback

    def test_euclidean_no_duration_matrix(
        self,
        sample_locations: list[Location],
    ) -> None:
        """Euclidean source should return None for duration matrix."""
        svc = DistanceService(source=DistanceSource.EUCLIDEAN)
        assert svc.generate_duration_matrix(sample_locations) is None


# ── OSRM Caching Integration Test ──────────────────────────────


class TestOsrmCaching:
    """Tests for OSRM response caching."""

    @patch("route_optimizer.optimization.services.osrm_service.requests.get")
    def test_second_call_uses_cache(
        self,
        mock_get: MagicMock,
        sample_locations: list[Location],
        mock_osrm_distance_response: dict,
    ) -> None:
        """Second call with same locations should hit cache, not API."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_osrm_distance_response
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        cache = RouteCache(enabled=True)
        svc = OsrmService(cache=cache)

        # First call — cache miss
        matrix1 = svc.get_distance_matrix(sample_locations)
        assert mock_get.call_count == 1

        # Second call — should be a cache hit
        matrix2 = svc.get_distance_matrix(sample_locations)
        assert mock_get.call_count == 1  # No additional API call
        assert matrix1 == matrix2
        assert cache.hits == 1


# ── Coordinate Validation Test ──────────────────────────────────


class TestOsrmCoordinateValidation:
    """Tests for ``OsrmService.validate_coordinates``."""

    def test_valid_coordinates(self, sample_locations: list[Location]) -> None:
        assert OsrmService.validate_coordinates(sample_locations) is True

    def test_empty_list_is_valid(self) -> None:
        assert OsrmService.validate_coordinates([]) is True
