import unittest
from datetime import date

from sitegen.prices import (
    Change, chart_bars, increase_rows, money, parse_changes, per, plan_cards, price_tag, signed, us_changes,
)

TODAY = date(2026, 10, 25)


def ch(plan, freq, old, new, eff, approx=False, sid="x"):
    return Change(id=f"{sid}-{plan}-{freq}-{eff}", service_id=sid, plan=plan, country="US", currency="USD",
                  frequency=freq, old=old, new=new, effective=date.fromisoformat(eff), approx_month=approx,
                  source="https://example.com/source")


class FormattingTest(unittest.TestCase):
    def test_money(self):
        self.assertEqual(money(19.99), "$19.99")
        self.assertEqual(money(119.0), "$119")
        self.assertEqual(money(44), "$44")

    def test_signed(self):
        self.assertEqual(signed(2.0), "+$2")
        self.assertEqual(signed(2.5), "+$2.50")
        self.assertEqual(signed(-7.0), "−$7")
        # float noise from subtraction must not leak into the text
        self.assertEqual(signed(19.99 - 17.99), "+$2")

    def test_per(self):
        self.assertEqual(per("monthly"), "/mo")
        self.assertEqual(per("annual"), "/yr")


class TagTest(unittest.TestCase):
    def test_recent_increase_tag(self):  # Netflix Standard
        cs = [ch("Standard", "monthly", 15.49, 17.99, "2025-01-21"), ch("Standard", "monthly", 17.99, 19.99, "2026-03-26")]
        t = price_tag(cs, "Standard", "monthly", "Netflix", TODAY)
        self.assertEqual((t.kind, t.text), ("up", "Standard is now $19.99/mo · +$2 since March"))

    def test_upcoming_flips_on_effective_date(self):  # Discovery+ Ad-free
        cs = [ch("Ad-free", "monthly", 9.99, 11.99, "2026-11-12")]
        self.assertEqual(price_tag(cs, "Ad-free", "monthly", "Discovery+", date(2026, 11, 11)).text,
                         "Goes up to $11.99/mo on Nov 12")
        self.assertEqual(price_tag(cs, "Ad-free", "monthly", "Discovery+", date(2026, 11, 12)).text,
                         "Ad-free is now $11.99/mo · +$2 since November")

    def test_upcoming_month_only(self):
        cs = [ch("Ad-free", "monthly", 9.99, 11.99, "2026-11-01", approx=True)]
        self.assertEqual(price_tag(cs, "Ad-free", "monthly", "Discovery+", TODAY).text,
                         "Goes up to $11.99/mo in November 2026")

    def test_upcoming_decrease(self):
        cs = [ch("Ultimate", "monthly", 29.99, 22.99, "2026-12-01")]
        t = price_tag(cs, "Ultimate", "monthly", "Xbox Game Pass", TODAY)
        self.assertEqual((t.kind, t.text), ("down", "Drops to $22.99/mo on Dec 1"))

    def test_old_change_gives_flat_tag(self):  # Microsoft 365 Personal, 2025-01-16
        cs = [ch("Personal", "monthly", 6.99, 9.99, "2025-01-16")]
        t = price_tag(cs, "Personal", "monthly", "Microsoft 365", TODAY)
        self.assertEqual((t.kind, t.text), ("flat", "Personal: $9.99/mo"))

    def test_no_changes_no_tag(self):
        self.assertIsNone(price_tag([], "Standard", "monthly", "Netflix", TODAY))
        cs = [ch("Premium", "monthly", 22.99, 24.99, "2025-01-21")]
        self.assertIsNone(price_tag(cs, "Standard", "monthly", "Netflix", TODAY))

    def test_decrease_tag_and_not_listed(self):  # Xbox Ultimate
        cs = [ch("Ultimate", "monthly", 19.99, 29.99, "2025-10-04", sid="xbox-game-pass"),
              ch("Ultimate", "monthly", 29.99, 22.99, "2026-04-22", sid="xbox-game-pass")]
        t = price_tag(cs, "Ultimate", "monthly", "Xbox Game Pass", TODAY)
        self.assertEqual((t.kind, t.text), ("down", "Ultimate is now $22.99/mo · −$7 since April"))
        up, past = increase_rows(cs, {"xbox-game-pass": "Xbox Game Pass"}, TODAY)
        self.assertEqual(up, [])
        self.assertEqual([r.effective for r in past], [date(2025, 10, 4)])

    def test_missing_plan_uses_service_name(self):  # Apple TV
        cs = [ch("", "monthly", 12.99, 14.99, "2026-08-28")]
        self.assertEqual(price_tag(cs, "", "monthly", "Apple TV", TODAY).text,
                         "Apple TV is now $14.99/mo · +$2 since August")
        self.assertEqual(plan_cards(cs, "Apple TV", TODAY)[0].label, "Apple TV")


class CardsAndChartTest(unittest.TestCase):
    def test_monthly_and_annual_share_a_card(self):  # Peacock Premium
        cs = [ch("Premium", "monthly", 10.99, 12.99, "2026-09-17"), ch("Premium", "annual", 109.99, 129.99, "2026-09-17")]
        [c] = plan_cards(cs, "Peacock", TODAY)
        self.assertEqual((c.price, c.yearly, c.badge, c.badge_kind), ("$12.99/mo", "or $129.99/yr", "+$2", "up"))
        self.assertEqual([b.value for b in chart_bars(cs, "Premium", "monthly", TODAY)], [10.99, 12.99])

    def test_annual_only_plan(self):
        cs = [ch("Yearly", "annual", 99.0, 119.0, "2026-08-28")]
        [c] = plan_cards(cs, "X", TODAY)
        self.assertEqual((c.price, c.yearly), ("$119/yr", None))

    def test_card_order_and_upcoming_badge(self):  # Discovery+
        cs = [ch("Ad-free", "monthly", 8.99, 9.99, "2025-02-07"), ch("With ads", "monthly", 4.99, 5.99, "2025-02-07"),
              ch("Ad-free", "monthly", 9.99, 11.99, "2026-11-12"), ch("With ads", "monthly", 5.99, 6.99, "2026-11-12")]
        cards = plan_cards(cs, "Discovery+", TODAY)
        self.assertEqual([(c.label, c.price, c.badge) for c in cards],
                         [("Ad-free", "$9.99/mo", "→ $11.99 on Nov 12"), ("With ads", "$5.99/mo", "→ $6.99 on Nov 12")])

    def test_only_upcoming_uses_old_price(self):
        cs = [ch("Ad-free", "monthly", 9.99, 11.99, "2026-11-12")]
        self.assertEqual(plan_cards(cs, "Discovery+", TODAY)[0].price, "$9.99/mo")
        bars = chart_bars(cs, "Ad-free", "monthly", TODAY)
        self.assertEqual([(b.label, b.value, b.upcoming) for b in bars],
                         [("Before Nov 2026", 9.99, False), ("Nov 2026", 11.99, True)])

    def test_aliases_join_renamed_plan(self):  # ESPN
        raw = parse_changes({"changes": [
            {"id": "a", "serviceId": "espn-plus", "plan": "ESPN+ / Select", "country": "US", "currency": "USD",
             "frequency": "monthly", "from": 11.99, "to": 12.99, "effective": "2025-10-21", "source": "s"},
            {"id": "b", "serviceId": "espn-plus", "plan": "ESPN Select", "country": "US", "currency": "USD",
             "frequency": "monthly", "from": 12.99, "to": 13.99, "effective": "2026-09-17", "source": "s"}]})
        cs = us_changes(raw, "espn-plus", {"ESPN+ / Select": "ESPN Select"})
        self.assertEqual([c.label for c in plan_cards(cs, "ESPN", TODAY)], ["ESPN Select"])
        self.assertEqual([b.label for b in chart_bars(cs, "ESPN Select", "monthly", TODAY)],
                         ["Before Oct 2025", "Oct 2025", "Sep 2026"])


class RowsTest(unittest.TestCase):
    def test_month_only_date(self):  # Peloton
        cs = [ch("All-Access", "monthly", 44, 49.99, "2025-10-01", approx=True)]
        up, past = increase_rows(cs, {"x": "Peloton"}, TODAY)
        self.assertEqual(past[0].when, "October 2025")

    def test_rows_grouped_and_ordered(self):
        cs = [ch("Ad-free", "monthly", 9.99, 11.99, "2026-11-12", sid="discovery-plus"),
              ch("With ads", "monthly", 5.99, 6.99, "2026-11-12", sid="discovery-plus"),
              ch("Premium", "monthly", 18.99, 21.49, "2026-10-21", sid="disney-plus"),
              ch("Standard", "monthly", 17.99, 19.99, "2026-03-26", sid="netflix")]
        names = {"discovery-plus": "Discovery+", "disney-plus": "Disney+", "netflix": "Netflix"}
        up, past = increase_rows(cs, names, TODAY)
        self.assertEqual([(r.service_id, r.when, r.lines) for r in up],
                         [("discovery-plus", "Nov 12, 2026", ["Ad-free $9.99 → $11.99/mo", "With ads $5.99 → $6.99/mo"])])
        self.assertEqual([r.service_id for r in past], ["disney-plus", "netflix"])

    def test_row_label_for_missing_plan(self):
        cs = [ch("", "monthly", 12.99, 14.99, "2026-08-28", sid="apple-tv")]
        _, past = increase_rows(cs, {"apple-tv": "Apple TV"}, TODAY)
        self.assertEqual(past[0].lines, ["Apple TV $12.99 → $14.99/mo"])


class ParseTest(unittest.TestCase):
    GOOD = {"id": "a", "serviceId": "s", "country": "US", "currency": "USD", "frequency": "monthly",
            "from": 1, "to": 2, "effective": "2026-01-01", "source": "u"}

    def test_parse_skips_malformed_and_rejects_non_list(self):
        self.assertEqual(len(parse_changes({"changes": [self.GOOD, dict(self.GOOD, id="b", frequency="weekly")]})), 1)
        with self.assertRaises(ValueError):
            parse_changes({"changes": {}})

    def test_parse_fields(self):
        [c] = parse_changes({"changes": [dict(self.GOOD, plan="P", dateApprox="month")]})
        self.assertEqual((c.plan, c.old, c.new, c.effective, c.approx_month), ("P", 1.0, 2.0, date(2026, 1, 1), True))
        [c] = parse_changes({"changes": [self.GOOD]})
        self.assertEqual((c.plan, c.approx_month), ("", False))

    def test_us_changes_filters_and_sorts(self):
        cs = parse_changes({"changes": [
            dict(self.GOOD, id="b", effective="2026-05-01"), dict(self.GOOD, id="a"),
            dict(self.GOOD, id="c", country="DE"), dict(self.GOOD, id="d", serviceId="other")]})
        self.assertEqual([c.id for c in us_changes(cs, "s", {})], ["a", "b"])


if __name__ == "__main__":
    unittest.main()
