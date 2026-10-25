"""Price data from the shared prices.json: parsing and everything the pages say about prices."""

import math
import re
from dataclasses import dataclass
from datetime import date, timedelta

# Fixed English names: strftime would follow the machine's locale.
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

FREQUENCIES = ("monthly", "annual")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RECENT = timedelta(days=365)
MINUS = "−"


@dataclass(frozen=True)
class Change:
    id: str
    service_id: str
    plan: str  # "" when prices.json has no plan
    country: str
    currency: str
    frequency: str  # "monthly" | "annual"
    old: float
    new: float
    effective: date
    approx_month: bool  # only the month of `effective` is known
    source: str


@dataclass(frozen=True)
class Tag:
    kind: str  # "up" | "down" | "flat"
    text: str


@dataclass(frozen=True)
class Card:
    label: str
    price: str
    yearly: str | None
    badge: str | None
    badge_kind: str


@dataclass(frozen=True)
class Bar:
    label: str
    value: float
    text: str
    upcoming: bool


@dataclass(frozen=True)
class Row:
    service_id: str
    effective: date
    when: str
    lines: list[str]
    sources: list[str]


def _is_price(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and v >= 0


def parse_changes(data: dict) -> list[Change]:
    """Same acceptance rule as the app's parsePriceChanges: malformed entries are skipped."""
    raw = data.get("changes") if isinstance(data, dict) else None
    if not isinstance(raw, list):
        raise ValueError("prices.json has no 'changes' list")
    out = []
    for c in raw:
        if not isinstance(c, dict):
            continue
        if not (isinstance(c.get("id"), str) and isinstance(c.get("serviceId"), str)
                and isinstance(c.get("country"), str) and isinstance(c.get("currency"), str)
                and c.get("frequency") in FREQUENCIES and _is_price(c.get("from")) and _is_price(c.get("to"))
                and isinstance(c.get("effective"), str) and DATE_RE.match(c["effective"])):
            continue
        try:
            effective = date.fromisoformat(c["effective"])
        except ValueError:
            continue
        out.append(Change(
            id=c["id"], service_id=c["serviceId"],
            plan=c["plan"] if isinstance(c.get("plan"), str) else "",
            country=c["country"], currency=c["currency"], frequency=c["frequency"],
            old=float(c["from"]), new=float(c["to"]), effective=effective,
            approx_month=c.get("dateApprox") == "month",
            source=c["source"] if isinstance(c.get("source"), str) else "",
        ))
    return out


def us_changes(changes: list[Change], service_id: str, aliases: dict[str, str]) -> list[Change]:
    """US changes of one service, renamed plans joined through `aliases`, oldest first."""
    out = [c for c in changes if c.country == "US" and c.service_id == service_id]
    out = [Change(**{**c.__dict__, "plan": aliases.get(c.plan, c.plan)}) for c in out]
    return sorted(out, key=lambda c: c.effective)


def money(x: float) -> str:
    x = round(x, 2)
    return f"${int(x)}" if x == int(x) else f"${x:.2f}"


def signed(x: float) -> str:
    x = round(x, 2)
    return ("+" if x >= 0 else MINUS) + money(abs(x))


def per(frequency: str) -> str:
    return "/mo" if frequency == "monthly" else "/yr"


def _mon_year(d: date) -> str:
    return f"{MONTHS[d.month - 1][:3]} {d.year}"


def _on(c: Change) -> str:
    """'on Nov 12', or 'in November 2026' when only the month is known."""
    if c.approx_month:
        return f"in {MONTHS[c.effective.month - 1]} {c.effective.year}"
    return f"on {MONTHS[c.effective.month - 1][:3]} {c.effective.day}"


def _when(c: Change) -> str:
    """'Nov 12, 2026', or 'November 2026' when only the month is known."""
    if c.approx_month:
        return f"{MONTHS[c.effective.month - 1]} {c.effective.year}"
    return f"{MONTHS[c.effective.month - 1][:3]} {c.effective.day}, {c.effective.year}"


def _kind(c: Change) -> str:
    return "down" if c.new < c.old else "up"


def _series(changes: list[Change], plan: str, frequency: str) -> list[Change]:
    return sorted((c for c in changes if c.plan == plan and c.frequency == frequency), key=lambda c: c.effective)


def _split(series: list[Change], today: date) -> tuple[list[Change], list[Change]]:
    """(in effect, upcoming); a change is in effect from its effective date on."""
    return [c for c in series if c.effective <= today], [c for c in series if c.effective > today]


def _current(series: list[Change], today: date) -> float:
    past, upcoming = _split(series, today)
    return past[-1].new if past else upcoming[0].old


def price_tag(changes: list[Change], plan: str, frequency: str, label: str, today: date) -> Tag | None:
    series = _series(changes, plan, frequency)
    if not series:
        return None
    past, upcoming = _split(series, today)
    if upcoming:
        c = upcoming[0]
        verb = "Drops to" if _kind(c) == "down" else "Goes up to"
        return Tag(_kind(c), f"{verb} {money(c.new)}{per(frequency)} {_on(c)}")
    last = past[-1]
    name = plan or label
    if last.effective > today - RECENT:
        return Tag(_kind(last), f"{name} is now {money(last.new)}{per(frequency)} · "
                                f"{signed(last.new - last.old)} since {MONTHS[last.effective.month - 1]} {last.effective.year}")
    return Tag("flat", f"{name}: {money(last.new)}{per(frequency)}")


def plan_cards(changes: list[Change], service_name: str, today: date) -> list[Card]:
    """One card per plan, cheapest first."""
    plans = list(dict.fromkeys(c.plan for c in changes))
    cards = []
    for plan in plans:
        freqs = {c.frequency for c in changes if c.plan == plan}
        main = "monthly" if "monthly" in freqs else "annual"
        series = _series(changes, plan, main)
        yearly = None
        if main == "monthly" and "annual" in freqs:
            annual = _series(changes, plan, "annual")
            # A yearly price older than the monthly one is probably out of date: leave it out.
            if annual[-1].effective >= series[-1].effective:
                yearly = f"or {money(_current(annual, today))}/yr"
        past, upcoming = _split(series, today)
        if upcoming:
            c = upcoming[0]
            badge, badge_kind = f"→ {money(c.new)} {_on(c)}", _kind(c)
        else:
            c = past[-1]
            badge, badge_kind = f"{signed(c.new - c.old)} · {_mon_year(c.effective)}", _kind(c)
        current = _current(series, today)
        monthly_equivalent = current if main == "monthly" else current / 12
        cards.append((monthly_equivalent, Card(label=plan or service_name, price=money(current) + per(main),
                                               yearly=yearly, badge=badge, badge_kind=badge_kind)))
    return [card for _, card in sorted(cards, key=lambda pair: pair[0])]


def chart_bars(changes: list[Change], plan: str, frequency: str, today: date) -> list[Bar]:
    series = _series(changes, plan, frequency)
    if not series:
        return []
    first = series[0]
    bars = [Bar(f"Before {_mon_year(first.effective)}", first.old, money(first.old), False)]
    bars += [Bar(_mon_year(c.effective) + (" (coming)" if c.effective > today else ""), c.new, money(c.new),
                 c.effective > today) for c in series]
    return bars


def increase_rows(us: list[Change], names: dict[str, str], today: date) -> tuple[list[Row], list[Row]]:
    """(upcoming, past) increases, one row per service and date; decreases are left out."""
    groups: dict[tuple[str, date], list[Change]] = {}
    for c in sorted(us, key=lambda c: (c.effective, c.service_id)):
        if c.new > c.old:
            groups.setdefault((c.service_id, c.effective), []).append(c)
    rows = []
    for (sid, effective), cs in groups.items():
        lines = [f"{c.plan or names.get(sid, sid)} {money(c.old)} → {money(c.new)}{per(c.frequency)} "
                 f"({signed(c.new - c.old)})" for c in cs]
        approx = next((c for c in cs if c.approx_month), cs[0])
        sources = list(dict.fromkeys(c.source for c in cs if c.source))
        rows.append(Row(service_id=sid, effective=effective, when=_when(approx), lines=lines, sources=sources))
    upcoming = sorted((r for r in rows if r.effective > today), key=lambda r: (r.effective, r.service_id))
    past = sorted((r for r in rows if r.effective <= today), key=lambda r: (r.effective, r.service_id), reverse=True)
    return upcoming, past


PRICE_TOKEN = re.compile(r"\{(price|monthly|yearly):([^}]*)\}")


def fill_prices(text: str, changes: list[Change], today: date) -> str:
    """Replaces {price:Plan}, {monthly:Plan} and {yearly:Plan} with that plan's current price
    ("$8.99/mo"); {price:...} picks monthly when the plan has it. Plan "" means no plan name.
    Raises ValueError when the plan or frequency has no data, so a stale FAQ fails the build."""
    def sub(m: re.Match) -> str:
        kind, plan = m.group(1), m.group(2)
        freqs = {c.frequency for c in changes if c.plan == plan}
        frequency = {"monthly": "monthly", "yearly": "annual"}.get(kind) or (
            "monthly" if "monthly" in freqs else "annual")
        series = _series(changes, plan, frequency)
        if not series:
            raise ValueError(f"no {frequency} US price for plan '{plan}' in {m.group(0)}")
        return money(_current(series, today)) + per(frequency)
    return PRICE_TOKEN.sub(sub, text)
