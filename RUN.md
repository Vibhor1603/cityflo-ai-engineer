# cityflo-otp MCP

```bash
uv run --with 'mcp<2' python server.py
```

Pin `mcp<2`: current `mcp` 2.x renamed FastMCP. Stdio transport (default).

Cursor MCP register (cwd = this folder):

```json
{"command":"uv","args":["run","--with","mcp<2","python","server.py"]}
```

Tools: `data_quality`, `route_verdicts`, `route_detail`, `trip`. Optional `trips_path` / `schedule_path` for a fresh slice. Defaults: `data/trips.csv`, `data/schedule_v2.csv`. `route_verdicts` / `route_detail` also take `hour_from` / `hour_to` (departure hour, inclusive) and `yardstick` (`export` | `rec114`).
