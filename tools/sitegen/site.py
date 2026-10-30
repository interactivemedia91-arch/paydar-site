"""Writes the whole site into an output directory and reports what needs attention."""

import re
import shutil
from datetime import date, datetime
from pathlib import Path

from .content import Catalog, Service, SiteConfig
from .prices import Change, parse_changes, us_changes
from .render import home_page, increases_page, privacy_page, service_page

STALE_AFTER_MONTHS = 6


class BuildError(Exception):
    """Something that would publish wrong or missing prices; the run must fail."""


def _months_old(checked: str, today: date) -> int:
    year, month = (int(x) for x in checked.split("-"))
    return (today.year * 12 + today.month) - (year * 12 + month)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _us_all(changes: list[Change], services: list[Service]) -> list[Change]:
    """Every US change, with a service's plan aliases applied when it has a content file."""
    by_id = {s.service_id: s for s in services}
    out = []
    for sid in dict.fromkeys(c.service_id for c in changes if c.country == "US"):
        aliases = by_id[sid].plan_aliases if sid in by_id else {}
        out += us_changes(changes, sid, aliases)
    return out


def _policy_date(privacy_md: str | None, today: date) -> date:
    """The policy's own "Last updated: 25 October 2026" line, so the sitemap doesn't claim a daily change."""
    m = re.search(r"Last updated: (\d{1,2}) (\w+) (\d{4})", privacy_md or "")
    if not m:
        return today
    try:
        return datetime.strptime(" ".join(m.groups()), "%d %B %Y").date()
    except ValueError:
        return today


def _sitemap(site: SiteConfig, services: list[Service], today: date, privacy_md: str | None = None) -> str:
    entries = [("/", today.isoformat()), ("/price-increases/", today.isoformat())]
    if privacy_md is not None:
        entries.append(("/privacy/", _policy_date(privacy_md, today).isoformat()))
    entries += [(f"/cancel/{s.slug}/", f"{s.checked}-01") for s in services]
    urls = "".join(f"  <url><loc>{site.base_url}{path}</loc><lastmod>{lastmod}</lastmod></url>\n"
                   for path, lastmod in entries)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")


def build_site(out: Path, site: SiteConfig, services: list[Service], prices: dict, today: date,
               static_dir: Path, catalog: Catalog | None = None, privacy_md: str | None = None) -> list[str]:
    changes = parse_changes(prices)
    if not any(c.country == "US" for c in changes):
        raise BuildError("prices.json has no usable US changes")
    warnings, errors = [], []
    if not site.provider_token:
        warnings.append("NO PROVIDER TOKEN: App Store links carry no campaign")

    for s in services:
        us = us_changes(changes, s.service_id, s.plan_aliases)
        if _months_old(s.checked, today) > STALE_AFTER_MONTHS:
            warnings.append(f"STALE {s.slug}: checked {s.checked}")
        if s.headline_plan is not None and not any(
                c.plan == s.headline_plan and c.frequency == s.headline_frequency for c in us):
            errors.append(f"HEADLINE NOT FOUND {s.slug}: {s.headline_plan} {s.headline_frequency}")
            continue
        try:
            brand = catalog.get(s.service_id) if catalog else None
            _write(out / "cancel" / s.slug / "index.html", service_page(site, s, us, today, brand))
        except ValueError as e:  # an FAQ price placeholder with no data behind it
            errors.append(f"PRICE NOT FOUND {s.slug}: {e}")
    if errors:
        raise BuildError("\n".join(errors))

    known = {s.service_id for s in services}
    for sid in sorted({c.service_id for c in changes if c.country == "US"} - known):
        warnings.append(f"NO PAGE for US service {sid}")

    us_all = _us_all(changes, services)
    _write(out / "price-increases" / "index.html", increases_page(site, services, us_all, today))
    _write(out / "index.html", home_page(site, services, catalog, us_all, today))
    if privacy_md is not None:
        _write(out / "privacy" / "index.html", privacy_page(site, privacy_md))
    elif site.privacy_url.startswith("/"):
        raise BuildError(f"privacyUrl is {site.privacy_url} but content/privacy.md is missing")
    _write(out / "sitemap.xml", _sitemap(site, services, today, privacy_md))
    _write(out / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {site.base_url}/sitemap.xml\n")
    private = ("*.json", ".DS_Store")  # provenance sidecars and Finder files are not for the site
    for f in static_dir.iterdir():
        if f.is_file() and not any(f.match(p) for p in private):
            shutil.copy2(f, out / f.name)
        elif f.is_dir():
            shutil.copytree(f, out / f.name, dirs_exist_ok=True, ignore=shutil.ignore_patterns(*private))
    return warnings
