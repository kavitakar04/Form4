from __future__ import annotations

import csv
import json
from pathlib import Path

from baseline_experiment import BASELINE_WINDOWS, BaselineConfig, run_baseline_experiment


def _write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _build_fixture_data(tmp_path: Path) -> tuple[Path, Path]:
    sell_events = [
        {"event_id": "E1", "clean_sell_flag": "true", "exclusion_reason": "", "event_date": "2026-01-10"},
        {"event_id": "E2", "clean_sell_flag": "true", "exclusion_reason": "", "event_date": "2026-01-11"},
        {"event_id": "E3", "clean_sell_flag": "true", "exclusion_reason": "", "event_date": "2026-01-12"},
        {"event_id": "E4", "clean_sell_flag": "false", "exclusion_reason": "derivative", "event_date": "2026-01-13"},
        {"event_id": "E2", "clean_sell_flag": "true", "exclusion_reason": "", "event_date": "2026-01-11"},
        {"event_id": "E5", "clean_sell_flag": "true", "exclusion_reason": "", "event_date": "2026-01-14"},
    ]

    rows: list[dict[str, object]] = []
    e1 = {-2: 0.01, -1: 0.01, 0: 0.02, 1: -0.01, 2: 0.03}
    e2 = {-2: 0.00, -1: -0.02, 0: 0.01, 1: 0.00, 2: 0.02}
    e3 = {-2: 0.01, -1: 0.00, 0: 0.01, 1: 0.01}
    for event_id, series in [("E1", e1), ("E2", e2), ("E3", e3)]:
        for event_time, ar in series.items():
            rows.append(
                {
                    "event_id": event_id,
                    "event_time": event_time,
                    "abnormal_return": ar,
                    "trade_date": "2026-01-15",
                    "raw_return": ar,
                    "benchmark_return": 0.0,
                }
            )

    sell_path = tmp_path / "sell_events_processed.csv"
    ret_path = tmp_path / "event_returns_processed.csv"
    _write_csv(sell_path, sell_events, ["event_id", "clean_sell_flag", "exclusion_reason", "event_date"])
    _write_csv(ret_path, rows, ["event_id", "event_time", "abnormal_return", "trade_date", "raw_return", "benchmark_return"])
    return sell_path, ret_path


def test_correct_aggregation(tmp_path: Path) -> None:
    sell_path, ret_path = _build_fixture_data(tmp_path)
    cfg = BaselineConfig(sell_events_path=sell_path, event_returns_path=ret_path, output_tables_dir=tmp_path / "tables", output_logs_dir=tmp_path / "logs")
    run_baseline_experiment(cfg)

    summary = _read_csv(tmp_path / "tables" / "baseline_car_summary.csv")
    row = next(r for r in summary if r["event_window"] == "[0,1]")

    assert int(row["sample_size"]) == 3
    assert abs(float(row["mean_car"]) - (0.04 / 3)) < 1e-10
    assert abs(float(row["median_car"]) - 0.01) < 1e-10


def test_sample_counts_consistency(tmp_path: Path) -> None:
    sell_path, ret_path = _build_fixture_data(tmp_path)
    cfg = BaselineConfig(sell_events_path=sell_path, event_returns_path=ret_path, output_tables_dir=tmp_path / "tables", output_logs_dir=tmp_path / "logs")
    run_baseline_experiment(cfg)

    attrition = _read_csv(tmp_path / "tables" / "baseline_sample_attrition.csv")
    dropped = _read_csv(tmp_path / "tables" / "baseline_window_drops.csv")

    attr_map = {r["step"]: int(r["count"]) for r in attrition}
    assert attr_map["total_sell_events"] == attr_map["events_flagged_clean"] + attr_map["events_flagged_excluded"]
    assert attr_map["post_join_clean_events"] == 3

    wide = next(r for r in dropped if r["event_window"] == "[-2,2]")
    assert int(wide["included_events"]) == 2
    assert int(wide["dropped_incomplete_window"]) == 1


def test_reproducibility_of_outputs(tmp_path: Path) -> None:
    sell_path, ret_path = _build_fixture_data(tmp_path)

    cfg1 = BaselineConfig(sell_events_path=sell_path, event_returns_path=ret_path, output_tables_dir=tmp_path / "tables1", output_logs_dir=tmp_path / "logs1")
    cfg2 = BaselineConfig(sell_events_path=sell_path, event_returns_path=ret_path, output_tables_dir=tmp_path / "tables2", output_logs_dir=tmp_path / "logs2")

    run_baseline_experiment(cfg1)
    run_baseline_experiment(cfg2)

    s1 = (tmp_path / "tables1" / "baseline_car_summary.csv").read_text()
    s2 = (tmp_path / "tables2" / "baseline_car_summary.csv").read_text()
    assert s1 == s2

    log1 = json.loads((tmp_path / "logs1" / "baseline_run_log.json").read_text())
    log2 = json.loads((tmp_path / "logs2" / "baseline_run_log.json").read_text())

    assert log1["run_signature"]["summary_sha256"] == log2["run_signature"]["summary_sha256"]
    assert log1["run_signature"]["windows"] == [list(w) for w in BASELINE_WINDOWS]
