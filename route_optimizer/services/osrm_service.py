"""
OSRM (Open Source Routing Machine) service.

Communicates with the OSRM Table API to produce real-world
road-distance and travel-duration matrices.

The public demo server (router.project-osrm.org) is used by default.
"""

from __future__ import annotations

import logging
from typing import Sequence

import requests

from route_optimizer.cache.route_cache import RouteCache
from route_optimizer.config.settings import settings
from route_optimizer.models.location import Location

logger = logging.getLogger(__name__)


class OsrmServiceError(Exception):
    """Raised when an OSRM API call fails irrecoverably."""


class OsrmService:
    """Fetches road-network distance and duration matrices from OSRM."""

    def __init__(self, cache: RouteCache | None = None) -> None:
        self._base_url = settings.osrm.base_url.rstrip("/")
        self._profile = settings.osrm.profile
        self._timeout = settings.osrm.request_timeout
        self._scaling_factor = settings.distance.scaling_factor
        self._cache = cache or RouteCache()

    # ── Public API ──────────────────────────────────────────────

    def get_distance_matrix(
        self,
        locations: Sequence[Location],
    ) -> list[list[int]]:
        """Return an NxN integer distance matrix (metres * scaling_factor / 1000).

        Distances are converted from metres (OSRM native) to km,
        then scaled to integers for OR-Tools.

        Args:
            locations: Ordered locations (index 0 = depot).

        Returns:
            Scaled integer distance matrix.

        Raises:
            OsrmServiceError: On API / network failure.
            ValueError:       On empty locations.
        """
        self._validate_locations(locations)
        data = self._fetch_table(locations, annotations="distance")
        raw_distances: list[list[float]] = data["distances"]

        n = len(locations)
        matrix: list[list[int]] = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                km = raw_distances[i][j] / 1000.0  # metres → km
                matrix[i][j] = int(round(km * self._scaling_factor))
        return matrix

    def get_duration_matrix(
        self,
        locations: Sequence[Location],
    ) -> list[list[int]]:
        """Return an NxN integer duration matrix (seconds * scaling_factor / 60).

        Durations are converted from seconds (OSRM native) to minutes,
        then scaled to integers for OR-Tools.

        Args:
            locations: Ordered locations (index 0 = depot).

        Returns:
            Scaled integer duration matrix.

        Raises:
            OsrmServiceError: On API / network failure.
            ValueError:       On empty locations.
        """
        self._validate_locations(locations)
        data = self._fetch_table(locations, annotations="duration")
        raw_durations: list[list[float]] = data["durations"]

        n = len(locations)
        matrix: list[list[int]] = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                minutes = raw_durations[i][j] / 60.0  # seconds → minutes
                matrix[i][j] = int(round(minutes * self._scaling_factor))
        return matrix

    def get_route_data(
        self,
        locations: Sequence[Location],
    ) -> dict[str, list[list[int]]]:
        """Return both distance and duration matrices in one call.

        Uses ``annotations=distance,duration`` so a single API request
        yields both matrices.

        Returns:
            ``{"distance_matrix": ..., "duration_matrix": ...}``
        """
        self._validate_locations(locations)
        data = self._fetch_table(locations, annotations="distance,duration")
        raw_distances: list[list[float]] = data["distances"]
        raw_durations: list[list[float]] = data["durations"]

        n = len(locations)
        dist_matrix: list[list[int]] = [[0] * n for _ in range(n)]
        dur_matrix: list[list[int]] = [[0] * n for _ in range(n)]

        for i in range(n):
            for j in range(n):
                km = raw_distances[i][j] / 1000.0
                dist_matrix[i][j] = int(round(km * self._scaling_factor))
                minutes = raw_durations[i][j] / 60.0
                dur_matrix[i][j] = int(round(minutes * self._scaling_factor))

        return {
            "distance_matrix": dist_matrix,
            "duration_matrix": dur_matrix,
        }

    # ── Internals ───────────────────────────────────────────────

    def _fetch_table(
        self,
        locations: Sequence[Location],
        annotations: str,
    ) -> dict:
        """Call the OSRM ``/table/v1/`` endpoint.

        Args:
            locations:   Ordered list of locations.
            annotations: Comma-separated list of annotations
                         (``"distance"``, ``"duration"``, or both).

        Returns:
            Parsed JSON response body.

        Raises:
            OsrmServiceError: On any failure (network, HTTP, OSRM error).
        """
        # Check cache first.
        cache_key = self._build_cache_key(locations, annotations)
        cached = self._cache.get(cache_key)
        if cached is not None:
            logger.info("OSRM cache hit for %d locations.", len(locations))
            return cached

        # Build URL: /table/v1/driving/lon1,lat1;lon2,lat2;...
        coords = ";".join(
            f"{loc.longitude},{loc.latitude}" for loc in locations
        )
        url = f"{self._base_url}/table/v1/{self._profile}/{coords}"
        params = {"annotations": annotations}

        try:
            response = requests.get(url, params=params, timeout=self._timeout)
            response.raise_for_status()
        except requests.exceptions.Timeout as exc:
            raise OsrmServiceError(
                f"OSRM request timed out after {self._timeout}s."
            ) from exc
        except requests.exceptions.ConnectionError as exc:
            raise OsrmServiceError(
                "Could not connect to OSRM server. "
                f"URL: {url}"
            ) from exc
        except requests.exceptions.HTTPError as exc:
            raise OsrmServiceError(
                f"OSRM returned HTTP {response.status_code}: "
                f"{response.text[:200]}"
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise OsrmServiceError(
                f"OSRM request failed: {exc}"
            ) from exc

        data = response.json()

        if data.get("code") != "Ok":
            raise OsrmServiceError(
                f"OSRM error: {data.get('code')} — "
                f"{data.get('message', 'unknown error')}"
            )

        # Store in cache.
        self._cache.set(cache_key, data)
        return data

    # ── Validation ──────────────────────────────────────────────

    @staticmethod
    def validate_coordinates(locations: Sequence[Location]) -> bool:
        """Return True if all locations have valid WGS-84 coordinates.

        This is a soft check (does not raise). The ``Location`` model
        already validates on construction.
        """
        for loc in locations:
            if not (-90 <= loc.latitude <= 90):
                return False
            if not (-180 <= loc.longitude <= 180):
                return False
        return True

    @staticmethod
    def _validate_locations(locations: Sequence[Location]) -> None:
        """Raise ``ValueError`` if the location list is empty."""
        if not locations:
            raise ValueError(
                "Cannot query OSRM with an empty location list."
            )

    @staticmethod
    def _build_cache_key(
        locations: Sequence[Location],
        annotations: str,
    ) -> str:
        """Deterministic cache key from location coordinates + annotations."""
        coords = "|".join(
            f"{loc.latitude:.6f},{loc.longitude:.6f}" for loc in locations
        )
        return f"{annotations}::{coords}"
