import unittest
from datetime import date

from sitegen.prices import (
    Change, chart_bars, fill_prices, glance_rows, increase_rows, money, parse_changes, per, percent, plan_cards, price_tag,
    signed, title_news, us_changes, year_summary,
)

TODAY = date(2026, 10, 25)


def ch(plan, freq, old, new, eff, approx=False, sid="x"):
    return Change(id=f"{sid}-{plan}-{freq}-{eff}", service_id=sid, plan=plan, country="US", currency="USD",
                  frequency=freq, old=old, new=new, effective=date.fromisoformat(eff), approx_month=approx,
                  source="https://example.com/source")


class SummaryTest(unittest.TestCase):
    CHANGES = [ch("Standard", "monthly", 17.99, 19.99, "2026-03-26", sid="netflix"),
               ch("Standard", "annual", 179.99, 199.99, "2026-03-26", sid="netflix"),
               ch("Individual", "monthly", 11.99, 12.99, "2026-01-15", sid="spotify"),
               ch("Family", "monthly", 22.99, 26.99, "2026-06-01", sid="youtube-premium"),
               ch("Individual", "monthly", 13.99, 15.99, "2026-06-01", sid="youtube-premium"),
               ch("Individual", "monthly", 10.99, 11.99, "2026-09-01", sid="spotify"),  # a second one
               ch("Ultimate", "monthly", 29.99, 22.99, "2026-04-22", sid="xbox"),  # a cut
               ch("Standard", "monthly", 15.49, 17.99, "2025-01-21", sid="netflix"),  # last year
               ch("Ad-free", "monthly", 9.99, 11.99, "2026-11-12", sid="discovery")]  # not yet

    def test_year_summary(self):
        s = year_summary(self.CHANGES, 2026, TODAY)
        self.assertEqual(s.increases, 4)  # netflix (one date, two plans), spotify ×2, youtube
        self.assertEqual(s.services, ["spotify", "netflix", "youtube-premium"])
        self.assertEqual(s.first_months, [("spotify", 1), ("netflix", 3), ("youtube-premium", 6)])
        self.assertEqual((s.typical, s.typical_percent), (2.0, "+11%"))  # monthly: +1, +2, +4, +2, +1
        self.assertEqual((s.biggest.service_id, s.biggest.plan), ("youtube-premium", "Family"))

    def test_empty_year(self):
        s = year_summary(self.CHANGES, 2027, TODAY)
        self.assertEqual((s.increases, s.services, s.biggest, s.typical_percent), (0, [], None, ""))

    def test_glance_rows(self):
        rows = glance_rows(self.CHANGES, {"netflix": ("Standard", "monthly")}, TODAY)
        self.assertEqual([r.service_id for r in rows], ["spotify", "youtube-premium", "xbox", "netflix", "discovery"])
        yt = rows[1]
        self.assertEqual((yt.plan, yt.now, yt.last.new), ("Individual", 15.99, 15.99))  # the cheaper plan raised that day
        xbox = rows[2]
        self.assertEqual((xbox.now, xbox.last.new < xbox.last.old), (22.99, True))  # a cut is the last change
        disc = rows[4]
        self.assertEqual((disc.now, disc.last), (9.99, None))  # only an upcoming change

    def test_percent(self):
        self.assertEqual(percent(17.99, 19.99), "+11%")
        self.assertEqual(percent(29.99, 22.99), "−23%")


class TitleNewsTest(unittest.TestCase):
    NETFLIX = [ch("Standard", "monthly", 15.49, 17.99, "2025-01-21"), ch("Standard", "monthly", 17.99, 19.99, "2026-03-26")]

    def test_recent_increase(self):
        self.assertEqual(title_news(self.NETFLIX, "Standard", "monthly", TODAY, "2026"),
                         "March price increase to $19.99/mo")
        # Another year's increase names its year.
        self.assertEqual(title_news(self.NETFLIX, "Standard", "monthly", date(2027, 2, 1), "2027"),
                         "March 2026 price increase to $19.99/mo")

    def test_upcoming_increase(self):
        changes = [ch("Ad-free", "monthly", 9.99, 11.99, "2026-11-12")]
        self.assertEqual(title_news(changes, "Ad-free", "monthly", TODAY, "2026"), "price increase to $11.99/mo on Nov 12")
        approx = [ch("Ad-free", "monthly", 9.99, 11.99, "2026-12-01", approx=True)]
        self.assertEqual(title_news(approx, "Ad-free", "monthly", TODAY, "2026"),
                         "price increase to $11.99/mo in December 2026")

    def test_no_news(self):
        self.assertIsNone(title_news(self.NETFLIX, "Standard", "monthly", date(2027, 4, 1), "2027"))  # over a year old
        self.assertIsNone(title_news([ch("Basic", "monthly", 9.99, 7.99, "2026-09-01")], "Basic", "monthly", TODAY, "2026"))
        self.assertIsNone(title_news([ch("Basic", "monthly", 9.99, 7.99, "2026-12-01")], "Basic", "monthly", TODAY, "2026"))
        self.assertIsNone(title_news(self.NETFLIX, "Premium", "monthly", TODAY, "2026"))  # another plan
        self.assertIsNone(title_news(self.NETFLIX, "Standard", "annual", TODAY, "2026"))


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
        self.assertEqual((t.kind, t.text), ("up", "Standard is now $19.99/mo · +$2 since March 2026"))

    def test_upcoming_flips_on_effective_date(self):  # Discovery+ Ad-free
        cs = [ch("Ad-free", "monthly", 9.99, 11.99, "2026-11-12")]
        self.assertEqual(price_tag(cs, "Ad-free", "monthly", "Discovery+", date(2026, 11, 11)).text,
                         "Goes up to $11.99/mo on Nov 12")
        self.assertEqual(price_tag(cs, "Ad-free", "monthly", "Discovery+", date(2026, 11, 12)).text,
                         "Ad-free is now $11.99/mo · +$2 since November 2026")

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
        self.assertEqual((t.kind, t.text), ("down", "Ultimate is now $22.99/mo · −$7 since April 2026"))
        up, past = increase_rows(cs, {"xbox-game-pass": "Xbox Game Pass"}, TODAY)
        self.assertEqual(up, [])
        self.assertEqual([r.effective for r in past], [date(2025, 10, 4)])

    def test_missing_plan_uses_service_name(self):  # Apple TV
        cs = [ch("", "monthly", 12.99, 14.99, "2026-08-28")]
        self.assertEqual(price_tag(cs, "", "monthly", "Apple TV", TODAY).text,
                         "Apple TV is now $14.99/mo · +$2 since August 2026")
        self.assertEqual(plan_cards(cs, "Apple TV", TODAY)[0].label, "Apple TV")


class CardsAndChartTest(unittest.TestCase):
    def test_monthly_and_annual_share_a_card(self):  # Peacock Premium
        cs = [ch("Premium", "monthly", 10.99, 12.99, "2026-09-17"), ch("Premium", "annual", 109.99, 129.99, "2026-09-17")]
        [c] = plan_cards(cs, "Peacock", TODAY)
        self.assertEqual((c.price, c.yearly, c.badge, c.badge_kind), ("$12.99/mo", "or $129.99/yr", "+$2 · Sep 2026", "up"))
        self.assertEqual([b.value for b in chart_bars(cs, "Premium", "monthly", TODAY)], [10.99, 12.99])

    def test_annual_only_plan(self):
        cs = [ch("Yearly", "annual", 99.0, 119.0, "2026-08-28")]
        [c] = plan_cards(cs, "X", TODAY)
        self.assertEqual((c.price, c.yearly), ("$119/yr", None))

    def test_cards_cheapest_first_with_upcoming_badge(self):  # Discovery+
        cs = [ch("Ad-free", "monthly", 8.99, 9.99, "2025-02-07"), ch("With ads", "monthly", 4.99, 5.99, "2025-02-07"),
              ch("Ad-free", "monthly", 9.99, 11.99, "2026-11-12"), ch("With ads", "monthly", 5.99, 6.99, "2026-11-12")]
        cards = plan_cards(cs, "Discovery+", TODAY)
        self.assertEqual([(c.label, c.price, c.badge) for c in cards],
                         [("With ads", "$5.99/mo", "→ $6.99 on Nov 12"), ("Ad-free", "$9.99/mo", "→ $11.99 on Nov 12")])

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


    def test_stale_yearly_price_is_hidden(self):  # Disney+ Premium: yearly last changed a year before monthly
        cs = [ch("Premium", "monthly", 15.99, 18.99, "2025-10-21"), ch("Premium", "annual", 159.99, 189.99, "2025-10-21"),
              ch("Premium", "monthly", 18.99, 21.49, "2026-10-21")]
        [c] = plan_cards(cs, "Disney+", TODAY)
        self.assertEqual((c.price, c.yearly), ("$21.49/mo", None))


class FillPricesTest(unittest.TestCase):
    CS = [ch("Premium", "monthly", 10.99, 12.99, "2026-09-17"), ch("Premium", "annual", 109.99, 129.99, "2026-09-17"),
          ch("", "monthly", 12.99, 14.99, "2026-08-28")]

    def test_tokens(self):
        self.assertEqual(fill_prices("{price:Premium}, or {yearly:Premium}; plain {monthly:}", self.CS, TODAY),
                         "$12.99/mo, or $129.99/yr; plain $14.99/mo")

    def test_upcoming_change_not_used_before_its_date(self):
        cs = [ch("Ad-free", "monthly", 9.99, 11.99, "2026-11-12")]
        self.assertEqual(fill_prices("{price:Ad-free}", cs, TODAY), "$9.99/mo")
        self.assertEqual(fill_prices("{price:Ad-free}", cs, date(2026, 11, 12)), "$11.99/mo")

    def test_unknown_plan_raises(self):
        with self.assertRaises(ValueError):
            fill_prices("{price:Ultra}", self.CS, TODAY)
        with self.assertRaises(ValueError):
            fill_prices("{yearly:}", self.CS, TODAY)


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
                         [("discovery-plus", "Nov 12, 2026", ["Ad-free $9.99 → $11.99/mo (+$2, +20%)", "With ads $5.99 → $6.99/mo (+$1, +17%)"])])
        self.assertEqual([r.service_id for r in past], ["disney-plus", "netflix"])

    def test_row_label_for_missing_plan(self):
        cs = [ch("", "monthly", 12.99, 14.99, "2026-08-28", sid="apple-tv")]
        _, past = increase_rows(cs, {"apple-tv": "Apple TV"}, TODAY)
        self.assertEqual(past[0].lines, ["Apple TV $12.99 → $14.99/mo (+$2, +15%)"])


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
