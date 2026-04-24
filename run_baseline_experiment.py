from __future__ import annotations

import argparse
from pathlib import Path

from baseline_experiment import BaselineConfig, run_baseline_experiment


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run baseline filing-date event study experiment.")
    parser.add_argument("--sell-events", default="data/processed/sell_events_processed.csv")
    parser.add_argument("--event-returns", default="data/processed/event_returns_processed.csv")
    parser.add_argument("--output-tables", default="outputs/tables")
    parser.add_argument("--output-logs", default="outputs/logs")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = BaselineConfig(
        sell_events_path=Path(args.sell_events),
        event_returns_path=Path(args.event_returns),
        output_tables_dir=Path(args.output_tables),
        output_logs_dir=Path(args.output_logs),
    )
    outputs = run_baseline_experiment(config)
    for name, path in outputs.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
