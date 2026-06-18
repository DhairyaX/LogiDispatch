"""
In-memory cache for OSRM route matrix responses.

Avoids repeated network calls when the same set of locations
is queried multiple times during a session.

Phase 5 can replace this with Redis or PostgreSQL-backed storage
behind the same interface.
"""

from __future__ import annotations

import logging
from typing import Any

from route_optimizer.config.settings import settings

logger = logging.getLogger(__name__)


class RouteCache:
    """Simple dictionary-backed in-memory cache.

    Keys are deterministic strings built from coordinates and annotation type.
    Values are parsed JSON response bodies from OSRM.
    """

    def __init__(self, enabled: bool | None = None) -> None:
        self._enabled = enabled if enabled is not None else settings.osrm.cache_enabled
        self._store: dict[str, Any] = {}
        self._hits: int = 0
        self._misses: int = 0

    # ── Public API ──────────────────────────────────────────────

    def get(self, key: str) -> Any | None:
        """Return cached value or ``None`` on miss.

        Args:
            key: Cache key string.

        Returns:
            Cached data if present and caching is enabled, else ``None``.
        """
        if not self._enabled:
            return None

        value = self._store.get(key)
        if value is not None:
            self._hits += 1
            logger.debug("Cache HIT  [hits=%d]: %s", self._hits, key[:60])
        else:
            self._misses += 1
            logger.debug("Cache MISS [misses=%d]: %s", self._misses, key[:60])
        return value

    def set(self, key: str, value: Any) -> None:
        """Store a value in the cache.

        Args:
            key:   Cache key string.
            value: Data to cache (typically a parsed JSON dict).
        """
        if not self._enabled:
            return
        self._store[key] = value
        logger.debug("Cache SET: %s", key[:60])

    def clear(self) -> None:
        """Remove all cached entries."""
        self._store.clear()
        self._hits = 0
        self._misses = 0
        logger.debug("Cache CLEARED.")

    # ── Diagnostics ─────────────────────────────────────────────

    @property
    def size(self) -> int:
        """Number of entries currently cached."""
        return len(self._store)

    @property
    def hits(self) -> int:
        """Total cache hits since creation / last clear."""
        return self._hits

    @property
    def misses(self) -> int:
        """Total cache misses since creation / last clear."""
        return self._misses

    @property
    def is_enabled(self) -> bool:
        """Whether caching is active."""
        return self._enabled
