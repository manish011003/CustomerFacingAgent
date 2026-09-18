"""Look-only departures for booking assist.

Scheduled rows come from the upcoming catalog. If nothing matches the request,
a random demo flight is generated. Neither path tickets anything.
"""

from __future__ import annotations

import random
import re
from typing import Any

from data.loader import load_scheduled_flights
from models.schemas import SuggestedFlight

CITIES = (
    "Delhi",
    "Mumbai",
    "Bengaluru",
    "Goa",
    "Hyderabad",
    "Chennai",
    "Kolkata",
    "Pune",
    "Kochi",
    "Jaipur",
)
CARRIERS = ("SK", "AI", "6E", "UK")
TIMES = ("06:15", "07:40", "08:40", "10:05", "12:20", "14:55", "16:40", "19:10", "21:25")
GATES = ("A04", "A12", "B03", "B12", "C07", "C11", "D02", "D14")
STATUSES = ("SCHEDULED", "ON TIME", "GATE OPEN", "BOARDING")


def _norm(value: str | None) -> str:
    return re.sub(r"[^a-z]+", "", (value or "").lower())


def _href(flight: str, origin: str, destination: str) -> str:
    from urllib.parse import urlencode

    return "/exit?" + urlencode({"flight": flight, "from": origin, "to": destination})


def _as_suggested(row: dict[str, Any], *, source: str, passengers: str | None = None) -> SuggestedFlight:
    origin = str(row.get("origin") or "Delhi")
    destination = str(row.get("destination") or "Goa")
    code = str(row.get("flight") or "SK-000")
    return SuggestedFlight(
        flight=code,
        origin=origin,
        destination=destination,
        date=str(row.get("date") or ""),
        date_label=str(row.get("date_label") or row.get("date") or ""),
        scheduled_departure=str(row.get("scheduled_departure") or "00:00"),
        scheduled_arrival=row.get("scheduled_arrival"),
        gate=row.get("gate"),
        status=str(row.get("status") or "SCHEDULED"),
        aircraft=row.get("aircraft"),
        source=source,  # type: ignore[arg-type]
        passengers=passengers,
        href=_href(code, origin, destination),
    )


def scheduled_flights() -> list[dict[str, Any]]:
    payload = load_scheduled_flights()
    rows = payload.get("flights") if isinstance(payload, dict) else payload
    return [row for row in (rows or []) if isinstance(row, dict)]


def upcoming_flights() -> list[SuggestedFlight]:
    rows = scheduled_flights()
    if rows:
        return [_as_suggested(row, source="scheduled") for row in rows]
    rng = random.Random(2026)
    return [_random_flight(rng=rng) for _ in range(8)]


def _date_matches(row: dict[str, Any], date: str | None) -> bool:
    if not date:
        return True
    blob = f"{row.get('date') or ''} {row.get('date_label') or ''}".lower()
    needle = date.strip().lower()
    return needle in blob or bool(re.search(r"\d{4}-\d{2}-\d{2}", date) and date[:10] in blob)


def _random_flight(
    *,
    origin: str | None = None,
    destination: str | None = None,
    date: str | None = None,
    passengers: str | None = None,
    rng: random.Random | None = None,
) -> SuggestedFlight:
    rng = rng or random.Random()
    start = origin or rng.choice(CITIES)
    rest = [city for city in CITIES if _norm(city) != _norm(start)]
    end = destination or rng.choice(rest)
    if _norm(start) == _norm(end):
        end = rest[0]
    code = f"{rng.choice(CARRIERS)}-{rng.randint(110, 989)}"
    depart = rng.choice(TIMES)
    hour, minute = (int(part) for part in depart.split(":"))
    arrive_hour = (hour + 2) % 24
    arrival = f"{arrive_hour:02d}:{minute:02d}"
    return SuggestedFlight(
        flight=code,
        origin=start.title() if start.islower() else start,
        destination=end.title() if end.islower() else end,
        date=date or "",
        date_label=date or "Open date",
        scheduled_departure=depart,
        scheduled_arrival=arrival,
        gate=rng.choice(GATES),
        status=rng.choice(STATUSES),
        aircraft="A320",
        source="random",
        passengers=passengers,
        href=_href(code, start, end),
    )


def suggest_flight(
    *,
    origin: str | None = None,
    destination: str | None = None,
    date: str | None = None,
    passengers: str | None = None,
) -> SuggestedFlight | None:
    """Look-only match after the passenger named a route. No guesswork before that."""
    if not origin or not destination:
        return None
    catalog = scheduled_flights()
    matches = [
        row
        for row in catalog
        if _norm(str(row.get("origin"))) == _norm(origin)
        and _norm(str(row.get("destination"))) == _norm(destination)
    ]
    dated = [row for row in matches if _date_matches(row, date)]
    chosen = dated or matches
    if chosen:
        return _as_suggested(chosen[0], source="scheduled", passengers=passengers)
    return _random_flight(origin=origin, destination=destination, date=date, passengers=passengers)
