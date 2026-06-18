"""
Rich-powered CLI printer for professional terminal output.

All display logic is centralised here so that business services
remain UI-agnostic.
"""

from __future__ import annotations

import io
import sys
from typing import Sequence

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from route_optimizer.config.settings import settings
from route_optimizer.models.location import Location
from route_optimizer.models.metrics import Metrics
from route_optimizer.models.route import Route
from route_optimizer.models.vehicle_route import VehicleRoute

# Force UTF-8 output on Windows to avoid cp1252 encoding errors.
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace"
    )
    sys.stderr = io.TextIOWrapper(
        sys.stderr.buffer, encoding="utf-8", errors="replace"
    )

# Module-level console instance — force_terminal enables colours
# even when output is piped; force_jupyter=False avoids auto-detection issues.
console = Console(force_terminal=True, force_jupyter=False)

# Colour palette — cohesive brand feel.
_CLR_TITLE = "bold bright_cyan"
_CLR_ACCENT = "bold bright_green"
_CLR_ARROW = "bold yellow"
_CLR_LABEL = "bold white"
_CLR_VALUE = "bright_magenta"
_CLR_SUCCESS = "bold green"
_CLR_ERROR = "bold red"
_CLR_WARNING = "bold yellow"
_CLR_DIM = "dim white"

# Vehicle-specific colours for visual distinction.
_VEHICLE_COLOURS = [
    "bright_cyan",
    "bright_green",
    "bright_magenta",
    "bright_yellow",
    "bright_red",
    "bright_blue",
    "orange1",
    "deep_pink1",
]


# ── Public API ──────────────────────────────────────────────────


def print_header() -> None:
    """Display the application banner."""
    title = Text(settings.app_name.upper(), style=_CLR_TITLE, justify="center")
    subtitle = Text(f"v{settings.version}", style=_CLR_DIM, justify="center")
    content = Text.assemble(title, "\n", subtitle)
    console.print()
    console.print(
        Panel(
            content,
            box=box.DOUBLE_EDGE,
            border_style="bright_cyan",
            padding=(1, 4),
        )
    )
    console.print()


def print_config_summary(
    distance_source: str,
    optimization_mode: str,
    vehicle_count: int | None = None,
) -> None:
    """Display the active configuration."""
    table = Table(
        box=box.SIMPLE,
        show_header=False,
        border_style="bright_cyan",
        padding=(0, 2),
    )
    table.add_column("Key", style=_CLR_LABEL, min_width=22)
    table.add_column("Value", style=_CLR_VALUE, min_width=16)

    table.add_row("Distance Source", distance_source.upper())
    table.add_row("Optimization Mode", optimization_mode.upper())
    if vehicle_count is not None:
        table.add_row("Vehicles Available", str(vehicle_count))

    console.print(table)
    console.print()


def print_locations_loaded(locations: Sequence[Location]) -> None:
    """Show a summary table of loaded locations."""
    table = Table(
        title="[>>] Loaded Locations",
        title_style=_CLR_ACCENT,
        box=box.ROUNDED,
        border_style="bright_green",
        header_style="bold bright_white",
        show_lines=True,
    )
    table.add_column("#", style="bold cyan", justify="center", width=4)
    table.add_column("Name", style="bright_white", min_width=24)
    table.add_column("Latitude", style="bright_yellow", justify="right")
    table.add_column("Longitude", style="bright_yellow", justify="right")

    for loc in locations:
        role = " [DEPOT]" if loc.id == 0 else ""
        table.add_row(
            str(loc.id),
            f"{loc.name}{role}",
            f"{loc.latitude:.4f}",
            f"{loc.longitude:.4f}",
        )

    console.print(table)
    console.print(
        f"  [bold]Total locations:[/bold] [{_CLR_VALUE}]{len(locations)}[/]",
    )
    console.print()


def print_matrix_generated(size: int, label: str = "Distance") -> None:
    """Confirm matrix creation."""
    console.print(
        f"  [+] [{_CLR_SUCCESS}]{label} matrix generated[/]  "
        f"[{_CLR_DIM}]({size}x{size})[/]"
    )


def print_optimization_started() -> None:
    """Indicate that the solver is running."""
    console.print(f"  [~] [{_CLR_LABEL}]Optimization started ...[/]")


def print_optimization_completed() -> None:
    """Indicate solver completion."""
    console.print(f"  [+] [{_CLR_SUCCESS}]Optimization completed[/]")
    console.print()


def print_fallback_warning() -> None:
    """Display a warning when OSRM failed and Euclidean fallback was used."""
    console.print(
        Panel(
            f"[{_CLR_WARNING}][!] OSRM unavailable. "
            f"Falling back to Euclidean distances.[/]",
            title="[bold yellow]Warning[/]",
            box=box.ROUNDED,
            border_style="yellow",
        )
    )
    console.print()


def print_route(route: Route) -> None:
    """Display the optimised route as a vertical itinerary (single vehicle)."""
    _print_route_panel(
        route.ordered_locations,
        title=">>> Optimized Route",
        border_colour="bright_cyan",
    )


def print_vehicle_routes(vehicle_routes: list[VehicleRoute]) -> None:
    """Display per-vehicle routes with colour-coded panels."""
    dp = settings.display.distance_precision

    for idx, vr in enumerate(vehicle_routes):
        colour = _VEHICLE_COLOURS[idx % len(_VEHICLE_COLOURS)]

        if vr.is_empty:
            console.print(
                Panel(
                    Text("  No stops assigned", style=_CLR_DIM),
                    title=f"[bold {colour}]{vr.vehicle_name} (idle)[/]",
                    box=box.ROUNDED,
                    border_style=colour,
                    padding=(0, 2),
                )
            )
            console.print()
            continue

        # Build itinerary lines.
        lines: list[Text] = []
        for i, loc in enumerate(vr.locations):
            is_depot = (i == 0 or i == len(vr.locations) - 1)
            label = loc.name
            if is_depot:
                label += "  [DEPOT]"
            style = _CLR_ACCENT if is_depot else "bright_white"
            lines.append(Text(f"  {label}", style=style))
            if i < len(vr.locations) - 1:
                lines.append(Text("        |", style=_CLR_ARROW))
                lines.append(Text("        v", style=_CLR_ARROW))

        # Append distance / duration summary.
        lines.append(Text(""))
        lines.append(
            Text(f"  Distance: {vr.distance:.{dp}f} km", style=_CLR_VALUE)
        )
        if vr.duration > 0:
            lines.append(
                Text(f"  Duration: {vr.duration:.{dp}f} min", style=_CLR_VALUE)
            )
        lines.append(
            Text(f"  Stops:    {vr.num_stops}", style=_CLR_VALUE)
        )

        body = Text("\n").join(lines)
        console.print(
            Panel(
                body,
                title=f"[bold {colour}]{vr.vehicle_name}[/]",
                box=box.ROUNDED,
                border_style=colour,
                padding=(1, 2),
            )
        )
        console.print()


def print_metrics(metrics: Metrics) -> None:
    """Display route metrics in a styled panel."""
    dp = settings.display.distance_precision
    tp = settings.display.time_precision

    table = Table(
        box=box.SIMPLE_HEAVY,
        show_header=False,
        border_style="bright_magenta",
        padding=(0, 2),
    )
    table.add_column("Metric", style=_CLR_LABEL, min_width=28)
    table.add_column("Value", style=_CLR_VALUE, justify="right", min_width=14)

    table.add_row("Distance Source", metrics.distance_source.upper())
    table.add_row("Optimization Mode", metrics.optimization_mode.upper())

    if metrics.vehicle_count > 1:
        table.add_row("Vehicles Available", str(metrics.vehicle_count))
        table.add_row("Vehicles Used", str(metrics.vehicles_used))

    table.add_row("Total Stops", str(metrics.total_stops))
    table.add_row("Total Distance", f"{metrics.total_distance:.{dp}f} km")

    if metrics.total_duration > 0:
        table.add_row("Total Duration", f"{metrics.total_duration:.{dp}f} min")

    table.add_row(
        "Avg Distance / Stop",
        f"{metrics.average_distance_per_stop:.{dp}f} km",
    )

    if metrics.total_duration > 0:
        table.add_row(
            "Avg Duration / Stop",
            f"{metrics.average_duration_per_stop:.{dp}f} min",
        )

    table.add_row("Execution Time", f"{metrics.execution_time:.{tp}f} sec")

    # ── Per-vehicle breakdown ───────────────────────────────────
    if metrics.vehicle_metrics:
        table.add_row("", "")  # Spacer
        table.add_row(
            "[bold bright_cyan]--- Per-Vehicle ---[/]", "",
        )
        for vm in metrics.vehicle_metrics:
            if vm.num_stops == 0:
                table.add_row(
                    f"  {vm.vehicle_name}",
                    "[dim]idle[/]",
                )
            else:
                detail = f"{vm.distance:.{dp}f} km"
                if vm.duration > 0:
                    detail += f" / {vm.duration:.{dp}f} min"
                detail += f" ({vm.num_stops} stops)"
                table.add_row(f"  {vm.vehicle_name}", detail)

    title = "--- Fleet Summary ---" if metrics.vehicle_count > 1 else "--- Route Metrics ---"
    console.print(
        Panel(
            table,
            title=f"[bold bright_magenta]{title}[/]",
            box=box.ROUNDED,
            border_style="bright_magenta",
            padding=(1, 1),
        )
    )
    console.print()


def print_footer() -> None:
    """Print a closing rule."""
    console.rule(style="bright_cyan")
    console.print(
        Text(
            "  Route optimization complete. Ready for dispatch.  ",
            style="bold bright_green",
            justify="center",
        )
    )
    console.rule(style="bright_cyan")
    console.print()


def print_error(message: str) -> None:
    """Display an error message."""
    console.print(
        Panel(
            f"[{_CLR_ERROR}][X] {message}[/]",
            title="[bold red]Error[/]",
            box=box.HEAVY,
            border_style="red",
        )
    )


# ── Internal helpers ────────────────────────────────────────────

def _print_route_panel(
    locations: list[Location],
    title: str = "Optimized Route",
    border_colour: str = "bright_cyan",
) -> None:
    """Render a single vertical itinerary inside a panel."""
    lines: list[Text] = []
    for i, loc in enumerate(locations):
        is_depot = (i == 0 or i == len(locations) - 1)
        label = loc.name
        if is_depot:
            label += "  [DEPOT]"
        style = _CLR_ACCENT if is_depot else "bright_white"
        lines.append(Text(f"  {label}", style=style))
        if i < len(locations) - 1:
            lines.append(Text("        |", style=_CLR_ARROW))
            lines.append(Text("        v", style=_CLR_ARROW))

    body = Text("\n").join(lines)
    console.print(
        Panel(
            body,
            title=f"[bold {border_colour}]{title}[/]",
            box=box.ROUNDED,
            border_style=border_colour,
            padding=(1, 2),
        )
    )
    console.print()
