#!/usr/bin/env python3
"""Measure Claude Code token burn from session transcripts.

Reads the usage figures Claude Code records in its own transcript JSONL files, so it
reports what actually happened rather than an estimate. Appends every run to
token-usage-history.csv, because Claude Code deletes transcripts after
cleanupPeriodDays (30 by default) and the baseline would otherwise vanish.

Usage:
    python token-usage-report.py                    # last 7 days, all projects
    python token-usage-report.py --days 1           # last 24 hours
    python token-usage-report.py --project myrepo   # only project folders containing "myrepo"
    python token-usage-report.py --no-log           # don't append to the CSV
"""

import argparse
import collections
import csv
import datetime
import glob
import json
import os

# Per-million-token list prices (input, output). THESE CHANGE: check current rates (the
# bundled `claude-api` skill or Anthropic's pricing page) before trusting a total. Wrong
# prices silently mis-rank the levers.
PRICES = {
    "claude-opus-5":     (5.0, 25.0),
    "claude-fable-5":    (10.0, 50.0),
    "claude-fable-5-1":  (10.0, 50.0),
    "claude-sonnet-5":   (2.0, 10.0),
    "claude-haiku-4-5":  (1.0, 5.0),
    "claude-opus-5-5":   (4.0, 20.0),
    "claude-sonnet-5-5": (2.0, 10.0),
    "claude-haiku-5-5":  (0.10, 0.50),
}
CACHE_WRITE_MULT = 1.25     # 5-minute TTL writes
CACHE_WRITE_1H_MULT = 2.0   # 1-hour TTL writes; Claude Code main sessions write these
CACHE_READ_MULT = 0.10
# Models whose cache-read price is not 0.10x input ($/Mtok).
CACHE_READ_PRICE = {
    "claude-opus-5-5":   0.20,
    "claude-sonnet-5-5": 0.20,
}

# Not real models: Claude Code's markers for locally-generated messages that cost nothing.
# Excluded silently so a genuinely unpriced new model still stands out in the warning.
NOT_MODELS = {"<synthetic>", "?"}

PROJECTS = os.path.expanduser(os.path.join("~", ".claude", "projects"))
HISTORY_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "token-usage-history.csv")


def cache_write_cost(inp, u):
    """$ x 1e6 for cache writes, pricing 1-hour and 5-minute TTL writes separately."""
    cw1h = min(u.get("cw1h", 0), u["cw"])
    return cw1h * inp * CACHE_WRITE_1H_MULT + (u["cw"] - cw1h) * inp * CACHE_WRITE_MULT


def cache_read_rate(model):
    """$/Mtok for cache reads on this model."""
    return CACHE_READ_PRICE.get(model, PRICES[model][0] * CACHE_READ_MULT)


def price(model, u):
    """Cost in dollars for one usage record, or None if the model is unpriced."""
    if model not in PRICES:
        return None
    inp, out = PRICES[model]
    return (
        u["in"] * inp
        + cache_write_cost(inp, u)
        + u["cr"] * cache_read_rate(model)
        + u["out"] * out
    ) / 1e6


def collect(days, project):
    cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
    roots = [d for d in glob.glob(os.path.join(PROJECTS, "*"))
             if os.path.isdir(d) and (not project or project.lower() in d.lower())]
    # Subagent transcripts live in <session>/subagents/*.jsonl, not beside the session
    # file. Miss them and subagent turns read as 0 even when offload is working.
    files = [
        f for r in roots
        for f in glob.glob(os.path.join(r, "*.jsonl"))
        + glob.glob(os.path.join(r, "*", "subagents", "*.jsonl"))
        if datetime.datetime.fromtimestamp(os.path.getmtime(f)) > cutoff
    ]

    by_lane = collections.defaultdict(collections.Counter)
    sessions = []
    unpriced = set()

    for f in files:
        is_sub = os.path.basename(os.path.dirname(f)) == "subagents"
        ctx, out_tok = [], 0
        with open(f, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                m = d.get("message")
                if not isinstance(m, dict):
                    continue
                u = m.get("usage")
                if not isinstance(u, dict):
                    continue

                model = m.get("model", "?")
                rec = {
                    "in": u.get("input_tokens", 0),
                    "cw": u.get("cache_creation_input_tokens", 0),
                    "cw1h": (u.get("cache_creation") or {}).get(
                        "ephemeral_1h_input_tokens", 0),
                    "cr": u.get("cache_read_input_tokens", 0),
                    "out": u.get("output_tokens", 0),
                }
                lane = "subagent" if (d.get("isSidechain") or is_sub) else "main"
                agg = by_lane[(model, lane)]
                agg["turns"] += 1
                for k, v in rec.items():
                    agg[k] += v
                if model not in PRICES and model not in NOT_MODELS:
                    unpriced.add(model)

                total_ctx = rec["in"] + rec["cw"] + rec["cr"]
                if total_ctx:
                    ctx.append(total_ctx)
                out_tok += rec["out"]

        if ctx and not is_sub:
            sessions.append({
                "id": os.path.basename(f)[:8],
                "turns": len(ctx),
                "peak": max(ctx),
                "avg": sum(ctx) // len(ctx),
                "out": out_tok,
            })

    return by_lane, sessions, unpriced, len(files)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--project", help="only project folders whose name contains this")
    ap.add_argument("--no-log", action="store_true")
    args = ap.parse_args()

    by_lane, sessions, unpriced, nfiles = collect(args.days, args.project)
    if not by_lane:
        print(f"No usage found in the last {args.days} day(s).")
        return

    rows, total = [], 0.0
    for (model, lane), u in by_lane.items():
        c = price(model, u)
        if c is None:
            continue
        total += c
        rows.append((c, model, lane, u))
    rows.sort(reverse=True)

    print(f"\n=== Claude Code token usage, last {args.days} day(s) "
          f"({nfiles} transcripts) ===\n")
    print(f"{'model':<20}{'lane':<10}{'turns':>7}{'cache_read':>15}"
          f"{'cache_wr':>12}{'output':>11}{'$':>9}{'$/turn':>9}")
    for c, model, lane, u in rows:
        print(f"{model:<20}{lane:<10}{u['turns']:>7,}{u['cr']:>15,}"
              f"{u['cw']:>12,}{u['out']:>11,}{c:>9,.0f}{c / u['turns']:>9.3f}")
    print(f"\nTOTAL ${total:,.0f} over {args.days}d "
          f"(~${total * 30 / args.days:,.0f}/30d, list-price equivalent)")

    # Cost composition: this is what tells you which lever to pull.
    comp = collections.Counter()
    for c, model, lane, u in rows:
        inp, out = PRICES[model]
        comp["cache_read (history re-read)"] += u["cr"] * cache_read_rate(model) / 1e6
        comp["cache_write (new context)"] += cache_write_cost(inp, u) / 1e6
        comp["output (text + thinking)"] += u["out"] * out / 1e6
        comp["uncached input"] += u["in"] * inp / 1e6
    print("\n--- cost composition ---")
    for k, v in comp.most_common():
        print(f"  {k:<32}${v:>8,.0f}  {v / total * 100:>5.1f}%")

    print("\n--- heaviest sessions by context ---")
    print(f"{'session':<10}{'turns':>7}{'ctx_peak':>11}{'ctx_avg':>10}{'output':>11}")
    for s in sorted(sessions, key=lambda x: x["avg"], reverse=True)[:8]:
        print(f"{s['id']:<10}{s['turns']:>7,}{s['peak']:>11,}"
              f"{s['avg']:>10,}{s['out']:>11,}")

    sub = sum(u["turns"] for (m, l), u in by_lane.items() if l == "subagent")
    mainturns = sum(u["turns"] for (m, l), u in by_lane.items() if l == "main")
    print(f"\nsubagent turns: {sub:,} of {sub + mainturns:,} "
          f"({sub / max(1, sub + mainturns) * 100:.1f}%)")

    if unpriced:
        print(f"\nWARNING unpriced models excluded from totals: {sorted(unpriced)}")
        print("  Add them to PRICES with current rates.")

    if not args.no_log:
        new = not os.path.exists(HISTORY_CSV)
        with open(HISTORY_CSV, "a", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            if new:
                w.writerow(["run_date", "window_days", "model", "lane", "turns",
                            "cache_read", "cache_write", "uncached_in", "output",
                            "est_usd", "usd_per_turn"])
            today = datetime.date.today().isoformat()
            for c, model, lane, u in rows:
                w.writerow([today, args.days, model, lane, u["turns"], u["cr"],
                            u["cw"], u["in"], u["out"], round(c, 2),
                            round(c / u["turns"], 4)])
        print(f"\nappended to {HISTORY_CSV}")


if __name__ == "__main__":
    main()
