import json
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from datetime import date
from pathlib import Path

from sitegen.content import SiteConfig, load_services
from sitegen.site import BuildError, build_site

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).parent / "fixtures"
TODAY = date(2026, 10, 25)
SITE = SiteConfig(base_url="https://getpaydarapp.com", app_id="6786868155", provider_token="123",
                  privacy_url="https://gist.github.com/x/privacy", support_email="help@example.com",
                  prices_url="https://example.com/prices.json")
PRICES = json.loads((FIXTURES / "prices.json").read_text())
SERVICES = load_services(FIXTURES / "services" / "valid")
PRIME, NETFLIX = SERVICES


class BuildSiteTest(unittest.TestCase):
    def build(self, services=SERVICES, site=SITE, prices=PRICES):
        with tempfile.TemporaryDirectory() as tmp:
            return build_site(Path(tmp), site, services, prices, TODAY, ROOT / "static")

    def test_builds_all_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            build_site(out, SITE, SERVICES, PRICES, TODAY, ROOT / "static")
            for rel in ("index.html", "price-increases/index.html", "cancel/netflix/index.html",
                        "cancel/amazon-prime/index.html", "site.css", "icon.png", "robots.txt"):
                self.assertTrue((out / rel).is_file(), rel)
            sitemap = (out / "sitemap.xml").read_text()
            for loc in ("https://getpaydarapp.com/", "https://getpaydarapp.com/price-increases/",
                        "https://getpaydarapp.com/cancel/netflix/", "https://getpaydarapp.com/cancel/amazon-prime/"):
                self.assertIn(f"<loc>{loc}</loc>", sitemap)
            self.assertIn("<lastmod>2026-10-01</lastmod>", sitemap)  # netflix checked 2026-10
            self.assertIn("Sitemap: https://getpaydarapp.com/sitemap.xml", (out / "robots.txt").read_text())
            self.assertIn("Standard is now $19.99/mo", (out / "cancel/netflix/index.html").read_text())
            self.assertEqual([f for f in out.rglob("*") if f.name.endswith(".json") or f.name == ".DS_Store"], [])

    def test_warnings(self):
        warnings = self.build(services=[PRIME, replace(NETFLIX, checked="2026-01")],
                              site=replace(SITE, provider_token=""))
        self.assertIn("STALE netflix: checked 2026-01", warnings)
        self.assertIn("NO PROVIDER TOKEN: App Store links carry no campaign", warnings)
        self.assertIn("NO PAGE for US service discovery-plus", warnings)

    def test_no_warnings_when_all_is_well(self):
        self.assertEqual(self.build(), ["NO PAGE for US service discovery-plus"])

    def test_missing_headline_is_fatal(self):
        with self.assertRaises(BuildError) as cm:
            self.build(services=[PRIME, replace(NETFLIX, headline_plan="Ultra")])
        self.assertIn("HEADLINE NOT FOUND netflix: Ultra monthly", str(cm.exception))

    def test_faq_price_without_data_is_fatal(self):
        faq = NETFLIX.faq + (("Cheaper?", "{price:Basic}"),)
        with self.assertRaises(BuildError) as cm:
            self.build(services=[PRIME, replace(NETFLIX, faq=faq)])
        self.assertIn("PRICE NOT FOUND netflix", str(cm.exception))

    def test_no_us_changes_is_fatal(self):
        only_de = {"changes": [c for c in PRICES["changes"] if c["country"] != "US"]}
        with self.assertRaises(BuildError):
            self.build(prices=only_de)


class CliTest(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-I", str(ROOT / "tools" / "build.py"),
                               "--content", str(FIXTURES / "content"), "--today", "2026-10-25", *args],
                              capture_output=True, text=True)

    def assert_untouched(self, out: Path, result):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertTrue((out / "marker.txt").exists())
        self.assertFalse((out / "index.html").exists())
        self.assertFalse(out.with_name(out.name + ".building").exists())

    def out_with_marker(self, tmp: str) -> Path:
        out = Path(tmp) / "site"
        out.mkdir()
        (out / "marker.txt").write_text("previous build")
        return out

    def test_unreachable_prices_exits_1_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.out_with_marker(tmp)
            self.assert_untouched(out, self.run_cli("--prices", "/nonexistent/prices.json", "--out", str(out)))

    def test_invalid_prices_exits_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text('{"changes": {}}')
            out = self.out_with_marker(tmp)
            self.assert_untouched(out, self.run_cli("--prices", str(bad), "--out", str(out)))

    def test_prices_without_us_data_exits_1_and_keeps_previous_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            empty = Path(tmp) / "empty.json"
            empty.write_text('{"changes": []}')
            out = self.out_with_marker(tmp)
            self.assert_untouched(out, self.run_cli("--prices", str(empty), "--out", str(out)))

    def test_builds_from_local_prices(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.out_with_marker(tmp)
            result = self.run_cli("--prices", str(FIXTURES / "prices.json"), "--out", str(out))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((out / "cancel" / "netflix" / "index.html").is_file())
            self.assertFalse((out / "marker.txt").exists())  # the old build was replaced
            self.assertIn("NO PAGE for US service discovery-plus", result.stdout)


if __name__ == "__main__":
    unittest.main()
