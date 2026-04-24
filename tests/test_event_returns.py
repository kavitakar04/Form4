from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from form4_pipeline.event_returns import (
    EventWindow,
    align_event_to_trading_day,
    build_event_return_panel,
    compute_event_cars,
    write_event_return_artifacts,
)


def _baseline_windows() -> list[EventWindow]:
    return [
        EventWindow(name="m1_p1", start=-1, end=1),
        EventWindow(name="m2_p2", start=-2, end=2),
        EventWindow(name="p0_p1", start=0, end=1),
        EventWindow(name="p0_p2", start=0, end=2),
    ]


def test_event_date_alignment_uses_first_trading_day_on_or_after_event_date() -> None:
    trading_dates = [
        Path("2026-04-16").name,
        Path("2026-04-17").name,
        Path("2026-04-20").name,
    ]
    from datetime import datetime

    parsed = [datetime.strptime(d, "%Y-%m-%d").date() for d in trading_dates]
    event_date = datetime.strptime("2026-04-18", "%Y-%m-%d").date()

    idx = align_event_to_trading_day(event_date, parsed)
    assert idx == 2


def test_window_construction_respects_locked_min_and_max_offsets() -> None:
    events = [
        {
            "event_id": "e1",
            "issuer_ticker": "ABC",
            "event_date": "2026-04-17",
            "clean_sell_flag": True,
        }
    ]
    market = [
        {"issuer_ticker": "ABC", "trade_date": "2026-04-15", "raw_return": 0.01, "benchmark_return": 0.0},
        {"issuer_ticker": "ABC", "trade_date": "2026-04-16", "raw_return": 0.02, "benchmark_return": 0.0},
        {"issuer_ticker": "ABC", "trade_date": "2026-04-17", "raw_return": 0.03, "benchmark_return": 0.0},
        {"issuer_ticker": "ABC", "trade_date": "2026-04-18", "raw_return": 0.04, "benchmark_return": 0.0},
        {"issuer_ticker": "ABC", "trade_date": "2026-04-19", "raw_return": 0.05, "benchmark_return": 0.0},
    ]

    rows = build_event_return_panel(events, market, _baseline_windows())
    assert [r["event_time"] for r in rows] == [-2, -1, 0, 1, 2]


def test_abnormal_return_is_raw_minus_benchmark() -> None:
    events = [{"event_id": "e1", "issuer_ticker": "ABC", "event_date": "2026-04-17", "clean_sell_flag": True}]
    market = [
        {"issuer_ticker": "ABC", "trade_date": "2026-04-17", "raw_return": 0.015, "benchmark_return": 0.005},
        {"issuer_ticker": "ABC", "trade_date": "2026-04-18", "raw_return": 0.010, "benchmark_return": 0.003},
        {"issuer_ticker": "ABC", "trade_date": "2026-04-19", "raw_return": 0.020, "benchmark_return": 0.007},
    ]

    rows = build_event_return_panel(events, market, [EventWindow(name="p0_p1", start=0, end=1)])
    assert rows[0]["abnormal_return"] == pytest.approx(0.01)
    assert rows[1]["abnormal_return"] == pytest.approx(0.007)


def test_car_aggregation_sums_abnormal_returns_across_window() -> None:
    event_returns = [
        {"event_id": "e1", "event_time": -1, "abnormal_return": 0.01},
        {"event_id": "e1", "event_time": 0, "abnormal_return": 0.02},
        {"event_id": "e1", "event_time": 1, "abnormal_return": -0.01},
    ]
    windows = [EventWindow(name="m1_p1", start=-1, end=1), EventWindow(name="p0_p2", start=0, end=2)]

    cars = compute_event_cars(event_returns, windows)
    car_map = {c["window_name"]: c for c in cars}

    assert car_map["m1_p1"]["car"] == pytest.approx(0.02)
    assert car_map["m1_p1"]["complete_window"] is True
    assert car_map["p0_p2"]["car"] == pytest.approx(0.01)
    assert car_map["p0_p2"]["complete_window"] is False


def test_processed_artifact_writing_is_deterministic_and_complete(tmp_path: Path) -> None:
    event_returns = [
        {
            "event_id": "b",
            "issuer_ticker": "B",
            "event_date": "2026-04-17",
            "trade_date": "2026-04-18",
            "event_time": 1,
            "raw_return": 0.1,
            "benchmark_return": 0.05,
            "abnormal_return": 0.05,
        },
        {
            "event_id": "a",
            "issuer_ticker": "A",
            "event_date": "2026-04-17",
            "trade_date": "2026-04-17",
            "event_time": 0,
            "raw_return": 0.1,
            "benchmark_return": 0.08,
            "abnormal_return": 0.02,
        },
    ]
    event_cars = [
        {
            "event_id": "a",
            "window_name": "p0_p1",
            "window_start": 0,
            "window_end": 1,
            "days_observed": 2,
            "days_expected": 2,
            "complete_window": True,
            "car": 0.04,
        }
    ]

    paths = write_event_return_artifacts(event_returns, event_cars, tmp_path, {"run_tag": "test"})
    second_paths = write_event_return_artifacts(event_returns, event_cars, tmp_path, {"run_tag": "test"})

    assert paths == second_paths
    with Path(paths["event_returns_processed"]).open() as f:
        rows = list(csv.DictReader(f))
    assert [r["event_id"] for r in rows] == ["a", "b"]

    manifest = json.loads(Path(paths["manifest"]).read_text())
    assert manifest["row_counts"]["event_returns_processed"] == 2
    assert manifest["row_counts"]["event_cars_processed"] == 1
