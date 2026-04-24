"""Form4 baseline pipeline package."""

from .event_returns import (
    align_event_to_trading_day,
    build_event_return_panel,
    compute_event_cars,
    load_event_windows,
    write_event_return_artifacts,
)

__all__ = [
    "align_event_to_trading_day",
    "build_event_return_panel",
    "compute_event_cars",
    "load_event_windows",
    "write_event_return_artifacts",
]
