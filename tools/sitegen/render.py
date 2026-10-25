"""HTML for the three page types. Everything user-visible goes through esc()."""

import math
from datetime import date
from html import escape
from urllib.parse import quote, urlparse

from .content import Service, SiteConfig
from .prices import MONTHS, Change, chart_bars, fill_prices, increase_rows, plan_cards, price_tag

APPLE_NOTE = ("<strong>Paying through Apple?</strong> Then Apple bills you. "
              "Cancel in Settings → your name → Subscriptions instead.")
CARD_TEXT = "Paydar puts every subscription on one radar and pings you before each charge. No bank login."
CHART_LINK = "Paydar flags increases like this before they hit your card →"
BAR_MAX_PX = 140

ICON_UP = ('<svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M3 11 11 3M4 3h7v7" '
           'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')
ICON_DOWN = ('<svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M3 5l8 8M11 6v7H4" '
             'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')
ICON_OUT = ('<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M6 18 18 6M7 6h11v11" '
            'stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>')
ICON_NEXT = ('<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M4 12h15m-6-6 6 6-6 6" '
             'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>')


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


def _shell(site: SiteConfig, *, title: str, description: str, path: str, ct: str, body: str,
           footer_note: str = "") -> str:
    url = site.base_url + path
    store = esc(app_store_url(site, ct))
    note = f"\n      <p>{esc(footer_note)}</p>" if footer_note else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{esc(url)}">
  <meta name="apple-itunes-app" content="app-id={esc(site.app_id)}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(url)}">
  <meta property="og:image" content="{esc(site.base_url)}/icon.png">
  <link rel="icon" href="/favicon.png">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="stylesheet" href="/site.css">
</head>
<body>
  <header class="site-header">
    <div class="wrap">
      <a class="brand" href="/"><img src="/icon.png" alt="" width="36" height="36">Paydar</a>
      <a class="desktop-app-link" href="{store}">Get the app {ICON_NEXT}</a>
    </div>
  </header>
  <main class="article">
    <div class="wrap">
{body}
    </div>
  </main>
  <footer class="site-footer">
    <div class="wrap">
      <nav class="footer-links"><a class="footer-brand" href="/">Paydar</a><span>·</span><span>Formerly Subsly</span><span>·</span><a href="{esc(site.privacy_url)}">Privacy</a><span>·</span><a href="mailto:{esc(site.support_email)}">Support</a></nav>{note}
    </div>
  </footer>
</body>
</html>
"""


def _paydar_card(site: SiteConfig, ct: str, title: str, text: str) -> str:
    return f"""      <aside class="paydar-card">
        <img class="cta-icon" src="/icon.png" alt="Paydar app icon" width="48" height="48">
        <div class="cta-copy">
          <h2>{esc(title)}</h2>
          <p>{esc(text)}</p>
        </div>
        <a class="cta-button" href="{esc(app_store_url(site, ct))}">Get Paydar, free {ICON_NEXT}</a>
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
        return f'      <a class="fastest" href="{esc(service.fastest_url)}">{inner}</a>\n'
    return f'      <div class="fastest">{inner}</div>\n'


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
    cards = []
    featured = plan or service.name
    for c in plan_cards(us, service.name, today):
        cls = "plan-card featured" if c.label == featured else "plan-card"
        price, unit = c.price[:-3], c.price[-3:]
        yearly = f'<p class="plan-yearly">{esc(c.yearly)}</p>' if c.yearly else ""
        badge = f'<p class="plan-change change-{c.badge_kind}">{esc(c.badge)}</p>' if c.badge else ""
        cards.append(f'<div class="{cls}"><h3 class="plan-name">{esc(c.label)}</h3>'
                     f'<p class="plan-price">{esc(price)}<span>{esc(unit)}</span></p>{yearly}{badge}</div>')
    chart = ""
    bars = chart_bars(us, plan, freq, today)
    if bars:
        top = max(b.value for b in bars) or 1
        cols = "".join(
            f'<div class="chart-column"><span class="bar-value">{esc(b.text)}</span>'
            f'<span class="bar{" is-upcoming" if b.upcoming else ""}" '
            f'style="height:{max(8, round(BAR_MAX_PX * b.value / top))}px"></span></div>' for b in bars)
        dates = "".join(f"<span>{esc(b.label)}</span>" for b in bars)
        unit = "per month" if freq == "monthly" else "per year"
        chart = f"""
        <figure class="price-chart" style="--n:{len(bars)}">
          <figcaption class="chart-caption">{esc(featured)} plan, {unit}<span class="chart-key"></span></figcaption>
          <div class="chart-columns">{cols}</div>
          <div class="chart-dates">{dates}</div>
        </figure>"""
    return f"""      <section class="prices">
        <h2 class="section-title">{esc(service.name)} prices now (US)</h2>
        <div class="plan-grid">{"".join(cards)}</div>{chart}
        <a class="price-cta" href="{esc(app_store_url(site, "seo-" + service.slug))}">{esc(CHART_LINK)}</a>
      </section>
"""


def _faq_html(service: Service, us: list[Change], today: date) -> str:
    items = "".join(f'<div class="faq-item"><dt>{esc(q)}</dt><dd>{esc(fill_prices(a, us, today))}</dd></div>'
                    for q, a in service.faq)
    return f"""      <section class="faq">
        <h2 class="section-title">Common questions</h2>
        <dl class="faq-list">{items}</dl>
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


def service_page(site: SiteConfig, service: Service, us: list[Change], today: date) -> str:
    has_prices = service.headline_plan is not None and bool(us)
    year = service.checked[:4]
    title = (f"How to cancel {service.name} ({year}): steps and current prices | Paydar" if has_prices
             else f"How to cancel {service.name} ({year}): step by step | Paydar")
    description = service.fastest_text + (" Steps, current US prices and price history." if has_prices
                                          else " Step-by-step guide.")
    steps = "".join(f"<li><p>{esc(s)}</p></li>" for s in service.steps)
    body = (f"      <h1 class=\"page-title\">How to cancel {esc(service.name)}</h1>\n"
            f"      <p class=\"page-meta\">Checked {_checked(service)} · {read_minutes(service)} min read</p>\n"
            + _tag_html(service, us, today)
            + _fastest_html(service)
            + f"      <ol class=\"steps\">{steps}</ol>\n"
            + _notes_html(service)
            + _paydar_card(site, "seo-" + service.slug, f"{service.name} is one. What about the rest?", CARD_TEXT) + "\n"
            + _prices_html(site, service, us, today)
            + _faq_html(service, us, today)
            + _sources_html(service, us))
    return _shell(site, title=title, description=description, path=f"/cancel/{service.slug}/",
                  ct="seo-" + service.slug, body=body, footer_note=f"Not affiliated with {service.name}.")


def increases_page(site: SiteConfig, services: list[Service], us_all: list[Change], today: date) -> str:
    names = {s.service_id: s.name for s in services}
    slugs = {s.service_id: s.slug for s in services}
    upcoming, past = increase_rows(us_all, names, today)

    def name_html(sid: str, cls: str) -> str:
        label = esc(names.get(sid) or sid.replace("-", " ").title())
        return f'<a class="{cls}" href="/cancel/{esc(slugs[sid])}/">{label}</a>' if sid in slugs else f'<span class="{cls}">{label}</span>'

    def sources_html(sources: list[str]) -> str:
        label = "Source" if len(sources) == 1 else "Sources"
        return f"{label}: " + ", ".join(_source_link(s) for s in sources)

    def lines_html(lines: list[str]) -> str:
        return "".join(f"<li>{esc(line)}</li>" for line in lines)

    if upcoming:
        coming = "".join(
            f'<div class="upcoming-card"><h3 class="service-heading">{name_html(r.service_id, "row-name")}</h3>'
            f'<p class="upcoming-date">{esc(r.when)}</p><ul class="row-lines">{lines_html(r.lines)}</ul>'
            f'<p class="row-source">{sources_html(r.sources)}</p></div>'
            for r in upcoming)
    else:
        coming = '<p class="empty">No announced increases right now.</p>'
    recent = "".join(
        f'<div class="recent-row"><div class="recent-top">{name_html(r.service_id, "recent-name")}'
        f'<time datetime="{r.effective.isoformat()}">{esc(r.when)}</time></div>'
        f'<ul class="row-lines">{lines_html(r.lines)}</ul>'
        f'<p class="row-source">{sources_html(r.sources)}</p></div>'
        for r in past)
    updated = f"{MONTHS[today.month - 1][:3]} {today.day}, {today.year}"
    body = f"""      <h1 class="page-title">Subscription price increases (US)</h1>
      <p class="page-meta">Updated {updated}</p>
      <section class="upcoming">
        <h2 class="feed-heading">Coming up</h2>
        {coming}
      </section>
{_paydar_card(site, "seo-price-increases", "Get pinged before the next one.", "Paydar tracks every subscription and flags announced price increases before they hit your card.")}
      <section class="recent">
        <h2 class="feed-heading">Recently</h2>
        <div class="recent-list">{recent}</div>
      </section>"""
    return _shell(site, title="Subscription price increases (US) | Paydar",
                  description="Every recent and announced US subscription price increase, with sources. Updated daily.",
                  path="/price-increases/", ct="seo-price-increases", body=body)


def home_page(site: SiteConfig, services: list[Service]) -> str:
    guides = "".join(f'<li><a href="/cancel/{esc(s.slug)}/">How to cancel {esc(s.name)}</a></li>' for s in services)
    body = f"""      <section class="home-hero">
        <img src="/icon.png" alt="Paydar app icon" width="112" height="112">
        <h1 class="page-title">Paydar</h1>
        <p class="home-pitch">Subscription tracker with renewal reminders. Every subscription on one radar, a heads-up before each charge.</p>
        <a class="cta-button home-cta" href="{esc(app_store_url(site, "seo-home"))}">Download on the App Store {ICON_NEXT}</a>
        <p class="home-small">Support: <a href="mailto:{esc(site.support_email)}">{esc(site.support_email)}</a> · <a href="{esc(site.privacy_url)}">Privacy Policy</a> · Formerly Subsly.</p>
      </section>
      <section class="home-section">
        <h2 class="section-title">Subscription price increases</h2>
        <p><a class="text-link" href="/price-increases/">Every recent and announced US price increase →</a></p>
      </section>
      <section class="home-section">
        <h2 class="section-title">Cancel guides</h2>
        <ul class="guide-list">{guides}</ul>
      </section>"""
    return _shell(site, title="Paydar - Subscription Tracker",
                  description="Subscription tracker with renewal reminders. Every subscription on one radar, a heads-up before each charge.",
                  path="/", ct="seo-home", body=body)
