"""
Domain model for a delivery vehicle.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Vehicle:
    """Immutable value object representing a delivery vehicle.

    Attributes:
        id:   Unique numeric identifier (0-indexed).
        name: Human-readable label (e.g. "Vehicle 1").
    """

    id: int
    name: str

    def __str__(self) -> str:
        return self.name
