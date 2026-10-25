import json
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from datetime import date
from pathlib import Path

from sitegen.content import SiteConfig, load_services
from sitegen.site import build_site

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).parent / "fixtures"
TODAY = date(2026, 10, 25)
SITE = SiteConfig(base_url="https://getpaydarapp.com", app_id="6786868155", provider_token="123",
                  privacy_url="https://gist.github.com/x/privacy", support_email="help@example.com",
                  prices_url="https://example.com/prices.json")
PRICES = json.loads((FIXTURES / "prices.json").read_text())
SERVICES = load_services(FIXTURES / "services" / "valid")


class BuildSiteTest(unittest.TestCase):
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

    def test_warnings(self):
        netflix = replace(SERVICES[1], checked="2026-01", headline_plan="Ultra")
        with tempfile.TemporaryDirectory() as tmp:
            warnings = build_site(Path(tmp), replace(SITE, provider_token=""), [SERVICES[0], netflix], PRICES, TODAY,
                                  ROOT / "static")
        self.assertIn("STALE netflix: checked 2026-01", warnings)
        self.assertIn("NO PROVIDER TOKEN: App Store links carry no campaign", warnings)
        self.assertIn("HEADLINE NOT FOUND netflix: Ultra monthly", warnings)
        self.assertIn("NO PAGE for US service discovery-plus", warnings)

    def test_no_warnings_when_all_is_well(self):
        with tempfile.TemporaryDirectory() as tmp:
            warnings = build_site(Path(tmp), SITE, SERVICES, PRICES, TODAY, ROOT / "static")
        self.assertEqual(warnings, ["NO PAGE for US service discovery-plus"])


class CliTest(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-I", str(ROOT / "tools" / "build.py"), *args],
                              capture_output=True, text=True, cwd=ROOT)

    def test_unreachable_prices_exits_1_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "marker.txt"
            marker.write_text("keep")
            result = self.run_cli("--prices", "/nonexistent/prices.json", "--out", tmp)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertTrue(marker.exists())
            self.assertFalse((Path(tmp) / "index.html").exists())

    def test_invalid_prices_exits_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text('{"changes": {}}')
            out = Path(tmp) / "out"
            result = self.run_cli("--prices", str(bad), "--out", str(out))
            self.assertEqual(result.returncode, 1)
            self.assertFalse(out.exists())

    def test_builds_from_local_prices(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "site"
            result = self.run_cli("--prices", str(FIXTURES / "prices.json"), "--out", str(out), "--today", "2026-10-25")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((out / "cancel" / "netflix" / "index.html").is_file())
            self.assertIn("service pages into", result.stdout)


if __name__ == "__main__":
    unittest.main()
