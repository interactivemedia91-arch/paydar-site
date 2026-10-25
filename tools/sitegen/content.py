"""Site config and the per-service content files (content/services/<serviceId>.json)."""

import json
import re
from dataclasses import dataclass
from pathlib import Path

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
CHECKED_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


class ContentError(Exception):
    """Every problem found, one per line."""


@dataclass(frozen=True)
class SiteConfig:
    base_url: str
    app_id: str
    provider_token: str
    privacy_url: str
    support_email: str
    prices_url: str


@dataclass(frozen=True)
class Service:
    service_id: str
    name: str
    slug: str
    checked: str  # "YYYY-MM"
    fastest_text: str
    fastest_url: str | None
    steps: tuple[str, ...]
    apple_billed: bool
    note: str | None
    faq: tuple[tuple[str, str], ...]
    cancel_sources: tuple[tuple[str, str], ...]  # (label, url)
    headline_plan: str | None
    headline_frequency: str
    plan_aliases: dict[str, str]


def load_site(path: Path) -> SiteConfig:
    d = json.loads(path.read_text(encoding="utf-8"))
    return SiteConfig(base_url=d["baseUrl"].rstrip("/"), app_id=d["appId"], provider_token=d.get("providerToken", ""),
                      privacy_url=d["privacyUrl"], support_email=d["supportEmail"], prices_url=d["pricesUrl"])


def _text(v) -> bool:
    return isinstance(v, str) and v.strip() != ""


def _check(d: dict, stem: str) -> list[str]:
    p = []
    if d.get("serviceId") != stem:
        p.append(f"serviceId must be '{stem}' (the file name)")
    for key in ("name", "slug", "checked"):
        if not _text(d.get(key)):
            p.append(f"{key} is missing")
    if _text(d.get("slug")) and not SLUG_RE.match(d["slug"]):
        p.append(f"slug '{d['slug']}' must be lowercase words joined by '-'")
    if _text(d.get("checked")) and not CHECKED_RE.match(d["checked"]):
        p.append("checked must be YYYY-MM")

    fastest = d.get("fastest")
    if not isinstance(fastest, dict) or not _text(fastest.get("text")):
        p.append("fastest.text is missing")
    elif "url" in fastest and not (_text(fastest["url"]) and fastest["url"].startswith("https://")):
        p.append("fastest.url must start with https://")

    steps = d.get("steps")
    if not (isinstance(steps, list) and 3 <= len(steps) <= 8 and all(_text(s) for s in steps)):
        p.append("steps must be 3–8 non-empty strings")
    if not isinstance(d.get("appleBilled"), bool):
        p.append("appleBilled must be true or false")
    if "note" in d and not _text(d["note"]):
        p.append("note must be a non-empty string when present")

    faq = d.get("faq")
    if not (isinstance(faq, list) and 3 <= len(faq) <= 4
            and all(isinstance(f, dict) and _text(f.get("q")) and _text(f.get("a")) for f in faq)):
        p.append("faq must be 3–4 items with q and a")

    sources = d.get("cancelSources")
    if not (isinstance(sources, list) and sources):
        p.append("cancelSources needs at least one entry")
    else:
        for i, s in enumerate(sources):
            if not (isinstance(s, dict) and _text(s.get("label"))):
                p.append(f"cancelSources[{i}].label is missing")
            if not (isinstance(s, dict) and _text(s.get("url")) and s["url"].startswith("https://")):
                p.append(f"cancelSources[{i}].url must start with https://")

    headline = d.get("headline")
    if headline is not None:
        if not (isinstance(headline, dict) and isinstance(headline.get("plan"), str)):
            p.append("headline.plan must be a string (\"\" for prices without a plan)")
        if not isinstance(headline, dict) or headline.get("frequency") not in ("monthly", "annual"):
            p.append("headline.frequency must be monthly or annual")
    aliases = d.get("planAliases", {})
    if not (isinstance(aliases, dict) and all(isinstance(k, str) and isinstance(v, str) for k, v in aliases.items())):
        p.append("planAliases must map plan names to plan names")
    return p


def _service(d: dict) -> Service:
    headline = d.get("headline")
    return Service(
        service_id=d["serviceId"], name=d["name"], slug=d["slug"], checked=d["checked"],
        fastest_text=d["fastest"]["text"], fastest_url=d["fastest"].get("url"),
        steps=tuple(d["steps"]), apple_billed=d["appleBilled"], note=d.get("note"),
        faq=tuple((f["q"], f["a"]) for f in d["faq"]),
        cancel_sources=tuple((s["label"], s["url"]) for s in d["cancelSources"]),
        headline_plan=headline["plan"] if headline else None,
        headline_frequency=headline["frequency"] if headline else "monthly",
        plan_aliases=dict(d.get("planAliases", {})),
    )


def load_services(directory: Path) -> list[Service]:
    problems, services, slugs = [], [], {}
    for path in sorted(directory.glob("*.json")):
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            problems.append(f"{path.name}: invalid JSON ({e})")
            continue
        if not isinstance(d, dict):
            problems.append(f"{path.name}: must be a JSON object")
            continue
        found = _check(d, path.stem)
        problems += [f"{path.name}: {x}" for x in found]
        if found:
            continue
        if d["slug"] in slugs:
            problems.append(f"{path.name}: duplicate slug '{d['slug']}' (also in {slugs[d['slug']]})")
            continue
        slugs[d["slug"]] = path.name
        services.append(_service(d))
    if problems:
        raise ContentError("\n".join(problems))
    return sorted(services, key=lambda s: s.name.lower())
