# Cityflo AI Engineer take-home — on-time performance MCP

Small MCP server over this week’s messy GPS export so an agent (and Priya) can answer: which routes were actually late, by how much, and which three were worst — as a defended verdict, not a mean.

## Run the server

```bash
uv run --with 'mcp<2' python server.py
```

Pin `mcp<2` because current `mcp` 2.x renamed FastMCP. Stdio transport is the default.

Cursor MCP register (cwd = this folder):

```json
{
  "command": "uv",
  "args": ["run", "--with", "mcp<2", "python", "server.py"]
}
```

See also `RUN.md`.

## Tools (`cityflo-otp`)

| Tool | Purpose |
|---|---|
| `data_quality` | Cleaning rules with counts and trip ids |
| `route_verdicts` | All routes: verdict, rank, share, median, p90, late_days, naive mean, fragile |
| `route_detail` | Per-day breakdown, worst trips, late trip ids per day, REC-114 side column |
| `trip` | One trip: raw fields, delay, cleaning status |

Optional on verdicts/detail: `trips_path`, `schedule_path`, thresholds (`late_min`, `share_min`, `min_late_days`, `min_trips`, `min_days`), `hour_from` / `hour_to`, `yardstick` (`export` \| `rec114`). Defaults match the locked Friday rule. Outputs are ids and numbers only (directive a).

## Deliverables

- **`DECISION.md`** — Priya’s Friday verdict: table, worst three, costs, four-part records for every consequential call
- **`decisions.jsonl`** — steering ledger (verbatim operator quotes + turn anchors)
- **`server.py`** — the MCP server
- Bundle: `HANDOFF.md`, `DATA_GUIDE.md`, `data/`

Do not commit `.cursor/` (gitignored; may hold local MCP auth).
