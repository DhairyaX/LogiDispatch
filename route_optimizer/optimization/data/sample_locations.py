"""
Sample delivery locations around Gurgaon, Haryana, India.

The first location in the list is always treated as the **depot / warehouse**.
Coordinates are realistic WGS-84 values sourced from mapping services.
"""

from route_optimizer.optimization.models.location import Location


def get_sample_locations() -> list[Location]:
    """Return a curated list of delivery stops in the Gurgaon NCR region.

    Returns:
        A list of :class:`Location` instances.  Index 0 is the warehouse.
        Contains 16 locations (1 depot + 15 delivery stops) to
        justify multi-vehicle routing.
    """
    return [
        # ── Depot / Warehouse ───────────────────────────────────
        Location(id=0, name="Cyber City (Warehouse)",
                 latitude=28.4949, longitude=77.0895),

        # ── Delivery Stops ──────────────────────────────────────
        Location(id=1, name="MG Road",
                 latitude=28.4796, longitude=77.0299),

        Location(id=2, name="Sector 29",
                 latitude=28.4602, longitude=77.0640),

        Location(id=3, name="Golf Course Road",
                 latitude=28.4498, longitude=77.0920),

        Location(id=4, name="Udyog Vihar",
                 latitude=28.5020, longitude=77.0843),

        Location(id=5, name="DLF Phase 3",
                 latitude=28.4944, longitude=77.1050),

        Location(id=6, name="Sohna Road",
                 latitude=28.4140, longitude=77.0560),

        Location(id=7, name="Sector 56",
                 latitude=28.4240, longitude=77.0990),

        Location(id=8, name="Huda City Centre",
                 latitude=28.4594, longitude=77.0723),

        Location(id=9, name="Sector 14",
                 latitude=28.4708, longitude=77.0266),

        Location(id=10, name="Sector 45",
                 latitude=28.4432, longitude=77.0708),

        Location(id=11, name="Palam Vihar",
                 latitude=28.5058, longitude=77.0412),

        Location(id=12, name="Manesar",
                 latitude=28.3567, longitude=76.9369),

        Location(id=13, name="South City 1",
                 latitude=28.4490, longitude=77.0622),

        Location(id=14, name="Nirvana Country",
                 latitude=28.4160, longitude=77.0485),

        Location(id=15, name="Sector 82",
                 latitude=28.3945, longitude=76.9910),
    ]
