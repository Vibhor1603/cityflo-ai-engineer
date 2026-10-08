# Decision record — Friday route review (Priya, Ops Lead)

**Week:** 2026-08-03 to 2026-08-09 · **Clean trips:** 5248 of 5292 · **Yardstick for verdicts:** export timetable only

**Verdict in one line:** Flag **R-14, R-33, R-26** as the worst three; also LATE are **R-37** and **R-31** (fragile). Clear **R-35** as a route but pre-clear rider remedies for its **19** Aug-5 trips. Do not apply REC-114 to the ranking.

---

## Verdict table (all 40 routes)

Source: `route_verdicts` defaults (`late_min=5`, `share_min=0.30`, `min_late_days=4`, `min_trips=60`, `min_days=5`, `yardstick=export`). Rank by share late, tiebreak median delay. Late-trip count = round(`n × share_late`).

| Rank | Route | Verdict | n | Share late | Median delay (min) | p90 (min) | Late days | Late trips | Fragile | Naive mean |
|---:|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| 1 | R-14 | LATE | 118 | 72.03% | 8.0 | 13.3 | 7/7 | 85 | no | 8.07 |
| 2 | R-33 | LATE | 104 | 47.12% | 5.0 | 10.0 | 7/7 | 49 | no | 5.36 |
| 3 | R-26 | LATE | 103 | 42.72% | 4.0 | 9.0 | 5/7 | 44 | no | 4.51 |
| 4 | R-37 | LATE | 105 | 40.00% | 4.0 | 9.0 | 6/7 | 42 | no | 4.13 |
| 5 | R-31 | LATE | 112 | 33.04% | 4.0 | 8.0 | 4/7 | 37 | **yes** | 3.59 |
| 6 | R-17 | ON_TIME | 147 | 27.89% | 3.0 | 8.0 | 2/7 | 41 | no | 2.98 |
| 7 | R-35 | ON_TIME | 132 | 24.24% | 2.0 | 49.8 | 1/7 | 32 | no | 8.05 |
| 8 | R-09 | ON_TIME | 146 | 22.60% | 2.0 | 7.5 | 2/7 | 33 | no | 2.31 |
| 9 | R-34 | ON_TIME | 124 | 22.58% | 3.0 | 8.0 | 2/7 | 28 | no | 2.51 |
| 10 | R-27 | ON_TIME | 143 | 22.38% | 2.0 | 8.0 | 0/7 | 32 | no | 2.60 |
| 11 | R-07 | ON_TIME | 147 | 21.77% | 3.0 | 7.4 | 1/7 | 32 | no | 2.73 |
| 12 | R-40 | ON_TIME | 152 | 21.71% | 3.0 | 7.0 | 0/7 | 33 | no | 2.61 |
| 13 | R-15 | ON_TIME | 119 | 21.01% | 3.0 | 8.0 | 1/7 | 25 | no | 2.67 |
| 14 | R-21 | ON_TIME | 124 | 20.97% | 2.0 | 7.0 | 1/7 | 26 | no | 1.82 |
| 15 | R-18 | ON_TIME | 154 | 20.78% | 2.0 | 7.0 | 0/7 | 32 | no | 2.03 |
| 16 | R-08 | ON_TIME | 126 | 20.63% | 3.0 | 7.0 | 2/7 | 26 | no | 2.36 |
| 17 | R-03 | ON_TIME | 103 | 20.39% | 2.0 | 7.0 | 1/7 | 21 | no | 1.70 |
| 18 | R-05 | ON_TIME | 105 | 19.05% | 2.0 | 7.0 | 0/7 | 20 | no | 2.34 |
| 19 | R-19 | ON_TIME | 125 | 18.40% | 3.0 | 7.0 | 1/7 | 23 | no | 2.33 |
| 20 | R-11 | ON_TIME | 137 | 16.79% | 2.0 | 7.4 | 1/7 | 23 | no | 2.26 |
| 21 | R-20 | ON_TIME | 145 | 16.55% | 2.0 | 6.6 | 0/7 | 24 | no | 1.97 |
| 22 | R-38 | ON_TIME | 146 | 16.44% | 1.0 | 7.0 | 0/7 | 24 | no | 1.49 |
| 23 | R-39 | ON_TIME | 154 | 16.23% | 2.0 | 6.0 | 0/7 | 25 | no | 1.81 |
| 24 | R-22 | ON_TIME | 112 | 16.07% | 2.0 | 6.0 | 1/7 | 18 | no | 1.82 |
| 25 | R-32 | ON_TIME | 133 | 15.79% | 1.0 | 7.0 | 0/7 | 21 | no | 1.17 |
| 26 | R-25 | ON_TIME | 137 | 14.60% | 1.0 | 7.0 | 2/7 | 20 | no | 1.45 |
| 27 | R-02 | ON_TIME | 105 | 14.29% | 2.0 | 6.0 | 0/7 | 15 | no | 1.34 |
| 28 | R-10 | ON_TIME | 126 | 14.29% | 1.0 | 6.5 | 0/7 | 18 | no | 1.07 |
| 29 | R-12 | ON_TIME | 112 | 13.39% | 2.0 | 6.0 | 0/7 | 15 | no | 1.79 |
| 30 | R-24 | ON_TIME | 146 | 10.96% | 1.0 | 6.0 | 0/7 | 16 | no | 0.84 |
| 31 | R-28 | ON_TIME | 151 | 9.93% | 1.0 | 5.0 | 0/7 | 15 | no | 0.62 |
| 32 | R-36 | ON_TIME | 132 | 9.85% | 1.0 | 5.0 | 0/7 | 13 | no | 0.22 |
| 33 | R-04 | ON_TIME | 144 | 9.72% | 0.0 | 5.0 | 0/7 | 14 | no | 0.17 |
| 34 | R-01 | ON_TIME | 153 | 8.50% | 1.0 | 5.0 | 0/7 | 13 | no | 0.82 |
| 35 | R-30 | ON_TIME | 147 | 7.48% | −1.0 | 5.0 | 0/7 | 11 | no | −0.38 |
| 36 | R-23 | ON_TIME | 132 | 6.06% | 0.0 | 5.0 | 0/7 | 8 | no | 0.11 |
| 37 | R-13 | ON_TIME | 133 | 6.02% | −1.0 | 4.8 | 0/7 | 8 | no | −0.93 |
| 38 | R-06 | ON_TIME | 117 | 5.13% | −2.0 | 3.4 | 0/7 | 6 | no | −1.45 |
| 39 | R-16 | ON_TIME | 146 | 4.79% | 0.0 | 4.0 | 0/7 | 7 | no | −0.19 |
| 40 | R-29 | ON_TIME | 151 | 3.97% | −1.0 | 4.0 | 0/7 | 6 | no | −0.93 |

**Worst three**

| # | Route | Share late | Median | p90 | Late trips | Late days |
|---|---|---:|---:|---:|---:|---:|
| 1 | R-14 | 72.03% | 8.0 | 13.3 | 85 | 7/7 |
| 2 | R-33 | 47.12% | 5.0 | 10.0 | 49 | 7/7 |
| 3 | R-26 | 42.72% | 4.0 | 9.0 | 44 | 5/7 |

Named challenger for #3: **R-37** (40.00% share, median 4.0, p90 9.0, **42** late trips, **6/7** late days).

---

## Cost (who pays)

From the same `route_verdicts` table:

| Bucket | Late trips | Who pays |
|---|---:|---|
| Five LATE routes (R-14, R-33, R-26, R-37, R-31) | **257** | Depot-head on-time incentive risk |
| Thirty-five ON_TIME routes | **724** | Refund / goodwill / ratings exposure if riders escalate |
| Network | **981** (18.7% of 5248) | — |

Most late trips (**724 / 981**) sit on routes we clear. That is still the right line: the network baseline is already **18.7%** late, and the Friday ask is which routes are **chronically** late, not which buses were late once. Clearing a route does not deny that its late trips happened; it refuses to treat a single bad day or a below-threshold week as a depot verdict.

**R-35 Aug 5 rider-remedy item (not a depot flag):** 19/19 trips late that day, day median delay **+52** min (`route_detail` R-35). Pre-clear refunds/goodwill for these trip ids rather than flagging the R-35 depot:

`T1-04505`, `T1-04506`, `T1-04507`, `T1-04508`, `T1-04509`, `T1-04510`, `T1-04511`, `T1-04512`, `T1-04513`, `T1-04514`, `T1-04515`, `T1-04516`, `T1-04517`, `T1-04518`, `T1-04519`, `T1-04520`, `T1-04521`, `T1-04522`, `T1-04523`

That is the cost of the day-consistency rule: **19** trips paid from the refund budget so one day cannot make or break a route.

---

## Four-part records

### 1. Lateness rule and day gate

- **The rule.** A trip is late if `actual_arrival − (scheduled_departure + export scheduled_runtime_min) > 5` minutes, after the cleaning pipeline. A route is LATE if (a) share of late trips ≥ 30% and (b) at least `ceil(4 × n_days / 7)` calendar days have day-share ≥ 30%; else ON_TIME if n ≥ 60 and n_days ≥ 5, else INSUFFICIENT. Rank LATE (and the table) by share late, tiebreak median delay. Fragile = verdict flips under leave-one-day-out.
- **The case it breaks on.** R-35: week share 24.24%, only 1/7 late-days, so ON_TIME — while naive mean delay is 8.05 (would rank #2) and p90 is 49.8 because Aug 5 is 19/19 late at median +52. The rule refuses to let one day define the route.
- **The cost, and who pays.** Nineteen Aug-5 rider-remedy trips (ids above) hit the refund/goodwill budget instead of the R-35 depot incentive. Network-wide, 724 late trips on cleared routes stay in the refund queue rather than depot reviews.
- **What would change my mind.** A second late-day on R-35 at ≥30% day-share in the same week, or a standing ops definition that a single day above a severity bar (e.g. median delay ≥ 30) auto-flags the route regardless of late-day count.

### 2. Worst-three ranking (R-26 vs R-37)

- **The rule.** Among routes, rank by share of late trips; tiebreak median delay. Late-days is a gate into LATE, not the rank key. R-26 is #3 (42.72%, 44 late trips, 5 late-days); R-37 is #4 (40.00%, 42 late trips, 6 late-days).
- **The case it breaks on.** Share gap is ~2.7 points (~3 trips). Leave-one-day-out at the 5-min threshold flips #3 to R-37 only when Aug 9 (R-26’s strongest late-day) is dropped. Ranking by late-days instead would put R-37 above R-26.
- **The cost, and who pays.** Putting R-26 in the worst three puts its depot on the hook for a route with 44 late trips; swapping to R-37 would move that spotlight by 2 late trips while R-37 already has more late calendar days (6 vs 5).
- **What would change my mind.** Occupancy (riders per trip), which we do not have — that is the strongest honest attack on #3. Corroboration only: AM peak `hour_from=7, hour_to=10, min_trips=20` (defaults unchanged) ranks R-26 #8 ON_TIME at 29.17% while R-37 is #5 ON_TIME at 34.62%; R-31 rises to #2 LATE at 50%. Peak view weakens R-26’s #3 claim and strengthens R-31; it does not rewrite the weekly verdict.

### 3. R-31 fragile but LATE

- **The rule.** Same LATE definition. R-31 meets it: 33.04% share, exactly 4/7 late-days, n=112. Tool marks `fragile=true` because leave-one-day-out can flip the verdict.
- **The case it breaks on.** Drop any one of its late-days (Aug 4, 5, 7, or 8) and it can fall out of LATE under the scaled day gate. It is the knife-edge LATE route, not a hand-clear.
- **The cost, and who pays.** Keeping it LATE exposes the R-31 depot on **37** late trips. Clearing it by hand would move those 37 into the “we said on-time” refund argument.
- **What would change my mind.** Next week’s data with late_days ≤ 3 or share &lt; 30% under the same rule — not a one-off override this week. AM peak corroboration (min_trips=20) actually makes R-31 look worse (50% share, #2), so peak is not a reason to clear it.

### 4. R-35 cleared as a route

- **The rule.** Day-consistent LATE gate (above). R-35: 24.24% share, 1 late-day → ON_TIME.
- **The case it breaks on.** Aug 5 alone: 19 trips, 100% late, median +52. Naive mean would hang the depot; the day gate does not.
- **The cost, and who pays.** Refund/goodwill for the 19 trip ids listed above — paid by rider ops, not the R-35 depot incentive.
- **What would change my mind.** Same as §1: a second qualifying late-day the same week, or a written severity override for catastrophic single days.

### 5. REC-114 not applied to verdicts

- **The rule.** Verdicts always use export `scheduled_runtime_min`. `schedule_v2` appears only as a side view (`yardstick=rec114` or `route_detail` rec114_side): revised runtime only for listed routes on/after `effective_date`.
- **The case it breaks on.** Literal “4xx series” is `vehicle_series=40` → R-40 only; `schedule_v2` has no R-40 row → join is empty. Applied by route instead: R-14 share falls 72.03% → 43.22% (still LATE, but fragile, late_days 7→4); **R-27 flips ON_TIME → LATE** (22.38% → 43.36%, 5 late-days) on a schedule row labelled “no change”; worst three become R-33, R-27, R-14.
- **The cost, and who pays.** Using REC-114 as the verdict yardstick would reshuffle depot exposure (hang R-27, soften R-14) on a two-line file with no operational rationale Priya can defend when people poke holes.
- **What would change my mind.** A signed ops note that names routes (not only “4xx”), states why revised runtimes supersede what riders were sold, and accepts the R-27 hang — then re-run with `yardstick=rec114` as the primary table.

### 6. Directive (a) — data retention

- **The rule.** Tool outputs carry trip ids, route ids, categories/statuses, and numbers only. No rider phone numbers, no verbatim complaint text, no ops_log prose in tool responses.
- **The case it breaks on.** `ops_log.txt` is free text; we do not join it into tools or echo it in MCP output. (It is also last week’s log — see caveats.)
- **The cost, and who pays.** Slightly less narrative colour in the tool; Priya still has the log file offline if needed.
- **What would change my mind.** A revised retention memo that explicitly allows category-plus-redacted summaries in tool traces.

### 7. Cleaning rules

- **The rule (generic, ordered).** (1) Unparseable arrival → drop (24). (2) Non-`+05:30` tz → convert arrival to IST; blank/malformed → assume IST and count (1 converted: T1-02864; 0 blank; 0 malformed). (3) After tz fix, arrival ≤ scheduled departure → drop (18). (4) Same route + scheduled_departure + actual_arrival on &gt;1 rows: identical runtime → keep one; differing runtime → exclude all (2 excluded: T1-03235, T1-03237). Clean set: **5248**.
- **The case it breaks on.** T1-02864 would look −282 min late without tz conversion; after convert, delay −2, kept. T1-03235/T1-03237 are one physical trip with two runtimes — excluding both drops evidence rather than guessing.
- **The cost, and who pays.** 44 rows out of ranking (device garbage / ambiguity). Dual-runtime exclude may under-count R-25 by one trip slot.
- **What would change my mind.** A device-side correction feed that recovers HH:60 stamps, or a depot attestation of which runtime was sold for the dual pair.

---

## Data issues (from `data_quality`)

| Rule | Count |
|---|---:|
| drop_unparseable_arrival | 24 |
| tz_converted_to_ist | 1 |
| tz_blank_assumed_ist | 0 |
| tz_malformed_assumed_ist | 0 |
| drop_arrival_not_after_departure | 18 |
| dedupe_identical_runtime kept / dropped | 0 / 0 |
| exclude_conflicting_runtime | 2 |
| rows_clean | 5248 |

---

## Caveats

- **`ops_log.txt` is last week’s log** (HANDOFF). It cannot explain Wed 2026-08-05 on this export. No other route shows an Aug-5 blowout like R-35, so a “city-wide” story does not fit this file either.
- **AM peak with default `min_trips=60`:** all routes INSUFFICIENT (slice too thin). That is the weekly floor working, not a bug. Corroboration-only run with `min_trips=20` is documented above; defaults unchanged.
- **REC-114 side numbers** (`yardstick=rec114`): R-14 43.22% / 4 late-days (LATE, fragile); R-27 43.36% / 5 late-days (LATE). Visible for the review; not the verdict.

---

## Independent check

Recomputed outside this agent session with a separate pandas script (same four cleaning rules, same lateness / day-gate / rank definition): **5248** clean; R-14 **72.0%** / R-33 **47.1%** / R-26 **42.7%** / R-37 **40.0%** / R-31 **33.0%**; **257** vs **724** late trips (LATE vs cleared); R-35 Aug 5 **19/19** late at median **+52**; rec114 R-14 **43.2%** with **4** late-days and R-27 **43.4%** with **5**. No discrepancies with the MCP tool outputs used above.
