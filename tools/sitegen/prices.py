"""Price data from the shared prices.json: parsing and everything the pages say about prices."""

import math
import re
from dataclasses import dataclass
from statistics import median
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


def percent(old: float, new: float) -> str:
    """'+11%': the change, rounded to a whole percent."""
    p = round((new - old) / old * 100)
    return ("+" if p >= 0 else MINUS) + f"{abs(p)}%"


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


def title_news(changes: list[Change], plan: str, frequency: str, today: date, year: str) -> str | None:
    """The headline plan's price news for the page title, the words people search for: an
    upcoming increase, or one in effect for less than RECENT. Decreases and older increases
    leave the title as it is. "price increase" comes early, before Google cuts long titles.
    `year` is the title's own year, not repeated after the month."""
    past, upcoming = _split(_series(changes, plan, frequency), today)
    if upcoming:
        c = upcoming[0]
        return f"price increase to {money(c.new)}{per(frequency)} {_on(c)}" if _kind(c) == "up" else None
    if past and past[-1].effective > today - RECENT and _kind(past[-1]) == "up":
        c = past[-1]
        month = MONTHS[c.effective.month - 1] + ("" if str(c.effective.year) == year else f" {c.effective.year}")
        return f"{month} price increase to {money(c.new)}{per(frequency)}"
    return None


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
    bars += [Bar(_mon_year(c.effective), c.new, money(c.new), c.effective > today) for c in series]
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
                 f"({signed(c.new - c.old)}, {percent(c.old, c.new)})" for c in cs]
        approx = next((c for c in cs if c.approx_month), cs[0])
        sources = list(dict.fromkeys(c.source for c in cs if c.source))
        rows.append(Row(service_id=sid, effective=effective, when=_when(approx), lines=lines, sources=sources))
    upcoming = sorted((r for r in rows if r.effective > today), key=lambda r: (r.effective, r.service_id))
    past = sorted((r for r in rows if r.effective <= today), key=lambda r: (r.effective, r.service_id), reverse=True)
    return upcoming, past


@dataclass(frozen=True)
class Summary:
    """A year's US price increases that are already in effect."""
    year: int
    increases: int  # one per service and date, however many plans it moved
    services: list[str]  # in the order they first went up that year
    first_months: list[tuple[str, int]]  # (service, month of its first increase that year), in that order
    typical: float  # median monthly-plan increase, in dollars
    typical_percent: str  # median monthly-plan increase, "+13%"
    biggest: Change | None  # the largest monthly-plan increase in dollars


def _first_months(ups: list[Change]) -> list[tuple[str, int]]:
    first: dict[str, int] = {}
    for c in ups:  # in date order
        first.setdefault(c.service_id, c.effective.month)
    return list(first.items())


def year_summary(us: list[Change], year: int, today: date) -> Summary:
    ups = sorted((c for c in us if c.new > c.old and c.effective.year == year and c.effective <= today),
                 key=lambda c: (c.effective, c.service_id))
    monthly = [c for c in ups if c.frequency == "monthly"]
    ratios = [(c.new - c.old) / c.old for c in monthly]
    return Summary(year=year, increases=len({(c.service_id, c.effective) for c in ups}),
                   services=list(dict.fromkeys(c.service_id for c in ups)),
                   first_months=_first_months(ups),
                   typical=round(median(c.new - c.old for c in monthly), 2) if monthly else 0.0,
                   typical_percent=percent(1, 1 + median(ratios)) if ratios else "",
                   biggest=max(monthly, key=lambda c: (c.new - c.old, c.effective)) if monthly else None)


@dataclass(frozen=True)
class Glance:
    """One service's line in the at-a-glance table."""
    service_id: str
    plan: str
    frequency: str
    now: float
    last: Change | None  # that plan's latest change in effect (a cut too: Xbox went down)


def glance_rows(us: list[Change], headlines: dict[str, tuple[str, str]], today: date) -> list[Glance]:
    """A line per service: its headline plan (else the plan of its latest monthly increase, the
    cheapest on that date, else of its latest change), the price today and its last change;
    latest change first."""
    rows = []
    for sid in dict.fromkeys(c.service_id for c in us):
        cs = [c for c in us if c.service_id == sid]
        if sid in headlines:
            plan, frequency = headlines[sid]
        else:
            pick = max((c for c in cs if c.new > c.old and c.frequency == "monthly"),
                       key=lambda c: (c.effective, -c.new), default=None) or max(cs, key=lambda c: c.effective)
            plan, frequency = pick.plan, pick.frequency
        series = _series(cs, plan, frequency)
        if not series:
            continue
        past = _split(series, today)[0]
        rows.append(Glance(sid, plan, frequency, _current(series, today), past[-1] if past else None))
    return sorted(rows, key=lambda r: (r.last.effective if r.last else date.min, r.service_id), reverse=True)


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
