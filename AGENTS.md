# Cityflo AI Engineer take-home (Vibhor Sharma)

Task: BRIEF.md. Bundle (HANDOFF.md, DATA_GUIDE.md, data/) is fetched into this folder.
The operator (Vibhor) makes the judgment calls; the agent proposes, builds, runs, and verifies.

Rules
- Ask before any consequential modelling choice (cleaning rule, lateness definition, ops directive handling). Propose one recommendation with numbers, do not hand back option lists.
- Every number written in DECISION.md must come from a tool call you actually ran in this session.
- Keep the MCP server small (Python, FastMCP via `uv run --with mcp`). Polish is not graded.
- No secrets in any file. `.cursor/` is gitignored and must stay that way.
- Data-retention memo: no rider phone numbers or verbatim complaint text in any tool output, trace, or log.
- Do not call `submit_assignment` until the operator explicitly says "submit".
