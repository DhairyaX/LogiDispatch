"""
Distance calculation service.

Provides Euclidean-approximation distance computation between
geographic coordinates and NxN distance-matrix generation.

Also acts as a unified gateway that delegates to the OSRM service
when ``DistanceSource.OSRM`` is configured, falling back to
Euclidean on failure.
"""

from __future__ import annotations

import logging
import math
from typing import Sequence

from route_optimizer.optimization.config.settings import DistanceSource, settings
from route_optimizer.optimization.models.location import Location

logger = logging.getLogger(__name__)


class DistanceService:
    """Service for geographic distance operations.

    Supports two backends:
        * **EUCLIDEAN** — flat-Earth approximation (Phase 1).
        * **OSRM** — real road-network distances via OSRM API (Phase 2).
    """

    def __init__(
        self,
        source: DistanceSource | None = None,
    ) -> None:
        self._km_per_deg_lat = settings.distance.km_per_degree_lat
        self._km_per_deg_lon = settings.distance.km_per_degree_lon
        self._scaling_factor = settings.distance.scaling_factor
        self._source = source or settings.distance.distance_source
        # Track whether a fallback occurred for CLI reporting.
        self.used_fallback: bool = False

    # ── Public API ──────────────────────────────────────────────

    @property
    def active_source(self) -> DistanceSource:
        """The distance source currently in use."""
        return self._source

    def calculate_distance(
        self,
        origin: Location,
        destination: Location,
    ) -> float:
        """Return the approximate surface distance in **kilometres**
        between two locations using an Euclidean flat-Earth projection.

        Args:
            origin:      Starting location.
            destination: Ending location.

        Returns:
            Distance in km (always >= 0).

        Raises:
            TypeError:  If either argument is not a :class:`Location`.
            ValueError: If coordinates are invalid (caught at model level).
        """
        self._validate_location(origin, "origin")
        self._validate_location(destination, "destination")

        delta_lat = (destination.latitude - origin.latitude) * self._km_per_deg_lat
        delta_lon = (destination.longitude - origin.longitude) * self._km_per_deg_lon

        return math.sqrt(delta_lat ** 2 + delta_lon ** 2)

    def generate_distance_matrix(
        self,
        locations: Sequence[Location],
    ) -> list[list[int]]:
        """Build a symmetric NxN distance matrix suitable for OR-Tools.

        When ``DistanceSource.OSRM`` is configured, this delegates to
        the OSRM service. If the OSRM call fails, it falls back to
        the Euclidean matrix and sets ``self.used_fallback = True``.

        Distances are **scaled to integers** (multiplied by
        ``settings.distance.scaling_factor``) because OR-Tools works
        with integer costs.

        Args:
            locations: Ordered sequence of locations.  Index 0 is the depot.

        Returns:
            A 2-D list of shape (N, N) with integer distances.

        Raises:
            ValueError: If *locations* is empty.
            TypeError:  If any element is not a :class:`Location`.
        """
        if not locations:
            raise ValueError("Cannot generate a distance matrix from an empty location list.")

        if self._source == DistanceSource.OSRM:
            try:
                return self._osrm_distance_matrix(locations)
            except Exception as exc:
                logger.warning(
                    "OSRM distance matrix failed (%s). "
                    "Falling back to Euclidean distances.",
                    exc,
                )
                self.used_fallback = True
                self._source = DistanceSource.EUCLIDEAN

        return self._euclidean_distance_matrix(locations)

    def generate_duration_matrix(
        self,
        locations: Sequence[Location],
    ) -> list[list[int]] | None:
        """Build an NxN duration matrix (scaled minutes) via OSRM.

        Returns ``None`` when the distance source is Euclidean (no
        duration data available) or when the OSRM call fails.

        Args:
            locations: Ordered sequence of locations.

        Returns:
            Scaled integer duration matrix, or ``None``.
        """
        if not locations:
            raise ValueError("Cannot generate a duration matrix from an empty location list.")

        if self._source != DistanceSource.OSRM:
            return None

        try:
            from route_optimizer.optimization.services.osrm_service import OsrmService, OsrmServiceError
            osrm = OsrmService()
            return osrm.get_duration_matrix(locations)
        except Exception as exc:
            logger.warning("OSRM duration matrix failed: %s", exc)
            return None

    # ── Private helpers ─────────────────────────────────────────

    def _euclidean_distance_matrix(
        self,
        locations: Sequence[Location],
    ) -> list[list[int]]:
        """Compute Euclidean distance matrix (Phase 1 original logic)."""
        n = len(locations)
        matrix: list[list[int]] = [[0] * n for _ in range(n)]

        for i in range(n):
            for j in range(i + 1, n):
                dist_km = self.calculate_distance(locations[i], locations[j])
                scaled = int(round(dist_km * self._scaling_factor))
                matrix[i][j] = scaled
                matrix[j][i] = scaled  # Symmetric

        return matrix

    def _osrm_distance_matrix(
        self,
        locations: Sequence[Location],
    ) -> list[list[int]]:
        """Fetch road-distance matrix from OSRM, falling back to
        Euclidean on failure."""
        try:
            from route_optimizer.optimization.services.osrm_service import OsrmService, OsrmServiceError
            osrm = OsrmService()
            return osrm.get_distance_matrix(locations)
        except Exception as exc:
            logger.warning(
                "OSRM unavailable (%s). Falling back to Euclidean distances.",
                exc,
            )
            self.used_fallback = True
            self._source = DistanceSource.EUCLIDEAN
            return self._euclidean_distance_matrix(locations)

    @staticmethod
    def _validate_location(loc: object, label: str) -> None:
        """Raise ``TypeError`` if *loc* is not a :class:`Location`."""
        if not isinstance(loc, Location):
            raise TypeError(
                f"Expected a Location for '{label}', got {type(loc).__name__}."
            )
