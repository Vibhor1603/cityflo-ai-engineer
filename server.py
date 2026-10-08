#!/usr/bin/env python3
"""Cityflo on-time performance MCP server. Ids and numbers only in tool output."""

from __future__ import annotations

import csv
import math
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from statistics import mean, median
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("cityflo-otp")

ROOT = Path(__file__).resolve().parent
DEFAULT_TRIPS = str(ROOT / "data" / "trips.csv")
DEFAULT_SCHEDULE = str(ROOT / "data" / "schedule_v2.csv")
REFERENCE_WEEK_DAYS = 7
IST = timedelta(hours=5, minutes=30)
IST_LABEL = "+05:30"
TZ_RE = re.compile(r"^([+-])(\d{2}):(\d{2})$")

Yardstick = Literal["export", "rec114"]


def _parse_arrival(raw: str) -> datetime | None:
    try:
        return datetime.strptime((raw or "").strip(), "%Y-%m-%d %H:%M")
    except ValueError:
        return None


def _parse_tz_offset(raw: str) -> timedelta | None:
    """Parse ±HH:MM to a timedelta east of UTC. None if blank or malformed."""
    s = (raw or "").strip()
    if not s:
        return None
    m = TZ_RE.match(s)
    if not m:
        return None
    sign = 1 if m.group(1) == "+" else -1
    return sign * timedelta(hours=int(m.group(2)), minutes=int(m.group(3)))


def _to_ist(arrival: datetime, tz_raw: str) -> tuple[datetime, str, str]:
    """
    Convert device arrival to IST wall clock.
    Returns (ist_arrival, tz_used_label, tz_action) where tz_action is
    one of: already_ist | converted | blank_assumed_ist | malformed_assumed_ist.
    """
    offset = _parse_tz_offset(tz_raw)
    if offset is None:
        action = "blank_assumed_ist" if not (tz_raw or "").strip() else "malformed_assumed_ist"
        return arrival, IST_LABEL, action
    if offset == IST:
        return arrival, IST_LABEL, "already_ist"
    # device wall = UTC + offset  =>  UTC = wall - offset  =>  IST = UTC + IST
    ist_arrival = arrival - offset + IST
    return ist_arrival, IST_LABEL, "converted"


def _quantile(vals: list[float], q: float) -> float | None:
    if not vals:
        return None
    vals = sorted(vals)
    idx = (len(vals) - 1) * q
    lo = int(idx)
    hi = min(lo + 1, len(vals) - 1)
    return vals[lo] * (1 - (idx - lo)) + vals[hi] * (idx - lo)


def required_late_days(n_days: int, min_late_days: int) -> int:
    """Scale min_late_days from a 7-day week onto days present (ceil)."""
    if n_days <= 0:
        return min_late_days
    return max(1, math.ceil(min_late_days * n_days / REFERENCE_WEEK_DAYS))


@dataclass
class TripRow:
    trip_id: str
    route: str
    vehicle_series: str
    scheduled_departure: str
    scheduled_runtime_min: float
    actual_arrival_raw: str
    actual_arrival: datetime | None  # IST wall after tz fix, if parseable/kept path
    tz_offset_raw: str
    tz_offset: str
    tz_action: str
    dep: datetime
    day: date
    cleaning_status: str
    delay_min: float | None


def load_schedule(schedule_path: str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    with open(schedule_path, newline="") as f:
        for r in csv.DictReader(f):
            out[r["route"]] = {
                "revised_runtime_min": int(r["revised_runtime_min"]),
                "effective_date": datetime.strptime(r["effective_date"], "%Y-%m-%d").date(),
            }
    return out


def load_and_clean(trips_path: str) -> tuple[list[TripRow], dict[str, Any]]:
    with open(trips_path, newline="") as f:
        raw_rows = list(csv.DictReader(f))

    # Working records through the pipeline
    # status starts unset; we mark drops in order
    records: list[dict[str, Any]] = []
    for r in raw_rows:
        dep = datetime.strptime(r["scheduled_departure"], "%Y-%m-%d %H:%M")
        records.append(
            {
                "trip_id": r["trip_id"],
                "route": r["route"],
                "vehicle_series": r["vehicle_series"],
                "scheduled_departure": r["scheduled_departure"],
                "scheduled_runtime_min": float(r["scheduled_runtime_min"]),
                "actual_arrival_raw": r["actual_arrival"],
                "tz_offset_raw": (r.get("tz_offset") or ""),
                "dep": dep,
                "day": dep.date(),
                "status": "pending",
                "arr_ist": None,
                "tz_offset": IST_LABEL,
                "tz_action": "pending",
            }
        )

    rule_ids: dict[str, list[str]] = {
        "drop_unparseable_arrival": [],
        "tz_converted_to_ist": [],
        "tz_blank_assumed_ist": [],
        "tz_malformed_assumed_ist": [],
        "drop_arrival_not_after_departure": [],
        "dedupe_identical_runtime_kept_one": [],
        "dedupe_identical_runtime_dropped": [],
        "exclude_conflicting_runtime": [],
    }

    # 1) unparseable arrival -> drop
    for rec in records:
        arr = _parse_arrival(rec["actual_arrival_raw"])
        if arr is None:
            rec["status"] = "drop_unparseable_arrival"
            rule_ids["drop_unparseable_arrival"].append(rec["trip_id"])
        else:
            rec["_arr_parsed"] = arr

    # 2) tz normalize to IST (only rows still pending)
    for rec in records:
        if rec["status"] != "pending":
            continue
        ist_arr, tz_label, action = _to_ist(rec["_arr_parsed"], rec["tz_offset_raw"])
        rec["arr_ist"] = ist_arr
        rec["tz_offset"] = tz_label
        rec["tz_action"] = action
        if action == "converted":
            rule_ids["tz_converted_to_ist"].append(rec["trip_id"])
        elif action == "blank_assumed_ist":
            rule_ids["tz_blank_assumed_ist"].append(rec["trip_id"])
        elif action == "malformed_assumed_ist":
            rule_ids["tz_malformed_assumed_ist"].append(rec["trip_id"])

    # 3) after tz fix, arrival <= scheduled departure -> drop
    for rec in records:
        if rec["status"] != "pending":
            continue
        if rec["arr_ist"] <= rec["dep"]:
            rec["status"] = "drop_arrival_not_after_departure"
            rule_ids["drop_arrival_not_after_departure"].append(rec["trip_id"])

    # 4) same route + scheduled_departure + actual_arrival (IST):
    #    identical runtime -> keep one (lowest trip_id); differing -> exclude all
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for rec in records:
        if rec["status"] != "pending":
            continue
        arr_key = rec["arr_ist"].strftime("%Y-%m-%d %H:%M")
        groups[(rec["route"], rec["scheduled_departure"], arr_key)].append(rec)

    for _key, members in groups.items():
        if len(members) < 2:
            continue
        runtimes = {m["scheduled_runtime_min"] for m in members}
        members_sorted = sorted(members, key=lambda m: m["trip_id"])
        if len(runtimes) == 1:
            keep = members_sorted[0]
            for m in members_sorted[1:]:
                m["status"] = "dedupe_identical_runtime_dropped"
                rule_ids["dedupe_identical_runtime_dropped"].append(m["trip_id"])
            rule_ids["dedupe_identical_runtime_kept_one"].append(keep["trip_id"])
        else:
            for m in members_sorted:
                m["status"] = "exclude_conflicting_runtime"
                rule_ids["exclude_conflicting_runtime"].append(m["trip_id"])

    for rec in records:
        if rec["status"] == "pending":
            rec["status"] = "kept"

    trips: list[TripRow] = []
    for rec in records:
        delay = None
        if rec["status"] == "kept" and rec["arr_ist"] is not None:
            sa = rec["dep"] + timedelta(minutes=rec["scheduled_runtime_min"])
            delay = (rec["arr_ist"] - sa).total_seconds() / 60.0
        trips.append(
            TripRow(
                trip_id=rec["trip_id"],
                route=rec["route"],
                vehicle_series=rec["vehicle_series"],
                scheduled_departure=rec["scheduled_departure"],
                scheduled_runtime_min=rec["scheduled_runtime_min"],
                actual_arrival_raw=rec["actual_arrival_raw"],
                actual_arrival=rec["arr_ist"],
                tz_offset_raw=rec["tz_offset_raw"],
                tz_offset=rec["tz_offset"],
                tz_action=rec.get("tz_action", "n/a"),
                dep=rec["dep"],
                day=rec["day"],
                cleaning_status=rec["status"],
                delay_min=delay,
            )
        )

    summary = {
        "rows_in": len(raw_rows),
        "rows_excluded": sum(1 for t in trips if t.cleaning_status != "kept"),
        "rows_clean": sum(1 for t in trips if t.cleaning_status == "kept"),
        "rules": [
            {
                "rule": "drop_unparseable_arrival",
                "count": len(rule_ids["drop_unparseable_arrival"]),
                "trip_ids": rule_ids["drop_unparseable_arrival"],
            },
            {
                "rule": "tz_converted_to_ist",
                "count": len(rule_ids["tz_converted_to_ist"]),
                "trip_ids": rule_ids["tz_converted_to_ist"],
            },
            {
                "rule": "tz_blank_assumed_ist",
                "count": len(rule_ids["tz_blank_assumed_ist"]),
                "trip_ids": rule_ids["tz_blank_assumed_ist"],
            },
            {
                "rule": "tz_malformed_assumed_ist",
                "count": len(rule_ids["tz_malformed_assumed_ist"]),
                "trip_ids": rule_ids["tz_malformed_assumed_ist"],
            },
            {
                "rule": "drop_arrival_not_after_departure",
                "count": len(rule_ids["drop_arrival_not_after_departure"]),
                "trip_ids": rule_ids["drop_arrival_not_after_departure"],
            },
            {
                "rule": "dedupe_identical_runtime_kept_one",
                "count": len(rule_ids["dedupe_identical_runtime_kept_one"]),
                "trip_ids": rule_ids["dedupe_identical_runtime_kept_one"],
            },
            {
                "rule": "dedupe_identical_runtime_dropped",
                "count": len(rule_ids["dedupe_identical_runtime_dropped"]),
                "trip_ids": rule_ids["dedupe_identical_runtime_dropped"],
            },
            {
                "rule": "exclude_conflicting_runtime",
                "count": len(rule_ids["exclude_conflicting_runtime"]),
                "trip_ids": rule_ids["exclude_conflicting_runtime"],
            },
        ],
    }
    return trips, summary


def clean_trips(trips: list[TripRow]) -> list[TripRow]:
    return [t for t in trips if t.cleaning_status == "kept" and t.delay_min is not None]


def apply_hour_filter(
    kept: list[TripRow], hour_from: int | None, hour_to: int | None
) -> list[TripRow]:
    """Inclusive hour_from / hour_to on scheduled departure hour. None = open bound."""
    out = []
    for t in kept:
        h = t.dep.hour
        if hour_from is not None and h < hour_from:
            continue
        if hour_to is not None and h > hour_to:
            continue
        out.append(t)
    return out


def trip_delay(
    t: TripRow,
    yardstick: Yardstick,
    schedule: dict[str, dict[str, Any]],
) -> float | None:
    """
    Delay minutes under yardstick.
    export: always export scheduled_runtime_min.
    rec114: export runtime everywhere; revised runtime only for schedule_v2
    routes on/after that route's effective_date. Never drops a trip.
    """
    if t.actual_arrival is None:
        return None
    runtime = t.scheduled_runtime_min
    if yardstick == "rec114":
        info = schedule.get(t.route)
        if info is not None and t.day >= info["effective_date"]:
            runtime = float(info["revised_runtime_min"])
    sa = t.dep + timedelta(minutes=runtime)
    return (t.actual_arrival - sa).total_seconds() / 60.0


def scope_trips(
    kept: list[TripRow],
    yardstick: Yardstick,
    schedule: dict[str, dict[str, Any]],
    hour_from: int | None,
    hour_to: int | None,
) -> list[tuple[TripRow, float]]:
    filtered = apply_hour_filter(kept, hour_from, hour_to)
    out: list[tuple[TripRow, float]] = []
    for t in filtered:
        d = trip_delay(t, yardstick, schedule)
        if d is not None:
            out.append((t, d))
    return out


def route_metrics(
    route_pairs: list[tuple[TripRow, float]],
    late_min: float,
    share_min: float,
    min_late_days: int,
    min_trips: int,
    min_days: int,
) -> dict[str, Any]:
    n = len(route_pairs)
    days = sorted({t.day for t, _ in route_pairs})
    n_days = len(days)
    delays = [d for _, d in route_pairs]
    late_flags = [d > late_min for d in delays]
    share = mean(late_flags) if late_flags else 0.0
    med = median(delays) if delays else None
    p90 = _quantile(delays, 0.90)
    naive_mean = mean(delays) if delays else None

    day_rows = []
    late_day_count = 0
    for d in days:
        day_pairs = [(t, delay) for t, delay in route_pairs if t.day == d]
        day_delays = [delay for _, delay in day_pairs]
        d_share = mean(x > late_min for x in day_delays) if day_delays else 0.0
        is_late_day = d_share >= share_min
        if is_late_day:
            late_day_count += 1
        late_trip_ids = sorted(t.trip_id for t, delay in day_pairs if delay > late_min)
        day_rows.append(
            {
                "day": d.isoformat(),
                "n": len(day_delays),
                "share_late": round(d_share, 4),
                "late_day": is_late_day,
                "median_delay": round(median(day_delays), 2) if day_delays else None,
                "late_trip_ids": late_trip_ids,
            }
        )

    need_ld = required_late_days(n_days, min_late_days)
    if n < min_trips or n_days < min_days:
        verdict = "INSUFFICIENT"
    elif share >= share_min and late_day_count >= need_ld:
        verdict = "LATE"
    else:
        verdict = "ON_TIME"

    return {
        "n": n,
        "n_days": n_days,
        "share_late": round(share, 4),
        "median_delay": round(med, 2) if med is not None else None,
        "p90_delay": round(p90, 2) if p90 is not None else None,
        "naive_mean_delay": round(naive_mean, 2) if naive_mean is not None else None,
        "late_days": late_day_count,
        "required_late_days": need_ld,
        "verdict": verdict,
        "days": day_rows,
    }


def build_verdicts(
    scoped: list[tuple[TripRow, float]],
    late_min: float,
    share_min: float,
    min_late_days: int,
    min_trips: int,
    min_days: int,
) -> list[dict[str, Any]]:
    by_route: dict[str, list[tuple[TripRow, float]]] = defaultdict(list)
    for t, d in scoped:
        by_route[t.route].append((t, d))

    all_days = sorted({t.day for t, _ in scoped})
    verdicts: list[dict[str, Any]] = []

    for route, pairs in by_route.items():
        m = route_metrics(pairs, late_min, share_min, min_late_days, min_trips, min_days)
        fragile = False
        for drop in all_days:
            subset = [(t, d) for t, d in pairs if t.day != drop]
            if not subset:
                continue
            m2 = route_metrics(subset, late_min, share_min, min_late_days, min_trips, min_days)
            if m2["verdict"] != m["verdict"]:
                fragile = True
                break
        verdicts.append({"route": route, **m, "fragile": fragile})

    verdicts.sort(key=lambda v: (-v["share_late"], -(v["median_delay"] or 0), v["route"]))
    for i, v in enumerate(verdicts, 1):
        v["rank"] = i
    return verdicts


def _params(
    trips_path: str | None,
    schedule_path: str | None,
    late_min: float,
    share_min: float,
    min_late_days: int,
    min_trips: int,
    min_days: int,
    hour_from: int | None,
    hour_to: int | None,
    yardstick: Yardstick,
) -> dict[str, Any]:
    return {
        "trips_path": trips_path or DEFAULT_TRIPS,
        "schedule_path": schedule_path or DEFAULT_SCHEDULE,
        "late_min": late_min,
        "share_min": share_min,
        "min_late_days": min_late_days,
        "min_trips": min_trips,
        "min_days": min_days,
        "reference_week_days": REFERENCE_WEEK_DAYS,
        "hour_from": hour_from,
        "hour_to": hour_to,
        "yardstick": yardstick,
    }


@mcp.tool()
def data_quality(trips_path: str | None = None) -> dict[str, Any]:
    """Cleaning rules with counts and trip_ids. No free text."""
    path = trips_path or DEFAULT_TRIPS
    _trips, summary = load_and_clean(path)
    return {"trips_path": path, **summary}


@mcp.tool()
def route_verdicts(
    trips_path: str | None = None,
    schedule_path: str | None = None,
    late_min: float = 5.0,
    share_min: float = 0.30,
    min_late_days: int = 4,
    min_trips: int = 60,
    min_days: int = 5,
    hour_from: int | None = None,
    hour_to: int | None = None,
    yardstick: Yardstick = "export",
) -> dict[str, Any]:
    """Per-route verdict, rank by share_late (tiebreak median_delay), fragile LODO flag."""
    p = _params(
        trips_path, schedule_path, late_min, share_min, min_late_days, min_trips, min_days,
        hour_from, hour_to, yardstick,
    )
    trips, _ = load_and_clean(p["trips_path"])
    kept = clean_trips(trips)
    schedule = load_schedule(p["schedule_path"])
    scoped = scope_trips(kept, yardstick, schedule, hour_from, hour_to)
    verdicts = build_verdicts(scoped, late_min, share_min, min_late_days, min_trips, min_days)
    slim = []
    for v in verdicts:
        slim.append(
            {
                "route": v["route"],
                "verdict": v["verdict"],
                "rank": v["rank"],
                "n": v["n"],
                "share_late": v["share_late"],
                "median_delay": v["median_delay"],
                "p90_delay": v["p90_delay"],
                "late_days": v["late_days"],
                "required_late_days": v["required_late_days"],
                "n_days": v["n_days"],
                "naive_mean_delay": v["naive_mean_delay"],
                "fragile": v["fragile"],
            }
        )
    late_ranked = [v["route"] for v in slim if v["verdict"] == "LATE"]
    return {
        "params": p,
        "n_clean_trips": len(kept),
        "n_scoped_trips": len(scoped),
        "worst_three": late_ranked[:3],
        "routes": slim,
    }


@mcp.tool()
def route_detail(
    route: str,
    trips_path: str | None = None,
    schedule_path: str | None = None,
    late_min: float = 5.0,
    share_min: float = 0.30,
    min_late_days: int = 4,
    min_trips: int = 60,
    min_days: int = 5,
    hour_from: int | None = None,
    hour_to: int | None = None,
    yardstick: Yardstick = "export",
) -> dict[str, Any]:
    """Per-day breakdown, worst trip ids, REC-114 side column when schedule_v2 applies."""
    p = _params(
        trips_path, schedule_path, late_min, share_min, min_late_days, min_trips, min_days,
        hour_from, hour_to, yardstick,
    )
    trips, _ = load_and_clean(p["trips_path"])
    kept = clean_trips(trips)
    schedule = load_schedule(p["schedule_path"])
    scoped = scope_trips(kept, yardstick, schedule, hour_from, hour_to)
    verdicts = build_verdicts(scoped, late_min, share_min, min_late_days, min_trips, min_days)
    v = next((x for x in verdicts if x["route"] == route), None)
    if v is None:
        return {"route": route, "error": "route_not_found", "params": p}

    route_pairs = [(t, d) for t, d in scoped if t.route == route]
    ranked = sorted(route_pairs, key=lambda td: (-td[1], td[0].trip_id))
    worst = [
        {
            "trip_id": t.trip_id,
            "day": t.day.isoformat(),
            "delay_min": round(d, 2),
            "late": d > late_min,
        }
        for t, d in ranked[:15]
    ]

    # Side column: the other yardstick, for routes in schedule_v2, on/after effective_date
    alt: Yardstick = "rec114" if yardstick == "export" else "export"
    rec114_side: dict[str, Any]
    if route in schedule:
        eff = schedule[route]["effective_date"]
        revised = schedule[route]["revised_runtime_min"]
        # side always reports rec114 numbers (export↔rec114 comparison for Priya)
        side_pairs = []
        hour_filtered = apply_hour_filter(kept, hour_from, hour_to)
        for t in hour_filtered:
            if t.route != route or t.day < eff:
                continue
            d = trip_delay(t, "rec114", schedule)
            if d is not None:
                side_pairs.append((t, d))
        if side_pairs:
            by_day: dict[str, list[float]] = defaultdict(list)
            for t, d in side_pairs:
                by_day[t.day.isoformat()].append(d)
            side_days = []
            late_day_count = 0
            for day_s in sorted(by_day):
                dd = by_day[day_s]
                d_share = mean(x > late_min for x in dd)
                is_ld = d_share >= share_min
                if is_ld:
                    late_day_count += 1
                side_days.append(
                    {
                        "day": day_s,
                        "n": len(dd),
                        "share_late": round(d_share, 4),
                        "late_day": is_ld,
                        "median_delay": round(median(dd), 2),
                    }
                )
            delays = [d for _, d in side_pairs]
            n_days = len(by_day)
            rec114_side = {
                "applies": True,
                "revised_runtime_min": revised,
                "effective_date": eff.isoformat(),
                "n": len(side_pairs),
                "n_before_effective_excluded": sum(
                    1 for t in hour_filtered if t.route == route and t.day < eff
                ),
                "share_late": round(mean(d > late_min for d in delays), 4),
                "median_delay": round(median(delays), 2),
                "p90_delay": round(_quantile(delays, 0.90) or 0.0, 2),
                "late_days": late_day_count,
                "required_late_days": required_late_days(n_days, min_late_days),
                "n_days": n_days,
                "days": side_days,
            }
        else:
            rec114_side = {
                "applies": True,
                "revised_runtime_min": revised,
                "effective_date": eff.isoformat(),
                "n": 0,
                "n_before_effective_excluded": sum(
                    1 for t in hour_filtered if t.route == route
                ),
            }
    else:
        rec114_side = {"applies": False}

    return {
        "params": p,
        "route": route,
        "verdict": v["verdict"],
        "rank": v["rank"],
        "fragile": v["fragile"],
        "n": v["n"],
        "share_late": v["share_late"],
        "median_delay": v["median_delay"],
        "p90_delay": v["p90_delay"],
        "naive_mean_delay": v["naive_mean_delay"],
        "late_days": v["late_days"],
        "required_late_days": v["required_late_days"],
        "n_days": v["n_days"],
        "days": v["days"],
        "worst_trips": worst,
        "rec114_side": rec114_side,
        "alt_yardstick": alt,
    }


@mcp.tool()
def trip(
    trip_id: str,
    trips_path: str | None = None,
    schedule_path: str | None = None,
    late_min: float = 5.0,
) -> dict[str, Any]:
    """Raw row fields, computed delay, cleaning status. Ids and numbers only."""
    path = trips_path or DEFAULT_TRIPS
    sched_path = schedule_path or DEFAULT_SCHEDULE
    trips, _ = load_and_clean(path)
    schedule = load_schedule(sched_path)
    t = next((x for x in trips if x.trip_id == trip_id), None)
    if t is None:
        return {"trip_id": trip_id, "error": "trip_not_found"}

    out: dict[str, Any] = {
        "trip_id": t.trip_id,
        "route": t.route,
        "vehicle_series": t.vehicle_series,
        "scheduled_departure": t.scheduled_departure,
        "scheduled_runtime_min": t.scheduled_runtime_min,
        "actual_arrival_raw": t.actual_arrival_raw,
        "actual_arrival": t.actual_arrival.strftime("%Y-%m-%d %H:%M") if t.actual_arrival else None,
        "tz_offset_raw": t.tz_offset_raw,
        "tz_offset": t.tz_offset,
        "tz_action": t.tz_action,
        "cleaning_status": t.cleaning_status,
        "delay_min": round(t.delay_min, 2) if t.delay_min is not None else None,
        "late": (t.delay_min is not None and t.delay_min > late_min),
        "late_min": late_min,
    }

    if t.route in schedule and t.cleaning_status == "kept" and t.actual_arrival is not None:
        eff = schedule[t.route]["effective_date"]
        revised = schedule[t.route]["revised_runtime_min"]
        if t.day >= eff:
            d114 = trip_delay(t, "rec114", schedule)
            out["rec114_side"] = {
                "applies": True,
                "effective_date": eff.isoformat(),
                "revised_runtime_min": revised,
                "delay_min": round(d114, 2) if d114 is not None else None,
                "late": (d114 is not None and d114 > late_min),
            }
        else:
            out["rec114_side"] = {
                "applies": False,
                "reason": "before_effective_date",
                "effective_date": eff.isoformat(),
            }
    else:
        out["rec114_side"] = {"applies": False}
    return out


if __name__ == "__main__":
    mcp.run(transport="stdio")
