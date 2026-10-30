import json
import unittest
from pathlib import Path

from sitegen.radar import aura_radius, place

FIXTURES = Path(__file__).parent / "fixtures"


class RadarTest(unittest.TestCase):
    def test_matches_the_app(self):
        # The app's own fixture (PaydarKitTests/Fixtures/radar.json), from the 1.x TypeScript.
        for case in json.loads((FIXTURES / "radar.json").read_text())["cases"]:
            got = place([(i["id"], i["days"]) for i in case["input"]["items"]])
            want = case["output"]
            self.assertEqual(list(got), [w["id"] for w in want])
            for w in want:
                angle, r = got[w["id"]]
                self.assertAlmostEqual(angle, w["angle"], places=9, msg=w["id"])
                self.assertAlmostEqual(r, w["r"], places=12, msg=w["id"])

    def test_aura_scale(self):
        self.assertAlmostEqual(aura_radius(0), 0.2)
        self.assertAlmostEqual(aura_radius(30), 1.0)
        self.assertAlmostEqual(aura_radius(45), 1.0)


if __name__ == "__main__":
    unittest.main()
