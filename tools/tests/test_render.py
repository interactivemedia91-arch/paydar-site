import json
import re
import unittest
from html.parser import HTMLParser
from dataclasses import replace
from datetime import date
from pathlib import Path

from sitegen.content import SiteConfig, load_catalog, load_services
from sitegen.prices import parse_changes, us_changes
from sitegen.render import app_store_url, home_page, increases_page, read_minutes, service_page

ROOT = Path(__file__).resolve().parents[2]

TODAY = date(2026, 10, 25)
SITE = SiteConfig(base_url="https://getpaydarapp.com", app_id="6786868155", provider_token="123",
                  privacy_url="https://gist.github.com/x/privacy", support_email="help@example.com",
                  prices_url="https://example.com/prices.json")


def _c(id_, sid, plan, old, new, eff, src="https://www.droid-life.com/2026/03/26/netflix/"):
    return {"id": id_, "serviceId": sid, "plan": plan, "country": "US", "currency": "USD", "frequency": "monthly",
            "from": old, "to": new, "effective": eff, "source": src}


CHANGES = parse_changes({"changes": [
    _c("n1", "netflix", "Standard with ads", 6.99, 7.99, "2025-01-21", "https://nerdist.com/article/netflix/"),
    _c("n2", "netflix", "Standard", 15.49, 17.99, "2025-01-21", "https://nerdist.com/article/netflix/"),
    _c("n3", "netflix", "Premium", 22.99, 24.99, "2025-01-21", "https://nerdist.com/article/netflix/"),
    _c("n4", "netflix", "Standard with ads", 7.99, 8.99, "2026-03-26"),
    _c("n5", "netflix", "Standard", 17.99, 19.99, "2026-03-26"),
    _c("n6", "netflix", "Premium", 24.99, 26.99, "2026-03-26"),
    _c("d1", "discovery-plus", "Ad-free", 9.99, 11.99, "2026-11-12", "https://example.com/discovery"),
    _c("u1", "unknown-service", "Basic", 5.0, 6.0, "2026-05-01", "https://example.com/unknown"),
]})
SERVICES = load_services(Path(__file__).parent / "fixtures" / "services" / "valid")
PRIME, NETFLIX = SERVICES


class _Faq(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tag, self.pairs = None, []

    def handle_starttag(self, tag, attrs):
        if tag in ("dt", "dd"):
            self.tag = tag
            if tag == "dt":
                self.pairs.append(["", ""])

    def handle_endtag(self, tag):
        self.tag = None

    def handle_data(self, data):
        if self.tag:
            self.pairs[-1][self.tag == "dd"] += data


def _faq_text(html):
    parser = _Faq()
    parser.feed(html[html.index('class="faq-list'):])
    return [tuple(p) for p in parser.pairs]


def netflix_page(site=SITE, service=NETFLIX):
    return service_page(site, service, us_changes(CHANGES, "netflix", {}), TODAY)


class ServicePageTest(unittest.TestCase):
    def test_service_sections_in_spec_order(self):
        html = netflix_page()
        marks = ["How to cancel Netflix</h1>", "Checked October 2026 · 1 min read",
                 "Standard is now $19.99/mo · +$2 since March", "Fastest way", "<ol", "Paying through Apple?",
                 "Netflix is one. What about the rest?", "Netflix prices now (US)", "Paydar flags increases",
                 "Do I keep watching after I cancel?", "Sources", "Not affiliated with Netflix."]
        body = html[html.index("<body"):]  # the head's JSON-LD repeats the questions
        positions = [body.find(m) for m in marks]
        self.assertNotIn(-1, positions, dict(zip(marks, positions)))
        self.assertEqual(positions, sorted(positions))

    def test_campaign_links(self):
        self.assertIn("https://apps.apple.com/app/apple-store/id6786868155?pt=123&amp;ct=seo-netflix&amp;mt=8", netflix_page())
        html = netflix_page(site=replace(SITE, provider_token=""))
        self.assertIn("https://apps.apple.com/app/id6786868155", html)
        self.assertNotIn("ct=", html)

    def test_app_store_url(self):
        self.assertEqual(app_store_url(SITE, "seo-home"),
                         "https://apps.apple.com/app/apple-store/id6786868155?pt=123&ct=seo-home&mt=8")

    def test_head_tags(self):
        html = netflix_page()
        self.assertIn('<link rel="canonical" href="https://getpaydarapp.com/cancel/netflix/">', html)
        self.assertIn('<meta name="apple-itunes-app" content="app-id=6786868155">', html)
        self.assertRegex(html, r"<title>How to cancel Netflix \(2026\)")

    def test_escapes_content(self):
        self.assertIn("Membership &amp; Billing", netflix_page())
        evil = replace(NETFLIX, steps=("Click <b>here</b>", "Two", "Three"))
        html = netflix_page(service=evil)
        self.assertIn("Click &lt;b&gt;here&lt;/b&gt;", html)
        self.assertNotIn("<b>here", html)

    def test_cards_chart_and_sources(self):
        html = netflix_page()
        for text in ("$8.99", "$19.99", "$26.99", "Before Jan 2025", "Mar 2026", "nerdist.com", "droid-life.com",
                     "https://help.netflix.com/en/node/407"):
            self.assertIn(text, html)

    def test_service_without_us_data(self):
        html = service_page(SITE, PRIME, [], TODAY)
        self.assertNotIn("price-alert", html)
        self.assertNotIn("prices now (US)", html)
        self.assertIn("<ol", html)
        self.assertIn("Amazon Prime is one. What about the rest?", html)

    def test_upcoming_bar_class_does_not_collide_with_page_sections(self):
        # ".upcoming" styles the price-increases section; a bar wearing it got pushed out of the chart.
        discovery = replace(NETFLIX, service_id="discovery-plus", name="Discovery+", slug="discovery-plus",
                            headline_plan="Ad-free")
        html = service_page(SITE, discovery, us_changes(CHANGES, "discovery-plus", {}), TODAY)
        self.assertIn('class="chart-column is-upcoming"', html)
        self.assertNotIn('class="bar upcoming"', html)
        self.assertIn("(announced)", html)  # the screen-reader table marks the announced price
        self.assertIn('<div class="sr-only"><table>', html)  # a bare sr-only table widens the page
        self.assertIn('class="key key-next">Announced', html)

    def test_chart_without_announced_price_has_no_legend(self):
        html = netflix_page()
        self.assertIn('class="price-chart', html)
        self.assertNotIn("key-next", html)

    def test_read_minutes(self):
        self.assertEqual(read_minutes(NETFLIX), 1)
        long = replace(NETFLIX, steps=tuple(["word " * 150] * 3))
        self.assertEqual(read_minutes(long), 3)


class OtherPagesTest(unittest.TestCase):
    def test_increases_page_links_and_order(self):
        us_all = [c for c in CHANGES if c.country == "US"]
        html = increases_page(SITE, SERVICES, us_all, TODAY)
        self.assertLess(html.find("Coming up"), html.find("Recently"))
        self.assertIn("Updated Oct 25, 2026", html)
        self.assertIn('href="/cancel/netflix/"', html)
        self.assertIn("Unknown Service", html)
        self.assertNotIn('href="/cancel/unknown-service/"', html)
        self.assertIn("ct=seo-price-increases", html)

    def test_home_page(self):
        html = home_page(SITE, SERVICES)
        self.assertIn('href="/cancel/amazon-prime/"', html)
        self.assertIn('href="/cancel/netflix/"', html)
        self.assertIn('href="/price-increases/"', html)
        self.assertIn("ct=seo-home", html)
        self.assertNotIn("Subsly", html)
        self.assertIn('href="https://gist.github.com/x/privacy">Privacy</a>', html)
        self.assertIn('<link rel="canonical" href="https://getpaydarapp.com/">', html)

    def test_home_page_chips_start_with_four_picked(self):
        catalog = load_catalog(ROOT / "content" / "catalog.json")
        html = home_page(SITE, SERVICES, catalog, [c for c in CHANGES if c.country == "US"], TODAY)
        self.assertEqual(html.count('aria-pressed="true"'), 4)
        picked = [catalog.brands[sid].price for sid in catalog.home_chips[:4]]
        self.assertIn(f"${sum(picked):,.2f}", html)
        self.assertEqual(html.count('class="blip"'), 4)
        self.assertIn('"@type": "MobileApplication"', html)

    def test_home_page_hero_arrives_in_order_and_the_pro_hint_sits_under_the_radar(self):
        catalog = load_catalog(ROOT / "content" / "catalog.json")
        html = home_page(SITE, SERVICES, catalog)
        order = [int(i) for i in re.findall(r'style="--i:(\d+)"', html)]
        self.assertEqual(order, list(range(6 + len(catalog.home_chips))))
        self.assertLess(html.index('class="radar"'), html.index('class="pro-hint"'))

    def test_structured_data(self):
        blocks = lambda html: [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html)]
        home = blocks(home_page(SITE, SERVICES))
        self.assertEqual([b["@type"] for b in home], ["WebSite", "Organization", "MobileApplication"])
        self.assertNotIn("aggregateRating", json.dumps(home))
        priced = (("Is there a cheaper plan?", 'Standard with ads, {price:Standard with ads}: the same shows & "most" films, with ads.'),)
        html = netflix_page(service=replace(NETFLIX, faq=NETFLIX.faq[:3] + priced))
        article, faq = blocks(html)
        self.assertEqual((article["@type"], faq["@type"]), ("Article", "FAQPage"))
        self.assertEqual(article["publisher"]["@id"], home[1]["@id"])
        # Every question and answer is the page's visible text, decoded, word for word.
        shown = _faq_text(html[html.index("<body"):])
        self.assertEqual(shown, [(q["name"], q["acceptedAnswer"]["text"]) for q in faq["mainEntity"]])
        self.assertIn(("Is there a cheaper plan?", 'Standard with ads, $8.99/mo: the same shows & "most" films, with ads.'),
                      shown)
        for text in json.dumps([article, faq], ensure_ascii=False), json.dumps(home, ensure_ascii=False):
            for leak in ("&amp;", "&#", "&quot;", "{price", "{monthly", "{yearly"):
                self.assertNotIn(leak, text)

    def test_script_blocks_cannot_be_closed_by_content(self):
        tricky = replace(NETFLIX, faq=NETFLIX.faq[:3] + (("Odd?", "Type <!--<script> or </script> here."),))
        html = service_page(SITE, tricky, us_changes(CHANGES, "netflix", {}), TODAY)
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
            self.assertNotIn("<", block)
            json.loads(block)
        self.assertIn("<h1", html[html.index("<body"):])

    def test_gsap_is_not_in_the_markup(self):
        # motion.js loads it on the homepage only when motion is allowed.
        for html in (netflix_page(), home_page(SITE, SERVICES)):
            self.assertNotIn("gsap", html)
            self.assertNotIn("ScrollTrigger", html)

    def test_only_local_scripts_and_no_external_assets(self):
        us_all = [c for c in CHANGES if c.country == "US"]
        for html in (netflix_page(), increases_page(SITE, SERVICES, us_all, TODAY), home_page(SITE, SERVICES)):
            for tag in re.findall(r"<script[^>]*>", html):
                self.assertTrue(re.fullmatch(r'<script src="/[\w.]+\.js" defer>', tag)
                                or tag in ('<script type="application/ld+json">',
                                           '<script type="application/json" id="home-data">'), tag)
            self.assertNotIn("<iframe", html)
            self.assertNotIn("@import", html)
            for src in re.findall(r'src="([^"]+)"', html):
                self.assertTrue(src.startswith("/"), src)
            for href in re.findall(r'<link rel="stylesheet" href="([^"]+)"', html):
                self.assertTrue(href.startswith("/"), href)


if __name__ == "__main__":
    unittest.main()
