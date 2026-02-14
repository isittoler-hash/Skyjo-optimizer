from __future__ import annotations

import json
from pathlib import Path


def summarize_reports(artifacts_root: str | Path) -> list[dict[str, object]]:
    root = Path(artifacts_root)
    rows: list[dict[str, object]] = []

    if not root.exists():
        return rows

    for report_path in sorted(root.glob("*/report.json")):
        payload = json.loads(report_path.read_text())
        metadata = payload.get("metadata", {})
        optimized = payload.get("optimized", {})
        benchmark = payload.get("benchmark", {})
        tournament = payload.get("tournament_benchmark", {})

        rows.append(
            {
                "run_dir": report_path.parent.name,
                "git_commit_hash": metadata.get("git_commit_hash", "unknown"),
                "seed": metadata.get("seed"),
                "timestamp": metadata.get("run_timestamp_utc"),
                "optimized_fitness": optimized.get("aggregate_fitness"),
                "benchmark_fitness": benchmark.get("aggregate_fitness"),
                "holdout_score": payload.get("holdout_score"),
                "heuristic_win_rate": tournament.get("win_rate_by_agent", {}).get("heuristic"),
            }
        )

    return rows


def write_summary_csv(rows: list[dict[str, object]], output: str | Path) -> Path:
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)

    headers = [
        "run_dir",
        "git_commit_hash",
        "seed",
        "timestamp",
        "optimized_fitness",
        "benchmark_fitness",
        "holdout_score",
        "heuristic_win_rate",
    ]

    lines = [",".join(headers)]
    for row in rows:
        values = [str(row.get(header, "")) for header in headers]
        lines.append(",".join(values))

    destination.write_text("\n".join(lines) + "\n")
    return destination
