from __future__ import annotations

import csv
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Iterable

BASELINE_WINDOWS: tuple[tuple[int, int], ...] = ((0, 1), (-1, 1), (0, 2), (-2, 2))


@dataclass(frozen=True)
class BaselineConfig:
    sell_events_path: Path = Path("data/processed/sell_events_processed.csv")
    event_returns_path: Path = Path("data/processed/event_returns_processed.csv")
    output_tables_dir: Path = Path("outputs/tables")
    output_logs_dir: Path = Path("outputs/logs")
    windows: tuple[tuple[int, int], ...] = BASELINE_WINDOWS


def _read_csv(path: Path) -> list[dict[str, str]]:
    if path.suffix.lower() != ".csv":
        raise ValueError(f"Only CSV inputs are supported for now: {path}")
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def _to_bool(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def _to_float(value: object) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    return float(text)


def _to_int(value: object) -> int | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    return int(float(text))


def _validate_inputs(sell_events: list[dict[str, str]], event_returns: list[dict[str, str]]) -> None:
    if not sell_events:
        raise ValueError("sell_events input is empty")
    if not event_returns:
        raise ValueError("event_returns input is empty")

    required_sell_cols = {"event_id", "clean_sell_flag", "exclusion_reason", "event_date"}
    required_ret_cols = {"event_id", "event_time", "abnormal_return"}
    missing_sell = required_sell_cols - set(sell_events[0].keys())
    missing_ret = required_ret_cols - set(event_returns[0].keys())
    if missing_sell:
        raise ValueError(f"sell_events missing required columns: {sorted(missing_sell)}")
    if missing_ret:
        raise ValueError(f"event_returns missing required columns: {sorted(missing_ret)}")


def _window_label(window: tuple[int, int]) -> str:
    return f"[{window[0]},{window[1]}]"


def _sample_std(values: list[float]) -> float | None:
    n = len(values)
    if n < 2:
        return None
    m = sum(values) / n
    var = sum((v - m) ** 2 for v in values) / (n - 1)
    return math.sqrt(var)


def _build_return_panel(event_returns: list[dict[str, str]]) -> dict[str, dict[int, float]]:
    panel: dict[str, dict[int, float]] = {}
    for row in event_returns:
        event_id = row["event_id"]
        event_time = _to_int(row["event_time"])
        abnormal_return = _to_float(row["abnormal_return"])
        if event_time is None or abnormal_return is None:
            continue
        panel.setdefault(event_id, {})[event_time] = abnormal_return
    return panel


def run_baseline_experiment(config: BaselineConfig) -> dict[str, Path]:
    config.output_tables_dir.mkdir(parents=True, exist_ok=True)
    config.output_logs_dir.mkdir(parents=True, exist_ok=True)

    sell_events = _read_csv(config.sell_events_path)
    event_returns = _read_csv(config.event_returns_path)
    _validate_inputs(sell_events, event_returns)

    total_events = len(sell_events)
    event_id_counts: dict[str, int] = {}
    for row in sell_events:
        event_id_counts[row["event_id"]] = event_id_counts.get(row["event_id"], 0) + 1

    duplicate_event_ids = sorted([k for k, count in event_id_counts.items() if count > 1])
    duplicate_rows = sum(event_id_counts[eid] for eid in duplicate_event_ids)

    clean_events = [row for row in sell_events if _to_bool(row.get("clean_sell_flag"))]
    excluded_events = [row for row in sell_events if not _to_bool(row.get("clean_sell_flag"))]

    exclusion_counts: dict[str, int] = {}
    for row in excluded_events:
        reason = (row.get("exclusion_reason") or "unspecified_exclusion").strip() or "unspecified_exclusion"
        exclusion_counts[reason] = exclusion_counts.get(reason, 0) + 1
    if duplicate_event_ids:
        exclusion_counts["duplicate_event_id"] = len(duplicate_event_ids)

    deduped_clean: dict[str, dict[str, str]] = {}
    for row in clean_events:
        deduped_clean.setdefault(row["event_id"], row)

    return_panel = _build_return_panel(event_returns)

    missing_return_panel_ids = sorted([eid for eid in deduped_clean if eid not in return_panel])
    final_clean_ids = sorted([eid for eid in deduped_clean if eid in return_panel])

    car_summary_rows: list[dict[str, object]] = []
    window_drop_rows: list[dict[str, object]] = []

    for window in config.windows:
        start, end = window
        required = set(range(start, end + 1))
        cars: list[float] = []

        for event_id in final_clean_ids:
            series = return_panel[event_id]
            if not required.issubset(series.keys()):
                continue
            cars.append(sum(series[t] for t in sorted(required)))

        n = len(cars)
        mean_car = sum(cars) / n if n else None
        med_car = median(cars) if n else None
        sd = _sample_std(cars)
        se = (sd / math.sqrt(n)) if (sd is not None and n > 0) else None
        t_stat = (mean_car / se) if (mean_car is not None and se not in (None, 0.0)) else None

        car_summary_rows.append(
            {
                "event_window": _window_label(window),
                "sample_size": n,
                "mean_car": mean_car,
                "median_car": med_car,
                "std_error": se,
                "t_stat": t_stat,
            }
        )
        window_drop_rows.append(
            {
                "event_window": _window_label(window),
                "included_events": n,
                "dropped_incomplete_window": len(final_clean_ids) - n,
            }
        )

    attrition_rows = [
        {"step": "total_sell_events", "count": total_events},
        {"step": "duplicate_event_id_rows", "count": duplicate_rows},
        {"step": "events_flagged_clean", "count": len(clean_events)},
        {"step": "events_flagged_excluded", "count": len(excluded_events)},
        {"step": "clean_events_missing_return_panel", "count": len(missing_return_panel_ids)},
        {"step": "post_join_clean_events", "count": len(final_clean_ids)},
    ]

    exclusion_rows = [
        {"exclusion_reason": reason, "count": count}
        for reason, count in sorted(exclusion_counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ]

    summary_path = config.output_tables_dir / "baseline_car_summary.csv"
    attrition_path = config.output_tables_dir / "baseline_sample_attrition.csv"
    exclusion_path = config.output_tables_dir / "baseline_exclusion_breakdown.csv"
    dropped_path = config.output_tables_dir / "baseline_window_drops.csv"

    _write_csv(
        summary_path,
        car_summary_rows,
        ["event_window", "sample_size", "mean_car", "median_car", "std_error", "t_stat"],
    )
    _write_csv(attrition_path, attrition_rows, ["step", "count"])
    _write_csv(exclusion_path, exclusion_rows, ["exclusion_reason", "count"])
    _write_csv(
        dropped_path,
        window_drop_rows,
        ["event_window", "included_events", "dropped_incomplete_window"],
    )

    summary_blob = summary_path.read_bytes()
    run_signature = {
        "sell_events_path": str(config.sell_events_path),
        "event_returns_path": str(config.event_returns_path),
        "windows": [list(w) for w in config.windows],
        "summary_sha256": hashlib.sha256(summary_blob).hexdigest(),
    }

    log_payload = {
        "filters_applied": [
            "clean_sell_flag == True",
            "drop duplicate event_id entries (keep first)",
            "retain events with return-panel records",
            "for each window retain events with complete event_time coverage and non-null abnormal_return",
        ],
        "final_sample_definition": "Filing-date events from sell_events_processed with clean_sell_flag=true and complete event-return coverage per window.",
        "dropped_observations": {
            "missing_return_panel_event_ids": missing_return_panel_ids,
            "window_drop_counts": window_drop_rows,
        },
        "attrition_steps": attrition_rows,
        "run_signature": run_signature,
    }

    log_path = config.output_logs_dir / "baseline_run_log.json"
    with log_path.open("w", encoding="utf-8") as f:
        json.dump(log_payload, f, indent=2)

    return {
        "summary": summary_path,
        "attrition": attrition_path,
        "exclusion_breakdown": exclusion_path,
        "window_drops": dropped_path,
        "log": log_path,
    }
