"""Writes the whole site into an output directory and reports what needs attention."""

import shutil
from datetime import date
from pathlib import Path

from .content import Service, SiteConfig
from .prices import Change, parse_changes, us_changes
from .render import home_page, increases_page, service_page

STALE_AFTER_MONTHS = 6


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


def _sitemap(site: SiteConfig, services: list[Service], today: date) -> str:
    entries = [("/", today.isoformat()), ("/price-increases/", today.isoformat())]
    entries += [(f"/cancel/{s.slug}/", f"{s.checked}-01") for s in services]
    urls = "".join(f"  <url><loc>{site.base_url}{path}</loc><lastmod>{lastmod}</lastmod></url>\n"
                   for path, lastmod in entries)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")


def build_site(out: Path, site: SiteConfig, services: list[Service], prices: dict, today: date,
               static_dir: Path) -> list[str]:
    changes = parse_changes(prices)
    warnings = []
    if not site.provider_token:
        warnings.append("NO PROVIDER TOKEN: App Store links carry no campaign")

    for s in services:
        us = us_changes(changes, s.service_id, s.plan_aliases)
        if _months_old(s.checked, today) > STALE_AFTER_MONTHS:
            warnings.append(f"STALE {s.slug}: checked {s.checked}")
        if s.headline_plan is not None and not any(
                c.plan == s.headline_plan and c.frequency == s.headline_frequency for c in us):
            warnings.append(f"HEADLINE NOT FOUND {s.slug}: {s.headline_plan} {s.headline_frequency}")
        _write(out / "cancel" / s.slug / "index.html", service_page(site, s, us, today))

    known = {s.service_id for s in services}
    for sid in sorted({c.service_id for c in changes if c.country == "US"} - known):
        warnings.append(f"NO PAGE for US service {sid}")

    _write(out / "price-increases" / "index.html", increases_page(site, services, _us_all(changes, services), today))
    _write(out / "index.html", home_page(site, services))
    _write(out / "sitemap.xml", _sitemap(site, services, today))
    _write(out / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {site.base_url}/sitemap.xml\n")
    for f in static_dir.iterdir():
        if f.is_file():
            shutil.copy2(f, out / f.name)
    return warnings
