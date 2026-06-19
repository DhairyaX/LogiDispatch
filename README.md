# 🚚 Logistics Route Optimization Engine

> **Phase 3** — Multi-Vehicle Route Optimization (Vehicle Routing Problem - VRP).

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [Business Context](#business-context)
- [Features](#features)
- [Architecture](#architecture)
- [Folder Structure](#folder-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [VRP vs TSP](#vrp-vs-tsp)
- [Vehicle Assignment Logic](#vehicle-assignment-logic)
- [OSRM Integration](#osrm-integration)
- [Example Output](#example-output)
- [Testing](#testing)
- [Future Roadmap](#future-roadmap)
- [License](#license)

---

## Project Overview

The **Logistics Route Optimization Engine** determines the optimal assignment and routing for a fleet of vehicles starting from a central warehouse, visiting a set of delivery stops exactly once, and returning to the warehouse.

| Capability                        | Phase 1 | Phase 2 | Phase 3 (Current) |
| --------------------------------- | ------- | ------- | ----------------- |
| Delivery location model           | ✅       | ✅       | ✅                 |
| Euclidean distance matrix         | ✅       | ✅       | ✅                 |
| OSRM road-network distances       |         | ✅       | ✅                 |
| TSP optimisation (Single Vehicle) | ✅       | ✅       | ✅                 |
| **VRP optimisation (Multi-Vehicle)**|       |         | ✅                 |
| **Automatic Stop Assignment**     |         |         | ✅                 |
| Optimise by distance / time       |         | ✅       | ✅                 |
| Route metrics per vehicle         |         |         | ✅                 |
| Professional Rich CLI             | ✅       | ✅       | ✅                 |
| Automated Pytest suite            | ✅ (24) | ✅ (45) | ✅ (72 tests)      |

---

## Problem Statement

Given a set of *N* delivery locations and *V* vehicles starting at a warehouse, find the **minimum-cost set of routes** — assigning stops to vehicles such that total travel distance (or duration) is minimised, work is balanced, every stop is visited exactly once, and every vehicle returns to the origin.

---

## Business Context

Previous phases relied on a single driver (TSP) to deliver all stops. As the number of stops scales (e.g. 15-20 stops), a single vehicle becomes a bottleneck.

Phase 3 introduces **Multi-Vehicle Routing**. 
- A fleet of vehicles splits the workload.
- OR-Tools automatically determines *which* vehicle visits *which* stops.
- Load balancing is achieved via an enforced distance span constraint.

---

## Features

- 📍 **Realistic Gurgaon locations** with 16 total stops (1 depot + 15 deliveries).
- 🚚 **Multi-Vehicle Support** — Configure any number of vehicles.
- 🛣️ **OSRM road-network routing** via public demo server.
- ⏱️ **Dual optimisation** — minimise distance OR travel time.
- 📐 **Euclidean fallback** — automatic degradation if OSRM is unavailable.
- 💾 **In-memory caching** — avoids repeated API calls.
- 🧮 **Google OR-Tools VRP solver** with custom dimensions for load-balancing.
- 📊 **Enhanced Fleet Metrics** — distance and duration per vehicle, total fleet stats.
- 🎨 **Rich CLI output** — distinct colour-coded panels per vehicle route.
- 🧪 **72 Pytest tests** — comprehensive coverage of TSP, VRP, Models, and APIs.

---

## Architecture

Phase 3 extends the architecture by introducing `VehicleService` and upgrading the `OptimizationService` to handle the VRP.

```
┌──────────┐
│  main.py │  <- Thin entry point
└────┬─────┘
     │
     ▼
┌────────────────┐       ┌──────────────────┐       ┌──────────────┐
│  RouteService  │──────>│ DistanceService   │──────>│ OsrmService  │
│ (orchestrator) │       └──────────────────┘       └──────┬───────┘
└────┬─────┬─────┘                                         │
     │     │                                        ┌──────▼───────┐
     │     └────────────>┌──────────────────┐       │  RouteCache  │
     │                   │ VehicleService    │       └──────────────┘
     ▼                   └──────────────────┘
┌──────────────────────┐
│ OptimizationService  │  <- OR-Tools VRP solver
└────┬─────────────────┘
     │
     ▼
┌──────────────────┐
│ MetricsService   │  <- Multi-vehicle KPI computation
└──────────────────┘
```

---

## Folder Structure

```
route_optimizer/
│
├── config/
│   └── settings.py                      # App configuration (vehicle_count=3)
│
├── data/
│   └── sample_locations.py              # 16 Gurgaon stops
│
├── models/
│   ├── vehicle.py                       # [NEW] Vehicle domain model
│   ├── vehicle_route.py                 # [NEW] Single vehicle's route model
│   ├── location.py                      
│   ├── route.py                         
│   └── metrics.py                       # Upgraded with per-vehicle stats
│
├── services/
│   ├── vehicle_service.py               # [NEW] Fleet manager
│   ├── optimization_service.py          # Upgraded to solve_vrp
│   ├── route_service.py                 # Upgraded to optimize_vrp
│   ├── metrics_service.py               # Upgraded to calculate_vrp
│   ├── distance_service.py              
│   └── osrm_service.py                  
│
├── cache/
│   └── route_cache.py                   
│
├── utils/
│   ├── printer.py                       # Upgraded with multi-panel CLI
│   └── timer.py                         
│
├── tests/
│   ├── test_vrp_optimizer.py            # [NEW] 27 VRP-specific tests
│   ├── test_distance_service.py         
│   ├── test_optimization_service.py     
│   └── test_osrm_service.py            
│
└── main.py                              # Upgraded flow
```

---

## Installation

### Prerequisites

- **Python 3.11+**
- **Internet connection** for OSRM.

### Steps

```bash
git clone <your-repo-url>
cd route_optimizer
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

---

## Usage

```bash
python -m route_optimizer.main
```

---

## Configuration

Settings are in `config/settings.py`. To configure the fleet size:

```python
# In OptimizerSettings:
vehicle_count: int = 3  # The number of available delivery vehicles.
```

If `vehicle_count = 1`, the system automatically degenerates to solving the classic Travelling Salesman Problem (TSP).

---

## VRP vs TSP

- **TSP (Travelling Salesman Problem)**: Single vehicle visits all stops.
- **VRP (Vehicle Routing Problem)**: Multiple vehicles share the workload. The solver must decide **routing** (order of stops) AND **assignment** (which vehicle takes which stop).

---

## Vehicle Assignment Logic

Stops are assigned automatically by the `OptimizationService` using OR-Tools. 

To distribute workload effectively across the fleet, the engine uses a custom `Count` dimension with soft constraint bounds and global span cost penalties.

### Workload Balancing Modes

The platform supports three distinct workload balancing modes, configurable in `settings.py`:

* **`DISTANCE_OPTIMAL`**: Disables workload balancing completely. The solver strictly minimises absolute distance. This is the most cost-efficient mathematically but can result in some vehicles sitting idle while others are overloaded.
* **`BALANCED`**: Evaluates distance alongside workload. The solver will attempt to evenly distribute stops across available vehicles, but will allow some variance to avoid pathologically long driving detours. Best for standard operations.
* **`STRICT`**: Heavily prioritises an exact mathematical distribution of stops across all available vehicles (e.g., 5 vehicles, 15 stops = exactly 3 stops per vehicle), regardless of the distance penalty. Useful when operational constraints (e.g., driver contracts, vehicle capacity) demand strict equality.

---

## OSRM Integration

Uses the public [OSRM Table API](http://project-osrm.org/docs/v5.24.0/api/#table-service) to compute distance and duration matrices in a single network call. Automatic Euclidean fallback ensures the application never crashes if the API is unreachable.

---

## Example Output

```
╔═════════════════════════════════════════════════════════════════════════════╗
║                     LOGISTICS ROUTE OPTIMIZATION ENGINE                     ║
║                                   v3.0.0                                    ║
╚═════════════════════════════════════════════════════════════════════════════╝

   Distance Source            OSRM               
   Optimization Mode          DISTANCE           
   Vehicles Available         3                  

...

  [~] Optimization started ...
  [+] Optimization completed

  [+] Distance matrix generated  (16x16)

┌───────────────────────────────── Vehicle 1 ─────────────────────────────────┐
│                                                                             │
│    Cyber City (Warehouse)  [DEPOT]                                          │
│          |                                                                  │
│          v                                                                  │
│    Udyog Vihar                                                              │
│          |                                                                  │
│          v                                                                  │
│    Palam Vihar                                                              │
...
│    Distance: 33.79 km                                                       │
│    Duration: 54.83 min                                                      │
│    Stops:    6                                                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

... [Vehicle 2 and Vehicle 3 Panels] ...

┌─────────────────────────── --- Fleet Summary --- ───────────────────────────┐
│                                                                             │
│    Distance Source                                              OSRM        │
│    Optimization Mode                                        DISTANCE        │
│    Vehicles Available                                              3        │
│    Vehicles Used                                                   3        │
│    Total Stops                                                    15        │
│    Total Distance                                        132.75 km          │
│    Total Duration                                       189.42 min          │
│                                                                             │
│    --- Per-Vehicle ---                                                      │
│      Vehicle 1                      33.79 km / 54.83 min (6 stops)          │
│      Vehicle 2                      49.23 km / 78.69 min (8 stops)          │
│      Vehicle 3                      49.73 km / 55.90 min (1 stops)          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Testing

Run the 72 Pytest tests:

```bash
python -m pytest route_optimizer/tests/ -v
```

### Coverage (72 tests)

- **VRP Tests (27)**: Assignment logic, duplicate prevention, depot boundaries, span balancing, vehicle caps, metrics.
- **OSRM Tests (21)**: Cache hits/misses, timeout fallbacks.
- **TSP Tests (11)**: Legacy single-vehicle routing.
- **Distance Tests (13)**: Matrix math and assertions.

---

## Future Roadmap

| Phase | Feature                        | Status     |
| ----- | ------------------------------ | ---------- |
| 1     | TSP + Euclidean + CLI          | ✅ Done     |
| 2     | OSRM + Duration + Cache        | ✅ Done     |
| 3     | Multi-vehicle VRP              | ✅ Current  |
| 4     | Vehicle capacity constraints   | 📋 Planned |
| 5     | Delivery time windows          | 📋 Planned |
| 6     | FastAPI REST backend           | 📋 Planned |
| 7     | React + Leaflet map frontend   | 📋 Planned |
| 8     | PostgreSQL route persistence   | 📋 Planned |

**Future Compatibility**: The Phase 3 architecture cleanly supports Phase 4's capacity constraints through `Vehicle` property extensions and OR-Tools dimensions, without requiring structural refactoring.

---

