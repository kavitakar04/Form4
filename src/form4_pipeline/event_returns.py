from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class EventWindow:
    name: str
    start: int
    end: int


def _to_date(value: Any) -> date:
    if isinstance(value, date):
        return value
    return datetime.strptime(str(value), "%Y-%m-%d").date()


def load_event_windows(config_path: str | Path) -> list[EventWindow]:
    """Load locked baseline event windows from JSON config."""
    payload = json.loads(Path(config_path).read_text())
    windows: list[EventWindow] = []
    for item in payload.get("event_windows", []):
        windows.append(EventWindow(name=item["name"], start=int(item["start"]), end=int(item["end"])))

    if not windows:
        raise ValueError("No event windows configured.")

    for window in windows:
        if window.start > window.end:
            raise ValueError(f"Invalid window {window.name}: start > end")

    return windows


def align_event_to_trading_day(event_date: date, trading_dates: list[date]) -> int | None:
    """Return index of first trading date on/after event date; None if unavailable."""
    for idx, trade_date in enumerate(trading_dates):
        if trade_date >= event_date:
            return idx
    return None


def build_event_return_panel(
    sell_events: list[dict[str, Any]],
    market_benchmark_rows: list[dict[str, Any]],
    windows: list[EventWindow],
) -> list[dict[str, Any]]:
    """
    Join clean sell events to prepared issuer/day raw + benchmark returns and compute AR.

    Expected market row fields: issuer_ticker, trade_date, raw_return, benchmark_return.
    """
    min_offset = min(window.start for window in windows)
    max_offset = max(window.end for window in windows)

    by_ticker: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in market_benchmark_rows:
        normalized = dict(row)
        normalized["trade_date"] = _to_date(normalized["trade_date"])
        by_ticker[normalized["issuer_ticker"]].append(normalized)

    for ticker_rows in by_ticker.values():
        ticker_rows.sort(key=lambda x: x["trade_date"])

    output: list[dict[str, Any]] = []
    for event in sell_events:
        if not event.get("clean_sell_flag", False):
            continue
        ticker = event["issuer_ticker"]
        if ticker not in by_ticker:
            continue

        event_date = _to_date(event["event_date"])
        ticker_rows = by_ticker[ticker]
        trading_dates = [row["trade_date"] for row in ticker_rows]
        zero_idx = align_event_to_trading_day(event_date, trading_dates)
        if zero_idx is None:
            continue

        for event_time in range(min_offset, max_offset + 1):
            row_idx = zero_idx + event_time
            if row_idx < 0 or row_idx >= len(ticker_rows):
                continue
            market_row = ticker_rows[row_idx]
            raw_return = float(market_row["raw_return"])
            benchmark_return = float(market_row["benchmark_return"])
            output.append(
                {
                    "event_id": event["event_id"],
                    "issuer_ticker": ticker,
                    "event_date": event_date.isoformat(),
                    "trade_date": market_row["trade_date"].isoformat(),
                    "event_time": event_time,
                    "raw_return": raw_return,
                    "benchmark_return": benchmark_return,
                    "abnormal_return": raw_return - benchmark_return,
                }
            )

    output.sort(key=lambda x: (x["event_id"], x["event_time"], x["trade_date"]))
    return output


def compute_event_cars(
    event_returns: list[dict[str, Any]],
    windows: list[EventWindow],
) -> list[dict[str, Any]]:
    """Compute event-level CAR for configured windows from abnormal returns."""
    rows_by_event: dict[str, dict[int, dict[str, Any]]] = defaultdict(dict)
    for row in event_returns:
        rows_by_event[row["event_id"]][int(row["event_time"])] = row

    output: list[dict[str, Any]] = []
    for event_id, indexed_rows in rows_by_event.items():
        for window in windows:
            expected_offsets = list(range(window.start, window.end + 1))
            available = [offset for offset in expected_offsets if offset in indexed_rows]
            complete = len(available) == len(expected_offsets)
            car_value = sum(float(indexed_rows[offset]["abnormal_return"]) for offset in available) if available else None
            output.append(
                {
                    "event_id": event_id,
                    "window_name": window.name,
                    "window_start": window.start,
                    "window_end": window.end,
                    "days_observed": len(available),
                    "days_expected": len(expected_offsets),
                    "complete_window": complete,
                    "car": car_value,
                }
            )

    output.sort(key=lambda x: (x["event_id"], x["window_start"], x["window_end"], x["window_name"]))
    return output


def write_event_return_artifacts(
    event_returns: list[dict[str, Any]],
    event_cars: list[dict[str, Any]],
    output_dir: str | Path,
    run_metadata: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Write reproducible processed artifacts and metadata manifest."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    event_returns_path = out_dir / "event_returns_processed.csv"
    event_cars_path = out_dir / "event_cars_processed.csv"
    manifest_path = out_dir / "event_returns_manifest.json"

    event_return_fields = [
        "event_id",
        "issuer_ticker",
        "event_date",
        "trade_date",
        "event_time",
        "raw_return",
        "benchmark_return",
        "abnormal_return",
    ]
    with event_returns_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=event_return_fields)
        writer.writeheader()
        for row in sorted(event_returns, key=lambda x: (x["event_id"], int(x["event_time"]), x["trade_date"])):
            writer.writerow({k: row.get(k) for k in event_return_fields})

    event_car_fields = [
        "event_id",
        "window_name",
        "window_start",
        "window_end",
        "days_observed",
        "days_expected",
        "complete_window",
        "car",
    ]
    with event_cars_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=event_car_fields)
        writer.writeheader()
        for row in sorted(event_cars, key=lambda x: (x["event_id"], x["window_start"], x["window_end"], x["window_name"])):
            writer.writerow({k: row.get(k) for k in event_car_fields})

    manifest = {
        "artifacts": {
            "event_returns_processed": str(event_returns_path),
            "event_cars_processed": str(event_cars_path),
        },
        "row_counts": {
            "event_returns_processed": len(event_returns),
            "event_cars_processed": len(event_cars),
        },
        "run_metadata": run_metadata or {},
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True))

    return {
        "event_returns_processed": str(event_returns_path),
        "event_cars_processed": str(event_cars_path),
        "manifest": str(manifest_path),
    }
