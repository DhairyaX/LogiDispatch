"""
Domain model for a geographic delivery location.
"""

from dataclasses import dataclass

# Valid coordinate bounds.
_MIN_LAT, _MAX_LAT = -90.0, 90.0
_MIN_LON, _MAX_LON = -180.0, 180.0


@dataclass(frozen=True)
class Location:
    """Immutable value object representing a delivery stop or warehouse.

    Attributes:
        id:        Unique numeric identifier.
        name:      Human-readable label (e.g. "Cyber City").
        latitude:  WGS-84 latitude  in decimal degrees.
        longitude: WGS-84 longitude in decimal degrees.
    """

    id: int
    name: str
    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        """Validate coordinates on construction."""
        if not (_MIN_LAT <= self.latitude <= _MAX_LAT):
            raise ValueError(
                f"Latitude {self.latitude} out of range "
                f"[{_MIN_LAT}, {_MAX_LAT}] for location '{self.name}'."
            )
        if not (_MIN_LON <= self.longitude <= _MAX_LON):
            raise ValueError(
                f"Longitude {self.longitude} out of range "
                f"[{_MIN_LON}, {_MAX_LON}] for location '{self.name}'."
            )

    def __str__(self) -> str:
        return f"{self.name} ({self.latitude:.4f}, {self.longitude:.4f})"
