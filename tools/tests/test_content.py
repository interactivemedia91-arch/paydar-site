import unittest
from pathlib import Path

from sitegen.content import ContentError, load_services, load_site

FIXTURES = Path(__file__).parent / "fixtures" / "services"


class ContentTest(unittest.TestCase):
    def test_loads_valid_service(self):
        services = load_services(FIXTURES / "valid")
        self.assertEqual([s.name for s in services], ["Amazon Prime", "Netflix"])
        nf = services[1]
        self.assertEqual(len(nf.steps), 4)
        self.assertIsInstance(nf.steps, tuple)
        self.assertEqual(nf.faq[0], ("Do I keep watching after I cancel?", "Yes, until the end of your current billing period."))
        self.assertEqual((nf.headline_plan, nf.headline_frequency), ("Standard", "monthly"))
        self.assertEqual(nf.fastest_url, "https://www.netflix.com/cancelplan")
        self.assertTrue(nf.apple_billed)

    def test_optional_fields(self):
        prime = load_services(FIXTURES / "valid")[0]
        self.assertIsNone(prime.headline_plan)
        self.assertIsNone(prime.note)
        self.assertEqual(prime.plan_aliases, {})

    def test_reports_every_problem_at_once(self):
        with self.assertRaises(ContentError) as cm:
            load_services(FIXTURES / "bad")
        msg = str(cm.exception)
        self.assertIn("badsvc.json: slug", msg)
        self.assertIn("badsvc.json: steps", msg)
        self.assertIn("badsvc.json: cancelSources[0].url", msg)

    def test_duplicate_slug(self):
        with self.assertRaises(ContentError) as cm:
            load_services(FIXTURES / "dup")
        self.assertIn("duplicate slug 'same'", str(cm.exception))

    def test_service_id_must_match_file_name(self):
        with self.assertRaises(ContentError) as cm:
            load_services(FIXTURES / "mismatch")
        self.assertIn("foo.json: serviceId", str(cm.exception))

    def test_real_content_dir_is_valid(self):
        self.assertTrue(load_services(Path(__file__).resolve().parents[2] / "content" / "services"))

    def test_site_config(self):
        site = load_site(Path(__file__).resolve().parents[2] / "content" / "site.json")
        self.assertEqual((site.base_url, site.app_id), ("https://getpaydarapp.com", "6786868155"))
        self.assertEqual(site.prices_url, "https://interactivemedia91-arch.github.io/prices.json")


if __name__ == "__main__":
    unittest.main()
