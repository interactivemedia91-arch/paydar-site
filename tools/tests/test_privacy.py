import unittest
from datetime import date

from sitegen.content import SiteConfig
from sitegen.render import markdown_html, privacy_page
from sitegen.site import _policy_date, _sitemap

SITE = SiteConfig(base_url="https://getpaydarapp.com", app_id="6786868155", provider_token="123",
                  privacy_url="/privacy/", support_email="help@example.com", prices_url="https://example.com/p.json")
POLICY = """## Privacy Policy

_Last updated: 25 October 2026_

### The short version

- Paydar has **no account**. See https://policies.google.com/privacy.
- Rates come from `open.er-api.com`.
"""


class PrivacyTest(unittest.TestCase):
    def test_page_demotes_headings_and_drops_the_duplicate_title(self):
        html = privacy_page(SITE, POLICY)
        self.assertEqual(html.count("Privacy Policy</h"), 1)  # only the page's h1
        self.assertIn("<h2>The short version</h2>", html)
        self.assertIn("<strong>no account</strong>", html)
        self.assertIn('<a href="https://policies.google.com/privacy">https://policies.google.com/privacy</a>.', html)
        self.assertIn("<code>open.er-api.com</code>", html)
        self.assertIn("<em>Last updated: 25 October 2026</em>", html)

    def test_markdown_escapes_html(self):
        html = markdown_html('<script>alert(1)</script> and https://x.example/a_b_c"onmouseover=1')
        self.assertNotIn("<script>", html)
        self.assertNotIn('"onmouseover', html)
        self.assertIn('href="https://x.example/a_b_c"', html)  # an underscore in a URL is not italics

    def test_crlf_files_still_drop_the_title(self):
        html = privacy_page(SITE, POLICY.replace("\n", "\r\n"))
        self.assertEqual(html.count("Privacy Policy</h"), 1)

    def test_policy_date_dates_the_sitemap_entry(self):
        today = date(2026, 10, 29)
        self.assertEqual(_policy_date(POLICY, today), date(2026, 10, 25))
        self.assertEqual(_policy_date("no date here", today), today)
        self.assertIn("<loc>https://getpaydarapp.com/privacy/</loc><lastmod>2026-10-25</lastmod>",
                      _sitemap(SITE, [], today, POLICY))
        self.assertNotIn("/privacy/", _sitemap(SITE, [], today, None))


if __name__ == "__main__":
    unittest.main()
