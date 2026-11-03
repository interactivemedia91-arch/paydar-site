"""HTML for the page types. Everything user-visible goes through esc()."""

import json
import math
import re
import zlib
from datetime import date
from html import escape
from urllib.parse import quote, urlparse

from .aura import field_style
from .content import Brand, Catalog, Service, SiteConfig
from .prices import (
    MONTHS, Change, PlanPrice, chart_bars, fill_prices, glance_rows, increase_rows, per, percent, plan_cards, plan_prices,
    price_tag, signed, title_news, year_summary,
)
from .prices import money as pmoney
from .radar import aura_radius, place

APPLE_NOTE = ("<strong>Paying through Apple?</strong> Then Apple bills you. "
              "Cancel in Settings → your name → Subscriptions instead.")
CARD_TEXT = "Paydar puts every subscription on one radar and pings you before each charge. No bank login."
CHART_LINK = "Paydar flags increases like this before they hit your card"
CTA_LABEL = "Get Paydar free on iPhone"
FACTS = "Free for 4 subscriptions · $9.99 once for unlimited · No bank login"
LAVENDER = "#7A5AF8"
BAR_MAX_PX = 140
DESCRIPTION = ("See every subscription charge 3 days before it hits. Paydar puts your renewals on one radar. "
               "No bank login, no account. Free for 4, $9.99 once for unlimited.")

ICON_UP = ('<svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M3 11 11 3M4 3h7v7" '
           'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')
ICON_DOWN = ('<svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M3 5l8 8M11 6v7H4" '
             'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')
ICON_OUT = ('<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M6 18 18 6M7 6h11v11" '
            'stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>')
ICON_NEXT = ('<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M4 12h15m-6-6 6 6-6 6" '
             'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>')
# The app icon's receipt radar as a line mark (the app's ReceiptRadar, same 24-unit geometry):
# torn paper half-disc, sweep, blip, Today point. The faint ring and wedge (.mark-detail) are
# hidden at small sizes, as in the app below 20 pt.
RADAR_MARK = ('<svg class="mark" viewBox="0 0 24 24" fill="none" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
              '<path class="mark-detail" d="M12 14.95 12 4.55A10.4 10.4 0 0 1 18.11 6.54Z" style="fill:var(--accent)" fill-opacity=".28"/>'
              '<path class="mark-detail" d="M6.28 14.95A5.72 5.72 0 0 1 17.72 14.95" stroke="currentColor" stroke-opacity=".3" stroke-width="1.3"/>'
              '<path d="M1.6 14.95A10.4 10.4 0 0 1 22.4 14.95V18.05L20.32 19.45 18.24 18.05 16.16 19.45 14.08 18.05 12 19.45 '
              '9.92 18.05 7.84 19.45 5.76 18.05 3.68 19.45 1.6 18.05Z" stroke="currentColor" stroke-width="1.9"/>'
              '<path d="M12 14.95 18.11 6.54" style="stroke:var(--accent)" stroke-width="1.9"/>'
              '<circle cx="8.21" cy="9.73" r="1.9" style="fill:var(--rise)"/><circle cx="12" cy="14.95" r="1.5" style="fill:var(--accent)"/></svg>')

# Homepage guide groups, by the app catalog's category.
GUIDE_GROUPS = (("Streaming", ("streaming",)), ("Music", ("music",)),
                ("Apps and storage", ("software", "productivity", "cloud")), ("Gaming", ("gaming",)))
SHORT_NAMES = {"hbo-max": "HBO Max", "amazon-prime": "Prime Video", "duolingo": "Duolingo",
               "apple-tv": "Apple TV", "adobe-cc": "Adobe CC"}


def esc(s: str) -> str:
    return escape(s, quote=True)


def app_store_url(site: SiteConfig, ct: str) -> str:
    if not site.provider_token:
        return f"https://apps.apple.com/app/id{site.app_id}"
    return (f"https://apps.apple.com/app/apple-store/id{site.app_id}"
            f"?pt={quote(site.provider_token)}&ct={quote(ct)}&mt=8")


def read_minutes(service: Service) -> int:
    parts = [service.fastest_text, *service.steps, service.note or "", *(q + " " + a for q, a in service.faq)]
    words = sum(len(p.split()) for p in parts)
    return max(1, math.ceil(words / 200))


def money(x: float) -> str:
    return f"${x:,.2f}"


def renew_in_days(service_id: str) -> int:
    """A stable example renewal day (2–28) for the homepage radar; the same in home.js."""
    return 2 + zlib.crc32(service_id.encode()) % 27


def _checked(service: Service) -> str:
    year, month = service.checked.split("-")
    return f"{MONTHS[int(month) - 1]} {year}"


def _source_link(url: str, label: str | None = None) -> str:
    """A link for http(s) URLs only; anything else from the data is shown as plain text."""
    text = esc(label if label is not None else _host(url))
    return f'<a href="{esc(url)}">{text}</a>' if url.startswith(("https://", "http://")) else text


def _host(url: str) -> str:
    host = urlparse(url).netloc
    return host[4:] if host.startswith("www.") else host


def analytics_html(site: SiteConfig) -> str:
    """Cloudflare Web Analytics' beacon (cookieless page views), when the site has a token."""
    if not site.analytics_token:
        return ""
    beacon = esc(json.dumps({"token": site.analytics_token}))
    return f"\n  <script type=\"module\" src=\"https://static.cloudflareinsights.com/beacon.min.js\" data-cf-beacon=\"{beacon}\"></script>"


def logo_html(brand: Brand | None, name: str, size: int, cls: str = "logo", lazy: bool = True) -> str:
    """The service's App Store icon, else its glyph on a brand tile, else its initial (the app's ServiceLogo)."""
    if brand and brand.logo:
        loading = ' loading="lazy"' if lazy else ""
        return f'<img class="{cls}" src="{esc(brand.logo)}" alt="" width="{size}" height="{size}"{loading}>'
    color = esc(brand.color if brand else "#5F5A73")
    if brand and brand.glyph:
        return (f'<span class="{cls}" style="background:{color}" aria-hidden="true"><svg viewBox="-4 -4 32 32">'
                f'<path d="{esc(brand.glyph)}" fill="#fff"/></svg></span>')
    return f'<span class="{cls}" style="background:{color}" aria-hidden="true">{esc(name[:1].upper())}</span>'


def _shell(site: SiteConfig, *, title: str, description: str, path: str, ct: str, body: str, field: str,
           footer_note: str = "", page_class: str = "", head_extra: str = "", scripts: str = "") -> str:
    url = site.base_url + path
    store = esc(app_store_url(site, ct))
    note = f'<p class="footer-note">{esc(footer_note)}</p>' if footer_note else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{esc(url)}">
  <meta name="apple-itunes-app" content="app-id={esc(site.app_id)}">
  <meta name="color-scheme" content="light dark">
  <meta name="theme-color" content="#F3F1F8" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#0B0A12" media="(prefers-color-scheme: dark)">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Paydar">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(url)}">
  <meta property="og:image" content="{esc(site.base_url)}/og.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Paydar: every charge, 3 days early. Your renewals on one radar.">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="/favicon.png?v=2">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png?v=2">
  <link rel="stylesheet" href="/site.css">{analytics_html(site)}{head_extra}
</head>
<body class="{page_class}">
  <div class="field" style="{esc(field)}" aria-hidden="true"></div>
  <a class="skip" href="#main">Skip to content</a>
  <header class="site-header">
    <div class="wrap header-bar">
      <a class="brand" href="/">{RADAR_MARK}<span>Paydar</span></a>
      <nav class="nav" aria-label="Site">
        <a href="/#guides">Cancel guides</a>
        <a href="/price-increases/">Price increases</a>
        <a href="/subscription-calculator/">Cost calculator</a>
      </nav>
      <a class="pill pill-ink pill-small" href="{store}"><span class="label-long">Get it on iPhone</span><span class="label-short">Get the app</span></a>
    </div>
  </header>
  <main id="main">
{body}
  </main>
  <footer class="site-footer">
    <div class="wrap">
      <p class="footer-word" aria-hidden="true">Paydar</p>
      <nav class="footer-links" aria-label="Footer">
        <a href="/#guides">Cancel guides</a>
        <a href="/price-increases/">Price increases</a>
        <a href="/subscription-calculator/">Cost calculator</a>
        <a href="{esc(site.privacy_url)}">Privacy</a>
        <a href="mailto:{esc(site.support_email)}">Support</a>
        <a href="{store}">App Store</a>
      </nav>
      {note}<p class="footer-note">Service names and logos belong to their owners. Paydar is an iPhone app by an independent developer.</p>
    </div>
  </footer>
  <script src="/lenis.min.js" defer></script>
  <script src="/motion.js" defer></script>{scripts}
</body>
</html>
"""


def _service_field(brand: Brand | None) -> str:
    color = brand.color if brand else LAVENDER
    return field_style([(color, 2.0), (LAVENDER, 1.0)])


def _paydar_card(site: SiteConfig, ct: str, title: str, text: str, brand: Brand | None = None,
                 name: str = "") -> str:
    tile = logo_html(brand, name, 44, "logo card-logo") if (brand or name) else ""
    return f"""      <aside class="paydar-card glass">
        <div class="card-marks">{tile}<span class="card-app">{RADAR_MARK}</span></div>
        <div class="card-copy">
          <h2>{esc(title)}</h2>
          <p>{esc(text)}</p>
        </div>
        <div class="card-action">
          <a class="pill pill-ink" href="{esc(app_store_url(site, ct))}">{esc(CTA_LABEL)} {ICON_NEXT}</a>
          <p class="facts">{esc(FACTS)}</p>
        </div>
      </aside>"""


def _tag_html(service: Service, us: list[Change], today: date) -> str:
    if service.headline_plan is None:
        return ""
    tag = price_tag(us, service.headline_plan, service.headline_frequency, service.name, today)
    if tag is None:
        return ""
    icon = {"up": ICON_UP, "down": ICON_DOWN}.get(tag.kind, "")
    return f'      <p class="price-alert tag-{tag.kind}">{icon}{esc(tag.text)}</p>\n'


def _fastest_html(service: Service) -> str:
    inner = (f'<span class="fastest-heading">Fastest way{ICON_OUT if service.fastest_url else ""}</span>'
             f"<span class=\"fastest-text\">{esc(service.fastest_text)}</span>")
    if service.fastest_url:
        return f'      <a class="fastest frost" href="{esc(service.fastest_url)}">{inner}</a>\n'
    return f'      <div class="fastest frost">{inner}</div>\n'


def _notes_html(service: Service) -> str:
    parts = []
    if service.apple_billed:
        parts.append(f"<p>{APPLE_NOTE}</p>")
    if service.note:
        parts.append(f"<p>{esc(service.note)}</p>")
    return f'      <div class="billing-note">{"".join(parts)}</div>\n' if parts else ""


def _prices_html(site: SiteConfig, service: Service, us: list[Change], today: date) -> str:
    plan, freq = service.headline_plan, service.headline_frequency
    if plan is None or not us:
        return ""
    rows = []
    featured = plan or service.name
    for c in plan_cards(us, service.name, today):
        cls = "plan-row featured" if c.label == featured else "plan-row"
        price, unit = c.price[:-3], c.price[-3:]
        yearly = f'<span class="plan-yearly">{esc(c.yearly)}</span>' if c.yearly else ""
        badge = f'<span class="plan-change change-{c.badge_kind}">{esc(c.badge)}</span>' if c.badge else ""
        rows.append(f'<li class="{cls}"><span class="plan-name">{esc(c.label)}</span>{badge}'
                    f'<span class="plan-price">{esc(price)}<span>{esc(unit)}</span>{yearly}</span></li>')
    chart = ""
    bars = chart_bars(us, plan, freq, today)
    if bars:
        top = max(b.value for b in bars) or 1
        unit = "per month" if freq == "monthly" else "per year"
        # An announced price is hatched: red when it goes up, green when it comes down.
        kinds = ["" if not b.upcoming else (" is-upcoming is-down" if i and b.value < bars[i - 1].value
                                            else " is-upcoming") for i, b in enumerate(bars)]
        cols = "".join(
            f'<div class="chart-column{k}"><span class="bar-value">{esc(b.text)}</span>'
            f'<span class="bar" style="height:{max(8, round(BAR_MAX_PX * b.value / top))}px"></span></div>'
            for b, k in zip(bars, kinds))
        dates = "".join(f'<span class="bar-date">{esc(b.label)}</span>' for b in bars)
        table = "".join(f"<tr><th scope=\"row\">{esc(b.label)}</th><td>{esc(b.text)}"
                        f"{' (announced)' if b.upcoming else ''}</td></tr>" for b in bars)
        # One series needs no legend; the two states do when an announced price is drawn.
        legend = ""
        if any(kinds):
            next_cls = "key key-next key-down" if all("is-down" in k for k in kinds if k) else "key key-next"
            legend = f'<span class="key key-now">In effect</span><span class="{next_cls}">Announced</span>'
        dense = " dense" if len(bars) > 4 else ""
        chart = f"""
        <figure class="price-chart frost{dense}" style="--n:{len(bars)}">
          <figcaption class="chart-caption"><span>{esc(featured)} plan, {unit}</span><span class="chart-keys">{legend}</span></figcaption>
          <div class="chart-columns" aria-hidden="true">{cols}</div>
          <div class="chart-dates" aria-hidden="true">{dates}</div>
          <div class="sr-only"><table><caption>{esc(featured)} price history, {unit}</caption>{table}</table></div>
        </figure>"""
    return f"""      <section class="prices">
        <h2 class="section-title">{esc(service.name)} prices now (US)</h2>
        <ul class="plan-list frost">{"".join(rows)}</ul>{chart}
        <a class="price-cta" href="{esc(app_store_url(site, "seo-" + service.slug))}">{esc(CHART_LINK)} {ICON_NEXT}</a>
      </section>
"""


def _faq_html(service: Service, us: list[Change], today: date) -> str:
    items = "".join(f'<div class="faq-item"><dt>{esc(q)}</dt><dd>{esc(fill_prices(a, us, today))}</dd></div>'
                    for q, a in service.faq)
    return f"""      <section class="faq">
        <h2 class="section-title">Common questions</h2>
        <dl class="faq-list frost">{items}</dl>
      </section>
"""


def _sources_html(service: Service, us: list[Change]) -> str:
    lines = []
    price_sources = list(dict.fromkeys(c.source for c in us if c.source))
    if price_sources and service.headline_plan is not None:
        links = ", ".join(_source_link(s) for s in price_sources)
        lines.append(f"<p>Prices: {links}</p>")
    links = ", ".join(_source_link(u, label) for label, u in service.cancel_sources)
    lines.append(f"<p>Cancel steps: {links}</p>")
    return f"""      <section class="sources">
        <h2>Sources</h2>
        {"".join(lines)}
      </section>"""


def service_page(site: SiteConfig, service: Service, us: list[Change], today: date,
                 brand: Brand | None = None) -> str:
    has_prices = service.headline_plan is not None and bool(us)
    year = service.checked[:4]
    news = title_news(us, service.headline_plan, service.headline_frequency, today, year) if has_prices else None
    if news:  # "Cancel YouTube Premium (2026): June price increase to $15.99/mo"
        title = f"Cancel {service.name} ({year}): {news} | Paydar"
    elif has_prices:
        title = f"How to cancel {service.name} ({year}): steps and current prices | Paydar"
    else:
        title = f"How to cancel {service.name} ({year}): step by step | Paydar"
    description = service.fastest_text + (" Steps, current US prices and price history." if has_prices
                                          else " Step-by-step guide.")
    steps = "".join(f"<li><p>{esc(s)}</p></li>" for s in service.steps)
    body = ("    <article class=\"wrap article\">\n"
            f"      <header class=\"guide-head\">{logo_html(brand, service.name, 64, 'logo guide-logo', lazy=False)}"
            f"<h1 class=\"page-title\">How to cancel {esc(service.name)}</h1></header>\n"
            f"      <p class=\"page-meta\">Checked {_checked(service)} · {read_minutes(service)} min read</p>\n"
            + _tag_html(service, us, today)
            + _fastest_html(service)
            + f"      <ol class=\"steps\">{steps}</ol>\n"
            + _notes_html(service)
            + _paydar_card(site, "seo-" + service.slug, f"{service.name} is one. What about the rest?", CARD_TEXT,
                           brand, service.name) + "\n"
            + _prices_html(site, service, us, today)
            + _faq_html(service, us, today)
            + _sources_html(service, us)
            + "\n    </article>")
    return _shell(site, title=title, description=description, path=f"/cancel/{service.slug}/",
                  ct="seo-" + service.slug, body=body, field=_service_field(brand), page_class="page-guide",
                  footer_note=f"Not affiliated with {service.name}.",
                  head_extra=_json_ld(_guide_ld(site, service, description)) + _json_ld(_faq_ld(service, us, today)))


def _guide_ld(site: SiteConfig, service: Service, description: str) -> dict:
    url = f"{site.base_url}/cancel/{service.slug}/"
    return {"@context": "https://schema.org", "@type": "Article",
            "headline": f"How to cancel {service.name}", "description": description, "url": url,
            "dateModified": f"{service.checked}-01",
            "author": _org(site), "publisher": _org(site),
            "mainEntityOfPage": url, "image": f"{site.base_url}/og.jpg"}


def _org(site: SiteConfig) -> dict:
    """Paydar the publisher; the same @id on every page, defined in full on the homepage."""
    return {"@type": "Organization", "@id": site.base_url + "/#org", "name": "Paydar", "url": site.base_url + "/"}


def _faq_ld(service: Service, us: list[Change], today: date) -> dict:
    """The guide's "Common questions", word for word as shown on the page."""
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": fill_prices(a, us, today)}}
                           for q, a in service.faq]}


def _json_ld(data: dict) -> str:
    text = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    return f'\n  <script type="application/ld+json">{text}</script>'


# The services the description names first, when they went up that year.
FAMOUS = ("netflix", "spotify", "disney-plus", "youtube-premium", "hbo-max", "peacock", "apple-tv", "hulu",
          "paramount-plus", "apple-music")


def _and(items: list[str]) -> str:
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def _when_short(c: Change) -> str:
    """'Mar 26, 2026', or 'Oct 2025' when only the month is known."""
    if c.approx_month:
        return f"{MONTHS[c.effective.month - 1][:3]} {c.effective.year}"
    return f"{MONTHS[c.effective.month - 1][:3]} {c.effective.day}, {c.effective.year}"


def increases_page(site: SiteConfig, services: list[Service], us_all: list[Change], today: date,
                   catalog: Catalog | None = None) -> str:
    names = {s.service_id: s.name for s in services}
    slugs = {s.service_id: s.slug for s in services}

    def name(sid: str) -> str:
        brand = catalog.get(sid) if catalog else None
        return names.get(sid) or (brand.name if brand else sid.replace("-", " ").title())

    upcoming, past = increase_rows(us_all, {sid: name(sid) for sid in {c.service_id for c in us_all}}, today)
    year = today.year
    summary = year_summary(us_all, year, today)
    tracked = len({c.service_id for c in us_all})

    def name_html(sid: str, cls: str) -> str:
        label = esc(name(sid))
        return f'<a class="{cls}" href="/cancel/{esc(slugs[sid])}/">{label}</a>' if sid in slugs else f'<span class="{cls}">{label}</span>'

    def sources_html(sources: list[str]) -> str:
        label = "Source" if len(sources) == 1 else "Sources"
        return f"{label}: " + ", ".join(_source_link(s) for s in sources)

    def lines_html(lines: list[str]) -> str:
        return "".join(f"<li>{esc(line)}</li>" for line in lines)

    def recent_html(rows) -> str:
        return "".join(
            f'<div class="recent-row"><div class="recent-top">{name_html(r.service_id, "recent-name")}'
            f'<time datetime="{r.effective.isoformat()}">{esc(r.when)}</time></div>'
            f'<ul class="row-lines">{lines_html(r.lines)}</ul>'
            f'<p class="row-source">{sources_html(r.sources)}</p></div>'
            for r in rows)

    if upcoming:
        coming = "".join(
            f'<div class="upcoming-card frost"><h3 class="service-heading">{name_html(r.service_id, "row-name")}</h3>'
            f'<p class="upcoming-date">{esc(r.when)}</p><ul class="row-lines">{lines_html(r.lines)}</ul>'
            f'<p class="row-source">{sources_html(r.sources)}</p></div>'
            for r in upcoming)
    else:
        coming = '<p class="empty">No announced increases right now.</p>'

    # The year in three numbers, then the same in a sentence (what a search snippet would quote).
    stats = (f'<div class="stat frost"><span class="stat-num">{len(summary.services)}</span>'
             f'<span class="stat-label">services raised prices</span></div>'
             f'<div class="stat frost"><span class="stat-num">{esc(summary.typical_percent or "–")}</span>'
             f'<span class="stat-label">typical increase</span></div>'
             f'<div class="stat frost"><span class="stat-num">{len(upcoming)}</span>'
             f'<span class="stat-label">{"increase" if len(upcoming) == 1 else "increases"} coming up</span></div>')
    if summary.services:
        b = summary.biggest
        lede = (f"So far in {year}, {len(summary.services)} of the {tracked} subscriptions we track raised their US prices. "
                f"The typical increase on a monthly plan was {signed(summary.typical)} ({summary.typical_percent})")
        lede += (f"; the biggest, {name(b.service_id)} {b.plan}, went up {pmoney(b.new - b.old)} to "
                 f"{pmoney(b.new)}{per(b.frequency)}." if b else ".")
    else:
        lede = f"No US price increases have taken effect in {year} yet."
    if upcoming:
        lede += f" Next: {name(upcoming[0].service_id)}, {upcoming[0].when}."

    headlines = {s.service_id: (s.headline_plan, s.headline_frequency) for s in services if s.headline_plan is not None}

    def glance_html(g) -> str:
        brand = catalog.get(g.service_id) if catalog else None
        plan = f'<span class="glance-plan">{esc(g.plan)}</span>' if g.plan else ""
        if g.last:
            kind = "down" if g.last.new < g.last.old else "up"
            change = (f'<span class="glance-delta {kind}">{esc(signed(g.last.new - g.last.old))} · '
                      f'{esc(percent(g.last.old, g.last.new))}</span>'
                      f'<time datetime="{g.last.effective.isoformat()}">{esc(_when_short(g.last))}</time>')
        else:
            change = '<span class="glance-delta">–</span>'
        return (f'<tr><td><div class="glance-service">{logo_html(brand, name(g.service_id), 32, "logo glance-logo")}'
                f'<div class="glance-text">{name_html(g.service_id, "glance-name")}{plan}</div></div></td>'
                f'<td class="glance-now">{esc(pmoney(g.now))}<span>{per(g.frequency)}</span>'
                # Narrow screens drop the third column and show the change here (one of the two is display: none).
                f'<div class="glance-change glance-change-inline">{change}</div></td>'
                f'<td><div class="glance-change">{change}</div></td></tr>')

    glance = "".join(glance_html(g) for g in glance_rows(us_all, headlines, today))

    timeline = ""
    for y in sorted({r.effective.year for r in past}, reverse=True):
        heading = f"{y} so far" if y == year else str(y)
        timeline += (f'      <section class="recent">\n        <h2 class="feed-heading">{heading}</h2>\n'
                     f'        <div class="recent-list frost">{recent_html([r for r in past if r.effective.year == y])}</div>\n'
                     f'      </section>\n')

    faq = _increases_faq(summary, upcoming, name, year)
    faq_html = "".join(f'<div class="faq-item"><dt>{esc(q)}</dt><dd>{esc(a)}</dd></div>' for q, a in faq)
    updated = f"{MONTHS[today.month - 1][:3]} {today.day}, {today.year}"
    card = _paydar_card(site, "seo-price-increases", "Get pinged before the next one.",
                        "Paydar tracks every subscription and flags announced price increases before they hit your card.")
    body = f"""    <article class="wrap article article-wide">
      <h1 class="page-title">Subscription price increases in {year}</h1>
      <p class="page-meta">Updated {updated} · US prices · every change links to its source</p>
      <div class="stat-row">{stats}</div>
      <p class="increases-lede">{esc(lede)}</p>
      <section class="upcoming">
        <h2 class="feed-heading">Coming up</h2>
        {coming}
      </section>
      <section class="glance">
        <h2 class="feed-heading">Every service at a glance</h2>
        <div class="glance-wrap frost"><table class="glance-table">
          <thead><tr><th scope="col">Service</th><th scope="col">Price now</th><th scope="col">Last change</th></tr></thead>
          <tbody>{glance}</tbody>
        </table></div>
      </section>
{card}
{timeline}      <section class="faq">
        <h2 class="section-title">Common questions</h2>
        <dl class="faq-list frost">{faq_html}</dl>
      </section>
    </article>"""
    famous = [name(sid) for sid in FAMOUS if sid in summary.services][:3]
    description = (f"{len(summary.services)} of the {tracked} US subscriptions we track raised prices in {year}"
                   + (f", including {_and(famous)}" if famous else "") + ". Every plan, date and source, updated daily.")
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                             for q, a in faq]}
    return _shell(site, title=f"Subscription price increases {year}: every US hike so far | Paydar",
                  description=description, path="/price-increases/", ct="seo-price-increases", body=body,
                  page_class="page-increases", head_extra=_json_ld(faq_ld),
                  field=field_style([("#FF6B70", 2.0), ("#E8B04B", 1.2), (LAVENDER, 1.0)]))


def _increases_faq(summary, upcoming, name, year: int) -> list[tuple[str, str]]:
    """The price-increase page's questions, answered from the data (the FAQ markup shows them word for word)."""
    faq = []
    if summary.services:
        by_month: dict[int, list[str]] = {}
        for sid, month in summary.first_months:
            by_month.setdefault(month, []).append(name(sid))
        months = "; ".join(f"{MONTHS[m - 1]}: {_and(ns)}" for m, ns in by_month.items())
        faq.append((f"Which subscriptions raised prices in {year}?",
                    f"{len(summary.services)} of the ones we track, so far. {months}."))
    if upcoming:
        nxt = " ".join(f"{name(r.service_id)}, {r.when}: {'; '.join(r.lines)}." for r in upcoming)
    else:
        nxt = "None announced right now. This page is updated every day."
    faq.append(("Which subscription price increases are coming next?", nxt))
    if summary.biggest:
        b = summary.biggest
        faq.append((f"How much have subscription prices gone up in {year}?",
                    f"The typical increase on a monthly plan was {signed(summary.typical)} a month "
                    f"({summary.typical_percent}), about {pmoney(summary.typical * 12)} a year. The biggest was "
                    f"{name(b.service_id)} {b.plan}: {signed(b.new - b.old)}, to {pmoney(b.new)}{per(b.frequency)}."))
    faq.append(("How can I avoid a subscription price increase?",
                "A new price usually starts at your first renewal on or after the change date, and services email "
                "existing subscribers first. Before then you can cancel, switch to a cheaper plan or move to yearly "
                "billing where it costs less. If you pay through Apple, manage it in Settings → your name → Subscriptions."))
    return faq


# ---- Subscription cost calculator ------------------------------------------------------------

CALC_GROUPS = GUIDE_GROUPS + (("Everything else", ()),)


def _plan_key(service_id: str, p) -> str:
    """The plan's id in the share link: 'netflix:standard-monthly'."""
    slug = re.sub(r"[^a-z0-9]+", "-", (p.plan or "plan").lower()).strip("-")
    return f"{service_id}:{slug}-{p.frequency}"


def calculator_page(site: SiteConfig, services: list[Service], us_all: list[Change], today: date,
                    catalog: Catalog | None = None) -> str:
    names = {s.service_id: s.name for s in services}
    slugs = {s.service_id: s.slug for s in services}
    headlines = {s.service_id: (s.headline_plan, s.headline_frequency) for s in services if s.headline_plan is not None}
    year = today.year

    def name(sid: str) -> str:
        brand = catalog.get(sid) if catalog else None
        return names.get(sid) or (brand.name if brand else sid.replace("-", " ").title())

    # Every service with a price: plan by plan from the price list, else the catalog's typical price.
    entries = []
    for sid in dict.fromkeys([*(c.service_id for c in us_all), *(catalog.brands if catalog else {})]):
        brand = catalog.get(sid) if catalog else None
        cs = [c for c in us_all if c.service_id == sid]
        if cs:
            plans, typical = plan_prices(cs, today), False
        elif brand and brand.price:
            plans, typical = [PlanPrice("", brand.frequency, brand.price, brand.price)], True
        else:
            continue
        head = headlines.get(sid)
        default = next((p for p in plans if head and (p.plan, p.frequency) == head), plans[0])
        category = brand.category if brand else "other"
        entries.append((sid, plans, default, typical, category))

    home = list(catalog.home_chips[:4]) if catalog else []
    picked = {_plan_key(sid, default) for sid, _, default, _, _ in entries if sid in home}

    def monthly(p) -> float:
        return p.now if p.frequency == "monthly" else p.now / 12

    def added(p) -> float:
        return (p.now - p.start) * (12 if p.frequency == "monthly" else 1)

    def plan_html(sid: str, p, typical: bool) -> str:
        key = _plan_key(sid, p)
        if typical:  # the catalog's price, which can be another product's: Amazon's is Prime Video's, not Prime's
            brand = catalog.get(sid) if catalog else None
            label = (SHORT_NAMES.get(sid) or brand.name) if brand and brand.name != name(sid) else "Typical price"
        else:
            label = p.plan or ("Monthly" if p.frequency == "monthly" else "Yearly")
        rise = (f'<span class="calc-rise">+{esc(pmoney(p.now - p.start))} in {year}</span>' if p.now > p.start else "")
        return (f'<li><label class="calc-plan"><input type="checkbox" value="{esc(key)}"'
                f' data-monthly="{monthly(p):.4f}" data-added="{added(p):.2f}"{" checked" if key in picked else ""}>'
                f'<span class="calc-plan-text"><span class="calc-plan-name">{esc(label)}</span>{rise}</span>'
                f'<span class="calc-plan-price">{esc(pmoney(p.now))}<span>{per(p.frequency)}</span></span></label></li>')

    def service_html(entry) -> str:
        sid, plans, _, typical, _ = entry
        brand = catalog.get(sid) if catalog else None
        title = (f'<a class="calc-name" href="/cancel/{esc(slugs[sid])}/">{esc(name(sid))}</a>' if sid in slugs
                 else f'<span class="calc-name">{esc(name(sid))}</span>')
        return (f'<div class="calc-service frost"><div class="calc-head">{logo_html(brand, name(sid), 36, "logo calc-logo")}'
                f'{title}</div><ul class="calc-plans">{"".join(plan_html(sid, p, typical) for p in plans)}</ul></div>')

    groups, used = "", set()
    for title, cats in CALC_GROUPS:
        items = [e for e in entries if e[0] not in used and (e[4] in cats or not cats)]
        used.update(e[0] for e in items)
        if items:
            items.sort(key=lambda e: name(e[0]).lower())
            groups += (f'      <section class="calc-group"><h2 class="calc-group-title">{esc(title)}</h2>'
                       f'{"".join(service_html(e) for e in items)}</section>\n')

    # The total the page opens with (the script takes over from there).
    chosen = [p for sid, plans, _, _, _ in entries for p in plans if _plan_key(sid, p) in picked]
    month = sum(monthly(p) for p in chosen)
    rise = sum(added(p) for p in chosen)
    picks = [f"{name(sid)} {default.plan}".strip() for sid, _, default, _, _ in entries if sid in home]
    rose = [name(sid) for sid, plans, _, _, _ in entries if any(p.now > p.start for p in plans)]

    rise_text = (f"{year}'s price increases add {pmoney(round(rise, 2))} a year to these." if rise > 0
                 else f"None of these went up in {year}.")
    store = esc(app_store_url(site, "seo-calculator"))
    faq = [(f"How much do {_and(picks)} cost a year?",
            f"{money(month * 12)} a year, or {money(month)} a month, at today's US prices before tax.")] if picks else []
    faq += [
        ("How do I work out what my subscriptions cost a year?",
         "Add up the monthly prices and multiply by 12, then add any yearly plans as they are. This calculator does it "
         "with today's US prices and counts a yearly plan as a twelfth of its price each month."),
        (f"Which subscriptions got more expensive in {year}?",
         f"{_and(rose)}. Every change, with its source, is on our price increases page." if rose
         else f"None of the ones listed here, so far in {year}."),
        ("Are these prices up to date?",
         "They come from the price list Paydar uses to flag increases, with a source for every change, and this page "
         "is rebuilt every day. US prices, before sales tax."),
    ]
    faq_html = "".join(f'<div class="faq-item"><dt>{esc(q)}</dt><dd>{esc(a)}</dd></div>' for q, a in faq)
    updated = f"{MONTHS[today.month - 1][:3]} {today.day}, {today.year}"
    body = f"""    <article class="wrap article article-wide calc">
      <h1 class="page-title">What do your subscriptions cost?</h1>
      <p class="page-meta">Tick what you pay for · US prices, updated {updated} · <a href="/price-increases/">every {year} price increase</a></p>
      <div class="calc-layout">
        <div class="calc-list">
{groups}        </div>
        <aside class="calc-total glass" aria-label="Your total" data-year="{year}">
          <p class="calc-month"><span class="calc-num" data-total="month">{esc(money(month))}</span> a month</p>
          <p class="calc-year"><span data-total="year">{esc(money(month * 12))}</span> a year</p>
          <p class="calc-added" data-total="added">{esc(rise_text)}</p>
          <p class="calc-live sr-only" aria-live="polite"></p>
          <div class="calc-actions">
            <button class="pill calc-share" type="button" hidden>Copy link to this list</button>
            <a class="pill pill-ink calc-cta" href="{store}">Track them in Paydar {ICON_NEXT}</a>
          </div>
          <p class="calc-note">Paydar puts each renewal on one radar and pings you before it charges.</p>
        </aside>
      </div>
      <section class="faq">
        <h2 class="section-title">Common questions</h2>
        <dl class="faq-list frost">{faq_html}</dl>
      </section>
    </article>"""
    others = len(entries) - 3
    description = (f"Tick what you pay for and see your monthly and yearly total at today's US prices for Netflix, "
                   f"Spotify, Disney+ and {others} more, plus what {year}'s price increases added.")
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                             for q, a in faq]}
    return _shell(site, title=f"Subscription cost calculator ({year} US prices) | Paydar", description=description,
                  path="/subscription-calculator/", ct="seo-calculator", body=body, page_class="page-calc",
                  head_extra=_json_ld(faq_ld), field=field_style([("#16A374", 1.6), ("#8A6BD6", 1.2), ("#4A9EFF", 1.0)]),
                  scripts='\n  <script src="/calc.js" defer></script>')


# ---- Homepage -------------------------------------------------------------------------------

def _chip(brand: Brand, on: bool, i: int) -> str:
    """A pick in the hero; i is its place in the hero's arrival (site.css)."""
    name = SHORT_NAMES.get(brand.service_id, brand.name)
    return (f'<button class="chip{" on" if on else ""}" type="button" aria-pressed="{"true" if on else "false"}" style="--i:{i}" '
            f'data-id="{esc(brand.service_id)}" data-name="{esc(name)}" data-color="{esc(brand.color)}" '
            f'data-price="{brand.price:.2f}">{logo_html(brand, name, 30, "chip-logo", lazy=False)}<span>{esc(name)}</span></button>')


REMINDER_PRESETS = ((0, "On the renewal day"), (1, "1 day before"), (3, "3 days before"), (7, "7 days before"),
                    (14, "14 days before"))


def _notice_text(name: str, price: float, days: int) -> tuple[str, str]:
    """The reminder on the phone (the same wording in home.js)."""
    when = "today" if days == 0 else "tomorrow" if days == 1 else f"in {days} days"
    return f"{name} renews {'today' if days == 0 else 'soon'}", f"On your radar: {money(price)} renews {when}"


def _presets_html() -> str:
    """The app's reminder lead times; 3 days, the app's default for a new subscription, starts chosen."""
    return "".join(f'<label class="preset"><input type="radio" name="remind" value="{days}"'
                   f'{" checked" if days == 3 else ""}><span>{esc(text)}</span></label>'
                   for days, text in REMINDER_PRESETS)


RADAR_INSET = 0.88  # the 30-day ring sits inside the half-disc, so logos on it stay inside too


def _blip(brand: Brand, angle: float, r: float, days: int) -> str:
    """A pick on the radar; its spot comes from radar.place() over every chip, so it never moves.
    Like the app, the radar shows logos only; the scale says how far each is."""
    x = 50 + 50 * RADAR_INSET * r * math.cos(math.radians(angle))
    y = 100 - 100 * RADAR_INSET * r * math.sin(math.radians(angle))
    name = SHORT_NAMES.get(brand.service_id, brand.name)
    return (f'<li class="blip" data-id="{esc(brand.service_id)}" style="left:{x:.2f}%;top:{y:.2f}%">'
            f'{logo_html(brand, name, 44, "blip-logo")}<span class="sr-only">{esc(name)} renews in {days} days</span></li>')


def _radar_scale() -> str:
    """The app's 7d / 14d / 30d marks along the radar's baseline, both sides of Today."""
    marks = []
    for days in (7, 14, 30):
        off = 50 * RADAR_INSET * aura_radius(days)
        for x in (50 - off, 50 + off):
            marks.append(f'<span style="left:{x:.2f}%">{days}d</span>')
    return f'<div class="radar-scale" aria-hidden="true">{"".join(marks)}</div>'


def _round_dollars(x: float) -> str:
    return f"${round(x):,}"


def _guides_html(services: list[Service], catalog: Catalog | None) -> str:
    groups = []
    used = set()
    for title, cats in GUIDE_GROUPS:
        items = [s for s in services if catalog and (b := catalog.get(s.service_id)) and b.category in cats]
        used.update(s.service_id for s in items)
        if items:
            groups.append((title, items))
    rest = [s for s in services if s.service_id not in used]
    if rest:
        groups.append(("More", rest))
    out = []
    for title, items in groups:
        links = "".join(f'<li><a href="/cancel/{esc(s.slug)}/">{logo_html(catalog.get(s.service_id) if catalog else None, s.name, 32, "guide-tile")}'
                        f'<span>{esc(s.name)}</span></a></li>' for s in items)
        out.append(f'<div class="guide-group"><h3>{esc(title)}</h3><ul>{links}</ul></div>')
    return "".join(out)


def _next_increase(services: list[Service], us_all: list[Change], today: date) -> str:
    names = {s.service_id: s.name for s in services}
    upcoming, past = increase_rows(us_all, names, today)
    row, label = (upcoming[0], "Announced") if upcoming else ((past[0], "Latest") if past else (None, ""))
    if row is None:
        return ""
    name = esc(names.get(row.service_id) or row.service_id.replace("-", " ").title())
    lines = "".join(f"<li>{esc(line)}</li>" for line in row.lines[:2])
    return (f'<a class="next-rise frost" href="/price-increases/"><span class="rise-name">{name}</span>'
            f'<span class="rise-label">{label} · {esc(row.when)}</span><ul>{lines}</ul>'
            f'<span class="rise-more">Every recent and announced US increase {ICON_NEXT}</span></a>')


def home_page(site: SiteConfig, services: list[Service], catalog: Catalog | None = None,
              us_all: list[Change] | None = None, today: date | None = None) -> str:
    store = esc(app_store_url(site, "seo-home"))
    chips_html, blips_html, field, total, spots = "", "", "", 0.0, {}
    soon_name, soon_price = "Netflix", 19.99
    if catalog:
        chips = [catalog.brands[sid] for sid in catalog.home_chips]
        picked = chips[:4]
        total = sum(b.price or 0 for b in picked)
        layout = place([(b.service_id, renew_in_days(b.service_id)) for b in chips], max_blips=len(chips),
                       radius_for_days=aura_radius)
        spots = {sid: {"a": round(a, 2), "r": round(r, 4), "d": renew_in_days(sid)} for sid, (a, r) in layout.items()}
        chips_html = "".join(_chip(b, b in picked, 5 + n) for n, b in enumerate(chips))
        blips_html = "".join(_blip(b, *layout[b.service_id], renew_in_days(b.service_id)) for b in picked)
        field = field_style([(b.color, b.price or 0) for b in picked])
        soonest = min(picked, key=lambda b: renew_in_days(b.service_id))
        soon_name, soon_price = SHORT_NAMES.get(soonest.service_id, soonest.name), soonest.price or 0
    else:
        chips = []
        field = field_style([])
    data = json.dumps({"spots": spots, "inset": RADAR_INSET}).replace("<", "\\u003c")
    notice_title, notice_line = _notice_text(soon_name, soon_price, 3)
    priced = sum(1 for s in services if s.headline_plan is not None)
    rise = _next_increase(services, us_all or [], today or date.today())
    screens = "".join(
        f'<figure class="screen"><picture><source srcset="/screens/{n}-dark.webp" media="(prefers-color-scheme: dark)">'
        f'<img src="/screens/{n}-light.webp" alt="{esc(alt)}" width="660" height="1434" loading="lazy"></picture>'
        f'<figcaption><strong>{esc(cap)}</strong> {esc(sub)}</figcaption></figure>'
        for n, alt, cap, sub in (
            ("calendar", "Paydar's calendar: renewals marked on each day of the month", "Calendar.",
             "Every renewal on its day, and what the month costs."),
            ("trials", "Paydar's subscription list with free trials and their end dates", "Free trials.",
             "The day each trial turns paid, with two reminders before it does."),
            ("caught", "Paydar confirming a payment was marked as paid", "Mark as paid.",
             "Log a charge in one tap and keep a history of what you spent."),
        ))
    body = f"""    <section class="hero wrap" aria-labelledby="hero-title">
      <div class="hero-copy">
        <h1 id="hero-title" style="--i:0">Every charge,<br> 3&nbsp;days early.</h1>
        <p class="lede" style="--i:1">Paydar is a subscription tracker for iPhone. Your next 30 days of renewals sit on one radar, and a reminder lands before each charge.</p>
        <div class="hero-action" style="--i:2">
          <a class="pill pill-ink pill-large" href="{store}">{esc(CTA_LABEL)} {ICON_NEXT}</a>
          <p class="facts">{esc(FACTS)}</p>
        </div>
      </div>
      <fieldset class="picker">
        <legend style="--i:3">Tap what you pay for</legend>
        <p class="mini-total glass" aria-hidden="true" style="--i:4"><span class="mini-month">{money(total)}</span> a month</p>
        <div class="chips">{chips_html}</div>
        <p class="more" style="--i:{5 + len(chips)}">Plus 100+ more services in the app, or add your own.</p>
      </fieldset>
      <div class="meter glass">
        <p class="meter-total"><span class="total-month">{money(total)}</span><span class="per">a month</span></p>
        <p class="meter-sub">About <span class="total-year">{_round_dollars(total * 12)}</span> a year for what you picked</p>
        <p class="sr-only meter-live" aria-live="polite"></p>
        <div class="radar">
          <span class="beam-clip" aria-hidden="true"><span class="beam"></span></span>
          <ul class="blips">{blips_html}</ul>
          {_radar_scale()}
          <span class="radar-today">Today</span>
        </div>
        <p class="pro-hint" hidden></p>
        <p class="meter-note">Typical US prices and example dates. In the app you enter your own.</p>
      </div>
    </section>

    <section class="reminders wrap" aria-labelledby="reminders-title">
      <figure class="phone" data-rv="3">
        <picture><source srcset="/screens/home-dark.webp" media="(prefers-color-scheme: dark)">
        <img src="/screens/home-light.webp" alt="Paydar's home screen: the monthly total, the radar of renewals and the list of what renews next" width="660" height="1434" loading="lazy"></picture>
        <div class="notice glass" role="img" aria-label="{esc(f"A Paydar reminder: {notice_title}. {notice_line}.")}"
             data-name="{esc(soon_name)}" data-price="{soon_price:.2f}">
          <span class="notice-app">{RADAR_MARK}PAYDAR <span>now</span></span>
          <strong class="notice-title">{esc(notice_title)}</strong>
          <span class="notice-line">{esc(notice_line)}</span>
        </div>
      </figure>
      <div class="reminders-copy">
        <h2 id="reminders-title" data-rv="1">A heads-up before every charge.</h2>
        <p data-rv="2">Paydar reminds you before each renewal, at the time of day you pick. Choose when, per subscription: one reminder or several.</p>
        <fieldset class="presets" data-rv="2">
          <legend class="sr-only">Preview a reminder</legend>
          {_presets_html()}
        </fieldset>
        <p data-rv="2">Free trials get two reminders: two days before the trial ends, and on the day. You decide while you still can.</p>
      </div>
    </section>

    <section class="pricing wrap" aria-labelledby="pricing-title">
      <div class="pricing-panel frost">
        <h2 id="pricing-title" data-rv="1">A tracker that isn't a subscription.</h2>
        <div class="plans">
          <div class="plan" data-rv="2">
            <p class="plan-price-big">Free</p>
            <p class="plan-what">Track up to 4 active subscriptions, with every feature.</p>
          </div>
          <div class="plan plan-pro" data-rv="2">
            <p class="plan-price-big">$9.99 <span>once</span></p>
            <p class="plan-what">Paydar Pro tracks as many as you like, for one payment that never renews.</p>
          </div>
        </div>
        <ul class="promises" data-rv="3">
          <li><strong>No bank login.</strong> Pick from 120+ popular services or add your own. Paydar never connects to a bank.</li>
          <li><strong>No account.</strong> Nothing to sign up for. Open the app and add your first subscription.</li>
          <li><strong>No ads, no tracking.</strong> Your data stays on your iPhone, backed up to your own private iCloud.</li>
        </ul>
        <a class="pill pill-ink pill-large" href="{store}" data-rv="3">{esc(CTA_LABEL)} {ICON_NEXT}</a>
      </div>
    </section>

    <section class="value wrap" aria-labelledby="value-title">
      <div class="value-copy">
        <h2 id="value-title" data-rv="1">Find what you barely use.</h2>
        <p data-rv="2">On the 25th, Paydar asks how much you used each subscription this month. It works out the cost per use and shows what you'd save by cutting the ones you barely touch.</p>
        <p data-rv="2">Then it walks you through cancelling, with step-by-step guides for popular services.</p>
      </div>
      <figure class="phone phone-tilt" data-rv="3">
        <picture><source srcset="/screens/stats-dark.webp" media="(prefers-color-scheme: dark)">
        <img src="/screens/stats-light.webp" alt="Paydar's stats: the monthly budget and the value check with the cost per use of each subscription" width="660" height="1434" loading="lazy"></picture>
      </figure>
    </section>

    <section class="guides wrap" id="guides" aria-labelledby="guides-title">
      <h2 id="guides-title" data-rv="1">How to cancel, step by step.</h2>
      <p class="guides-lede" data-rv="2">Checked guides for {len(services)} services. {priced} of them also show current US prices and their history.</p>
      <div class="guide-groups" data-rv="3">{_guides_html(services, catalog)}</div>
      <div class="watch" data-rv="3">
        {rise}
        <div class="watch-copy">
          <h3>Prices keep moving.</h3>
          <p>Paydar watches announced US price changes for the services you track and tells you before your price goes up. It never changes a price by itself: it asks you first.</p>
        </div>
      </div>
    </section>

    <section class="screens wrap" aria-labelledby="screens-title">
      <h2 id="screens-title" data-rv="1">Everything you pay for, in one place.</h2>
      <div class="screen-row">{screens}</div>
    </section>

    <section class="close wrap" aria-labelledby="close-title">
      <h2 id="close-title" data-rv="1">Your next charge is already on its way.</h2>
      <a class="pill pill-ink pill-large" href="{store}">{esc(CTA_LABEL)} {ICON_NEXT}</a>
      <p class="facts">iPhone only · iOS 18 or later · {esc(FACTS)}</p>
    </section>"""
    # WebSite gives Google the site's name; Organization its logo. No ratings until real ones exist.
    site_ld = {"@context": "https://schema.org", "@type": "WebSite", "name": "Paydar", "url": site.base_url + "/"}
    org_ld = {"@context": "https://schema.org", **_org(site), "logo": site.base_url + "/icon.png"}
    ld = {"@context": "https://schema.org", "@type": "MobileApplication", "name": "Paydar",
          "operatingSystem": "iOS 18.0 or later", "applicationCategory": "FinanceApplication",
          "description": DESCRIPTION, "url": site.base_url + "/",
          "installUrl": f"https://apps.apple.com/app/id{site.app_id}",
          "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
          "publisher": {"@id": site.base_url + "/#org"}}
    return _shell(site, title="Paydar: subscription tracker and renewal reminders for iPhone",
                  description=DESCRIPTION, path="/", ct="seo-home", body=body, field=field, page_class="page-home",
                  head_extra=_json_ld(site_ld) + _json_ld(org_ld) + _json_ld(ld),
                  scripts=f'\n  <script type="application/json" id="home-data">{data}</script>\n  <script src="/home.js" defer></script>')


# ---- Privacy --------------------------------------------------------------------------------

URL_RE = re.compile(r"https?://[^\s<>()\"',]+[^\s<>()\"',.:;]")


def _emphasis(text: str) -> str:
    s = esc(text)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*`]+)\*\*", r"<strong>\1</strong>", s)
    return re.sub(r"(?<![\w*])_([^_]+)_(?!\w)", r"<em>\1</em>", s)


def _inline_md(text: str) -> str:
    """Bare URLs become links (found on the raw text, so escaping and emphasis never cut one)."""
    out, last = [], 0
    for m in URL_RE.finditer(text):
        out += [_emphasis(text[last:m.start()]), f'<a href="{esc(m.group())}">{esc(m.group())}</a>']
        last = m.end()
    out.append(_emphasis(text[last:]))
    return "".join(out)


def markdown_html(md: str, shift: int = 0) -> str:
    """The small Markdown subset the privacy policy uses: headings, paragraphs, lists, bold, italics, code, links."""
    out, para, items = [], [], []

    def flush() -> None:
        if para:
            out.append(f"<p>{_inline_md(' '.join(para))}</p>")
            para.clear()
        if items:
            out.append("<ul>" + "".join(f"<li>{_inline_md(i)}</li>" for i in items) + "</ul>")
            items.clear()

    for line in md.replace("\r\n", "\n").splitlines():
        stripped = line.strip()
        if not stripped or stripped == "---":
            flush()
        elif re.match(r"#{1,6} ", stripped):
            flush()
            level = min(max(len(stripped) - len(stripped.lstrip("#")) - shift, 2), 4)
            out.append(f"<h{level}>{_inline_md(stripped.lstrip('#').strip())}</h{level}>")
        elif stripped.startswith("- "):
            if para:
                flush()
            items.append(stripped[2:])
        else:
            para.append(stripped)
    flush()
    return "\n".join(out)


def privacy_page(site: SiteConfig, policy_md: str) -> str:
    policy = re.sub(r"\A\s*#{1,6} Privacy Policy[ \t]*\r?\n", "", policy_md)
    html = markdown_html(policy, shift=1)
    body = f"""    <article class="wrap article prose">
      <h1 class="page-title">Privacy Policy</h1>
{html}
    </article>"""
    return _shell(site, title="Privacy Policy | Paydar",
                  description="What Paydar does with your data: it stays on your iPhone and in your own iCloud.",
                  path="/privacy/", ct="seo-privacy", body=body, page_class="page-privacy",
                  field=field_style([(LAVENDER, 1.0), ("#16A374", 0.6)]))
