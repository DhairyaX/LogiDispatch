"""
Application-wide configuration settings.

Centralizes all tunable parameters so that future phases
(API keys, database URLs, feature flags) can be added here
without touching business logic.
"""

from dataclasses import dataclass, field
from enum import Enum


class DistanceSource(str, Enum):
    """Selects how distances are computed."""

    EUCLIDEAN = "euclidean"
    OSRM = "osrm"


class OptimizationMode(str, Enum):
    """Selects the cost metric the solver minimises."""

    DISTANCE = "distance"
    DURATION = "duration"


@dataclass(frozen=True)
class OptimizerSettings:
    """Settings for the OR-Tools optimization engine."""

    # Maximum solver wall-clock time in seconds.
    solver_time_limit_seconds: int = 5

    # OR-Tools first-solution strategy name.
    # Common choices: "PATH_CHEAPEST_ARC", "SAVINGS", "CHRISTOFIDES".
    first_solution_strategy: str = "PATH_CHEAPEST_ARC"

    # OR-Tools local-search metaheuristic.
    # Common choices: "GUIDED_LOCAL_SEARCH", "SIMULATED_ANNEALING", "TABU_SEARCH".
    local_search_metaheuristic: str = "GUIDED_LOCAL_SEARCH"

    # What metric to optimise: "distance" or "duration".
    optimization_mode: OptimizationMode = OptimizationMode.DISTANCE

    # Number of delivery vehicles (VRP).  Set to 1 for TSP mode.
    vehicle_count: int = 5


@dataclass(frozen=True)
class DistanceSettings:
    """Settings for distance calculations."""

    # Approximate km-per-degree at Gurgaon's latitude (~28.45°N).
    # 1° latitude  ≈ 111.32 km
    # 1° longitude ≈ 111.32 × cos(28.45°) ≈ 97.97 km
    km_per_degree_lat: float = 111.32
    km_per_degree_lon: float = 97.97

    # Internal distance scaling factor used by OR-Tools (integer solver).
    # Distances are multiplied by this before being passed to the solver
    # and divided by it when reading results back.
    scaling_factor: int = 1000

    # Which backend produces the distance / duration matrices.
    distance_source: DistanceSource = DistanceSource.OSRM


@dataclass(frozen=True)
class OsrmSettings:
    """Settings for the OSRM routing service."""

    # Public OSRM demo server.
    base_url: str = "https://router.project-osrm.org"

    # Profile used for routing (driving, cycling, walking).
    profile: str = "driving"

    # HTTP request timeout in seconds.
    request_timeout: int = 30

    # Whether to enable in-memory response caching.
    cache_enabled: bool = True


@dataclass(frozen=True)
class DisplaySettings:
    """Settings for CLI display."""

    # Separator character and width for Rich panels / rules.
    separator_char: str = "═"
    separator_width: int = 60

    # Number of decimal places for distances / metrics.
    distance_precision: int = 2
    time_precision: int = 4


@dataclass(frozen=True)
class AppSettings:
    """Root configuration object that aggregates all sub-settings."""

    app_name: str = "Logistics Route Optimization Engine"
    version: str = "3.0.0"

    optimizer: OptimizerSettings = field(default_factory=OptimizerSettings)
    distance: DistanceSettings = field(default_factory=DistanceSettings)
    osrm: OsrmSettings = field(default_factory=OsrmSettings)
    display: DisplaySettings = field(default_factory=DisplaySettings)


# Module-level singleton — import this wherever settings are needed.
settings = AppSettings()
