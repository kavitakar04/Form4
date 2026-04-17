from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .event_returns import (
    build_event_return_panel,
    compute_event_cars,
    load_event_windows,
    write_event_return_artifacts,
)


def _read_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open() as f:
        return list(csv.DictReader(f))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build baseline event-return artifacts.")
    parser.add_argument("--events", required=True, help="Path to sell_events_processed CSV.")
    parser.add_argument("--market", required=True, help="Path to market+benchmark prepared CSV.")
    parser.add_argument("--config", required=True, help="Path to locked event-window config JSON.")
    parser.add_argument("--output-dir", required=True, help="Directory for processed artifacts.")
    parser.add_argument("--run-tag", default="manual", help="Optional run tag for manifest metadata.")
    args = parser.parse_args()

    windows = load_event_windows(args.config)
    events = _read_csv(args.events)
    market = _read_csv(args.market)

    event_returns = build_event_return_panel(events, market, windows)
    event_cars = compute_event_cars(event_returns, windows)

    write_event_return_artifacts(
        event_returns=event_returns,
        event_cars=event_cars,
        output_dir=args.output_dir,
        run_metadata={
            "run_tag": args.run_tag,
            "config_path": str(args.config),
            "window_config": json.loads(Path(args.config).read_text()),
        },
    )


if __name__ == "__main__":
    main()
