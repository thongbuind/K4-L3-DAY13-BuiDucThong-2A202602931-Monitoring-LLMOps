"""Render the six required dashboard panels from the JSONL log contract.

This intentionally uses only the standard library: it is easy to run in the
lab environment and produces a portable HTML artifact suitable for evidence.
"""

from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


def percentile(values: list[float], p: int) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((p / 100) * len(ordered) + 0.5) - 1))
    return ordered[index]


def load_records(path: Path, minutes: int) -> list[dict[str, Any]]:
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=minutes)
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
            timestamp = datetime.fromisoformat(record["ts"].replace("Z", "+00:00"))
        except (KeyError, ValueError, json.JSONDecodeError):
            continue
        if timestamp >= cutoff:
            records.append(record)
    return records


def value(record: dict[str, Any], key: str) -> float | None:
    candidate = record.get(key)
    return float(candidate) if isinstance(candidate, int | float) else None


def render(records: list[dict[str, Any]], minutes: int) -> str:
    requests = [item for item in records if item.get("event") == "request_received"]
    responses = [item for item in records if item.get("event") == "response_sent"]
    failures = [item for item in records if item.get("event") == "request_failed"]
    latencies = [item for item in (value(row, "latency_ms") for row in responses) if item is not None]
    ttfts = [item for item in (value(row, "ttft_ms") for row in responses) if item is not None]
    costs = [item for item in (value(row, "cost_usd") for row in responses) if item is not None]
    token_in = [item for item in (value(row, "tokens_in") for row in responses) if item is not None]
    token_out = [item for item in (value(row, "tokens_out") for row in responses) if item is not None]
    quality = [item for item in (value(row, "quality_score") for row in responses) if item is not None]
    tool_events = [row for row in records if row.get("tool_success") is not None]
    tool_success = sum(row.get("tool_success") is True for row in tool_events)
    errors = len(failures) / len(requests) * 100 if requests else 0.0
    retrieval = tool_success / len(tool_events) * 100 if tool_events else 0.0
    error_types: dict[str, int] = {}
    for row in failures:
        error_types[str(row.get("error_type", "unknown"))] = error_types.get(str(row.get("error_type", "unknown")), 0) + 1

    panels = [
        ("Latency percentiles and TTFT", "ms · threshold P95 ≤ 3,000", [
            f"P50: {percentile(latencies, 50):.0f} ms", f"P95: {percentile(latencies, 95):.0f} ms", f"P99: {percentile(latencies, 99):.0f} ms", f"TTFT P95: {percentile(ttfts, 95):.0f} ms"]),
        ("Request traffic", "requests/min · threshold ≥ 1", [
            f"Requests: {len(requests)}", f"Rate: {len(requests) / minutes:.2f} requests/min"]),
        ("Error rate and retrieval success", "percent · error threshold ≤ 2", [
            f"Error rate: {errors:.2f}%", f"Retrieval success: {retrieval:.2f}%", f"Breakdown: {html.escape(json.dumps(error_types) if error_types else 'none')}"]),
        ("Cost over time", "USD · total threshold ≤ 2.50", [
            f"Total: ${sum(costs):.6f}", f"Average/request: ${mean(costs):.6f}" if costs else "Average/request: $0.000000"]),
        ("Input and output tokens", "tokens · threshold total ≤ 50,000", [
            f"Input: {sum(token_in):.0f}", f"Output: {sum(token_out):.0f}", f"Total: {sum(token_in) + sum(token_out):.0f}"]),
        ("Quality proxy", "score 0–1 · threshold mean ≥ 0.75", [
            f"Mean quality: {mean(quality):.2f}" if quality else "Mean quality: 0.00", f"Scored responses: {len(quality)}"]),
    ]
    cards = "\n".join(
        "<section><h2>{}</h2><p class=unit>{}</p>{}</section>".format(
            html.escape(title), html.escape(unit), "".join(f"<p>{line}</p>" for line in lines)
        )
        for title, unit, lines in panels
    )
    generated = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return f"""<!doctype html>
<html lang="en"><meta charset="utf-8"><title>Day 13 Monitoring Dashboard</title>
<style>body{{font-family:system-ui,sans-serif;background:#0b1020;color:#eef2ff;margin:2rem}}header{{margin-bottom:1rem}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem}}section{{background:#18213d;border:1px solid #35436b;border-radius:12px;padding:1.1rem}}h1,h2{{margin:.1rem 0 .5rem}}h2{{font-size:1.1rem}}p{{margin:.4rem 0}}.unit{{color:#9db0dc;font-size:.9rem}}</style>
<body><header><h1>K4-L3A Day 13 Monitoring &amp; LLMOps</h1><p>Source: data/logs.jsonl · Time range: last {minutes} minutes · Refresh: regenerate every 30 seconds</p><p>Generated: {generated}</p></header><main class="grid">{cards}</main></body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Render the lab's six-panel dashboard")
    parser.add_argument("--logs", type=Path, default=REPO_ROOT / "data" / "logs.jsonl")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "submission" / "evidence" / "11-dashboard-overview.html")
    parser.add_argument("--minutes", type=int, default=60)
    args = parser.parse_args()
    if args.minutes <= 0:
        parser.error("--minutes must be positive")
    if not args.logs.exists():
        parser.error(f"log file not found: {args.logs}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    records = load_records(args.logs, args.minutes)
    args.output.write_text(render(records, args.minutes), encoding="utf-8")
    print(f"Rendered six-panel dashboard from {len(records)} records: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
